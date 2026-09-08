# Continue here — K-line independent judge v3

Date: 2026-09-08

This is the active handoff for the user's chart-recognition research line:

```text
K-line chart -> causal features -> market state -> state-transition recognition -> independent recognition validation
```

The current question is chart/state recognition quality, not strategy P&L or optimal frequency.

## Active branch and immutable baselines

```text
branch = research/kline-independent-judge-v3
base = research/kline-transition-recognition-v2
v1 result commit = cd9353c87101ae5965b71b4f48685f417b5595e2
v2 result commit = f5531a47a7de1cb89f0a1190694f56e1c5136a87
v3 result commit = c6487eab13fca2cd79a0c1c30fbc41c4943eede5
```

V1/V2 remain immutable development evidence. Earlier state-frequency and reversal/IM research lines remain separate and untouched.

## Why v3 exists

V2 obtained near-99% point-state agreement after aligning the centered v1 oracle to the time its future six bars were actually observable. That established strong causal/time-axis consistency, but the recognizer and oracle still used closely related state formulas and nearly the same K-line segment.

Therefore v3 was preregistered before its first replay to use a structurally different algorithmic judge.

Protocol:

`docs/research/KLINE_INDEPENDENT_JUDGE_V3_PROTOCOL.md`

## Frozen v3 independent judge

The recognizer under test is unchanged from v1/v2. V3 changes only the offline answer key.

Independent judge:

```text
clock = 5m
centered picture = 17 bars / +/-8 bars / 80 trading minutes
availability lag = +8 eligible bars
strict-prior reference = 480 finite observations
transition confirmation = 2 consecutive judge labels
transition match tolerance = +/-3 eligible bars
```

Judge features are deliberately different from the recognizer:

- correlation of log close with bar ordinal (`linear_r`);
- endpoint displacement relative to full local high-low channel;
- terminal close location inside that channel;
- local turning-point density;
- centered median and maximum `log(high/low)`;
- strict-prior ranks of those OHLC-range quantities.

Forbidden judge inputs include BDCI, DII, signed efficiency, realized volatility, v1/v2 oracle fields, online state, future return/P&L, 2026 and UK-derived inputs.

## Formal v3 execution

A one-shot GitHub-hosted run was used only because the ordinary execution shell cannot directly access the repository payload. It was deleted immediately after success.

Formal run facts:

```text
immutable market package validation = PASS
52 Parquet partitions hash/row/symbol/date validated
full repository pytest = 86 passed, 1 warning
formal independent-judge replay = PASS
result bundle commit = c6487eab13fca2cd79a0c1c30fbc41c4943eede5
```

Outputs:

`experiments/kline_independent_judge_v3/`

## Formal independent point-state result

### CSI1000 / 000852.SH

```text
n_scored = 20,543
balanced_accuracy = 0.7576
macro_F1 = 0.7532
concrete_coverage = 0.9210
conditional_accuracy_when_concrete = 0.7940
exact_accuracy_including_abstention = 0.7313
yearly balanced_accuracy median = 0.7503
yearly balanced_accuracy min = 0.7113
```

Per-state F1:

```text
UpTrend = 0.8563
DownTrend = 0.8279
Range = 0.5652
Shock = 0.7632
```

### STAR50 / 000688.SH

```text
n_scored = 9,351
balanced_accuracy = 0.7559
macro_F1 = 0.7339
concrete_coverage = 0.9402
conditional_accuracy_when_concrete = 0.7572
exact_accuracy_including_abstention = 0.7119
yearly balanced_accuracy median = 0.7516
yearly balanced_accuracy min = 0.7174
```

Per-state F1:

```text
UpTrend = 0.7961
DownTrend = 0.8517
Range = 0.6070
Shock = 0.6807
```

## Formal independent transition result

The independent point-state result is robust, but transition agreement remains weak.

### CSI1000

```text
judge transitions scored = 875
online transitions = 2,196
matched = 298
transition precision = 0.1357
transition recall = 0.3406
transition F1 = 0.1941
false transitions/day = 0.7135
median delay vs judge availability = -1 bar / -5 minutes
```

### STAR50

```text
judge transitions scored = 409
online transitions = 1,266
matched = 135
transition precision = 0.1066
transition recall = 0.3301
transition F1 = 0.1612
false transitions/day = 0.8640
median delay vs judge availability = -1 bar / -5 minutes
```

The frozen v3 adjudication is:

`weak_independent_algorithmic_agreement`

This label is caused only by transition F1 failing the preregistered useful threshold of 0.30 on both assets. The point-state metrics themselves exceed the strong v3 accuracy/F1/coverage thresholds.

## Plain-language interpretation

The most defensible current statement is:

> The system has a real, reasonably strong ability to recognize ongoing K-line states across a structurally different chart description: roughly 75–76% balanced four-state agreement, ~92–94% concrete coverage, stable across years. This is much more credible than interpreting the v2 99% as human-like accuracy.

But:

> The system still changes its mind far too often. Independent transition precision is only ~11–14%, so many online state changes are not recognized as genuine changes by the orthogonal geometry judge.

`Range` remains the weakest point-state class, especially recall. Trend-state recognition is substantially stronger.

## Next scientifically meaningful step

Do not tune the independent v3 judge after seeing these results.

The next research should target the **online transition policy**, not ordinary point-state classification:

1. reduce false transitions without changing the frozen raw state classifier;
2. require transition evidence beyond two consecutive labels, using preregistered causal change evidence;
3. specifically study trend <-> range transitions and shock entry/exit;
4. evaluate against the frozen independent v3 judge, preserving v3 as the answer key;
5. avoid optimizing only aggregate transition F1; report precision/recall/delay and per-transition-type results;
6. Level 5 still requires fresh held-out data or independent human/external annotation.

## Scope boundary

- chart/state recognition only, not profitability;
- no 2026;
- no UK alert validation;
- no production/live trading;
- no mutation of other repositories;
- no post-result v3 judge tuning;
- V1/V2/V3 historical results remain immutable development evidence.