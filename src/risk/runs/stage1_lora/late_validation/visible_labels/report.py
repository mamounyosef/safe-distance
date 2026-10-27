"""Visible-danger labelling report (this PC, free): person vs Gemma, both vs the truth, and the model's catch rate
on the crash windows where the danger is visible.

  agreement      person vs Gemma on batch 1: % same answer, Cohen's kappa (agreement beyond luck; 1 perfect, 0 luck)
  vs truth       how often each says "yes" on real crash windows and on the decoys (normal windows)
  visible        crash windows the PERSON marked "yes" (danger visible) -> the stage 1 model's catch rate on them
                 (step 1000, late-validation predictions), next to its catch rate on all of them

Windows the person flags as bad examples (BAD_EXAMPLES below, e.g. blurry footage) are listed and left out of the
"visible" numbers; the agreement numbers are given with and without them.

Inputs:  <data_dir>/set.json, human_labels.json, gemma_labels.json; late_validation/results/predictions/step1000.npz
Output:  results/report.json (counts and rates only, in git) and a printed summary

RUN IT (from the repo root):
    python src\\risk\\runs\\stage1_lora\\late_validation\\visible_labels\\report.py
"""

import json
from collections import Counter
from pathlib import Path

import numpy as np
import yaml

HERE = Path(__file__).resolve().parent
LV = HERE.parent
CFG = yaml.safe_load((HERE / "config.yaml").read_text(encoding="utf-8"))
DATA = Path(CFG["set"]["data_dir"])
STEP = 1000                                        # the chosen stage 1 checkpoint
THRESHOLDS = (0.5, 0.8, 0.9)
BAD_EXAMPLES = {"w022": "blurry lights, bad footage (person, 2026-10-27)",
                "w253": "video upside down (person, 2026-10-27)"}
GROUP_S = {0: 0.5, 1: 1.0, 2: 1.5}                 # Nexar group -> clip stops this long before the crash
ANSWERS = ("yes", "no", "unsure")


def kappa(a: list[str], b: list[str]) -> float:
    """Cohen's kappa: (observed agreement - agreement expected by luck) / (1 - agreement expected by luck)."""
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] / n * cb[k] / n for k in ANSWERS)
    return float((po - pe) / (1 - pe)) if pe < 1 else float("nan")


def agreement(rows: list[dict]) -> dict:
    a, b = [r["person"] for r in rows], [r["gemma"] for r in rows]
    table = {p: {g: sum(1 for r in rows if r["person"] == p and r["gemma"] == g) for g in ANSWERS} for p in ANSWERS}
    return {"windows": len(rows), "same_answer_pct": round(100 * sum(x == y for x, y in zip(a, b)) / len(rows), 1),
            "cohens_kappa": round(kappa(a, b), 3), "person_rows_vs_gemma_columns": table}


