# K-line independent judge v3 — frozen protocol

Date frozen: 2026-09-08
Assets: CSI1000 `000852.SH`, STAR50 `000688.SH`
Primary clock: repository-verified `5m` K-line bars
Status: **results-blind before first independent-judge score**

## 1. Goal

V1/V2 showed that the causal recognizer can reproduce a same-family centered rule once information availability is aligned. V3 asks a harder question:

> Does the current causal recognizer agree with a structurally different, offline chart-shape judge that does **not** use BDCI, DII, signed efficiency, realized volatility, or the v1 state thresholds?

This is still algorithmic validation, not human annotation and not Level 5.

## 2. Frozen recognizer under test

The recognizer is unchanged from v1/v2:

- raw online state from `kline_state_recognition.py`;
- two-consecutive-bar causal persistence decoder from v2;
- no threshold, window, state vocabulary, or decoder changes in v3.

## 3. Independent judge design

The independent judge uses a centered **17-bar** local picture (`+/- 8` five-minute bars, 80 trading minutes). This deliberately differs from the recognizer's 12-bar trailing window.

The judge may inspect the completed centered picture only for evaluation. Its label becomes scoreable only after the rightmost `+8` bar has closed on the same trading day.

The judge uses only these geometric quantities:

1. `linear_r` — Pearson correlation between bar ordinal and log close across the 17-bar picture;
2. `channel_displacement` — endpoint price displacement divided by the full local high-low channel width;
3. `terminal_channel_location` — final close location inside the local high-low channel;
4. `turning_point_density` — fraction of interior closes that are local extrema;
5. `centered_median_log_range` — median `log(high/low)` across the picture;
6. `centered_max_log_range` — maximum `log(high/low)` across the picture;
7. strict-prior empirical ranks for (5) and (6), using the preceding 480 finite reference observations only.

The judge is forbidden from reading:

- `online_state`, `online_decoded_state`;
- `oracle_state` or v1/v2 oracle fields;
- BDCI;
- DII;
- signed efficiency;
- realized volatility;
- forward returns / P&L / strategy outcomes;
- 2026 or UK-derived inputs.

## 4. Frozen independent state rule

Exactly the existing five semantic outputs are retained:

`UpTrend`, `DownTrend`, `Range`, `Shock`, `Uncertain`.

### Shock

`Shock` if either independent OHLC-range condition holds:

```text
centered_median_log_range_rank_prior480 >= 0.95
OR centered_max_log_range_rank_prior480 >= 0.995
```

### UpTrend

All must hold:

```text
linear_r >= 0.70
channel_displacement >= 0.40
terminal_channel_location >= 0.70
turning_point_density <= 0.45
```

### DownTrend

All must hold:

```text
linear_r <= -0.70
channel_displacement <= -0.40
terminal_channel_location <= 0.30
turning_point_density <= 0.45
```

### Range

All must hold:

```text
abs(linear_r) <= 0.40
abs(channel_displacement) <= 0.30
turning_point_density >= 0.35
```

Otherwise `Uncertain`.

No threshold sweep or post-result rule change is allowed in v3.

## 5. Point-state scoring

For each independent judge center timestamp `t`, the truth label is evaluated against the causal decoded recognizer at the first same-day eligible bar whose information set includes the complete judge picture, i.e. `t + 8 eligible bars`.

Last-of-day judge centers whose +8 availability point does not exist are audited and excluded rather than carried overnight.

Primary point metrics per asset:

- n_scored;
- concrete prediction coverage;
- exact accuracy including abstention;
- conditional accuracy when recognizer is concrete;
- balanced accuracy across four concrete states;
- macro F1;
- per-state precision/recall/F1/support;
- confusion matrix;
- yearly stability.

## 6. Transition scoring

Independent judge labels are debounced with the same neutral two-consecutive-label confirmation rule only to avoid single-bar label flicker; this does not change the judge's geometric thresholds.

A judge transition centered at `t` becomes available at `t + 8 eligible bars`. The causal recognizer transition is matched one-to-one by destination state within `+/- 3` eligible bars of that availability time.

Report precision, recall, F1, false transitions/day and delay relative to judge availability.

## 7. Frozen interpretation grades

These are **independent algorithmic agreement grades**, not the v1/v2 Level system and not human-equivalent accuracy.

### Strong independent agreement

Both assets separately satisfy:

```text
balanced_accuracy >= 0.60
macro_f1 >= 0.60
transition_f1 >= 0.45
concrete_coverage >= 0.85
```

### Useful independent agreement

Both assets separately satisfy:

```text
balanced_accuracy >= 0.50
macro_f1 >= 0.50
transition_f1 >= 0.30
concrete_coverage >= 0.75
```

### Weak independent agreement

At least one asset fails the useful gates.

Regardless of result, v3 does not award Level 5. Fresh held-out data or independent human/external annotations are still required for that claim.

## 8. Required outputs

Write only under:

`experiments/kline_independent_judge_v3/`

Required files:

- `RESULT_CARD.md`
- `summary.json`
- `input_identity.json`
- `judge_contract.json`
- `judge_timeseries.csv`
- `confusion_matrix.csv`
- `per_state_metrics.csv`
- `yearly_metrics.csv`
- `transition_events.csv`
- `availability_audit.json`
- `execution_receipt.json`

## 9. Scope boundary

- chart/state recognition only;
- no profitability claim;
- no 2026;
- no UK alert validation;
- no production/live trading;
- no mutation of other repositories;
- v1/v2 results remain immutable baselines;
- if v3 is weak, preserve the weak result and preregister a later study rather than tuning this judge until it agrees.