# R1_A bounded method calibration — completed and not promoted

## Decision

`BOUNDED_SYNTHETIC_METHOD_REVIEW_COMPLETED_NO_CONFIRMATION_AUTHORITY`.

The authorized finite method comparison has executed. Neither a formally ready confirmation estimator nor an information-efficiency solution has been established. R1_A remains a historical research lead, not a disproved mechanism. This round ends the specified estimator sweep rather than triggering more bandwidth, grouping or significance searches.

Freeze commit: `3032c6567b15c7df705f09101d63ba1caeadd4d1`.
Decisive code commit: `bd1b4b7fac45bf5075be84a4a666287df4a411b9`.
Actions run: `34662714569`, job `103468357915`: SUCCESS.
Evidence: `docs/ops/evidence/r1a_method_calibration_20260912/`.

## What actually ran

Three implementable procedures plus one known-covariance oracle were evaluated on seven fixed synthetic models, 28 fixed index/ETF/horizon designs, and 2,000 replicates per model. This produces 392,000 design datasets within 14,000 joint replicate universes; the design datasets are not independent of one another. All 784 method/design/DGP rows, 84 joint-family rows, 336 planning-ratio rows and 20 explicit multiple-control scenarios are retained.

Historical inputs were the original 3,098 R1_A pair identities, endpoint-availability timestamps, already disclosed nuisance SD/SE values, and trading_day columns from five hash-verified CSI1000 calendar partitions. No market OHLC column, ETF endpoint-return ledger, 2026 price file or new confirmation result was loaded by the method runner. The decisive checkout independently enforced that real ETF outcome files and new candidate data were absent.

The means in the null simulations are zero. The power cases impose constant 2/4/6bp effects on the identical random draws. These are assumptions, not old R1_A means treated as true. No historical p-value was recalculated with an alternative method.

## Methods and different estimands

1. `GRAPH_T_BASELINE`: the earlier union-of-calendar-exposure-cliques estimator, unchanged.
2. `EXPOSURE_SCORE_HAC6`: copied residual scores on every touched calendar block, followed by a fixed Bartlett six-block-lag covariance. It accounts for cross-block serial terms but duplicates some contributions. This is a PSD incidence-score adaptation with an IID floor, not an automatic application of a standard HAC theorem to multiply attached pairs.
3. `FIVE_YEAR_GROUP_T`: five calendar-year mean estimates, requiring both event and control paths to lie in their year, followed by t[4]. With heterogeneous effects, its equal-year estimand differs from the original pair-weighted mean. This target change is explicit, and no real equal-year return table was computed.
4. `ORACLE_MEAN_NORMAL_REFERENCE`: the simulator knows the true imposed covariance and hence the full-pair-mean variance. This is unavailable in practice and is never an eligible deployed procedure. Gaussian coverage is an oracle reference; heavy-tail coverage remains a normal approximation.

All procedures/model parameters were fixed before results. Inference validity requires assumptions about covariance, dependence decay or approximately independent group estimates. None is established merely by software tests or a finite simulation grid.

## Cross-block dependence: there is an improvement, not a universal repair

Nominal 5% single-contrast false rejection ranges over all 28 designs:

| Imposed scenario | Old graph | Exposure-score HAC6 | Five-year group t |
|---|---:|---:|---:|
| Independent Gaussian | 3.65%-4.25% | 0.90%-1.65% | 4.45%-5.15% |
| Independent shared-block Gaussian | 4.60%-6.45% | 1.20%-3.40% | 4.40%-5.75% |
| AR block correlation 0.6 | 7.55%-22.65% | 2.20%-5.45% | 5.20%-7.00% |
| AR block correlation 0.9 | 18.55%-50.30% | 6.15%-19.85% | 9.30%-16.00% |
| Heavy-tailed AR(0.6) | 7.85%-22.70% | 2.20%-5.45% | 4.70%-6.30% |
| Heteroskedastic AR(0.6) | 12.00%-26.95% | 2.90%-5.75% | 5.15%-6.30% |
| Signed event/control and exact reuse, AR(0.6) | 4.00%-4.90% | 1.10%-2.05% | 4.45%-5.20% |

HAC6 substantially improves the specified moderate-serial cases, but strong persistence still causes substantial over-rejection. It is often conservative in easier cases. The five-year method has acceptable displayed-family behavior here but its marginal tests over-reject in the strong-serial scenario; it also changes the weighting target. Do not summarize it as having failed all joint error checks.

The joint simulation shares calendar shocks across carriers and pair innovations across horizons/layers. This directly checks the probability of at least one false rejection, not a sum of marginal rates. For the 14-contrast ETF family:

| Imposed serial correlation | Old graph family error | HAC6 family error | Group-t family error |
|---|---:|---:|---:|
| 0.6 | 11.75% | 2.40% | 1.75% |
| 0.9 | 38.60% | 10.35% | 5.10% |