def main() -> None:
    items = {it["name"]: it for it in json.loads((DATA / "set.json").read_text())}
    human = json.loads((DATA / "human_labels.json").read_text())
    gemma = json.loads((DATA / "gemma_labels.json").read_text())
    p = np.load(LV / f"results/predictions/step{STEP}.npz", allow_pickle=True)
    risk_of = dict(zip([str(i) for i in p["ids"]], 1.0 / (1.0 + np.exp(-p["logits"]))))

    rows = []
    for name, it in items.items():
        if it["batch"] != 1:
            continue
        rid = f"nexar_crash|{it['clip']}|{it['end_cache_frame']}"
        rows.append({"name": name, "truth": it["kind"], "person": human.get(name, {}).get("label"),
                     "gemma": gemma.get(name, {}).get("label"), "bad": name in BAD_EXAMPLES,
                     "risk": float(risk_of[rid]) if it["kind"] == "crash" else None})
    missing = [r["name"] for r in rows if r["person"] is None or r["gemma"] is None]
    both = [r for r in rows if r["person"] and r["gemma"]]

    vs_truth = {}
    for who in ("person", "gemma"):
        vs_truth[who] = {t: dict(Counter(r[who] for r in both if r["truth"] == t)) for t in ("crash", "decoy")}

    crash = [r for r in rows if r["truth"] == "crash" and r["person"] and not r["bad"]]
    visible = [r for r in crash if r["person"] == "yes"]
    caught = {}
    for t in THRESHOLDS:
        caught[str(t)] = {"all_crash_windows_pct": round(100 * np.mean([r["risk"] > t for r in crash]), 1),
                          "visible_by_person_pct": round(100 * np.mean([r["risk"] > t for r in visible]), 1)
                          if visible else None}

    report = {"what": "visible-danger labels on late-validation crash windows ending 1.5 s before the crash; "
                      "person vs Gemma 4 31B; stage 1 step 1000 catch rate where danger is visible",
              "batch1_windows": len(rows), "missing_labels": missing, "bad_examples": BAD_EXAMPLES,
              "agreement_all": agreement(both),
              "agreement_without_bad": agreement([r for r in both if not r["bad"]]),
              "answers_vs_truth": vs_truth,
              "crash_windows_used": len(crash), "visible_by_person": len(visible),
              "visible_share_pct": round(100 * len(visible) / len(crash), 1) if crash else None,
              "visible_share_estimate_from_train_alerts_pct": 47.1,
              "model_step": STEP, "caught": caught}
    # --- one window per clip (last frame only, Nexar's own setup): every labelled last-frame window, all batches ---
    last = []
    for name, it in items.items():
        if name not in human or it["end_back"] != 0 or name in BAD_EXAMPLES:
            continue
        r = None
        if it["kind"] == "crash":
            r = float(risk_of[f"nexar_crash|{it['clip']}|{it['end_cache_frame']}"])
        last.append({"name": name, "truth": it["kind"], "group": it["nexar_group"], "person": human[name]["label"],
                     "risk": r})
    per_timing = {}
    for g, sec in GROUP_S.items():
        rs = [r for r in last if r["truth"] == "crash" and r["group"] == g]
        vis = [r for r in rs if r["person"] == "yes"]
        per_timing[f"{sec}s"] = {
            "labelled": len(rs), "visible_yes": len(vis), "not_visible_no": sum(r["person"] == "no" for r in rs),
            "unsure": sum(r["person"] == "unsure" for r in rs),
            "visible_pct": round(100 * len(vis) / len(rs), 1) if rs else None,
            **{f"caught_all_pct_at_{t}": round(100 * np.mean([r["risk"] > t for r in rs]), 1) if rs else None
               for t in THRESHOLDS},
            **{f"caught_visible_pct_at_{t}": round(100 * np.mean([r["risk"] > t for r in vis]), 1) if vis else None
               for t in THRESHOLDS}}
    decoys = [r for r in last if r["truth"] == "decoy"]
    report["last_frame_policy"] = {"per_timing": per_timing,
                                   "decoys_labelled": len(decoys),
                                   "decoys_person": dict(Counter(r["person"] for r in decoys))}
    (HERE / "results" / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\nONE WINDOW PER CLIP (last frame), all batches, bad examples left out:")
    for k, v in per_timing.items():
        print(f"  {k}: labelled {v['labelled']}, visible {v['visible_yes']} ({v['visible_pct']}%), "
              f"no {v['not_visible_no']}, unsure {v['unsure']} | caught at 0.5/0.8/0.9: all "
              f"{v['caught_all_pct_at_0.5']}/{v['caught_all_pct_at_0.8']}/{v['caught_all_pct_at_0.9']}%, visible "
              f"{v['caught_visible_pct_at_0.5']}/{v['caught_visible_pct_at_0.8']}/{v['caught_visible_pct_at_0.9']}%")
    print(f"  decoys: {len(decoys)} labelled, person: {report['last_frame_policy']['decoys_person']}")

    print(f"batch 1: {len(rows)} windows, missing labels: {missing or 'none'}")
    for k in ("agreement_all", "agreement_without_bad"):
        a = report[k]
        print(f"{k}: {a['windows']} windows, same answer {a['same_answer_pct']}%, kappa {a['cohens_kappa']}")
        print("   person (rows) vs Gemma (columns) yes/no/unsure:",
              {pk: list(v.values()) for pk, v in a["person_rows_vs_gemma_columns"].items()})
    print("answers vs truth:", json.dumps(vs_truth))
    print(f"crash windows (without bad): {len(crash)}; person says danger visible: {len(visible)} "
          f"({report['visible_share_pct']}%; estimate from train alerts: 47.1%)")
    for t, v in caught.items():
        print(f"  model step {STEP} at {t}: caught {v['all_crash_windows_pct']}% of all, "
              f"{v['visible_by_person_pct']}% of the visible ones")


if __name__ == "__main__":
    main()
