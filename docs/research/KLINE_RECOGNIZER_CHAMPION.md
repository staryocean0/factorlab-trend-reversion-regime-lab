# K-line recognizer champion registry

Date: 2026-09-09

This file is the canonical human-readable record of the currently promoted K-line recognizer.

Research governance is intentionally split:
- the **Champion Registry** records the best complete recognizer;
- the **Contribution Ledger** records validated reusable partial contributions from challengers, including challengers that did not win overall;
- immutable challenger result bundles preserve the full experiment history.

Canonical governance narrative: `docs/research/KLINE_RECOGNIZER_AUTHORITY.md`.
Canonical contribution ledger: `experiments/kline_recognizer_contributions.json`.

## Current champion

- version: **v5 probability hysteresis**
- branch: `research/kline-recognizer-hysteresis-v5`
- immutable result commit: `e4ddffd3c190ba18739587aabf73844b3daa2230`
- result bundle: `experiments/kline_recognizer_hysteresis_v5/`
- classifier: pooled multinomial linear classifier, `C=1.0`
- switch margin: `0.05`
- minimum new-state probability: `0.45`
- confirmation bars: `4`

Pre-2025 rolling-CV worst-cell metrics:
- minimum balanced accuracy: `0.7536614040741304`
- minimum macro F1: `0.7562810194148302`
- minimum transition F1: `0.17902813299232734`
- maximum false transitions/day: `1.2396694214876034`

2025 consumed-data diagnostic, not fresh OOS:
- CSI1000 balanced accuracy `0.8148213880`, macro F1 `0.8073204262`, transition F1 `0.2029702970`, false transitions/day `1.1687242798`;
- STAR50 balanced accuracy `0.7706466653`, macro F1 `0.7752394001`, transition F1 `0.1912568306`, false transitions/day `1.0452674897`.

## Challenger history after v5

- v6 type-specific transition policy: **not promoted**. Manual transition-type confirmation route rejected.
- v7 causal Markov persistence filter: **not promoted**. Best point-eligible candidate had minimum transition F1 `0.118`, max false transitions/day `2.095`.
- v8 learned switch gate: **not promoted**. No candidate satisfied the point-state eligibility floors.
- v9 temporal-context primary classifier: **not promoted as a complete recognizer**, but **its temporal-context effect is retained as a contribution** because it improved transition F1 and reduced false transitions while sacrificing point-state accuracy.

The key v9 retained contribution is not a new champion. It is an integration target for later challengers:
- 3-bar temporal context: min transition F1 `0.2028`, max false transitions/day `1.0744`, but min balanced accuracy `0.7353`;
- 6-bar temporal context: min transition F1 `0.2481`, max false transitions/day `0.7273`, but min balanced accuracy `0.6577`.

## Promotion invariant

1. The champion remains unchanged when a challenger fails.
2. A failed challenger may still contribute a validated component to the contribution ledger.
3. A retained contribution never changes the champion by itself.
4. To replace the champion, a later integrated challenger must pass its own frozen promotion gate as a complete recognizer.
5. Failed challengers remain archived evidence; they never erase or weaken the current champion record.
6. Consumed 2025 evidence cannot be used to select or rescue a challenger.
7. Unless a later protocol explicitly opens new untouched evidence, no claim of fresh OOS or production readiness is made.

Current status: **v5 remains the champion; v9 temporal context is a retained contribution for integration research.**
