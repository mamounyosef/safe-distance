# Per-scene comparison: `metric3d-v2-small-fp16+clahe4_p10` vs `metric3d-v2-small-fp16_p10`

Generated automatically from `per_scene.json` by `compare_per_scene.py`. Do not edit by hand.

In-path objects, within 10% of the nearest surface.
The unit of evidence is the scene: frames of one scene show the same objects many times.

|  |  |
| --- | --- |
| Scenes / paired objects | 69 / 1680 |
| Baseline within 10% | 856 (50.9%) |
| Candidate within 10% | 1145 (68.2%) |
| Gain | +17.2% (95% CI +10.7% to +23.7%, resampling scenes) |
| Scenes better / worse / equal | 45 / 12 / 12 |
| Sign test over scenes, p | 1.3e-05 |
| Share of the gain from the single best scene | 9.3% |
| Git commit | `83793d9` |

## Per scene

| Scene | Objects | Baseline within 10% | Candidate within 10% | Change |
| --- | --- | --- | --- | --- |
| scene-1007 | 8 | 6 | 8 | +2 |
| scene-1008 | 1 | 0 | 0 | +0 |
| scene-1010 | 1 | 1 | 1 | +0 |
| scene-1011 | 1 | 1 | 1 | +0 |
| scene-1012 | 11 | 8 | 5 | -3 |
| scene-1014 | 1 | 0 | 0 | +0 |
| scene-1016 | 6 | 1 | 1 | +0 |
| scene-1017 | 43 | 15 | 34 | +19 |
| scene-1018 | 17 | 2 | 13 | +11 |
| scene-1019 | 29 | 14 | 14 | +0 |
| scene-1020 | 2 | 0 | 2 | +2 |
| scene-1021 | 1 | 1 | 0 | -1 |
| scene-1022 | 5 | 0 | 2 | +2 |
| scene-1023 | 12 | 5 | 9 | +4 |
| scene-1024 | 15 | 6 | 11 | +5 |
| scene-1044 | 43 | 13 | 39 | +26 |
| scene-1045 | 41 | 35 | 41 | +6 |
| scene-1046 | 40 | 34 | 40 | +6 |
| scene-1047 | 41 | 40 | 41 | +1 |
| scene-1048 | 40 | 34 | 33 | -1 |
| scene-1049 | 38 | 12 | 27 | +15 |
| scene-1050 | 39 | 10 | 28 | +18 |
| scene-1051 | 33 | 1 | 18 | +17 |
| scene-1053 | 2 | 0 | 0 | +0 |
| scene-1054 | 12 | 1 | 2 | +1 |
| scene-1055 | 3 | 2 | 2 | +0 |
| scene-1056 | 4 | 0 | 3 | +3 |
| scene-1062 | 7 | 6 | 6 | +0 |
| scene-1063 | 4 | 0 | 0 | +0 |
| scene-1064 | 12 | 5 | 9 | +4 |
| scene-1065 | 32 | 7 | 21 | +14 |
| scene-1066 | 32 | 9 | 16 | +7 |
| scene-1067 | 42 | 4 | 30 | +26 |
| scene-1068 | 42 | 9 | 23 | +14 |
| scene-1069 | 37 | 23 | 32 | +9 |
| scene-1070 | 41 | 28 | 36 | +8 |
| scene-1071 | 45 | 30 | 40 | +10 |
| scene-1072 | 57 | 19 | 46 | +27 |
| scene-1073 | 40 | 23 | 25 | +2 |
| scene-1074 | 40 | 30 | 34 | +4 |
| scene-1075 | 40 | 33 | 35 | +2 |
| scene-1076 | 41 | 26 | 28 | +2 |
| scene-1078 | 10 | 5 | 10 | +5 |
| scene-1079 | 48 | 28 | 37 | +9 |
| scene-1080 | 66 | 49 | 56 | +7 |
| scene-1081 | 39 | 14 | 24 | +10 |
| scene-1082 | 40 | 0 | 1 | +1 |
| scene-1083 | 40 | 14 | 24 | +10 |
| scene-1084 | 27 | 11 | 13 | +2 |
| scene-1085 | 14 | 4 | 7 | +3 |
| scene-1086 | 3 | 3 | 0 | -3 |
| scene-1087 | 3 | 1 | 3 | +2 |
| scene-1088 | 15 | 1 | 12 | +11 |
| scene-1090 | 2 | 2 | 1 | -1 |
| scene-1091 | 14 | 13 | 13 | +0 |
| scene-1092 | 28 | 26 | 18 | -8 |
| scene-1093 | 41 | 39 | 27 | -12 |
| scene-1095 | 20 | 16 | 14 | -2 |
| scene-1096 | 31 | 22 | 14 | -8 |
| scene-1097 | 37 | 24 | 20 | -4 |
| scene-1098 | 24 | 18 | 21 | +3 |
| scene-1099 | 34 | 23 | 24 | +1 |
| scene-1101 | 2 | 0 | 1 | +1 |
| scene-1102 | 21 | 17 | 8 | -9 |
| scene-1104 | 48 | 11 | 19 | +8 |
| scene-1105 | 7 | 3 | 3 | +0 |
| scene-1108 | 18 | 0 | 1 | +1 |
| scene-1109 | 22 | 2 | 3 | +1 |
| scene-1110 | 25 | 16 | 15 | -1 |
