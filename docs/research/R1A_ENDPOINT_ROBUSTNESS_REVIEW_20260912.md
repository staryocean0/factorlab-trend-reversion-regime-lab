# R1_A endpoint robustness — interpretation and program decision

## Decision

Completed: `RETROSPECTIVE_ENDPOINT_ROBUSTNESS_COMPLETED_NO_PRODUCTION`.

Scientific interpretation: **R1_A remains a historical short-horizon lead, not a statistically established trading edge.** The fixed calendar-dependence/multiplicity checks do not justify promotion. This is INCONCLUSIVE evidence, not a zero-effect/equivalence finding or closure of the R1_A mechanism identity.

Sources: `docs/ops/evidence/r1a_endpoint_robustness_20260912/REPORT.md`, `robustness_receipt.json`, `all_56_inference_cells.csv`, and `missing_residual_scenarios_NOT_ESTIMATES.csv`.

Freeze commit: `f098e4702c03a6374dfd8332fcfc1ee10882cced`. Decisive code commit: `c7365dcd6111c248dcb6ab833306bb7a58c7e265`. Cloud run: `34658568504`, job `103456110997`, SUCCESS after synthetic tests.

All endpoint means and original source/availability information were already known before this freeze. This is a retrospective uncertainty analysis of the fixed table, not a prospective preregistration, untouched validation set, or correction of every earlier research choice.

## Dependence changes uncertainty, not the historical means

The primary specification uses fixed 20-trading-day calendar blocks. Two pairs are connected if either their event or control path touches a common block, including event-to-control cross-role sharing. Multiple shared blocks are counted once. The graph sandwich has an IID-SE floor and approximate t reference with occupied-block degrees of freedom. Fixed sensitivities use a shifted 20-day origin and two 5-day origins. None was selected based on its result.

This is a specifically documented calendar-exposure adaptation of dependency-robust inference. Its negligible-off-graph-dependence and effective-sample assumptions have not been proved for this dataset; the t calibration is a heuristic, not an exact finite-sample guarantee. A green CI cannot validate those assumptions.

| Carrier | h | Unchanged paired mean bp | IID SE bp | Primary dependence SE bp | Pointwise 95% interval bp | 14-comparison interval bp |
|---|---:|---:|---:|---:|---|---|
| 512100.SH | 15 | +4.368 | 1.560 | 2.169 | [+0.029,+8.707] | [-2.211,+10.948] |
| 512100.SH | 30 | +7.074 | 2.198 | 3.676 | [-0.279,+14.427] | [-4.077,+18.224] |
| 588000.SH | 15 | +3.118 | — | 2.851 | [-2.585,+8.821] | [-5.529,+11.766] |
| 588000.SH | 30 | +3.963 | — | 3.697 | [-3.432,+11.358] | [-7.251,+15.177] |

The complete seven-horizon table for both carriers is retained, including negative and imprecise cells. Under the primary 14-contrast Bonferroni adjustment, **zero of 14** lower bounds are strictly positive. The stronger all-four-specification check over 56 displayed contrasts also yields **zero positive cells**. It is not necessary to rely on that stricter check to reach the non-promotion decision: the primary check already fails to establish positive increments.

At CSI1000 h15 the pointwise interval only barely excludes zero; both 5-day variants include zero pointwise. At h30 the primary pointwise interval already includes zero. Do not cherry-pick another block origin to restore a significance declaration.

Displayed-family adjustment does not correct unknown earlier signal/payoff searches, repeated reuse of these years, matching confounding, source error or informative observation selection. No fresh-OOS or causal certificate is issued.

## Positive evidence that survives, with narrower meaning

Exact control reuse is not extreme at the CSI1000 short locations: h15 has 1,177 distinct controls among 1,268 observed pairs; h30 has 1,170 among 1,259; maximum reuse is four in both. Giving every distinct control equal total weight still gives +3.780/+6.356bp at h15/h30.

A deterministic no-overlap diagnostic selects clocks from ALL original pairs before checking endpoint availability. At h15 it retains 901 observed pairs with +2.816bp increment; at h30, 759 pairs with +6.405bp. The minimum increment after separately deleting each exposure year is +2.600/+4.995bp. No bad year is removed from the primary table.

