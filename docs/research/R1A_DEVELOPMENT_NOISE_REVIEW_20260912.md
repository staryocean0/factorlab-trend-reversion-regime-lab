# R1_A actual Development difference-noise review

## Decision

**`DEVELOPMENT_NOISE_ACCOUNTING_COMPLETED_NOT_ALPHA_TEST`**.

The authorized real-noise decomposition has executed. Two different bottlenecks are now observable: event-leg dispersion dominates individual paired observations, while the retained retrospective control assignment produces concentrated, overlapping calendar exposures. This does not identify irreducible noise, prove a causal shock model, supply a validated mean standard error or establish a new alpha PASS.

Freeze commit: `6315a8c8f0f31b34b02d40392ea2d5b484ad5f33`.
Decisive code: `ea7baea732a8b664509b168937c9ab45b31f22ad`.
Actions run `34664796626`, job `103474436130`: SUCCESS.
Evidence: `docs/ops/evidence/r1a_development_noise_20260912/`.

## Scope — actual Development, not relabeled Validation

CSI1000 uses the original 2015-01-05..2020-12-31 Development period: 350,561 observed index minutes, 1,462 trading dates, 1,752 eligible and matched R1_A events, and 1,482 distinct controls. STAR50 uses only its short 2020-07-23..2020-12-31 context: 26,400 minutes, 110 dates, 156 pairs and 143 distinct controls. The latter is a small contextual check, not a six-year replication.

Only seven manifest/hash-verified pre2021 price partitions were accessible in the decisive checkout. No 2021-2025 prices/return ledgers, ETF prices, MO prices or 2026 candidate prices were read. The original R1_A engine, thresholds, structural nonoverlap and nearest-control algorithm were reused unchanged inside these date limits. A separately named DEV cohort was generated; the existing Validation pairs were neither replaced nor rematched. Every cohort requires 240 remaining observed bars within its allowed input period, so the same pairs are used at all seven horizons.

The inherited same-year control pool and within-year normalizations are retrospective. A control can occur after its event. Outcome-blind nearest-neighbor matching is not synonymous with an online-available control rule; no causal or live-trading authority is inferred.

## 1. Individual-pair dispersion is not mostly a noisy control

Using empirical ddof=0 moments, exactly:

`V(E-C) = V(E) + V(C) - 2 Cov(E,C)`.

All horizons, years and both directions are retained. Illustrative CSI1000 results (SD in bp; variance contributions sum to 100%, including negative covariance terms):

| Horizon | Event SD | Control SD | Difference SD | Event variance / difference variance | Control variance / difference variance | Covariance term / difference variance |
|---:|---:|---:|---:|---:|---:|---:|
| 15 | 70.745 | 49.940 | 82.659 | 73.25% | 36.50% | -9.75% |
| 30 | 99.850 | 68.887 | 114.823 | 75.62% | 35.99% | -11.61% |

The h15/h30 event-control correlations are 0.0943/0.1113. Covariance removes 8.89%/10.40% of the sum of the two marginal variances, not most of it. Signed and unsigned paired dispersions are close here. A large universally cancelling common component is not established by these observations.

These SDs describe individual historical paired outcomes; they are NOT standard errors of an incremental mean and must not be compared to an alpha CI as though they were. Centered dispersion may include effect heterogeneity and regime differences, not only unpredictable noise.

## 2. Calendar accounting reveals a different problem

Each simple return was represented exactly as a sum of price changes divided by its own entry price. Signed weights from ALL event legs and ALL control legs were accumulated on the original observed minute clock. Overnight changes are assigned to the next observed price date. Daily sums retain every trading date, including zero-exposure dates, and are divided by the fixed full-sample pair-per-day rate. Their calendar average equals the original paired mean; no log/simple approximation is used.

This is diagnostic contribution bookkeeping, NOT a feasible portfolio: the control assignments were retrospective and overlapping capital is not modeled.

In the resulting CSI1000 daily contribution variance decomposition:

| Horizon | Event contribution | Control contribution | Covariance term |
|---:|---:|---:|---:|
| 15 | 21.00% | 82.68% | -3.68% |
| 30 | 24.55% | 79.30% | -3.85% |

There is no contradiction with the individual-pair table. Event outcomes are relatively dispersed across the calendar; selected controls reuse and overlap the same realized price paths. Calendar contribution variance is a different observable quantity from pair variance and from the unknown long-run variance of a sample mean.

The geometry is concrete:

