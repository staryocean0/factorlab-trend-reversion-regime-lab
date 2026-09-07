# Reversal / Mean-Reversion Baseline Whitepaper v0.1

Status: specification for first executable research iteration.  
Scope: MR0, MR1, REV0 only. No trend-following strategy.

## 1. Observation timing

All phase-1 signals are evaluated after a bar is fully closed.

Let completed bar `t` contain `(O_t, H_t, L_t, C_t)`.

Features may use:

- all completed bars through `t`;
- current bar OHLC for rejection/failure evidence;
- lagged reference/scale statistics that are explicitly shifted before `t`.

A signal formed at close `t` may enter no earlier than open `t+1`.

## 2. Physical horizons

Primary bar size: 5 trading minutes.

Default horizons:

- anchor lookback: 120 trading minutes;
- ATR scale: 120 trading minutes;
- prior breakout range: 60 trading minutes;
- prior directional leg: 60 trading minutes;
- shock concentration window: 60 trading minutes.

The same physical horizons are used on 1m robustness data by changing bar counts, not by changing the economic time scale.

## 3. Causal anchor

Let `N_A` be the bar count corresponding to 120 trading minutes.

The anchor is an EMA of **prior closes**:

`A_t = EMA(C_{<=t-1}; span=N_A)`.

The current close is excluded from the anchor.

This ensures that the displacement of the signal bar is measured against a reference that was already known before that bar closed.

## 4. Causal ATR scale

True range is:

`TR_i = max(H_i-L_i, |H_i-C_{i-1}|, |L_i-C_{i-1}|)`.

Scale at signal time is the mean of true range strictly before the signal bar:

`ATR^-_t = mean(TR_{t-N_ATR}, ..., TR_{t-1})`.

The baseline normalized stretch is:

`S_t = (C_t - A_t) / ATR^-_t`.

Positive `S_t` means above anchor; negative means below.

## 5. Lagged breakout range and failed acceptance

For the prior 60 trading minutes, excluding bar `t`:

`U_t = max(H_{t-N_R}, ..., H_{t-1})`

`D_t = min(L_{t-N_R}, ..., L_{t-1})`.

Upside break:

`B^+_t = I(H_t > U_t)`.

Downside break:

`B^-_t = I(L_t < D_t)`.

Failed upside acceptance:

`F^+_t = I(H_t > U_t and C_t <= U_t)`.

Failed downside acceptance:

`F^-_t = I(L_t < D_t and C_t >= D_t)`.

This is intentionally strict and simple: the current bar attempted to leave the old range but closed back inside it.

## 6. Directional leg

For the 60-trading-minute prior/current path:

`R^leg_t = log(C_t) - log(C_{t-N_L})`.

Leg direction:

`d_t = sign(R^leg_t)`.

Path efficiency:

`E_t = |R^leg_t| / sum_{i=t-N_L+1}^t |r_i|`.

`E_t` approaches 1 for a monotone path and approaches 0 for a highly oscillatory path.

ATR-normalized leg displacement:

`D^leg_t = (C_t - C_{t-N_L}) / ATR^-_t`.

## 7. Shock concentration diagnostic

For a 60-trading-minute window:

`Q_t = |r_t| / sum_{i=t-N_Q+1}^t |r_i|`.

This is not a signal in v0.1. It is a failure-analysis coordinate.

High `Q_t` means the latest bar contributes a large share of recent absolute movement.

## 8. MR0 — naked stretch reversion

Baseline threshold:

`z = 2.0`.

Signal:

- if `S_t <= -z`: `signal_t = +1`;
- if `S_t >= +z`: `signal_t = -1`;
- otherwise `0`.

This strategy deliberately fades extreme displacement without confirmation.

Its purpose is to establish the raw mean-reversion opportunity and expose its failure under accepted directional movement.

## 9. MR1 — stretch plus failed acceptance

Use the same stretch condition as MR0, plus rejection:

Long:

`S_t <= -z and F^-_t = 1`.

Short:

`S_t >= +z and F^+_t = 1`.

MR1 differs from MR0 by one mechanism only: failed range acceptance.

## 10. REV0 — failed breakout after an established directional leg

Baseline leg requirements:

`E_t >= 0.60`

and

`|D^leg_t| >= 1.50`.

Short reversal:

`D^leg_t >= 1.50`, `E_t >= 0.60`, and `F^+_t = 1`.

Long reversal:

`D^leg_t <= -1.50`, `E_t >= 0.60`, and `F^-_t = 1`.

The trade is opposite the established leg.

REV0 does not follow trends. The directional-leg measurement is only a precondition for identifying a turning-point candidate.

## 11. Diagnostic execution

For a nonzero signal at close `t`:

entry price:

`P_entry = O_{t+1}`.

For fixed holding `h` bars:

`P_exit = C_{t+h}`.

Gross directional diagnostic return:

`R_event = signal_t * (P_exit / P_entry - 1)`.

No signal can enter on bar `t`.

The first iteration uses fixed holding periods instead of a stop/target engine to avoid intrabar ordering ambiguity.

## 12. Frozen-anchor reversion outcome

At signal time store `A_t`.

For a long signal, the anchor is considered touched on the first future bar `k` such that:

`H_{t+k} >= A_t`.

For a short signal:

`L_{t+k} <= A_t`.

The anchor is frozen at `A_t`; it does not update after entry.

Report:

- hit probability within 30/60/120 trading minutes;
- median bars to hit conditional on success.

This outcome directly tests the "return toward mean" mechanism.

## 13. Bar geometry diagnostics

The implementation also records:

`CLV_t = (2C_t-H_t-L_t)/(H_t-L_t)`,

upper-wick ratio,

lower-wick ratio.

They are not required for MR0/MR1/REV0 entry in v0.1. They are retained to explain failures before proposing a next iteration.

## 14. Amount diagnostic

If `amount` is present, compute a robust log-amount z-score relative to prior observations.

It is not an entry condition in v0.1.

The source field is transaction amount in CNY and must not be relabeled as share volume or turnover.

## 15. Session rule

Diagnostic fixed-horizon returns are masked if entry/exit require crossing into another `trading_day`.

The bar-count horizon is measured in tradable bars. Lunch handling and exact continuous-auction session filters must be verified in the data audit before economic interpretation.

## 16. First robustness pass

Only after unchanged v0.1 baseline results exist:

- MR stretch: 1.5 / 2.0 / 2.5 ATR;
- REV efficiency: 0.50 / 0.60 / 0.70;
- REV leg displacement: 1.0 / 1.5 / 2.0 ATR;
- holding: 30 / 60 / 120 trading minutes;
- 5m vs matched 1m.

All cells are reported; no best-cell-only reporting.

## 17. Non-negotiable falsification checks

- Prefix invariance: appending future data must not change features/signals already computed.
- Monotone accepted path must not trigger REV0 merely because it is stretched.
- Failed breakout after a qualifying leg must trigger the appropriate opposite REV0 direction.
- MR1 must be a strict subset of MR0 for the same stretch threshold.
- Diagnostic return must enter at next-bar open, not the signal close.
- Cross-day diagnostic returns must be masked under the phase-1 contract.

## 18. What v0.1 does not solve

It does not yet solve:

- optimal equilibrium anchor;
- stop loss / take profit;
- overlapping position management;
- event de-duplication;
- transaction cost calibration;
- tradable carrier selection;
- news/information shock identification;
- trend/reversal arbitration.

Those are intentionally deferred until the baseline's failure atlas shows which problem matters.
