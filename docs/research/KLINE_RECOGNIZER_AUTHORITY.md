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
- a negative result that rules out a design family and prevents repeated work.

Canonical file:
- `experiments/kline_recognizer_contributions.json`

A contribution is not itself the champion. It is an evidence-backed component that may be integrated into a later challenger.

### 3. Challenger Result Bundles

Each version is an immutable challenger experiment with its own protocol, code, tests and result bundle.

A challenger can have three outcomes:
1. **promoted** — the complete challenger passes the frozen promotion gate and replaces the champion;
2. **not promoted, contribution retained** — the full version loses, but one or more specific effects are validated and entered in the contribution ledger;
3. **not promoted, no retained contribution** — the result is archived as negative evidence only.

## Promotion invariant

Only a complete challenger that passes its preregistered pre-diagnostic promotion gate and any frozen safety veto may replace the champion.

Contribution discovery does not change the champion. A contribution must be integrated into a new challenger and that integrated challenger must itself pass the same governance process before becoming the new champion.

## Research loop

The required loop is:

`champion -> challenger -> result -> extract validated contributions -> integrate promising contribution into next challenger -> compare again -> promote only if complete challenger wins`

This prevents two opposite errors:
- losing the best known recognizer after several failed experiments;
- throwing away useful partial progress merely because a full version did not win.

## Canonical example: v9 -> v10

V9 did **not** beat the then-champion v5 as a complete recognizer. However, it established a reusable contribution: causal temporal context materially improved transition recognition and reduced false transitions, with a point-state accuracy cost when temporal context replaced the primary classifier.

That contribution was retained rather than discarded.

V10 then integrated only the useful part back into v5:
- v5 current-state classifier remained the primary head;
- six-bar temporal context became a 30% auxiliary log-probability contribution;
- the exact v5 hysteresis decoder remained unchanged.

V10 passed the frozen pre-2025 promotion gate and the frozen 2025 safety veto. Therefore the contribution-extraction loop produced a new champion.

This example is now part of the authoritative research method: a failed full version can still create a contribution that later produces a winner.

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
- v6: not promoted; manual transition-type confirmation route rejected;
- v7: not promoted; Markov persistence route rejected;
- v8: not promoted; learned switch-gate route rejected;
- v9: not promoted as a complete recognizer; temporal-context contribution retained;
- v10: contribution integration succeeded and was promoted.

Previous champion v5 remains preserved in the champion registry under `previous_champion` with its immutable result commit and metrics.