- 25.34% of pairs use a control entry reused by at least another pair; maximum exact reuse is 10.
- Control date is later than the event date/index in 38.13% of pairs (comparison is by entry index); median absolute event-control date distance is 49 trading days, p90 150 days.
- About 20.15%/20.21% of h15/h30 within-pair event/control intervals overlap. This is retained as inherited geometry, not silently removed using future treatment information.
- At h15/h30, aggregate control minute-weight squared energy is 2.96x/3.73x the sum of the individual-control energies. This energy comparison assumes independent equal-variance elementary minute-return shocks; it is not an estimated real-market variance inflation factor.
- Exact repeated control entries account for 17.77%/14.11% of aggregate control energy. Additional cross-products between DIFFERENT but overlapping control intervals account for 48.46%/59.09%. Those cross-products are signed and can be negative in general; no negative component was clipped.

Thus merely requiring unique control IDs would not resolve all observed exposure concentration. Nor does this accounting prove that a new assignment can remove the concentration while preserving covariate balance, event coverage, the target estimand and statistical validity.

Daily centered products at lags 0/1/5/20/60 are retained without choosing a bandwidth or deriving p-values. Same-index returns on unrelated dates must not be treated as the same realized shock. A latent common economic factor has not been separately identified.

## 3. Heterogeneity and tails are not a free variance-reduction result

The fixed year x parent-direction x 30-minute-clock strata account for only 8.66%/7.36% of CSI1000 h15/h30 difference variance between strata; 91.34%/92.64% remains within those strata. There are 101 strata, six singletons. The complete empirical covariance identity is checked, including the singleton groups.

These are ex-post group means, not a causally available predictor. Even the displayed between-stratum portion cannot simply be claimed as achievable out-of-sample noise removal.

The top 1% of centered squared deviations contribute 32.13%/29.05% of h15/h30 pair dispersion; top 5% contribute 60.23%/58.46%. Nothing was trimmed, winsorized or filtered. The calendar contribution distribution is more concentrated still, but it is not the same sample unit. These observations motivate careful tail/overlap accounting, not automatic exclusion of difficult years or large moves.

## 4. Unequal-noise control-count accounting

A transparent hypothetical calculation now uses observed Development marginal Ve/Vc instead of assuming they are equal, while explicitly imposing event-control noise independence and independent added controls:

`V(E - mean_K C) / V(E - C_independent) = (Ve + Vc/K)/(Ve+Vc)`.

For h15/h30, K=infinity would retain approximately 66.74%/67.75% of this INDEPENDENT-reference variance, an information multiple of only 1.50x/1.48x. Positive correlation between controls reduces the benefit further. All fixed K=1/2/5/10/infinity and rho=0/0.5 cases are retained.

This is not a bound on the actual correlated/reused assignment, not a forecast, and not a measured gain from a new design. It does show why simply adding controls cannot be claimed to deliver the large information improvement discussed previously under unrelated planning assumptions. No controls were actually added.

## 5. What is and is not justified next

The generic estimator sweep remains closed. No new SE, p-value, confidence interval, preferred horizon or alpha decision was produced. The historical R1_A lead and previous non-promotion conclusions stand.

The concrete design issue is now the **control baseline and its exposure allocation**, not another significance formula: any subsequent proposal should use only information available at event time, explicitly address exact and overlapping control reuse, preserve the intended event population or disclose non-identification, and report covariate balance/coverage before outcomes. Replacing the old finite matched-pair contrast is a NEW measurement design, not a repair that retroactively promotes old results.

A future comparison would have to show both reduced concentration and useful noise reduction without erasing the question of incremental advantage over parent continuation. Simply dropping events, changing the side/year/horizon, or letting an ex-post common-factor fit explain away returns is not authorized. This round does not implement such a redesign or certify its feasibility.

There is no outstanding routine local data-transfer request. The qualified inference and data-role gates for new confirmation remain unresolved. The known 2026 candidate remains unopened, and no confirmation clock starts here.

## Engineering and evidence

Eight deterministic CSV tables retain 1,908 Development/context pairs, 13,356 horizon-specific leg records, full covariance partitions, clock/lag accounting and assumptions-only control scenarios. Regression verifies pinned original references, exact identities/counts and tightly bounded floating differences without rewriting original receipts. Synthetic tests separately verify common-noise cancellation, negative covariance, unequal marginal noise, reused intervals, exact simple-return telescoping and refusal to open post2020/mixed-role price files.

Sources and complete values: `noise_receipt.json`, `leg_variance.csv`, `stratum_covariance.csv`, `clock_accounting.csv`, `control_scale_scenarios.csv`, `calendar_lag_products.csv` and the two underlying Development ledgers in the evidence directory.

Primary mathematical references:

- Covariance normalization: https://numpy.org/doc/2.0/reference/generated/numpy.cov.html
- Total covariance identity: https://statproofbook.github.io/P/cov-tot
- Total variance identity: https://statproofbook.github.io/P/var-tot.html

`BLACKBOX_query_count=3`; `production_authority=false`; `fresh_oos=false`; `confirmation_protocol_frozen=false`; `confirmation_clock_started=false`; `horizon_selected=false`.
