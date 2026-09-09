# K-line recognizer Shock-exit soft-inertia v12 — protocol

Date frozen: 2026-09-09

Goal: integrate exactly one audited historical contribution into the current v10 champion: the v6 finding that Shock exits benefit from extra inertia, while avoiding v6's costly hard extra confirmation bars.

## Authority boundary

- current champion remains `v10_temporal_blend`;
- champion result commit remains `723404633fccb0a52181d2090cadbca3114dcc67`;
- v11 was not promoted and does not change the champion;
- source contribution: `v6_soft_transition_asymmetry` from the Contribution Ledger;
- v7 and v8 contributions are explicitly out of scope for v12;
- champion and contribution authority files are read-only during execution.

## Fixed champion structure

V12 inherits v10 unchanged:
- primary state head: pooled multinomial linear classifier, C=1.0;
- temporal auxiliary: six-bar temporal-context linear classifier, C=0.1;
- temporal log-probability blend alpha=0.30;
- fallback to primary head when temporal context is unavailable;
- base hysteresis: switch margin 0.05, minimum new-state probability 0.45, confirmation 4 bars.

## Only v12 modification: soft Shock-exit inertia

V6 showed that harder Shock exits reduced churn but hard waiting damaged point-state accuracy.

V12 therefore does **not** add confirmation bars.

Instead, while the already-decoded current state is `Shock`, before evaluating whether the current bar should leave Shock, apply a small causal log-odds bonus to the Shock probability:

`log p_adj(Shock) = log p_blend(Shock) + gamma`

All other class log probabilities are unchanged, then probabilities are renormalized.

When current state is not Shock, probabilities are unchanged.

The existing v5/v10 hysteresis rules are then applied to the adjusted probability row.

This is a soft state-dependent prior inside recognizer A, not a new evaluator or post-classification tool.

## Frozen candidate menu

Exactly 3 challengers:
- gamma = 0.10
- gamma = 0.20
- gamma = 0.30

The unchanged v10 champion is the comparison baseline only.

No post-result gamma expansion.

## Rolling evaluation

Same pre-2025 folds:
- train through 2021 -> validate 2022;
- train through 2022 -> validate 2023;
- train through 2023 -> validate 2024.

Both assets scored separately in every fold.

A v12 candidate must be noninferior to the v10 champion across aggregate worst-cell metrics:
- minimum balanced accuracy >= 0.7553851080081395;
- minimum macro F1 >= 0.7591912321042829;
- minimum transition F1 >= 0.19843342036553524;
- maximum false transitions/day <= 1.2066115702479339.

Material improvement requires at least one:
- minimum transition F1 improves by >= 0.01;
- maximum false transitions/day falls by >= 0.05;
- minimum balanced accuracy improves by >= 0.01;
- minimum macro F1 improves by >= 0.01.

Among promotable candidates select:
1. highest minimum transition F1;
2. lowest maximum false transitions/day;
3. highest minimum balanced accuracy;
4. highest minimum macro F1;
5. smaller gamma.

If none qualifies, v10 remains champion. Any local v12 effect may still be audited for the Contribution Ledger.

## 2025 safety diagnostic

Only after a pre-2025 candidate qualifies:
- refit the fixed v10 heads through 2024;
- run the selected gamma once on 2025;
- compare against unchanged v10 on the same consumed diagnostic;
- 2025 cannot select gamma or modify any other component.

Safety veto if either asset degrades versus v10 by more than:
- balanced accuracy: 0.01;
- macro F1: 0.01;
- transition F1: 0.01;
- false transitions/day: +0.05.

2025 is already-consumed evidence, not fresh OOS.

## Forbidden

- changing v10 alpha;
- changing either classifier C;
- changing feature surfaces;
- changing ordinary transition rules;
- hard extra Shock confirmation bars;
- adding v7 persistence or v8 switch-gate signals;
- asset-specific gamma;
- expanding gamma after results;
- 2025-based selection or rescue;
- P&L-based selection;
- runner mutation of champion/contribution authority files.
