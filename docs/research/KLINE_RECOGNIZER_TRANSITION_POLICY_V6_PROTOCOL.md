# K-line recognizer transition policy v6 protocol

Goal: improve the same recognizer A by changing only its state-switch policy. No new evaluator, no new label source, no new feature family.

Baseline:
- v5 linear recognizer remains fixed.
- v3 independent judge remains frozen benchmark.

Research question:
Can transition decisions improve when switch rules depend on transition type rather than one universal threshold?

Transition classes:
1. Trend -> Range: slow confirmation. Avoid false exits caused by normal pullbacks.
2. Range -> Trend: stronger confirmation. Avoid false breakouts.
3. Normal -> Shock: fast response. Risk states require early detection.
4. Shock -> Recovery: slow release. Avoid premature recovery.

Allowed tuning dimensions only:
- transition type;
- switch probability margin;
- minimum new-state probability;
- confirmation bars.

Forbidden:
- adding new chart features;
- changing classifier model;
- changing benchmark labels;
- tuning on 2025;
- adding new evaluators.

Selection:
- rolling pre-2025 data only;
- optimize transition F1 while maintaining point-state floors:
  - balanced accuracy >= 0.75;
  - macro F1 >= 0.72.

Final diagnostics:
- false transitions/day;
- transition precision/recall/F1;
- transition delay;
- point-state metrics.

Success target:
- transition F1 improvement over v5;
- false transitions materially reduced;
- point-state accuracy retained.
