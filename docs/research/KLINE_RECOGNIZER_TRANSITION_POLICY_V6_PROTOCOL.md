# K-line recognizer transition policy v6 protocol

Date frozen: 2026-09-08

Goal: improve the same recognizer A by changing only its state-switch policy. No new evaluator, no new label source, no new feature family.

## Fixed baseline

- classifier family remains the v4-selected multinomial linear recognizer;
- classifier regularization remains `C=1.0`;
- causal feature surface remains unchanged;
- v3 independent judge remains the frozen benchmark/label source;
- v5 universal policy remains an explicit baseline candidate:
  - switch margin `0.05`;
  - minimum new-state probability `0.45`;
  - confirmation `4` bars.

## Research question

Can the same recognizer make better transition decisions when confirmation rules depend on transition type rather than one universal rule?

## Transition classes

1. `trend_to_range`: `UpTrend/DownTrend -> Range`.
2. `range_to_trend`: `Range -> UpTrend/DownTrend`.
3. `enter_shock`: any non-Shock state -> `Shock`.
4. `exit_shock`: `Shock` -> any non-Shock state.
5. `default`: all remaining concrete-to-concrete changes, fixed at the v5 universal rule.

## Frozen candidate menu

No post-result expansion is allowed.

Each of the four explicit transition classes has exactly two preregistered settings:

| transition type | fast / permissive | slow / strict |
|---|---|---|
| trend_to_range | margin 0.05, min probability 0.45, 4 bars | margin 0.10, min probability 0.55, 5 bars |
| range_to_trend | margin 0.05, min probability 0.45, 3 bars | margin 0.10, min probability 0.55, 4 bars |
| enter_shock | margin 0.00, min probability 0.45, 1 bar | margin 0.05, min probability 0.55, 2 bars |
| exit_shock | margin 0.05, min probability 0.45, 4 bars | margin 0.10, min probability 0.55, 5 bars |

The Cartesian product of the two settings across the four transition types gives exactly `2^4 = 16` type-specific candidates. Add the unchanged v5 universal policy as the seventeenth candidate.

`default` transitions always use margin `0.05`, minimum probability `0.45`, confirmation `4` bars.

## Causal decoder rules

- state memory resets at each trading day;
- initial state entry uses the default v5 rule (margin is irrelevant before an existing state exists);
- when the top-probability class equals the current state, pending transition evidence is cleared;
- otherwise the decoder classifies `(current_state -> proposed_state)` into one of the transition types above and applies that type's frozen rule;
- a transition qualifies only when both the minimum proposed-state probability and probability-margin conditions pass;
- qualifying evidence must persist for the configured consecutive-bar count;
- a different proposed state resets the pending count;
- no second transition filter is applied after the type-specific decoder.

## Selection data

Use rolling pre-2025 folds only:

- train through 2021 -> validate 2022;
- train through 2022 -> validate 2023;
- train through 2023 -> validate 2024.

Both CSI1000 and STAR50 are scored separately in every fold. 2025 is forbidden from model/policy selection.

## Selection objective

First require worst-cell point-state floors across all fold x asset cells:

- balanced accuracy >= 0.75;
- macro F1 >= 0.72.

Among eligible candidates choose lexicographically:

1. highest minimum transition F1 across fold x asset cells;
2. lowest maximum false transitions/day;
3. highest minimum balanced accuracy;
4. highest minimum macro F1;
5. lower total confirmation-bar burden;
6. lower total probability-margin burden;
7. lower total minimum-probability burden;
8. deterministic candidate id.

If none of the 16 type-specific candidates pass the point floors, preserve the v5 universal baseline.

## 2025 diagnostic

After selection is locked, refit the unchanged linear model through 2024 and compare selected v6 vs v5 universal policy on 2025.

2025 was already inspected in v4/v5, so this is consumed-development diagnostic evidence, not fresh OOS validation.

## Success interpretation

V6 is a useful improvement only if the 2025 diagnostic shows, on both assets separately:

- transition F1 >= the v5 diagnostic transition F1;
- false transitions/day < the v5 diagnostic false transitions/day;
- balanced accuracy >= 0.75;
- macro F1 >= 0.72.

A stronger target is transition F1 >= 0.30 and false transitions/day <= 0.80 on both assets, but failure to hit the stronger target does not permit reopening the frozen candidate menu.

## Forbidden

- new chart features;
- changing classifier family or `C`;
- changing benchmark labels;
- tuning on 2025;
- new evaluator layers;
- P&L-based selection;
- post-result candidate expansion.
