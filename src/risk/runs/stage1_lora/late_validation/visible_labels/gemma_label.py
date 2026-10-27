"""Gemma 4 31B (Ollama Cloud) labels the visible-danger windows: the same question the person answers.

For each window: the 16 frames (960 x 540, oldest first) + the system prompt from config.yaml, thinking ON,
temperature 0, the answer forced into JSON (label yes / no / unsure, first_visible_frame, what, reason).
Saved per window as soon as it is done (a re-run skips finished windows), with the reasoning ("thinking"),
the time it took and the token counts.

Speed: one worker per API key, running in parallel; each key takes every other window.
Keys are read ONLY from the environment variables in config.yaml (api_key_env, then <api_key_env>_2, _3, ...).

Output: <data_dir>/gemma_labels.json  (NOT in git: with set.json it says which windows are crashes)

RUN IT (from the repo root; make_set.py first):
    .venv\\Scripts\\python.exe src\\risk\\runs\\stage1_lora\\late_validation\\visible_labels\\gemma_label.py [--batch 1] [--limit N]
"""

import argparse
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml
from ollama import Client

HERE = Path(__file__).resolve().parent
CFG = yaml.safe_load((HERE / "config.yaml").read_text(encoding="utf-8"))
G = CFG["gemma"]

# ---- CONFIG ----
DATA = Path(CFG["set"]["data_dir"])
OUT = DATA / "gemma_labels.json"
SCHEMA = {"type": "object",
          "properties": {"label": {"type": "string", "enum": ["yes", "no", "unsure"]},
                         "first_visible_frame": {"type": ["integer", "null"], "minimum": 1, "maximum": 16},
                         "what": {"type": "string"}, "reason": {"type": "string"}},
          "required": ["label", "first_visible_frame", "what", "reason"]}
# ----------------

LOCK = threading.Lock()


def keys() -> list[str]:
    """Every API key found in the environment: OLLAMA_API_KEY, OLLAMA_API_KEY_2, ..."""
    found, base = [], G["api_key_env"]
    for name in [base] + [f"{base}_{k}" for k in range(2, 10)]:
        if os.environ.get(name):
            found.append(os.environ[name])
    if not found:
        raise SystemExit(f"no API key: set {base} (and {base}_2 for a second worker)")
    return found


def load() -> dict:
    return json.loads(OUT.read_text()) if OUT.exists() else {}


def save_one(name: str, row: dict) -> None:
    """Add one window's answer to the file at once (atomic write, one writer at a time)."""
    with LOCK:
        done = load()
        done[name] = row
        tmp = OUT.with_suffix(".tmp")
        tmp.write_text(json.dumps(done, indent=1))
        tmp.replace(OUT)


def label_one(client: Client, worker: int, it: dict) -> None:
    """Ask Gemma about one window and save the answer."""
    frames = [str(p) for p in sorted((DATA / "frames" / it["name"]).glob("*.jpg"))]
    if len(frames) != 16:
        raise SystemExit(f"{it['name']}: {len(frames)} frames, expected 16 (run make_set.py)")
    t0 = time.time()
    r = client.chat(model=G["model"], think=G["think"], format=SCHEMA, options={"temperature": G["temperature"]},
                    messages=[{"role": "system", "content": CFG["system_prompt"]},
                              {"role": "user", "content": CFG["user_prompt"], "images": frames}])
    secs = time.time() - t0
    try:
        ans = json.loads(r.message.content)
    except json.JSONDecodeError:
        ans = {"label": None, "parse_error": r.message.content[:500]}
    row = {**ans, "thinking": r.message.thinking, "secs": round(secs, 1), "worker": worker,
           "prompt_tokens": r.prompt_eval_count, "output_tokens": r.eval_count,
           "model": G["model"], "think": G["think"], "at": time.strftime("%Y-%m-%d %H:%M:%S")}
    save_one(it["name"], row)
    print(f"  {it['name']}  worker {worker}  {secs:5.1f} s  label {ans.get('label')!s:7s} "
          f"tokens in {r.prompt_eval_count} out {r.eval_count}  | {ans.get('what', '')[:60]}", flush=True)


def worker_loop(worker: int, key: str, items: list[dict]) -> None:
    """One API key works through its share of the windows; a failed call is retried twice, then skipped."""
    client = Client(host=G["host"], headers={"Authorization": "Bearer " + key})
    for it in items:
        for attempt in range(3):
            try:
                label_one(client, worker, it)
                break
            except Exception as e:                           # network / rate limit: wait and try again
                print(f"  {it['name']}  worker {worker}  attempt {attempt + 1} failed: {type(e).__name__}: "
                      f"{str(e)[:200]}", flush=True)
                if getattr(e, "status_code", None) in (401, 402, 403):   # no credit / bad key: retrying cannot help
                    print(f"  worker {worker}: stopping (status {e.status_code})", flush=True)
                    return
                time.sleep(10 * (attempt + 1))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=1, help="1 = the 55 windows the person also labels; 2 = the rest")
    ap.add_argument("--limit", type=int, default=0, help="only the first N windows still to do (0 = all)")
    a = ap.parse_args()
    done = load()
    todo = [it for it in json.loads((DATA / "set.json").read_text()) if it["batch"] == a.batch and it["name"] not in done]
    if a.limit:
        todo = todo[:a.limit]
    ks = keys()
    print(f"{len(todo)} windows to do (batch {a.batch}), {len(ks)} API key(s) in parallel, model {G['model']}, "
          f"thinking {G['think']}")
    t0 = time.time()
    with ThreadPoolExecutor(len(ks)) as pool:
        for w, k in enumerate(ks, 1):
            pool.submit(worker_loop, w, k, todo[w - 1::len(ks)])   # each key takes every other window
    done = load()
    times = [done[it["name"]]["secs"] for it in todo if it["name"] in done]
    print(f"finished {len(times)}/{len(todo)} in {time.time() - t0:.0f} s"
          + (f"; per window: mean {sum(times) / len(times):.1f} s, max {max(times):.1f} s" if times else ""))


if __name__ == "__main__":
    main()