These diagnostics support retaining a short-horizon lead. They do not make the thinned observations independent or validate a new trading rule. Longer horizons are less stable: CSI1000 h60/h120 increments on the clock-disjoint subsets are -0.953/-0.221bp, versus +6.976/+7.026bp in the original observed table. This is a sensitivity to cohort/overlap structure, not proof that overlap alone caused an upward bias.

STAR50 short-horizon effects weaken too: equal-control h15/h30 increments are +2.010/+2.427bp; clock-disjoint increments +1.384/+1.910bp. It remains related secondary evidence, not independent confirmation of CSI1000 alpha.

## Missingness: pooled stability is not annual stability

No missing ETF price or outcome was filled. The direct tipping threshold is algebraic: if N original pairs contain n observed pairs and m missing pairs, the mean missing ETF increment that makes the full-original-cohort mean zero is `-sum(observed ETF increments)/m`.

For CSI1000 pooled h15/h30, the missing paired-increment means required for zero are approximately -197.824/-240.700bp. These are not measured returns, a likelihood judgment, or proof missingness can be ignored.

The annual view is materially weaker. CSI1000 h30 in **2021** has 159 observed of 186 original pairs. Its observed increment is +1.257bp, but only **-7.403bp** average increment across the 27 missing pairs would make that year's full-cohort mean zero. Therefore the earlier '5/5 observed annual means positive' is not a demonstrated '5/5 full-cohort years positive'.

The separately declared residual scenarios anchor missingness to known index outcomes. If missing ETF-minus-index residuals have the same mean as observed residuals within that year (gamma=0, an assumption only), the 2021 h30 full-cohort scenario is **-0.643bp**. At h15 the 2021 observed increment is already -0.093bp. All pooled/year gamma scenarios from -100 to +100bp are retained without declaring any range empirically plausible.

Where no ETF pairs are missing, a tipping point is not applicable. The generated report's `UNQUANTIFIED` cells for those secondary-carrier tipping entries mean N/A/no missing pairs, not failed inference. 'Mean identified' in the scenario receipt refers only to the finite original observed cohort under inherited source assumptions, not a population or causal effect.

## Program consequence

Do not promote to execution economics or describe R1_A as a proven tradable alpha on the strength of the existing table. Also do not declare the mechanism false: the signs and several influence checks remain encouraging, while uncertainty and selection remain unresolved.

The useful next stage is a fixed confirmation design on genuinely unused or prospective observations, with the data role and observation/exit treatment declared before outcomes. Do not repeatedly search block sizes, matching rules, horizons, years, sides, thresholds or ETF structures on the same history until a preferred p-value appears. New data must be separately admitted; a date label alone does not make a sample fresh or unseen. No BLACKBOX query #4 is authorized.

No routine local transfer task remains for the existing historical pack. This round did not fetch new market data or introduce live trades, costs, stops, targets, borrow, options or futures.

## Engineering and preserved history

The old full-path v1, endpoint protocol, data pack and decisive receipts are untouched. CSI1000's failed all-seven-endpoint common-cohort return table remains unopened. All 56 inference rows, all leave-year/side influence results, 924 pooled/year/gamma scenarios and all deterministic thinning decisions are retained.

Run with a fresh directory:

```bash
PYTHONPATH=src:. python research/r1a_endpoint_robustness/study.py --output /tmp/r1a-robustness-new
```

## Method sources and limits

- Aronow, Samii and Assenova, dyadic cluster-robust variance: https://arxiv.org/abs/1312.3398 . Shared members motivate explicit cross-role dependence accounting; this study's calendar hyperedges are an adaptation, not an automatic application of all paper assumptions.
- Kojevnikov, Marmer and Song, network-dependent inference: https://arxiv.org/abs/1903.01059 . Validity depends on dependence decay and network density; those are assumptions here, not facts established by receipt generation.
- NIST Bonferroni method: https://www.itl.nist.gov/div898/handbook/prc/section4/prc473.htm . The union-bound family correction does not require independent contrasts but does require valid marginal uncertainty statements.
- Manski and Tabord-Meehan, mean estimation with missing data: https://journals.sagepub.com/doi/10.1177/1536867X1701700311 . Missing-outcome assumptions matter; this run uses transparent algebraic scenarios, not invented outcomes.

`BLACKBOX_query_count=3`; `production_authority=false`; `fresh_oos=false`. No holding period selected. Closed R1_B/R2/MO identities are not reopened.
