# Continue here — direct K-line recognizer optimization v4

Date: 2026-09-08

The user explicitly corrected the research direction: stop building evaluator-on-evaluator layers. From v4 onward the architecture is intentionally simple:

```text
one recognizer A -> one frozen benchmark -> optimize A -> temporal holdout
```

The independent v3 judge is frozen and is only a label/benchmark source. Do not create another judge to analyze it.

## Active branch

```text
branch = research/kline-recognizer-optimization-v4
base = research/kline-independent-judge-v3
v3 result commit = c6487eab13fca2cd79a0c1c30fbc41c4943eede5
v4 result commit = 40e1a35bf134fd7eb9191a4537a9a2eea7f58a9c
```

## V4 optimization design

Protocol:

`docs/research/KLINE_RECOGNIZER_OPTIMIZATION_V4_PROTOCOL.md`

Temporal split:

```text
train/development <= 2022-12-31
validation / model selection = 2023-2024
final temporal holdout = 2025
```

2025 was not used for feature/model/hyperparameter/confirmation selection.

Fixed candidate menu = 13 configurations:

- current rule baseline, confirmation=2;
- class-balanced L2 multinomial linear model, C={0.1,1,10}, confirmation={1,2,3};
- diagonal Gaussian classifier, confirmation={1,2,3}.

Only the original causal K-line feature surface is available to fitted recognizers. Independent-judge fields are labels only, never features.

## Formal execution

Formal run completed successfully:

```text
immutable 52-partition market package validation = PASS
full repository pytest = PASS
13-candidate validation selection = PASS
selected configuration locked before 2025 = PASS
2025 holdout replay = PASS
v4 result commit = 40e1a35bf134fd7eb9191a4537a9a2eea7f58a9c
```

The one-shot GitHub workflow was deleted after completion.

Outputs:

`experiments/kline_recognizer_optimization_v4/`

## Selected recognizer

Validation selected:

```text
family = linear
C = 1.0
confirmation_bars = 3
```

Validation metrics:

```text
CSI1000 balanced_accuracy = 0.8462
CSI1000 macro_F1 = 0.8400
CSI1000 transition_F1 = 0.1544
CSI1000 false transitions/day = 1.7624

STAR50 balanced_accuracy = 0.8090
STAR50 macro_F1 = 0.8097
STAR50 transition_F1 = 0.1391
STAR50 false transitions/day = 1.7190
```

## 2025 holdout — direct recognizer improvement

### CSI1000

Optimized A:

```text
balanced_accuracy = 0.857
macro_F1 = 0.842
exact_accuracy = 0.843
transition_F1 = 0.140
false transitions/day = 1.753
```

Same-holdout frozen v3 recognizer baseline:

```text
balanced_accuracy = 0.750
macro_F1 = 0.740
exact_accuracy = 0.702
transition_F1 = 0.121
false transitions/day = 0.757
```

Optimized per-state F1:

```text
UpTrend = 0.904
DownTrend = 0.900
Range = 0.840
Shock = 0.723
```

### STAR50

Optimized A:

```text
balanced_accuracy = 0.815
macro_F1 = 0.810
exact_accuracy = 0.817
transition_F1 = 0.139
false transitions/day = 1.671
```

Same-holdout frozen v3 recognizer baseline:

```text
balanced_accuracy = 0.731
macro_F1 = 0.711
exact_accuracy = 0.679
transition_F1 = 0.139
false transitions/day = 0.844
```

Optimized per-state F1:

```text
UpTrend = 0.753
DownTrend = 0.938
Range = 0.835
Shock = 0.713
```

## V4 adjudication

Frozen result:

`recognizer_not_yet_improved`

This does **not** mean the classifier failed. Point-state recognition improved materially and generalized into the 2025 temporal holdout. The failure is specifically that the selected classifier changes state too frequently:

- transition F1 remains below the frozen 0.25 target;
- false transitions/day rose materially above the 0.70 target.

## Correct next engineering direction

Do not build a v4 judge, meta-judge, or new analysis layer.

Improve the same recognizer A directly. The next model should jointly address classification and switching behavior, for example using the selected linear model's class scores/probabilities plus a causal hysteresis / switching-cost decision rule.

The problem is now concrete:

```text
point-state classifier = substantially improved
state switching policy = too reactive
```

A proper next candidate search may tune recognizer-internal parameters such as probability margin, minimum confidence, challenger-vs-incumbent margin, and confirmation duration, using train/validation only. 2025 v4 remains immutable evidence and must not be reused as the next selection set; any next optimization needs a newly declared temporal/CV scheme or other held-back evidence.

## Scope boundary

- optimize recognizer A itself;
- fixed benchmark only, no evaluator chain;
- no 2026 unless explicitly opened as a genuinely new evaluation period under a new protocol;
- no UK validation;
- no profitability or live-trading claim;
- no mutation of unrelated repositories.
