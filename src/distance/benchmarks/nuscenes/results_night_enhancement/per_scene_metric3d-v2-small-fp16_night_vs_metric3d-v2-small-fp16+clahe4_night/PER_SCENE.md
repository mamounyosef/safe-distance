# Per-scene comparison: `metric3d-v2-small-fp16+clahe4_p10` vs `metric3d-v2-small-fp16_p10`

Generated automatically from `per_scene.json` by `compare_per_scene.py`. Do not edit by hand.

In-path objects, within 10% of the nearest surface.
The unit of evidence is the scene: frames of one scene show the same objects many times.

|  |  |
| --- | --- |
| Scenes / paired objects | 3 / 94 |
| Baseline within 10% | 52 (55.3%) |
| Candidate within 10% | 77 (81.9%) |
| Gain | +26.6% (95% CI -9.8% to +63.4%, resampling scenes) |
| Scenes better / worse / equal | 2 / 1 / 0 |
| Sign test over scenes, p | 1 |
| Share of the gain from the single best scene | 104.0% |
| Git commit | `250f2b1` |

## Per scene

| Scene | Objects | Baseline within 10% | Candidate within 10% | Change |
| --- | --- | --- | --- | --- |
| scene-1077 | 41 | 8 | 34 | +26 |
| scene-1094 | 41 | 36 | 32 | -4 |
| scene-1100 | 12 | 8 | 11 | +3 |
