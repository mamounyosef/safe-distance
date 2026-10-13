"""20 MM-AU crash clips with their labels drawn on, as ONE video (this PC, free).

MM-AU's frames are in .tar.gz archives split into 2 GB parts on Hugging Face, which can
only be read from the start. So we STREAM the start of each of its 6 archives (nothing
saved except the clips we keep) and keep a few clips from each: a spread over MM-AU's
sources and crash types, not a fully random draw.

Labels per clip (from MM-AU's spreadsheets): crash type, abnormal start frame (danger
begins), accident frame (collision), abnormal end frame. Shown:
    frames relative to the collision, "ABNORMAL" from the abnormal start, red frame at the collision,
    a 1.5 s freeze at the abnormal start and at the collision.
MM-AU does not state its frame rate, so clips play at PLAY_FPS and times are given in frames.

RUN IT (from the repo root):

    .venv\\Scripts\\python.exe src\\risk\\data\\data_code\\mmau_samples.py

Output: C:\\Users\\mamou\\Downloads\\mmau_samples.mp4 (+ mmau_samples.json).
"""

from __future__ import annotations

import io
import json
import sys
import tarfile
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import requests
from huggingface_hub import get_token

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sample_video import Writer, card, text  # noqa: E402

# ---- CONFIG ----
BASE = "https://huggingface.co/datasets/JeffreyChou/MM-AU/resolve/main/"
META = Path(r"C:\safe-distance-data\mmau\meta")
OUT = Path.home() / "Downloads" / "mmau_samples.mp4"
# archive -> (its parts, clips to keep, keep every Nth clip met while streaming)
ARCHIVES = {
    "DADA-2000": ([f"DADA-2000_chunks/DADA2000.part_a{c}" for c in "abcd"], 3, 1),   # PNG, about 0.3 GB per clip
    "CAP 1-10": ([f"CAP-DATA_chunks/1-10/1-10.part_a{c}" for c in "abc"], 4, 5),
    "CAP 11": ([f"CAP-DATA_chunks/11/11.part_a{c}" for c in "abc"], 4, 5),
    "CAP 12-42": ([f"CAP-DATA_chunks/12-42/12-42.part_a{c}" for c in "abc"], 3, 5),
    "CAP 43": ([f"CAP-DATA_chunks/43/43.part_a{c}" for c in "abc"], 3, 5),
    "CAP 44-62": ([f"CAP-DATA_chunks/44-62/44-62.part_a{c}" for c in "abc"], 3, 5),
}
SIZE, PLAY_FPS = (1280, 720), 20.0
FREEZE_S, TITLE_S = 1.5, 1.5
# ----------------


class Parts(io.RawIOBase):
    """The archive's parts, one after another, read as one stream over HTTP (nothing written to disk)."""

    def __init__(self, parts: list[str]):
        self.parts, self.resp, self.it, self.buf = list(parts), None, None, b""
        self.session = requests.Session()
        tok = get_token()
        if tok:
            self.session.headers["Authorization"] = f"Bearer {tok}"

    def readable(self) -> bool:
        return True

    def readinto(self, b) -> int:
        while not self.buf:
            if self.it is None:
                if not self.parts:
                    return 0
                self.resp = self.session.get(BASE + self.parts.pop(0), stream=True, timeout=120)
                self.resp.raise_for_status()
                self.it = self.resp.iter_content(1 << 20)
            try:
                self.buf = next(self.it)
            except StopIteration:
                self.it = None
        n = min(len(b), len(self.buf))
        b[:n], self.buf = self.buf[:n], self.buf[n:]
        return n


def labels() -> dict[tuple[int, int], dict]:
    """(type folder, video number) -> that clip's label row, from both spreadsheets."""
    out = {}
    types = pd.read_excel(META / "cap_text_annotations.xls", sheet_name="Sheet1")
    names = dict(zip(types.iloc[:, 0], types.iloc[:, 1]))
    for f, sheet in (("dada_text_annotations.xlsx", "Sheet1"), ("cap_text_annotations.xls", "annotation file")):
        for _, r in pd.read_excel(META / f, sheet_name=sheet).iterrows():
            out[(int(r["type"]), int(r["video"]))] = {
                "type_name": names.get(r["type"], "?"), "start": int(r["abnormal start frame"]),
                "collision": int(r["accident frame"]), "end": int(r["abnormal end frame"]),
                "total": int(r["total frames"]), "light": "night" if r["light(day,night)1-2"] == 2 else "day"}
    return out


def clips_from(parts: list[str], keep: int, every: int):
    """Yield (type, video, [frame bytes]) for every `every`-th clip met in the archive, `keep` of them."""
    tf = tarfile.open(fileobj=io.BufferedReader(Parts(parts), 1 << 22), mode="r|gz")
    current, frames, seen, kept = None, [], 0, 0
    for m in tf:
        p = Path(m.name).parts
        if not m.isfile() or "images" not in p:
            continue
        i = p.index("images")
        key = (int(p[i - 2]), int(p[i - 1]))                   # <type>/<video>/images/<frame>
        if key != current:
            if current is not None and frames:
                yield current, frames
                kept += 1
                if kept >= keep:
                    return
            current, frames = key, []
            seen += 1
        if (seen - 1) % every == 0:                            # only read frames of clips we keep
            frames.append((p[-1], tf.extractfile(m).read()))
    if frames and kept < keep:
        yield current, frames


def main() -> None:
    lab = labels()
    wr, shown, n_total = Writer(OUT, SIZE, PLAY_FPS), [], sum(k for _, k, _ in ARCHIVES.values())
    for arch, (parts, keep, every) in ARCHIVES.items():
        for key, frames in clips_from(parts, keep, every):
            L = lab.get(key)
            k = len(shown) + 1
            frames.sort()
            print(f"[{k}/{n_total}] {arch} type {key[0]} video {key[1]}: {len(frames)} frames, "
                  f"label {'found' if L else 'MISSING'}", flush=True)
            if not L:
                continue
            wr.write(card(SIZE, [f"MM-AU clip {k}/{n_total}   ({arch}, video {key[1]})",
                                 f"type {key[0]}: {L['type_name']}   {L['light']}",
                                 f"abnormal start frame {L['start']}, collision frame {L['collision']}, "
                                 f"{len(frames)} frames (frame rate not stated by MM-AU)"]), TITLE_S)
            for j, (_, data) in enumerate(frames, 1):              # MM-AU frame numbers start at 1
                img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
                img = cv2.resize(img, SIZE)
                d = j - L["collision"]
                text(img, f"{d:+d} frames {'before' if d < 0 else 'after'} collision", (15, 40), 1.0)
                if L["start"] <= j < L["collision"]:
                    text(img, "ABNORMAL (labelled: danger begins)", (15, 85), 0.9, (0, 200, 255))
                if j >= L["collision"]:
                    cv2.rectangle(img, (0, 0), (SIZE[0] - 1, SIZE[1] - 1), (0, 0, 255), 10)
                    text(img, "COLLISION (labelled)", (15, 85), 0.9, (0, 0, 255))
                wr.write(img, FREEZE_S if j in (L["start"], L["collision"]) else 0.0)
            shown.append({"n": k, "archive": arch, "type": key[0], "video": key[1], **L, "frames": len(frames)})
    wr.close()
    OUT.with_suffix(".json").write_text(json.dumps(shown, indent=1, ensure_ascii=False))
    print(f"saved {OUT} ({len(shown)} clips)")


if __name__ == "__main__":
    main()
