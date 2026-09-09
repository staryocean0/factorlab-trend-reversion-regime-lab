# K-line recognizer temporal-blend v10 — protocol

Date frozen: 2026-09-09

Goal: integrate the retained v9 temporal-context contribution into the v5 champion without replacing the v5 current-state evidence or decoder.

## Authority boundary

- current champion remains `v5_probability_hysteresis`;
- champion result commit remains `e4ddffd3c190ba18739587aabf73844b3daa2230`;
- v9 is a failed complete challenger but contributes validated temporal information;
- the champion registry is read-only during v10 execution;
- v10 may become champion only after a complete preregistered promotion pass and a separate governance update.

Canonical authority files:
- `docs/research/KLINE_RECOGNIZER_AUTHORITY.md`;
- `experiments/kline_recognizer_champion.json`;
- `experiments/kline_recognizer_contributions.json`.

## Architecture

V10 keeps two recognizer-internal probability heads:

1. **primary head** — the exact v5 pooled multinomial linear classifier on the 12 frozen current causal K-line features, `C=1.0`;
2. **temporal auxiliary head** — the v9 temporal-context classifier using the same 12 features represented as current value, previous value, trailing mean and current-minus-trailing-mean.

The temporal head is auxiliary only. It may not replace the primary head.

For each bar, combine class probabilities using a log-probability blend:

`log p_blend(k) = (1-alpha) * log p_primary(k) + alpha * log p_temporal(k)`

then normalize across the four states.

This preserves the v5 classifier as the dominant evidence source whenever `alpha < 0.5`.

The final decoded state uses the exact frozen v5 hysteresis policy:
- switch margin `0.05`;
- minimum new-state probability `0.45`;
- confirmation bars `4`.

No new postprocessor, switch gate, Markov layer or confirmation rule is permitted.

## Retained v9 auxiliary configurations

V9 showed that `C=0.1` was the most point-preserving member for both useful temporal horizons. Therefore v10 freezes temporal auxiliary regularization at `C=0.1` and tests only:

- temporal horizon `3` bars;
- temporal horizon `6` bars.

No other temporal horizon or auxiliary C may be added after results.

## Frozen blend menu

Exactly 6 challengers:

- horizon in `{3, 6}`;
- blend weight `alpha in {0.10, 0.20, 0.30}`.

The unchanged v5 champion is the comparison baseline only.

## Rolling evaluation

Same pre-2025 folds:
- train through 2021 -> validate 2022;
- train through 2022 -> validate 2023;
- train through 2023 -> validate 2024.

Both assets are scored separately in every fold.

V10 must satisfy across every fold x asset cell:
- balanced accuracy >= v5 worst-cell balanced accuracy `0.7536614040741304`;
- macro F1 >= v5 worst-cell macro F1 `0.7562810194148302`;
- transition F1 >= v5 worst-cell transition F1 `0.17902813299232734`;
- false transitions/day <= v5 worst-cell maximum `1.2396694214876034`.

Material improvement requires at least one:
- minimum transition F1 improves by >= `0.01`;
- maximum false transitions/day falls by >= `0.05`;
- minimum balanced accuracy improves by >= `0.01`;
- minimum macro F1 improves by >= `0.01`.

Among candidates passing all noninferiority gates and at least one material-improvement gate, select lexicographically:
1. highest minimum transition F1;
2. lowest maximum false transitions/day;
3. highest minimum balanced accuracy;
4. highest minimum macro F1;
5. smaller alpha;
6. shorter temporal horizon.

If no candidate qualifies, v5 remains champion and v10 is archived as not promoted.

## 2025 safety diagnostic

Only after a pre-2025 candidate qualifies:
- refit primary and temporal heads through 2024;
- run 2025 diagnostic once;
- 2025 cannot select alpha, horizon, C, feature surface or decoder;
- if the candidate materially degrades either asset versus v5 on balanced accuracy, macro F1, transition F1 or false transitions/day, mark a safety veto and do not update champion.

2025 is already-consumed development evidence and is not fresh OOS.

## Forbidden

- changing v5 decoder parameters;
- changing primary classifier family or C;
- new chart feature families;
- new temporal horizons;
- new auxiliary C values;
- asset-specific blend weights;
- post-result candidate expansion;
- 2025-based selection or rescue;
- P&L-based selection;
- champion-registry mutation from the runner.
