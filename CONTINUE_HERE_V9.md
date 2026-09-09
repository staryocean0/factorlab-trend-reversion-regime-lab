# Continue here — temporal-context v9 contribution extraction

Date: 2026-09-09

## Authority state

Champion remains **v5 probability hysteresis** at result commit `e4ddffd3c190ba18739587aabf73844b3daa2230`.

V9 is **not promoted** as a complete recognizer. Its formal result is stored under `experiments/kline_recognizer_temporal_context_v9/` with `eligible_for_champion_update=false`.

## Retained v9 contribution

V9 established that causal temporal context contains real transition information:

- 3-bar context improved worst-cell transition F1 from v5's `0.1790` to `0.2028` and reduced max false transitions/day from `1.2397` to `1.0744`, but reduced minimum balanced accuracy from `0.7537` to `0.7353`.
- 6-bar context improved worst-cell transition F1 to `0.2481` and reduced max false transitions/day to `0.7273`, but reduced minimum balanced accuracy to `0.6577`.

Therefore temporal context is retained as a contribution, not as a champion.

Canonical authority files:
- `docs/research/KLINE_RECOGNIZER_AUTHORITY.md`
- `docs/research/KLINE_RECOGNIZER_CHAMPION.md`
- `experiments/kline_recognizer_champion.json`
- `experiments/kline_recognizer_contributions.json`

## Next challenger

V10 should integrate the v9 temporal contribution back into v5 rather than replace v5:

- keep v5 current-state classifier as primary head;
- keep the exact v5 hysteresis decoder;
- train a temporal auxiliary head using the retained v9 temporal feature surface;
- combine primary and temporal probabilities with a small frozen blend weight;
- tune only a small frozen blend menu on pre-2025 rolling folds;
- champion registry remains read-only during the run;
- only a complete v10 promotion pass can justify a later governance update of the champion registry.
