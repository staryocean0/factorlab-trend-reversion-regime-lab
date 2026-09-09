# K-line recognizer temporal-context v9 protocol

Date frozen: 2026-09-09

## Governance first

The canonical current champion is read from:
- `docs/research/KLINE_RECOGNIZER_CHAMPION.md`
- `experiments/kline_recognizer_champion.json`

At protocol freeze the champion is **v5 probability hysteresis**, immutable result commit `e4ddffd3c190ba18739587aabf73844b3daa2230`.

V9 is a challenger only. A failed v9 must not alter the champion files. A successful v9 may alter them only after all preregistered promotion and safety gates below pass.

## Research question

Can the primary four-state classifier improve by directly observing how the existing causal K-line features evolve over several bars, while keeping the already-promoted v5 switching policy unchanged?

V9 is deliberately not another post-classifier filter. It changes the primary state model only.

## Fixed upstream components

- frequency: 5-minute bars;
- assets: `000852.SH` and `000688.SH`;
- raw causal feature family: the same 12 v4 features;
- labels / benchmark: frozen v3 `independent_judge_available_state` at its declared information-availability time;
- decoder after the classifier: exactly the current v5 hysteresis policy:
  - switch margin `0.05`;
  - minimum new-state probability `0.45`;
  - confirmation bars `4`;
- pooled model across both assets;
- no asset-specific model or parameter;
- 2025 never participates in candidate selection.

## Temporal feature surface

Base feature vector `F_t` is the existing 12-feature v4 causal vector.

For one frozen context horizon `h`, the v9 input is exactly:

1. current features: `F_t`;
2. one-bar change: `F_t - F_{t-1}`;
3. trailing mean including current bar: `mean(F_{t-h+1}, ..., F_t)`;
4. window displacement: `F_t - F_{t-h+1}`.

This produces `12 x 4 = 48` model inputs.

All temporal calculations:
- are backward-looking only;
- reset at trading-day boundaries;
- reset at `contiguous_run_id` boundaries;
- require every bar in the window to belong to the same contiguous run;
- never bridge lunch/data gaps unless the upstream contiguous-run logic itself marks those rows as one valid run;
- never use centered/future values.

Rows without sufficient history for the chosen horizon are simply ineligible for v9 prediction/training; they are not filled from future data.

## Frozen candidate menu

Exactly six v9 challengers:

- context horizon `h in {3, 6}` bars;
- class-balanced L2 multinomial linear classifier with `C in {0.1, 1.0, 10.0}`.

No new classifier family, hidden layer, threshold, decoder parameter or post-result candidate may be added after outcomes are visible.

## Training

The four-state classifier is pooled across CSI1000 and STAR50.

Use class-balanced sample weights exactly in spirit of v4. Standardization is fit on the training interval only.

## Rolling pre-2025 selection

- train through 2021-12-31 -> validate 2022;
- train through 2022-12-31 -> validate 2023;
- train through 2023-12-31 -> validate 2024.

Both assets are scored separately in each validation year.

For each candidate compute worst-cell / max-cell aggregates across all six `fold x asset` cells:
- minimum balanced accuracy;
- minimum macro F1;
- minimum transition F1;
- maximum false transitions/day.

Frozen v5 benchmark from its immutable result bundle:
- minimum balanced accuracy `0.7536614040741304`;
- minimum macro F1 `0.7562810194148302`;
- minimum transition F1 `0.17902813299232734`;
- maximum false transitions/day `1.2396694214876034`.

A v9 candidate is pre-2025 promotable only if ALL hold:
- minimum balanced accuracy >= v5 minimum balanced accuracy;
- minimum macro F1 >= v5 minimum macro F1;
- minimum transition F1 >= v5 minimum transition F1;
- maximum false transitions/day <= v5 maximum false transitions/day;
- and at least one material improvement holds:
  - minimum balanced accuracy improves by >= `0.010`, or
  - minimum macro F1 improves by >= `0.010`, or
  - minimum transition F1 improves by >= `0.010`, or
  - maximum false transitions/day improves by >= `0.050`.

Among promotable candidates select lexicographically:
1. highest minimum balanced accuracy;
2. highest minimum macro F1;
3. highest minimum transition F1;
4. lowest maximum false transitions/day;
5. shorter context horizon;
6. smaller `C`.

If no candidate is promotable, v5 remains champion and v9 is closed as failed without using 2025 to rescue it.

## 2025 consumed-data safety diagnostic

Only after one v9 candidate is selected entirely from pre-2025 folds:
- refit that exact configuration through 2024-12-31;
- run it once on 2025;
- compare separately with the frozen v5 2025 diagnostic.

2025 is already-consumed development evidence, not fresh OOS and cannot choose a different v9 configuration.

A catastrophic-regression safety veto prevents champion replacement if on either asset any of the following holds versus v5:
- balanced accuracy lower by more than `0.030`;
- macro F1 lower by more than `0.030`;
- transition F1 lower by more than `0.030`;
- false transitions/day higher by more than `0.300`.

If the pre-2025 gate passes and the 2025 safety veto does not trigger, v9 may replace v5 in the champion registry. Otherwise v5 remains champion.

## Required outputs

Under `experiments/kline_recognizer_temporal_context_v9/`:
- `RESULT_CARD.md`
- `summary.json`
- `candidate_cv.csv`
- `diagnostic_2025.csv` when a pre-2025 candidate is selected;
- `per_state_2025.csv` when applicable;
- `transition_events_2025.csv` when applicable;
- `selected_recognizer.json` when applicable;
- `input_identity.json`
- `execution_receipt.json`

## Forbidden

- changing v5 champion files before promotion succeeds;
- adding a new post-processing/filter layer;
- changing v3 labels;
- adding new raw K-line indicator families;
- asset-specific parameters;
- 2025-based candidate selection or rescue;
- future/centered features;
- P&L-based model selection;
- post-result menu expansion;
- fresh-OOS or production claims.
