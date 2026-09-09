# K-line recognizer authority narrative

Date: 2026-09-09

This is the canonical governance narrative for K-line recognizer research.

## Three separate authorities

### 1. Champion Registry

The champion is the best complete recognizer currently promoted for use as the baseline of all new research.

Canonical files:
- `docs/research/KLINE_RECOGNIZER_CHAMPION.md`
- `experiments/kline_recognizer_champion.json`

A failed challenger never replaces, erases, weakens, or silently changes the champion. When a new champion is promoted, the prior champion must remain explicitly recorded as historical authority rather than disappearing.

### 2. Contribution Ledger

A challenger may fail as a complete recognizer while still producing a validated reusable contribution.

Examples of valid contributions include:
- a feature family that improves transition recognition but hurts point-state accuracy;
- a decoder idea that reduces false transitions but loses recall;
- a model component that is useful only when blended with the champion;
- a structural fact discovered during failed research, such as extreme rare-event imbalance;
- a negative result that rules out a design family and prevents repeated work.

Canonical file:
- `experiments/kline_recognizer_contributions.json`

A contribution is not itself the champion. It is an evidence-backed component that may be integrated into a later challenger.

### 3. Challenger Result Bundles

Each version is an immutable challenger experiment with its own protocol, code, tests and result bundle.

A challenger can have three outcomes:
1. **promoted** — the complete challenger passes the frozen promotion gate and replaces the champion;
2. **not promoted, contribution retained** — the full version loses, but one or more specific effects are validated and entered in the contribution ledger;
3. **not promoted, no retained positive contribution** — the result is archived as negative evidence, which itself may constrain future design.

## Promotion invariant

Only a complete challenger that passes its preregistered pre-diagnostic promotion gate and any frozen safety veto may replace the champion.

Contribution discovery does not change the champion. A contribution must be integrated into a new challenger and that integrated challenger must itself pass the same governance process before becoming the new champion.

## Mandatory historical-contribution audit

A non-promoted version must not be summarized only as "failed". Before the research program moves on, its result should be checked for:
- positive local effects;
- explicit costs/tradeoffs;
- structural facts learned about the problem;
- negative design evidence;
- whether any retained effect is suitable for one-at-a-time integration into the current champion.

Historical audit document:
- `docs/research/KLINE_RECOGNIZER_HISTORICAL_CONTRIBUTION_AUDIT_V6_V9.md`

The audit must not retroactively change old promotion decisions. It only changes what knowledge is retained from those experiments.

## Research loop

The required loop is:

`champion -> challenger -> result -> contribution audit -> retain useful positive/negative evidence -> integrate one promising contribution into next challenger -> compare again -> promote only if complete challenger wins`

This prevents two opposite errors:
- losing the best known recognizer after several failed experiments;
- throwing away useful partial progress merely because a full version did not win.

## Historical contribution audit: v6-v9

### v6

Complete version: not promoted.

Retained contribution: **state-transition direction asymmetry, especially Shock-exit inertia**.

V6 showed that making Shock exit more persistent could reduce false transitions and improve transition F1, but hard extra confirmation bars reduced point-state accuracy. Therefore the reusable idea is a **soft state-dependent inertia/prior**, not the original hard typed decoder.

### v7

Complete version: not promoted.

Retained contribution: **previous-state / persistence information contains useful point-state signal**.

The best point-eligible Markov candidate raised pre-2025 worst-cell balanced accuracy from about 0.754 to about 0.774 and macro F1 from about 0.756 to about 0.780, while transition F1 fell to about 0.118 and false transitions rose to about 2.095/day. The useful component is therefore the low-weight persistence prior, not direct Markov-forward argmax decoding.

### v8

Complete version: not promoted.

Retained structural contribution: **true state switches are an extreme rare-event problem**, only about 1.44%-1.53% of switch-training rows.

Retained positive local effect: a learned switch-confidence signal can strongly suppress churn. Hard gating could push max false transitions below 0.8/day and even below 0.5/day, but point-state accuracy collapsed. Therefore future use, if any, must be soft and rare-event-aware; hard allow/deny gating remains rejected.

### v9

Complete version: not promoted.

Retained contribution: causal temporal context improves transition recognition and false-switch control, but is too costly when it replaces the primary classifier.

This contribution was successfully integrated in v10.

## Canonical example: v9 -> v10

V9 did **not** beat the then-champion v5 as a complete recognizer. However, it established a reusable contribution: causal temporal context materially improved transition recognition and reduced false transitions, with a point-state accuracy cost when temporal context replaced the primary classifier.

That contribution was retained rather than discarded.

V10 then integrated only the useful part back into v5:
- v5 current-state classifier remained the primary head;
- six-bar temporal context became a 30% auxiliary log-probability contribution;
- the exact v5 hysteresis decoder remained unchanged.

V10 passed the frozen pre-2025 promotion gate and the frozen 2025 safety veto. Therefore the contribution-extraction loop produced a new champion.

This example is now part of the authoritative research method: a failed full version can still create a contribution that later produces a winner.

## V11 local refinement result

V11 tested only higher six-bar temporal blend weights `0.35/0.40/0.45` against champion v10.

Outcome: **not promoted**.

Best v11 candidate: `alpha=0.45`.

Pre-2025 worst-cell comparison:
- balanced accuracy: v10 `0.7554` -> v11 `0.7576`;
- macro F1: v10 `0.7592` -> v11 `0.7618`;
- transition F1: v10 `0.1984` -> v11 `0.2011`;
- max false transitions/day: v10 `1.2066` -> v11 `1.1653`.

All four metrics moved in the favorable direction, but the improvement did not meet the frozen material-improvement threshold. Therefore v10 remains champion and v11 is retained only as evidence that the temporal-weight axis still has small positive effect but is entering diminishing returns. The alpha grid must not be expanded after seeing this result.

## Current authority state

Current champion: **v10 temporal blend**.

Promoted result commit: `723404633fccb0a52181d2090cadbca3114dcc67`.

Pre-2025 worst-cell metrics:
- minimum balanced accuracy: `0.7553851080081395`;
- minimum macro F1: `0.7591912321042829`;
- minimum transition F1: `0.19843342036553524`;
- maximum false transitions/day: `1.2066115702479339`.

Consumed 2025 diagnostic, not fresh OOS:
- CSI1000: balanced accuracy `0.8142904554`, macro F1 `0.8105197658`, transition F1 `0.2313624679`, false transitions/day `1.0905349794`;
- STAR50: balanced accuracy `0.7892740156`, macro F1 `0.7907867773`, transition F1 `0.2197802198`, false transitions/day `1.0164609053`.

Historical lineage after v5:
- v6: not promoted; soft transition-asymmetry contribution retained;
- v7: not promoted; low-weight persistence-prior contribution retained;
- v8: not promoted; rare-event switch-confidence contribution retained;
- v9: not promoted as a complete recognizer; temporal-context contribution retained;
- v10: v9 contribution integration succeeded and was promoted;
- v11: not promoted; higher temporal-weight near-miss contribution retained.

## Next integration order

Do not combine the audited v6/v7/v8 contributions at once.

Starting from champion v10, the next challenger should test **one retained contribution only** so attribution remains clear.

Priority order:
1. v6 soft Shock-exit inertia — simplest and most directly tied to false-switch control;
2. v7 low-weight persistence prior — potentially useful for point-state accuracy but higher interaction risk;
3. v8 rare-event switch-confidence signal — most complex and should be attempted only as a soft rare-event-aware auxiliary.

Previous champion v5 remains preserved in the champion registry under `previous_champion` with its immutable result commit and metrics.
