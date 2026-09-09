# K-line recognizer authority narrative

Date: 2026-09-09

This is the canonical governance narrative for K-line recognizer research.

## Three authorities

1. **Champion Registry** — the best complete recognizer currently promoted.
2. **Contribution Ledger** — reusable positive or negative knowledge from any challenger, including challengers that did not win overall.
3. **Immutable Challenger Results** — the complete protocol/code/result history for every version.

Canonical files:
- `docs/research/KLINE_RECOGNIZER_CHAMPION.md`
- `experiments/kline_recognizer_champion.json`
- `experiments/kline_recognizer_contributions.json`
- `docs/research/KLINE_RECOGNIZER_HISTORICAL_CONTRIBUTION_AUDIT_V6_V9.md`

## Core invariants

- A failed challenger never replaces, erases or weakens the current champion.
- A failed challenger must be audited for local positive effects, costs, structural facts and negative design evidence.
- A retained contribution is not itself a champion.
- A contribution may change the champion only after being integrated into a new complete challenger that independently passes its frozen promotion gate and any frozen safety veto.
- Contributions should normally be integrated **one at a time** so attribution remains clear.
- 2025 is already-consumed development evidence and may not select or rescue a challenger.
- No fresh-OOS or production-readiness claim is made unless a later protocol explicitly opens untouched evidence.

Research loop:

`champion -> challenger -> result -> contribution audit -> retain evidence -> integrate one contribution -> compare again -> promote only if the complete challenger wins`

## Historical contribution audit

### v6 — type-specific transition policy

Complete version: **not promoted**.

Retained contribution: **transition-direction asymmetry, especially Shock-exit inertia**.

Hard extra Shock-exit confirmation reduced false transitions and improved transition F1 but hurt point-state accuracy. The reusable idea is therefore a **soft Shock-exit inertia**, not the original hard typed decoder.

### v7 — Markov persistence filter

Complete version: **not promoted**.

Retained contribution: **previous-state / persistence information contains useful point-state classification signal**.

Best point-eligible v7 candidate:
- minimum balanced accuracy `0.7739355167` versus then-champion v5 `0.7536614041`;
- minimum macro F1 `0.7800117166` versus `0.7562810194`;
- but transition F1 collapsed to `0.1176470588` and max false transitions/day rose to `2.0950413223`.

Therefore only a **low-weight persistence prior** may be revisited; direct Markov-forward argmax decoding remains rejected.

### v8 — learned switch gate

Complete version: **not promoted**.

Retained structural fact: true state switches are an extreme rare-event problem, only about `1.44%-1.53%` of switch-training rows.

Retained local effect: switch confidence can strongly suppress churn, but hard vetoing destroys point-state recognition. Any future use must be soft and rare-event-aware; hard allow/deny gating remains rejected.

### v9 — temporal-context primary classifier

Complete version: **not promoted**.

Retained contribution: temporal context improves transition recognition and false-switch control but is too costly when it replaces current-state evidence.

This contribution was successfully integrated into v10.

## Champion lineage

### v10 — current champion

V10 integrated the v9 six-bar temporal contribution into v5 as a 30% log-probability auxiliary while preserving the v5 primary head and decoder.

Result commit: `723404633fccb0a52181d2090cadbca3114dcc67`.

Pre-2025 worst-cell metrics:
- minimum balanced accuracy `0.7553851080081395`;
- minimum macro F1 `0.7591912321042829`;
- minimum transition F1 `0.19843342036553524`;
- maximum false transitions/day `1.2066115702479339`.

Consumed 2025 diagnostic:
- CSI1000: BA `0.8142904554`, Macro F1 `0.8105197658`, Transition F1 `0.2313624679`, false/day `1.0905349794`;
- STAR50: BA `0.7892740156`, Macro F1 `0.7907867773`, Transition F1 `0.2197802198`, false/day `1.0164609053`.

### v11 — higher temporal-weight refinement

Outcome: **not promoted**.

Best candidate alpha `0.45` improved all four pre-2025 aggregate metrics slightly:
- BA `0.7575591438`;
- Macro F1 `0.7617585588`;
- Transition F1 `0.2010582011`;
- max false/day `1.1652892562`.

The gain did not meet the frozen material-improvement threshold. Contribution retained: higher temporal weight remains mildly positive but is in a diminishing-returns region. The alpha grid is closed.

### v12 — soft Shock-exit inertia integration

Outcome: **not promoted**.

Best candidate `gamma=0.10`:
- minimum balanced accuracy `0.7555505391`;
- minimum macro F1 `0.7592463437`;
- minimum transition F1 `0.1989528796`;
- maximum false transitions/day `1.1942148760`.

All four metrics moved slightly in the favorable direction versus v10, confirming the v6 Shock-exit contribution is real, but the effect was too small for promotion. Larger gamma reduced churn further but began to damage point-state and transition quality. The gamma axis is closed and must not be expanded after this result.

V10 therefore remains champion.

## Current authority state

Current champion: **v10 temporal blend**.

Previous champion v5 remains fully preserved in the champion registry.

Post-v5 lineage:
- v6: not promoted; Shock-exit asymmetry retained;
- v7: not promoted; low-weight persistence prior retained;
- v8: not promoted; rare-event switch-confidence signal retained;
- v9: not promoted; temporal-context contribution retained;
- v10: v9 contribution integration succeeded and was promoted;
- v11: not promoted; diminishing-return temporal-weight contribution retained;
- v12: not promoted; soft Shock-exit effect revalidated as small positive contribution.

## Next integration order

The v6 contribution has now been tested against champion v10 and produced only a small non-promotable gain. Do not continue tuning it.

Next challenger must test **only the v7 contribution**:
- keep champion v10 completely fixed;
- learn the historical transition matrix from pre-validation labels as in v7;
- use it only as a **small causal probability prior** blended into v10 probabilities;
- never let Markov argmax replace the v10 decoder;
- do not include v6 Shock inertia or v8 switch confidence in that challenger.

Only after the v7 contribution is resolved may the v8 soft rare-event signal be attempted.