The prespecified limited screen requires both marginal-size safeguards and joint-family Monte Carlo upper bounds, plus >=99% quantification. No non-oracle method clears all conditions. The known-covariance oracle has zero severe marginal/family flags but is excluded by design, not because it empirically failed.

All methods quantified every replicate in this run. Low rejection therefore is not produced by silently discarding problematic simulation draws. This is one stipulated joint dependence structure, not a test of every possible family dependence. The previous simulation used different seeds and simpler random effects; this is not intended as byte-identical reproduction of its rejection counts.

## Lower error is not the same as more information

An illustrative fixed signed/reuse simulation at CSI1000 index h15 and imposed 4bp mean gives positive family14 detection probabilities of 32.00% for the old graph, 13.15% for HAC6, 7.80% for group t and 38.05% for the known-covariance oracle. The geometry is the entire historical-sized cohort, not one future year. This example does not rank methods for live deployment: the group target is different, the oracle is unavailable, and the DGP is only an assumption. It illustrates why more conservative uncertainty correction cannot be sold as a gain in sample information.

The signed scenario also matters scientifically. Opposite event/control factor loadings and reused clock innovations yield much milder graph distortion than unsigned persistent common effects. That does not establish that actual R1_A noise behaves this way. It does show that the earlier worst-case unsigned model is not a universal description of the paired-price process. A real nuisance-noise decomposition, rather than another search for a favorable p-value, is the informative next question.

## Can simply adding controls solve the information problem?

Using the previous plug-in power assumptions, a 243-trading-day index budget with family 14 and target power 80% requires the following reductions in variance of the measured increment:

| Assumed effect | h15 variance reduction needed | h30 variance reduction needed |
|---|---:|---:|
| 2bp | 98.66% | 99.50% |
| 4bp | 94.65% | 98.01% |
| 6bp | 87.96% | 95.52% |

At 4bp, the corresponding information multipliers are approximately 18.69x and 50.27x. These inherit the old nuisance/variance-rate assumptions; they are not achieved R-squared values, universal lower bounds, new sample-size commitments or forecasts about decades of stationary markets.

A separate transparent calculation considers equal event and control noise variance, event noise independent of the control noises, and K controls with common pairwise noise correlation r:

`Var(event - mean_K_controls) / Var(event - one_control) = [1 + r + (1-r)/K]/2`.

With independent controls (r=0), K=2 gives ratio 0.75, K=5 gives 0.60, and K=infinity gives 0.50. Thus even infinitely many independent controls only provide 2x information in this balanced model, versus the 18.69x/50.27x old one-year planning gaps. Positive control correlation weakens the benefit. This is an explicit assumption-based bound, not a universal statement or a measured event/control decomposition for R1_A. A radically different noise composition could change the conclusion and must be measured honestly.

No control was actually added, no regression/residualization fitted, and no new matching or signal rule was implemented.

## Program action and finite stop

Do not launch formal confirmation, select a new estimator for the existing R1_A means, or open 2026 candidate outcomes on these results. Preserve R1_A as an unconfirmed lead; neither the mechanism nor its observed historical mean is refuted by a failed method screen.

This finite estimator screen is complete. Do not extend it with different lags, group counts, seeds or model deletions to manufacture a screen PASS. If further research is authorized, the concrete question is a Development-only decomposition of event noise, control noise and signed/common calendar components, with no new significance certificate. Any candidate variance-reducing measurement must preserve the intended estimand or explicitly declare a new one, be available without future information, and show useful efficiency before consuming a confirmation set. This future task is not executed or frozen by the present receipt.

No routine local data transfer is outstanding. All 2021-2025 source files and previous experiments remain intact; the 2026 candidate is still metadata-only with unresolved R1_A-specific exposure. The earlier full-path insufficiency and failed primary all-seven-endpoint common cohort are not rewritten or opened.

## Reproduction and primary method references

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=src:. \
  python research/r1a_method_calibration/study.py --output /tmp/r1a-method-new
```

- Newey and West, positive-semidefinite HAC construction and its assumptions: https://www.nber.org/papers/t0055 . The duplicate-incidence adaptation above has additional structure and is not automatically covered by the original theorem.
- Kojevnikov, Marmer and Song, network dependence and the tradeoff between dependence decay and network density: https://arxiv.org/abs/1903.01059 . The real dependence conditions have not been verified here.
- Ibragimov and Mueller, group-estimator t inference: https://collaborate.princeton.edu/en/publications/t-statistic-based-correlation-and-heterogeneity-robust-inference/ . Approximate independence and distributional conditions of group estimates are substantive assumptions, not consequences of creating five groups.

`BLACKBOX_query_count=3`; `production_authority=false`; `fresh_oos=false`; `confirmation_protocol_frozen=false`; `confirmation_clock_started=false`; `horizon_selected=false`.
