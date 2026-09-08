# K-line recognizer hysteresis v5 — protocol

Date frozen: 2026-09-08
Parent: `research/kline-recognizer-optimization-v4`
Goal: improve the **same recognizer A** by making its state changes confidence-aware. No new evaluator/judge layer is introduced.

## 1. Architecture

Only two roles exist:

1. **Recognizer A** — the object being improved.
2. **Frozen v3 independent judge** — unchanged label/benchmark source.

V5 does not create another analysis tool. The v3 judge formulas, availability timing, and transition matching tolerance remain unchanged.

## 2. Base classifier is locked

V4 selected the regularized multinomial linear classifier with:

- `C = 1.0`;
- the existing 12 causal K-line features;
- class-balanced training loss.

V5 does **not** reopen model-family, feature, or `C` selection. It changes only A's internal state-switch policy.

## 3. Probability-aware state policy

At each eligible 5-minute bar the locked linear classifier produces probabilities for:

- `UpTrend`
- `DownTrend`
- `Range`
- `Shock`

A maintains one current confirmed state.

### Initial state

A concrete state is entered after the same top-probability class satisfies the selected confirmation count and its probability is at least `min_new_probability`.

### State switch

If the top-probability class differs from the current state, the candidate new state must satisfy **both**:

1. `p(new) >= min_new_probability`;
2. `p(new) - p(current) >= switch_margin`.

The same qualifying new state must persist for `confirmation_bars` consecutive eligible bars before A switches.

Otherwise A keeps the current state. A temporary loss of confidence does not itself erase a confirmed state.

State memory resets at each trading day; no overnight state carry is allowed.

## 4. Frozen tuning menu

Exactly the following policy grid is allowed:

- `switch_margin in {0.00, 0.05, 0.10, 0.15, 0.20}`
- `min_new_probability in {0.00, 0.45, 0.55, 0.65}`
- `confirmation_bars in {2, 3, 4}`

Total policies: `5 x 4 x 3 = 60`.

The v4 state policy is represented by:

`switch_margin=0.00, min_new_probability=0.00, confirmation_bars=3`.

No additional threshold, smoothing constant, model family, feature, or candidate may be introduced after tuning results are observed.

## 5. Temporal tuning folds

2025 has already been inspected in v4 and therefore is **not** an untouched holdout anymore. It must not be used for v5 parameter selection.

V5 selects the hysteresis policy only from rolling pre-2025 folds:

1. train through `2021-12-31`, validate calendar year `2022`;
2. train through `2022-12-31`, validate calendar year `2023`;
3. train through `2023-12-31`, validate calendar year `2024`.

Both CSI1000 and STAR50 are scored separately in every fold.

The linear model is refit for each fold using only information available through that fold's training end.

## 6. Tuning objective

A candidate is **eligible for selection** only if across every fold and both assets:

- balanced accuracy >= `0.75`;
- macro F1 >= `0.72`.

Among eligible candidates select lexicographically:

1. maximize the minimum transition F1 across all fold x asset cells;
2. minimize the maximum false transitions/day across all fold x asset cells;
3. maximize the minimum balanced accuracy across all fold x asset cells;
4. maximize the minimum macro F1 across all fold x asset cells;
5. deterministic simplicity tie-break: smaller `switch_margin`, then smaller `min_new_probability`, then smaller `confirmation_bars`.

If no policy satisfies the point-state floors, V5 fails closed and retains the v4 policy.

## 7. 2025 diagnostic only

After the policy is selected and locked, refit the locked linear classifier once using all eligible labeled data through `2024-12-31`.

Then score calendar year 2025 for:

- selected v5 policy;
- frozen v4 policy (`margin=0`, `min_probability=0`, `confirmation=3`).

Because 2025 was already viewed in v4, this comparison is **development diagnostic evidence only**, not a new holdout or fresh OOS claim.

## 8. Metrics

For each fold/asset and for the 2025 diagnostic report:

- balanced accuracy;
- macro F1;
- exact accuracy;
- concrete coverage;
- per-state precision/recall/F1/support;
- transition precision/recall/F1;
- false transitions/day.

The main engineering question is whether hysteresis reduces false state changes without destroying point-state recognition.

## 9. Boundaries

- optimize recognizer A directly;
- v3 judge remains frozen;
- no 2025 parameter selection;
- no 2026;
- no P&L or strategy-outcome selection;
- no production/live-trading claim;
- after v5 tuning results appear, preserve them and do not reopen the frozen candidate grid.
