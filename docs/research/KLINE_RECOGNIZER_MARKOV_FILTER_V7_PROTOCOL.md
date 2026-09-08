# K-line recognizer Markov persistence filter v7 — protocol

Date frozen: 2026-09-08

Goal: improve the same recognizer A by replacing hand-written transition confirmation counts with a causal learned state-persistence filter. No new evaluator or label source is introduced.

## Fixed components

- base classifier: the v4-selected multinomial linear classifier;
- classifier regularization: `C=1.0`;
- causal feature surface: unchanged from v4/v5;
- benchmark / supervised state labels: frozen v3 independent judge at declared information-availability time;
- current promoted baseline: v5 universal hysteresis policy;
- v6 type-specific fixed-confirmation result is preserved as a failed branch and is not used as a baseline.

## Markov filter

For each rolling training fold, learn one pooled 4x4 transition matrix across CSI1000 and STAR50 from pre-validation concrete v3 available labels only.

States:
- UpTrend
- DownTrend
- Range
- Shock

Training rules:
- count only within-day consecutive eligible labeled rows;
- never count overnight transitions;
- add Laplace pseudocount `1.0` to every transition cell before row normalization;
- learn a pooled class prior from the same training labels with pseudocount `1.0` per class;
- no 2025 labels may enter model or policy selection.

Online filtering is strictly causal. At each bar:

1. the locked linear classifier produces four emission probabilities `e_t`;
2. prior predictive state probability is `q_t = p_{t-1} @ T_eta`;
3. posterior is proportional to `q_t * e_t^beta`;
4. normalize to sum to one;
5. emit the posterior argmax as the current concrete state;
6. reset posterior at each trading day to `training_prior * e_t^beta`, normalized.

No backward smoothing, future bars, Viterbi look-ahead, or second confirmation filter is permitted.

`T_eta` is formed by raising every learned transition probability to power `eta` and row-normalizing. Higher `eta` sharpens the learned persistence/transition structure.

## Frozen candidate menu

Exactly 12 Markov candidates:

- transition sharpness `eta in {0.5, 1.0, 2.0, 4.0}`;
- emission power `beta in {0.5, 1.0, 2.0}`.

Add the unchanged v5 universal hysteresis policy as the thirteenth baseline candidate for comparison only.

No post-result candidate expansion.

## Rolling selection

- train through 2021 -> validate 2022;
- train through 2022 -> validate 2023;
- train through 2023 -> validate 2024.

Both assets are scored separately in every fold.

Point-state eligibility floors across all fold x asset cells:
- balanced accuracy >= 0.75;
- macro F1 >= 0.72.

A Markov candidate may be promoted over v5 only if its pre-2025 aggregate also satisfies:
- minimum transition F1 >= v5 minimum transition F1;
- maximum false transitions/day <= v5 maximum false transitions/day;
- and at least one material improvement:
  - minimum transition F1 improves by >= 0.01, or
  - maximum false transitions/day falls by >= 0.05.

Among promotable Markov candidates select lexicographically:
1. highest minimum transition F1;
2. lowest maximum false transitions/day;
3. highest minimum balanced accuracy;
4. highest minimum macro F1;
5. smaller `eta`;
6. smaller `beta`.

If no Markov candidate is promotable, keep v5 as the active recognizer.

## 2025 diagnostic

Only after selection is frozen:
- refit classifier and transition matrix through 2024;
- compare the selected v7 candidate (if any) against v5 on 2025.

2025 has already been consumed in earlier development, so it is diagnostic only, not fresh OOS.

A 2025 useful-improvement diagnostic requires both assets separately:
- transition F1 >= v5;
- false transitions/day <= v5;
- balanced accuracy >= 0.75;
- macro F1 >= 0.72.

Strong target remains:
- transition F1 >= 0.30;
- false transitions/day <= 0.80.

Failure does not permit reopening the frozen candidate menu.

## Forbidden

- new evaluator layers;
- changing v3 labels;
- new chart features;
- changing classifier family or `C`;
- asset-specific hand-tuned transition parameters;
- 2025-based selection;
- backward smoothing / future information;
- P&L-based selection;
- post-result parameter expansion.
