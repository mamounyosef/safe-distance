"""What MM-AU's labels contain, counted from its annotation files (this PC, free).

MM-AU (Fang et al., CVPR 2024, CC BY-NC 4.0, Hugging Face JeffreyChou/MM-AU):
11,730 dashcam accident videos from two sources, DADA-2000 (1,962) and CAP (9,768).
Per video: accident type (1 of 58, "ego-car hits ..." or between other road users),
whether an accident occurs, the frames where the abnormal part starts, where the
collision happens, and where it ends. Separately, object boxes (MMAU_Detv1, COCO style).

RUN IT (from the repo root, after downloading the annotation files to MMAU_META):

    .venv\\Scripts\\python.exe src\\risk\\data\\data_code\\mmau_stats.py

Writes src/risk/data/mmau_stats.json and prints a summary.
"""

from __future__ import annotations

import json
import zipfile
from collections import Counter
from pathlib import Path

import pandas as pd

MMAU_META = Path(r"C:\safe-distance-data\mmau\meta")
OUT = Path(__file__).resolve().parents[1] / "mmau_stats.json"


def sheets() -> dict[str, pd.DataFrame]:
    """The per-video annotation tables of both sources, with the same column names."""
    dada = pd.read_excel(MMAU_META / "dada_text_annotations.xlsx", sheet_name="Sheet1")
    cap = pd.read_excel(MMAU_META / "cap_text_annotations.xls", sheet_name="annotation file")
    return {"DADA-2000": dada, "CAP": cap}


def main() -> None:
    types = pd.read_excel(MMAU_META / "cap_text_annotations.xls", sheet_name="Sheet1")
    type_text = dict(zip(types.iloc[:, 0], types.iloc[:, 1]))
    res = {"types": {int(k): v for k, v in type_text.items()}, "sources": {}}
    for src, df in sheets().items():
        occ = df["whether an accident occurred (1/0)"]
        tai, tco = df["abnormal start frame"], df["accident frame"]
        gap = (tco - tai)[occ == 1]                                    # frames from abnormal start to collision
        ego = df["type"].map(lambda t: str(type_text.get(t, "")).startswith("ego-car"))
        res["sources"][src] = {
            "videos": len(df), "accident_occurred": int((occ == 1).sum()),
            "ego_car_involved": int(ego.sum()), "other_road_users_only": int((~ego).sum()),
            "types_used": int(df["type"].nunique()),
            "total_frames": {"median": float(df["total frames"].median()), "p10": float(df["total frames"].quantile(.1)),
                             "p90": float(df["total frames"].quantile(.9))},
            "frames_abnormal_start_to_collision": {"median": float(gap.median()), "p10": float(gap.quantile(.1)),
                                                   "p90": float(gap.quantile(.9))},
            "top_types": {f"{t}: {type_text.get(t)}": int(n) for t, n in Counter(df["type"]).most_common(12)},
            "light": {str(k): int(v) for k, v in Counter(df["light(day,night)1-2"]).items()}}
    # Object boxes (COCO style): categories, how many images, whether they say which object crashes.
    z = zipfile.ZipFile(MMAU_META / "MMAU_Detv1" / "labels.zip")
    coco = json.loads(z.read("labels/test.json"))
    res["boxes_test_split"] = {"keys": list(coco), "categories": coco.get("categories"),
                               "images": len(coco.get("images", [])), "annotations": len(coco.get("annotations", [])),
                               "example_image": coco["images"][0] if coco.get("images") else None,
                               "example_annotation": coco["annotations"][0] if coco.get("annotations") else None}
    txt = [n for n in z.namelist() if n.endswith(".txt")]
    res["boxes_txt_example"] = {"file": txt[0], "content": z.read(txt[0]).decode()[:400], "txt_files": len(txt)}
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str))
    print(json.dumps(res, indent=1, ensure_ascii=False, default=str)[:7000])


if __name__ == "__main__":
    main()
