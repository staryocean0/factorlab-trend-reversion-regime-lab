# Continue here — K-line state recognition v1

Date: 2026-09-08

This is the active handoff for the user's explicit next research priority:

```text
K-line chart -> features -> market state -> state-transition recognition -> recognition accuracy
```

The immediate question is **how well the system can recognize K-line structure**, not which strategy/frequency is most profitable.

## Active branch

```text
branch = research/kline-state-recognition-v1
base = research/state-frequency-adaptation-v1
```

The earlier state-frequency branch is preserved unchanged as a separate line. Its missing `Unsafe/Recovering` state-pool gate is not bypassed or reconstructed here. Frozen v0.15 reversal/IM material also remains untouched.

## Plain-language objective

Build a measurable chart-reading system that can:

1. look only at K-lines already closed;
2. measure transparent chart properties;
3. say whether the current shape is `UpTrend`, `DownTrend`, `Range`, `Shock`, or `Uncertain`;
4. detect when the state changes;
5. compare those answers with a separate offline chart-shape judge;
6. report an honest Level 2/3/4 result instead of a trading P&L result.

Level 5 is deliberately unavailable in v1 because it requires fresh held-out data or independent human/external chart annotations.

## Frozen protocol

Read first:

`docs/research/KLINE_STATE_RECOGNITION_V1_PROTOCOL.md`

The protocol was finalized **before any real historical recognition score was observed**. During preflight review, the original 24-bar design was shortened to a 12 x 5m (60 trading minute) primary chart window and an explicit `recognition_eligible` gate was added. This avoided structurally penalizing timestamps where the recognizer or centered judge physically lacked enough bars. This was a results-blind design correction, not a response to empirical recognition performance.

Frozen primary design:

```text
clock = 5m
short window = 6 bars / 30m
primary online window = 12 bars / 60m
centered offline judge = +/- 6 bars
strict-prior shock reference = 480 finite observations
transition confirmation = 2 consecutive eligible bars
transition match tolerance = +/- 3 eligible bars / 15m
```

Frozen concrete states:

```text
UpTrend
DownTrend
Range
Shock
```

`Uncertain` is a real abstention. On an eligible row, `Uncertain` against a concrete judge state counts as a recognition miss.

## Implemented files

- causal chart/state core:
  - `src/regime_lab/kline_state_recognition.py`
- strict separated evaluator:
  - `src/regime_lab/kline_state_evaluation.py`
- formal historical runner:
  - `scripts/run_kline_state_recognition_v1.py`
- guardrail tests:
  - `tests/test_kline_state_recognition.py`

The recognizer uses only past/present K-line information. The centered offline judge may inspect a fixed local future radius **only for evaluation** and its fields are forbidden from online inputs.

The strict evaluator explicitly assigns F1=0 when a supported concrete class is completely missed, so failed classes cannot disappear from macro-F1 because precision is undefined.

## Capability rubric

### Level 2

End-to-end recognition/scoring exists but at least one Level-3 gate fails.

### Level 3 — useful historical recognition

Both CSI1000 and STAR50 separately require:

```text
balanced_accuracy >= 0.55
transition_F1 >= 0.40
concrete coverage >= 0.60
every concrete state support >= 100
```

### Level 4 — strong historical recognition

Both assets separately require:

```text
balanced_accuracy >= 0.70
transition_F1 >= 0.60
concrete coverage >= 0.75
>= 3 eligible yearly slices
yearly median balanced_accuracy >= 0.60
no eligible year balanced_accuracy < 0.50
```

### Level 5

Not awardable by this consumed-history v1. Requires independent/fresh evidence.

## Current validation status

Synthetic/preflight checks have covered:

- four-state rule behavior;
- missing rank context -> abstain;
- future K-line changes do not alter earlier causal features;
- missing late-morning bars are not disguised as the lunch break;
- 2026 fails closed;
- two-bar transition confirmation;
- destination-specific transition matching;
- zero transition matches -> F1=0;
- empty transition side is safe;
- eligible abstention counts as a miss;
- physically ineligible warm-up rows are excluded from the exam;
- fully missed supported class -> per-state F1=0 and remains in macro-F1.

A local synthetic reconstruction reached `ALL_CHECKS_PASS` after the strict missed-class F1 correction.

The current shell still cannot clone GitHub because DNS resolution fails, so this handoff does **not** claim that full repository `python -m pytest -q` has run in a real clone. GitHub Actions were not used as substitute compute.

## What is still missing

The **real historical recognition score** has not yet been generated, because this execution surface cannot access the repository Parquet payloads in a runnable clone.

Therefore do not yet claim that the project has achieved Level 2, 3, or 4 empirically. The honest state is:

> recognition exam built + synthetic guardrails passed; real CSI1000/STAR50 historical score pending data-capable execution.

## Next data-capable execution

From a real clone of this branch:

```text
python scripts/validate_seed.py
python -m pytest -q
python scripts/run_kline_state_recognition_v1.py
```

Required outputs are written only under:

`experiments/kline_state_recognition_v1/`

The key human-readable result is `RESULT_CARD.md`; it will state the achieved Level and the gates that failed if it does not advance.

## Scope boundary

- this is chart/state recognition, not a profitability test;
- no 2026;
- no UK alert validation;
- no production/live trading;
- no mutation of other repositories;
- no threshold/model/frequency search after seeing v1 results;
- if v1 is weak, preserve it and preregister v2 rather than tuning v1 until it passes.
