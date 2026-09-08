# K-line state recognition v1 — frozen protocol

Date frozen: 2026-09-08  
Assets: CSI1000 `000852.SH`, STAR50 `000688.SH`  
Primary clock: repository-verified `5m` K-line bars  
Status: **results-blind before first empirical recognition score**

## 1. Goal

Build and evaluate one transparent pipeline:

```text
K-line geometry -> causal features -> online market state -> state-transition events -> recognition score
```

This stage does **not** ask which state or frequency makes the most money. It asks whether the system can reliably recognize the shape/state of the K-line path itself.

## 2. Separation between recognizer and judge

The online recognizer may use only bars closed at or before decision time `t`.

The evaluation judge is a separate offline visual-reference label. It is allowed to use a centered K-line window around `t` so that it can describe the completed local chart shape. The centered judge is used **only for scoring** and must never be fed into the recognizer, thresholds, strategy routing, or live features.

This separation prevents the circular claim “we defined the state, therefore our state recognition is correct.”

## 3. Fixed semantic state vocabulary

Exactly five outputs are allowed:

- `UpTrend` — persistent upward directional structure;
- `DownTrend` — persistent downward directional structure;
- `Range` — direction switches / inefficient path dominate;
- `Shock` — unusually violent local movement/volatility, regardless of direction;
- `Uncertain` — evidence is mixed or insufficient.

`Uncertain` is an explicit abstention, not silently remapped to a favorable state.

## 4. Data role and quality gate

Use only `regime_lab.market_data.load_market_data` on the repository's immutable market package and `data/manifest.json` hashes.

Primary data is `5m` because the task is chart-structure recognition rather than microsecond execution. `1m` can be a later sensitivity study; it must not be introduced after seeing the first 5m score in order to improve the result.

For every used bar require, when fields exist:

```text
high_frequency_analysis_eligible == true
causal_flat_fill == false
source_minute_count >= 1
```

No silent filling. Missing five-minute bars break a feature run. The ordinary same-day lunch break is a valid trading-clock bridge only from the actual 11:30 endpoint into the 13:00/13:05 restart; a missing late-morning bar may not be disguised as lunch continuity. 2026 is excluded. Supplied history is consumed development material, not fresh OOS.

## 5. Frozen causal feature set

The primary visual window is 12 x 5m bars (60 trading minutes). A 6-bar short window (30 minutes) is used for direction agreement. A strict-prior history of 480 finite reference observations supplies causal empirical ranks for shock/volatility context.

The recognizer uses only these transparent K-line properties:

1. `signed_efficiency_6` — net displacement / absolute path over 6 bars;
2. `signed_efficiency_12` — same over 12 bars;
3. `bdci_12` — bar-direction continuity score over 12 bars;
4. `dii_12` — directional impulse over 12 bars;
5. `realized_volatility_12`;
6. `volatility_rank_prior480` — empirical rank of current 12-bar RV against the preceding 480 finite causal RV observations;
7. `abs_return_rank_prior480` — empirical rank of the latest absolute 5m return against the preceding 480 finite causal absolute-return observations;
8. `body_to_range_ratio_6` median;
9. `wick_imbalance_6` median = lower-wick share minus upper-wick share;
10. `close_location_value_6` median.

No future return, P&L, strategy result, UK alert, frequency-test outcome, or 2026 value is permitted on the recognizer feature surface.

## 6. Frozen online-state rule

### Shock override

`Shock` if either:

```text
volatility_rank_prior480 >= 0.90
abs_return_rank_prior480 >= 0.995
```

### Directional state

Define three signed votes:

```text
sign(signed_efficiency_6)
sign(signed_efficiency_12)
sign(dii_12)
```

A directional trend candidate requires at least two votes with the same non-zero sign and either:

```text
(bdci_12 >= 60 and abs(signed_efficiency_12) >= 0.30)
OR
abs(dii_12) >= 1.25
```

Positive direction -> `UpTrend`; negative direction -> `DownTrend`.

### Range

`Range` if all hold:

```text
bdci_12 <= 40
abs(signed_efficiency_12) <= 0.20
abs(dii_12) < 1.25
```

Otherwise return `Uncertain`.

The 60/40 BDCI and +/-1.25 DII anchors reuse pre-existing transparent indicator defaults rather than being optimized on this study's score.

## 7. Offline visual-reference judge

The judge uses a fixed centered radius of 6 five-minute bars around each timestamp, giving a 13-bar local K-line picture and 12 local returns (60 trading minutes total).

Within the centered window compute:

- signed/absolute path efficiency;
- BDCI-like direction continuity;
- DII-like directional impulse;
- realized volatility.

For shock context, the judge's centered local RV is ranked against the same strict-prior causal RV history. The center bar's absolute return uses the same strict-prior absolute-return rank as the online view; future bars do not redefine the historical shock threshold.

Judge labels use the same semantic anchors:

