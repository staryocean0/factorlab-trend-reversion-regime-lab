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

- version: **v10 temporal blend**
- branch: `research/kline-recognizer-temporal-blend-v10`
- immutable result commit: `723404633fccb0a52181d2090cadbca3114dcc67`
- result bundle: `experiments/kline_recognizer_temporal_blend_v10/`

Recognizer structure:
- primary classifier: pooled multinomial linear classifier, `C=1.0`, same 12 current causal K-line features as v5;
- temporal auxiliary: six-bar temporal-context linear classifier, `C=0.1`;
- blend: log-probability blend with primary weight `0.70` and temporal weight `0.30`;
- when temporal context is unavailable, prediction falls back exactly to the primary v5 head;
- decoder: unchanged v5 probability hysteresis — switch margin `0.05`, minimum new-state probability `0.45`, confirmation `4` bars.

Pre-2025 rolling-CV worst-cell metrics:
- minimum balanced accuracy: `0.7553851080081395`
- minimum macro F1: `0.7591912321042829`
- minimum transition F1: `0.19843342036553524`
- maximum false transitions/day: `1.2066115702479339`

2025 consumed-data diagnostic, not fresh OOS:
- CSI1000 balanced accuracy `0.8142904554`, macro F1 `0.8105197658`, transition F1 `0.2313624679`, false transitions/day `1.0905349794`;
- STAR50 balanced accuracy `0.7892740156`, macro F1 `0.7907867773`, transition F1 `0.2197802198`, false transitions/day `1.0164609053`.

2025 safety veto: **not triggered**.

## Previous champion preserved

The previous champion remains fully preserved and is not overwritten:

- version: **v5 probability hysteresis**
- branch: `research/kline-recognizer-hysteresis-v5`
- immutable result commit: `e4ddffd3c190ba18739587aabf73844b3daa2230`
- result bundle: `experiments/kline_recognizer_hysteresis_v5/`

Its pre-2025 worst-cell metrics were:
- minimum balanced accuracy `0.7536614040741304`;
- minimum macro F1 `0.7562810194148302`;
- minimum transition F1 `0.17902813299232734`;
- maximum false transitions/day `1.2396694214876034`.

## Challenger and contribution lineage

- v6 type-specific transition policy: **not promoted**.
- v7 causal Markov persistence filter: **not promoted**.
- v8 learned switch gate: **not promoted**.
- v9 temporal-context primary classifier: **not promoted as a complete recognizer**, but its temporal-context signal was retained as a contribution.
- v10 temporal blend: **promoted** after integrating the v9 six-bar temporal contribution back into v5 at 30% weight while preserving the v5 decoder.

This is the canonical example of the contribution rule: a failed version may still contain a useful component; that component can be integrated into the champion in a new challenger; only the integrated challenger may become the new champion after passing promotion.

## Promotion invariant

1. The champion remains unchanged when a challenger fails.
2. A failed challenger may still contribute a validated component to the contribution ledger.
3. A retained contribution never changes the champion by itself.
4. To replace the champion, a later integrated challenger must pass its own frozen promotion gate and any frozen safety veto as a complete recognizer.
5. The prior champion must remain explicitly preserved as historical authority after promotion.
6. Failed challengers remain archived evidence; they never erase or weaken the current champion record.
7. Consumed 2025 evidence cannot be used to select or rescue a challenger.
8. Unless a later protocol explicitly opens new untouched evidence, no claim of fresh OOS or production readiness is made.

Current status: **v10 temporal blend is the champion; v5 is the preserved previous champion.**
