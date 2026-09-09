# K-line recognizer champion registry

Date: 2026-09-09

This file is the canonical human-readable record of the currently promoted K-line recognizer. Research versions are challengers only. A challenger does not replace the champion unless its preregistered promotion gate passes before any consumed diagnostic period is used.

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

- v6 type-specific transition policy: **not promoted**. Pre-2025 minimum transition F1 `0.145`, max false transitions/day `1.434`.
- v7 causal Markov persistence filter: **not promoted**. Best point-eligible candidate had minimum transition F1 `0.118`, max false transitions/day `2.095`.
- v8 learned switch gate: **not promoted**. No candidate satisfied the point-state eligibility floors, so 2025 was not used to rescue the model.

## Promotion invariant

1. The champion remains unchanged when a challenger fails.
2. A new research version may be recorded as successful only after its frozen pre-diagnostic promotion gate passes.
3. Only after that gate passes may this registry be changed to point to the new champion.
4. Failed challengers remain archived evidence; they never erase or weaken the current champion record.
5. Consumed 2025 evidence cannot be used to select or rescue a challenger.
6. Unless a later protocol explicitly opens new untouched evidence, no claim of fresh OOS or production readiness is made.

Current status: **v5 remains the champion.**