- `Shock` on the same 0.90 RV-rank / 0.995 center-bar absolute-return-rank concept;
- `UpTrend` / `DownTrend` when centered direction is coherent by the same 60 BDCI / 0.30 efficiency / 1.25 DII anchors;
- `Range` when centered BDCI <= 40, efficiency <= 0.20 and |DII| < 1.25;
- otherwise `Uncertain`.

The judge is an offline chart-shape oracle, not a tradable label and not a production state source.

## 8. Evaluation eligibility

A timestamp enters the recognition exam only when **both** sides have all information required by their frozen contracts:

```text
all online 6/12-bar features finite
strict-prior 480-reference ranks available
centered oracle 13-bar geometry finite
oracle strict-prior shock context available
```

This warm-up/geometry gate is called `recognition_eligible`.

Rows that are ineligible because history or centered geometry is physically unavailable are not counted as recognition mistakes. Once a row is eligible, however, an online `Uncertain` against a concrete oracle state **does** count as a miss. This prevents both impossible warm-up penalties and artificial accuracy from excessive abstention.

## 9. State-transition recognition

Raw one-bar flips are too noisy to count as genuine regime changes. Both online and oracle label streams therefore use the same fixed confirmation rule on `recognition_eligible` rows:

```text
new concrete state must appear in 2 consecutive eligible bars
```

Concrete states are `UpTrend`, `DownTrend`, `Range`, `Shock`; `Uncertain` does not generate a destination transition event.

An online transition is considered matched to an oracle transition when the destination state is the same and the online event lies within +/- 3 eligible 5m bars (15 minutes) of the oracle event. One online event can match at most one oracle event and vice versa.

Report transition precision, recall, F1, false transitions/day, and signed detection delay in bars/minutes. If both precision and recall are defined and equal zero, transition F1 is exactly `0`, not missing.

## 10. Recognition metrics

Score CSI1000 and STAR50 separately first; pooled metrics are secondary.

For `recognition_eligible` timestamps where the oracle has a concrete state, report:

```text
n_scored
online_concrete_coverage
exact_accuracy_including_abstention
conditional_accuracy_when_online_concrete
balanced_accuracy_4state
macro_f1_4state
per_state precision / recall / f1 / support
confusion matrix
```

An online `Uncertain` prediction against a concrete oracle state counts as a miss for exact/balanced/F1 metrics; this prevents abstaining on every difficult chart from looking artificially accurate.

Also report the metrics by calendar year. For Level-4 stability, a year is eligible only when:

```text
n_scored >= 1000
min concrete-state support >= 25
balanced_accuracy is defined
```

Years/classes with too little support are `inconclusive`, not silently dropped.

## 11. Project-specific capability levels

This rubric is a project maturity scale, not a universal ML benchmark.

### Level 1 — feature extraction only

K-line properties can be measured but no end-to-end state score exists.

### Level 2 — end-to-end recognizer exists

Feature -> state -> transition -> score pipeline runs, but at least one Level-3 gate fails.

### Level 3 — useful historical chart-state recognition

Both assets separately satisfy all:

```text
balanced_accuracy >= 0.55
transition_F1 >= 0.40
concrete coverage >= 0.60
support >= 100 for every concrete state
```

### Level 4 — strong historical chart-state recognition

Both assets separately satisfy all:

```text
balanced_accuracy >= 0.70
transition_F1 >= 0.60
concrete coverage >= 0.75
at least 3 eligible yearly slices
yearly median balanced_accuracy >= 0.60
no eligible year balanced_accuracy < 0.50
```

### Level 5 — independently validated recognition

Cannot be awarded by v1. It requires either fresh held-out future data or independent human/external chart annotations that were not used to define this judge.

Therefore v1 can award at most Level 4.

## 12. Candidate/search budget

Exactly one frozen v1 recognizer and one frozen judge are permitted before the first empirical score. No threshold sweep, feature subset search, model family search, state-name rewrite, or post-result frequency change is allowed in v1.

If v1 is weak, preserve the result and open v2 with a new preregistration rather than editing v1 until it passes.

## 13. Required outputs

Write only under:

```text
experiments/kline_state_recognition_v1/
```

Required files:

```text
RESULT_CARD.md
summary.json
input_identity.json
feature_contract.json
state_timeseries.csv
transition_events.csv
confusion_matrix.csv
per_state_metrics.csv
yearly_metrics.csv
execution_receipt.json
```

The result card must state the achieved Level 1-4 or `inconclusive`, plus the specific failing gates.

## 14. What this study can and cannot claim

A positive v1 result can support:

> the causal recognizer can reproduce a separately defined completed local K-line shape/state with measurable historical accuracy and transition timing.

It does not establish:

- profitable trading;
- optimal strategy frequency;
- future return prediction;
- production routing authority;
- fresh OOS validation;
- Level 5 recognition.
