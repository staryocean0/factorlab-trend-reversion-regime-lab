# Continue here — K-line transition recognition v2

Date: 2026-09-08

This is the active handoff for the user's chart-recognition research line:

```text
K-line chart -> causal features -> market state -> state-transition recognition -> recognition accuracy
```

The current question is chart/state recognition quality, not strategy P&L or optimal frequency.

## Active branch

```text
branch = research/kline-transition-recognition-v2
base = research/kline-state-recognition-v1
v1 formal result commit = cd9353c87101ae5965b71b4f48685f417b5595e2
v2 formal result commit = f5531a47a7de1cb89f0a1190694f56e1c5136a87
current branch head after one-shot workflow cleanup = 573a0722db9a2f8ed1cb50554878f0af8d309d9c
```

V1 remains immutable as the Level-2 baseline. Earlier state-frequency and reversal/IM lines remain separate and untouched.

## V1 baseline

V1 used a prefix-only 60-minute online recognizer and a centered `+/-6` five-minute-bar offline judge, but scored both at the same center timestamp.

Formal V1 result:

```text
CSI1000 balanced accuracy = 0.3743
CSI1000 coverage = 0.5211
CSI1000 transition F1 = 0.0062

STAR50 balanced accuracy = 0.3808
STAR50 coverage = 0.5124
STAR50 transition F1 = 0.0132
```

When V1 emitted a concrete state, conditional accuracy was about 70–74%, but it abstained frequently and transition timing appeared catastrophically weak.

## V2 diagnosis and frozen design

Inspection of the immutable V1 transition table showed many same-destination online/oracle transitions separated by about exactly six eligible 5-minute bars. This is structurally expected because a centered judge label at `t` uses data through `t+6 bars` and is not actually knowable at its retrospective center timestamp.

V2 was preregistered before its first replay in:

`docs/research/KLINE_TRANSITION_RECOGNITION_V2_PROTOCOL.md`

V2 changed no raw feature formulas or numerical state thresholds.

It added exactly two frozen changes:

1. causal persistence decoder using the already-frozen two-consecutive-bar confirmation rule; once a concrete state is confirmed, raw `Uncertain` keeps that stable state until another concrete state confirms;
2. offline oracle labels/events are scored six **eligible** bars later, at the time their centered-window information is actually available.

Transition tolerance remained `+/-3` eligible bars. No threshold sweep or widening occurred.

## Formal v2 execution

A one-shot GitHub-hosted run was used because the ordinary cloud shell cannot clone/download the repository payload due DNS/network isolation. The workflow was deleted immediately after the successful run.

Formal execution passed:

```text
immutable data package validation = PASS
52 Parquet partitions = hash/row/symbol/date validated
full repository pytest = PASS
formal v2 replay = PASS
result bundle commit = f5531a47a7de1cb89f0a1190694f56e1c5136a87
```

Outputs live under:

`experiments/kline_transition_recognition_v2/`

## Formal v2 primary result

The frozen internal maturity rubric awards **Level 4** under availability-aligned scoring.

### CSI1000 / 000852.SH

```text
n_scored = 44,502
balanced_accuracy = 0.9940
macro_F1 = 0.9948
concrete_coverage = 0.9998
exact_accuracy = 0.9955
transition_F1 = 0.7795
transition_precision = 0.6416
transition_recall = 0.9930
median delay vs oracle availability = 0 bars / 0 minutes
median delay vs structural center = +6 bars / +30 minutes
false transitions/day = 0.2959
```

### STAR50 / 000688.SH

```text
n_scored = 22,100
balanced_accuracy = 0.9907
macro_F1 = 0.9917
concrete_coverage = 1.0000
exact_accuracy = 0.9931
transition_F1 = 0.7202
transition_precision = 0.5671
transition_recall = 0.9863
median delay vs oracle availability = 0 bars / 0 minutes
median delay vs structural center = +6 bars / +30 minutes
false transitions/day = 0.4186
```

All frozen Level-4 gates passed.

## Critical interpretation — do not overclaim the 99% score

The ~99% availability-aligned point-state score is **not** evidence that the system has independent human-like visual recognition accuracy of 99%.

After shifting the centered judge by its six-bar availability lag, the online 12-bar causal window and the judge's centered 12-return window cover almost the same K-line segment and use the same semantic thresholds. Therefore the availability-aligned score is primarily a strong **causal implementation / time-axis consistency** result.

The most informative secondary diagnostic for ordinary same-center chart reading is the persistence decoder without the six-bar alignment:

```text
CSI1000 same-center decoded balanced_accuracy = 0.6597
CSI1000 same-center decoded coverage = 0.8888
CSI1000 same-center decoded macro_F1 = 0.6895

STAR50 same-center decoded balanced_accuracy = 0.6678
STAR50 same-center decoded coverage = 0.9153
STAR50 same-center decoded macro_F1 = 0.6798
```

This is a real improvement over V1's raw 0.37–0.38 balanced accuracy and shows that treating market state as persistent rather than erasing it on every ambiguous bar materially improves recognition.

Availability alignment **without** the persistence decoder remained much weaker:

```text
CSI1000 aligned-raw balanced_accuracy = 0.4730
STAR50 aligned-raw balanced_accuracy = 0.4443
```

So the persistence state machine contributes real value; the near-perfect final point score additionally reflects the shared-window/shared-rule alignment.

## Remaining weakness

Transition recall is now very high, but precision is only about 64% on CSI1000 and 57% on STAR50. The system therefore detects almost all scoreable structural changes but still emits too many extra transitions.

Also, the offline judge is not independent of the recognizer: it shares state semantics and closely related formulas. This prevents any Level-5 or human-like recognition claim.

## Next scientifically meaningful step

Do **not** tune V2 until the 99% number gets even higher.

The next step should be a separately preregistered orthogonal/independent visual benchmark that does not reuse the recognizer's state formulas as the answer key. Preferred evidence order:

1. independent human/external chart annotations if available;
2. otherwise an orthogonal offline geometry/change-point judge built from distinct formulas and frozen before replay;
3. keep V1/V2 scores as development evidence and never relabel them fresh OOS.

The next benchmark should focus especially on:

- false transition reduction;
- trend <-> range changes;
- shock entry/exit;
- whether same-center decoded ~66–67% accuracy survives an independent answer key.

## Scope boundary

- chart/state recognition only, not profitability;
- no 2026;
- no UK alert validation;
- no production/live trading;
- no mutation of other repositories;
- no post-result V2 threshold/tolerance search;
- V1 and V2 historical results remain immutable development evidence.
