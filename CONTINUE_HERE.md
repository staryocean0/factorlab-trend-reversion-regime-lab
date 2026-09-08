# Continue here — K-line state recognition v1

Date: 2026-09-08

This is the active handoff for the user's explicit research priority:

```text
K-line chart -> features -> market state -> state-transition recognition -> recognition accuracy
```

The immediate question is how well the system can recognize K-line structure, not which strategy/frequency is most profitable.

## Active branch

```text
branch = research/kline-state-recognition-v1
base = research/state-frequency-adaptation-v1
formal result commit = cd9353c87101ae5965b71b4f48685f417b5595e2
```

The earlier state-frequency branch remains a separate line. Frozen v0.15 reversal/IM material remains untouched.

## Frozen v1 design

Read:

`docs/research/KLINE_STATE_RECOGNITION_V1_PROTOCOL.md`

The protocol was finalized before any real historical recognition score was observed.

```text
clock = 5m
short window = 6 bars / 30m
primary online window = 12 bars / 60m
centered offline judge = +/- 6 bars
strict-prior shock reference = 480 finite observations
transition confirmation = 2 consecutive eligible bars
transition match tolerance = +/- 3 eligible bars / 15m
```

Concrete states:

```text
UpTrend
DownTrend
Range
Shock
```

`Uncertain` is a real abstention. On an eligible row, `Uncertain` against a concrete judge state counts as a miss.

## Implemented files

- `src/regime_lab/kline_state_recognition.py`
- `src/regime_lab/kline_state_evaluation.py`
- `scripts/run_kline_state_recognition_v1.py`
- `tests/test_kline_state_recognition.py`

The recognizer is prefix-only. The centered offline judge may inspect a fixed local future radius only for evaluation and is forbidden from online inputs.

## Formal execution completed

A one-shot GitHub-hosted execution was used only after the ordinary cloud shell and direct binary-download routes were blocked by DNS/network isolation. It is not the default research-compute path.

Formal run facts:

```text
immutable data manifest partitions validated = 52
000852.SH 5m rows = 128,290
000688.SH 5m rows = 63,456
full pytest = 76 passed
formal recognition exam = completed
result bundle commit = cd9353c87101ae5965b71b4f48685f417b5595e2
```

Required result bundle exists under:

`experiments/kline_state_recognition_v1/`

## Formal v1 capability result

Primary project capability: **Level 2**.

### CSI1000 / 000852.SH

```text
n_scored = 33,768
balanced_accuracy_4state = 0.3743
macro_f1_4state = 0.4739
concrete_coverage = 0.5211
conditional_accuracy_when_online_concrete = 0.7372
exact_accuracy_including_abstention = 0.3842
transition_f1 = 0.0062
false_transitions_per_day = 0.8207
```

Per-state F1:

```text
UpTrend = 0.5260
DownTrend = 0.3699
Range = 0.2860
Shock = 0.7138
```

### STAR50 / 000688.SH

```text
n_scored = 15,929
balanced_accuracy_4state = 0.3808
macro_f1_4state = 0.4732
concrete_coverage = 0.5124
conditional_accuracy_when_online_concrete = 0.7036
exact_accuracy_including_abstention = 0.3605
transition_f1 = 0.0132
false_transitions_per_day = 0.9557
```

Per-state F1:

```text
UpTrend = 0.4191
DownTrend = 0.4530
Range = 0.3390
Shock = 0.6818
```

## Plain-language interpretation

The current recognizer is selective: when it commits to a concrete state, it is correct roughly 70–74% of the time, but it only commits on about 51–52% of concrete-judge cases. Shock recognition is the strongest current component. Range and ordinary directional-state recall are much weaker.

The largest failure is state-transition recognition. Transition F1 is only about 0.6% on CSI1000 and 1.3% on STAR50, so v1 does not yet reliably recognize when the chart changes from one regime to another.

This is why Level 3 failed despite respectable conditional accuracy on the subset where the recognizer commits.

## Frozen capability gates

Level 3 requires both assets separately:

```text
balanced_accuracy >= 0.55
transition_F1 >= 0.40
concrete coverage >= 0.60
every concrete state support >= 100
```

v1 failed the first three gates on both assets.

Level 4 requires materially stronger accuracy/transition/stability. Level 5 requires fresh held-out data or independent human/external annotation and cannot be awarded by this consumed-history study.

## Next research step

Do not retune v1 after seeing the score. Preserve this result.

Open a separately preregistered v2 aimed specifically at the observed failure modes:

1. improve state-transition detection rather than P&L;
2. reduce excessive abstention while preserving precision;
3. improve `Range` recognition and ordinary trend recall;
4. keep `Shock` as a benchmark strength rather than overfitting it;
5. use temporal smoothing/change-point evidence only if frozen before v2 empirical scoring;
6. rerun both assets and year slices under a new v2 protocol.

## Scope boundary

- chart/state recognition only, not profitability;
- no 2026;
- no UK alert validation;
- no production/live trading;
- no mutation of other repositories;
- no post-result v1 threshold/model/frequency search;
- preserve the Level-2 result as the v1 baseline.
