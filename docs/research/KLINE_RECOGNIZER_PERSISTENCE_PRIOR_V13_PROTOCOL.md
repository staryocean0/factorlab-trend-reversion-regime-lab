# K-line recognizer low-weight persistence-prior v13 — protocol

Date frozen: 2026-09-09

Goal: integrate exactly one audited historical contribution into current champion v10: the v7 finding that previous-state/persistence information improves point-state classification, without reusing the failed v7 Markov decoder.

## Authority boundary

- current champion: `v10_temporal_blend`;
- champion result commit: `723404633fccb0a52181d2090cadbca3114dcc67`;
- source contribution: `v7_persistence_prior_point_state_signal`;
- v6/v12 Shock-exit inertia is out of scope;
- v8 switch-confidence signal is out of scope;
- champion and contribution authority files are read-only during execution.

## Fixed champion structure

V13 inherits v10 unchanged:
- primary state head: pooled multinomial linear classifier, C=1.0;
- temporal auxiliary: six-bar temporal-context linear classifier, C=0.1;
- temporal blend alpha=0.30;
- temporal-unavailable fallback to primary head;
- v5/v10 hysteresis decoder: margin 0.05, minimum new-state probability 0.45, confirmation 4 bars.

## Historical persistence model

For each rolling training fold, fit exactly the v7 pooled 4x4 transition matrix from pre-validation concrete v3 available labels:
- count only within-day consecutive labeled rows;
- no overnight transition counts;
- Laplace pseudocount 1.0;
- pooled across CSI1000 and STAR50;
- no validation-year or 2025 labels in the matrix fit.

Transition sharpness is fixed at `eta=2.0`, inherited from the v7 point-state-best candidate `markov_eta2_beta2`.

## Only v13 modification: one-step low-weight persistence prior

Let `e_t` be the complete v10 blended four-state probability on the current bar.

For each trading day:
- first valid bar: final probability is exactly `e_t`;
- later valid bars: take the **previous bar's v10 base probability** `e_(t-1)` (not a recursively filtered posterior) and form one-step predictive prior:

`q_t = e_(t-1) @ T_eta2`

Then blend this prior weakly into the current v10 probability:

`log p_t(k) = log e_t(k) + rho * log q_t(k)`

and normalize across four states.

Important:
- the prior uses previous **base v10 probabilities**, not previous v13 posterior;
- therefore no recursive Markov filter is recreated;
- no Markov argmax or Markov decoder is permitted;
- the final probabilities still pass through the unchanged v10 hysteresis decoder.

## Frozen candidate menu

Exactly 3 challengers:
- rho = 0.05
- rho = 0.10
- rho = 0.15

No post-result rho expansion.

## Rolling evaluation

- train through 2021 -> validate 2022;
- train through 2022 -> validate 2023;
- train through 2023 -> validate 2024.

Both assets scored separately.

V13 must be noninferior to champion v10 on aggregate worst-cell metrics:
- min balanced accuracy >= 0.7553851080081395;
- min macro F1 >= 0.7591912321042829;
- min transition F1 >= 0.19843342036553524;
- max false transitions/day <= 1.2066115702479339.

Material improvement requires at least one:
- min balanced accuracy +0.01;
- min macro F1 +0.01;
- min transition F1 +0.01;
- max false transitions/day -0.05.

Selection among promotable candidates:
1. highest min transition F1;
2. lowest max false transitions/day;
3. highest min balanced accuracy;
4. highest min macro F1;
5. smaller rho.

If none qualifies, v10 remains champion. Any local effect is audited for the Contribution Ledger.

## 2025 safety diagnostic

Only after a pre-2025 candidate qualifies:
- refit fixed v10 heads and transition matrix through 2024;
- run selected rho once on 2025;
- compare against unchanged v10;
- 2025 cannot select rho or change any component.

Safety veto if either asset degrades versus v10 by more than:
- balanced accuracy 0.01;
- macro F1 0.01;
- transition F1 0.01;
- false transitions/day +0.05.

2025 is consumed evidence, not fresh OOS.

## Forbidden

- recursive v7 posterior filtering;
- Markov argmax decoding;
- changing v10 alpha or classifiers;
- changing v10 decoder;
- adding v6/v12 Shock inertia;
- adding v8 switch confidence;
- changing eta after result;
- expanding rho after result;
- asset-specific rho;
- 2025 selection/rescue;
- P&L selection;
- runner mutation of champion/contribution authority files.
