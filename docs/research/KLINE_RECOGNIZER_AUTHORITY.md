# K-line recognizer authority narrative

Date: 2026-09-09

This is the canonical governance narrative for K-line recognizer research.

## Three separate authorities

### 1. Champion Registry

The champion is the best complete recognizer currently promoted for use as the baseline of all new research.

Canonical files:
- `docs/research/KLINE_RECOGNIZER_CHAMPION.md`
- `experiments/kline_recognizer_champion.json`

A failed challenger never replaces, erases, weakens, or silently changes the champion.

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

Only a complete challenger that passes its preregistered pre-diagnostic promotion gate may replace the champion.

Contribution discovery does not change the champion. A contribution must be integrated into a new challenger and that integrated challenger must itself pass the same governance process before becoming the new champion.

## Research loop

The required loop is:

`champion -> challenger -> result -> extract validated contributions -> integrate promising contribution into next challenger -> compare again -> promote only if complete challenger wins`

This prevents two opposite errors:
- losing the best known recognizer after several failed experiments;
- throwing away useful partial progress merely because a full version did not win.

## Current authority state

Current champion: **v5 probability hysteresis**.

Post-v5 challenger status:
- v6: not promoted; manual transition-type confirmation route rejected;
- v7: not promoted; Markov persistence route rejected;
- v8: not promoted; learned switch-gate route rejected;
- v9: not promoted as a complete recognizer, but its temporal-context effect is retained as a contribution because it improved transition F1 and reduced false transitions while sacrificing point-state accuracy.

The next challenger must therefore start from the v5 champion and attempt to integrate the useful temporal-context contribution in a controlled way. The v5 champion remains authoritative until such an integrated challenger passes promotion.
