# Historical contribution audit — K-line recognizer v6 to v9

Date: 2026-09-09

Purpose: prevent the research program from treating a non-promoted challenger as if it contributed nothing. This audit separates complete-version promotion from reusable partial contribution.

Authority rule:
- the current champion remains the best complete recognizer;
- a failed challenger may still produce positive or negative reusable evidence;
- a retained contribution may be integrated only through a new challenger;
- no contribution changes the champion by itself.

## V6 — type-specific transition policy

Complete-version result: **not promoted**.

The selected typed policy slightly improved point-state recognition versus the then-v5 champion, but made transition quality and false-switch control worse overall.

Retained positive contribution: **transition direction asymmetry is real, especially Shock-exit stickiness**.

Evidence from the frozen v6 candidate table shows that, holding the other typed rules fixed, making Shock exit stricter repeatedly reduced false transitions and improved transition F1, but at the cost of point-state accuracy. One representative comparison:
- less-sticky Shock exit: min balanced accuracy about 0.759, min transition F1 about 0.145, max false transitions/day about 1.434;
- more-sticky Shock exit: min balanced accuracy about 0.736, min transition F1 about 0.158, max false transitions/day about 1.219.

Interpretation:
- Shock exit should not necessarily be treated the same as ordinary state changes;
- hard extra confirmation bars are too costly;
- future use, if any, should be a soft state-dependent inertia/prior, not a hard typed decoder.

Retained negative contribution:
- hand-written type-specific confirmation counts are not a good final architecture.

## V7 — causal Markov persistence filter

Complete-version result: **not promoted**.

Best point-eligible candidate: `markov_eta2_beta2`.

Compared with v5 pre-2025 worst-cell metrics:
- min balanced accuracy: 0.754 -> about 0.774;
- min macro F1: 0.756 -> about 0.780;
- min transition F1: 0.179 -> about 0.118;
- max false transitions/day: 1.240 -> about 2.095.

Retained positive contribution: **previous-state / persistence information contains useful current-state classification signal**.

Interpretation:
- state-history prior can improve static four-state classification;
- the failure came from allowing the Markov posterior argmax to become the final state sequence, which made the recognizer too switchy;
- future use, if revisited, should be as a low-weight auxiliary prior or feature blended into the primary classifier, never as a replacement decoder without new evidence.

Retained negative contribution:
- direct causal Markov forward-filter argmax is rejected as a final decoder for this recognizer family.

## V8 — learned switch gate

Complete-version result: **not promoted**; no candidate met point-state eligibility floors.

Retained structural contribution: **true state changes are an extreme rare-event problem**.

Across rolling training folds, switch positives were only about 1.44% to 1.53% of switch-training rows.

Retained positive contribution: **a learned switch-confidence signal can suppress churn**.

Examples from the frozen candidate table:
- a stronger gate configuration reduced max false transitions/day to about 0.756, but min balanced accuracy fell to about 0.480;
- an even stronger configuration reduced max false transitions/day to about 0.475, but min balanced accuracy fell to about 0.439.

Interpretation:
- the gate contains information relevant to false-switch suppression;
- a hard veto is destructive because the event is extremely imbalanced and the gate blocks too much legitimate state evolution;
- any future use should be soft (penalty, confidence weight, calibration feature, or ranking signal), not a hard allow/deny switch;
- any learned switch component must explicitly respect the ~1.5% positive-rate structure.

Retained negative contribution:
- hard learned switch gating without a rare-event-aware integration mechanism is rejected.

## V9 — temporal-context primary classifier

Complete-version result: **not promoted**, but its temporal-context contribution was already retained and successfully integrated into v10.

Key contribution:
- 3-bar and 6-bar temporal context improved transition recognition and false-switch control while sacrificing point-state accuracy when used as a replacement classifier.

Successful integration outcome:
- v10 blended the 6-bar temporal head at low weight with the v5 primary head and became the new champion.

## Contribution map after audit

| Source | Retained contribution | Reuse status |
|---|---|---|
| v6 | state-change direction asymmetry; especially soft Shock-exit inertia | retained, not yet integrated into champion |
| v7 | low-weight previous-state/persistence prior may improve point-state classification | retained, not yet integrated into champion |
| v8 | rare-event switch confidence can suppress churn; ~1.5% positive-rate fact | retained, not yet integrated into champion |
| v9 | temporal context improves transition quality | successfully integrated into v10 champion |

## Priority rule for future challengers

Do not combine all retained contributions at once.

Use one contribution at a time against the current champion so attribution remains clear. A contribution that fails integration remains in the ledger as evidence and does not weaken the champion.
