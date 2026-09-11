# Continue here — reversal / mean-reversion research

## Latest completed stage

**`RETROSPECTIVE_ENDPOINT_ROBUSTNESS_COMPLETED_NO_PRODUCTION`**

The fixed R1_A endpoint table has now undergone calendar-dependence, multiple-comparison, repeated-control, nonoverlap, leave-year and missing-outcome sensitivity checks. This work is complete; do not redesign or rerun it as an unseen validation experiment.

Scientific interpretation: **R1_A remains a historical short-horizon lead, not a statistically established trading edge.** No execution promotion; no zero-effect/equivalence finding; no closure of the R1_A mechanism identity.

Read first:

1. `docs/research/R1A_ENDPOINT_ROBUSTNESS_REVIEW_20260912.md`
2. `docs/ops/evidence/r1a_endpoint_robustness_20260912/REPORT.md`
3. `docs/ops/evidence/r1a_endpoint_robustness_20260912/robustness_receipt.json`
4. `docs/governance/R1A_ENDPOINT_ROBUSTNESS_FREEZE@1.0.json`
5. `PROMPT.md`

Freeze commit `f098e4702c03a6374dfd8332fcfc1ee10882cced`; decisive run `34658568504`, job `103456110997`: SUCCESS after synthetic tests. All 14 historical means were already known before the new uncertainty calculations. This is retrospective analysis, not fresh OOS or correction of all prior research choices.

## Main result

The primary 20-trading-day calendar-exposure graph accounts for either event or control paths touching shared blocks, including cross-role reuse. The approximate graph-sandwich/t intervals use an IID-SE floor. Fixed shifted-origin and 5-day sensitivities were also reported; no variance specification was selected after results.

| Carrier | h | Mean increment bp | Primary pointwise 95% interval | Primary 14-comparison interval |
|---|---:|---:|---|---|
| 512100.SH | 15 | +4.368 | [+0.029,+8.707] | [-2.211,+10.948] |
| 512100.SH | 30 | +7.074 | [-0.279,+14.427] | [-4.077,+18.224] |
| 588000.SH | 15 | +3.118 | [-2.585,+8.821] | [-5.529,+11.766] |
| 588000.SH | 30 | +3.963 | [-3.432,+11.358] | [-7.251,+15.177] |

Zero of all 14 primary adjusted lower bounds are positive; zero cells survive all four specifications under the 56-comparison check. Intervals include positive and negative effects: do not say the strategy is proved useless.

CSI1000 h15/h30 remain positive with equal-control weights (+3.780/+6.356bp), clock-disjoint diagnostic cohorts (+2.816/+6.405bp) and every exposure-year deletion (minimum +2.600/+4.995bp). Longer horizons are weaker; h60/h120 disjoint increments turn negative. These are sensitivity cohorts, not new trade rules or proof of independence.

## Selection caveat is now quantified

At CSI1000 h30, the 2021 observed annual mean is +1.257bp among 159/186 pairs. Mean missing paired return of -7.403bp across the other 27 would make the full year's cohort mean zero. A declared gamma=0 residual-equality scenario gives -0.643bp for that year; this is an assumption-based scenario, not measured missing returns.

Pooled missing tipping thresholds are much farther away (-197.824/-240.700bp at h15/h30), but pooled robustness does not establish annual robustness. All fixed gamma scenarios and years are retained. No missing ETF price or outcome was imputed.

The inference calibration/dependence assumptions are not independently proved. Multiple-comparison adjustment covers displayed contrasts only, not unknown historical signal/payoff searches. Observational matching is not causal identification.

## Current frontier

Retain R1_A as a lead; do not promote it to a confirmed or executable strategy. The next useful evidence is a separately frozen confirmation design using genuinely unused or prospective observations, including data-role and observation/exit policy before outcomes. Do not retune horizons, matching, side/year filters, block sizes or instruments on these same years to recover significance. No new BLACKBOX query is authorized.

No local data-transfer task remains for the existing historical pack. No new market data or live-account action was taken in this stage.

## Preserved earlier states

- Endpoint diagnostic: `ENDPOINT_DIAGNOSTIC_COMPLETE_DESCRIPTIVE`, both ETFs and all seven per-horizon cells measured; still true.
- Original full-path v1: `PARTIAL_CARRIER_TRANSPORT` under its own unchanged definition; still true.
- CSI1000 all-seven-endpoint common cohort failed its 2021 gate; its ETF return table is still unopened.
- Original signals, matched pairs, directions, timestamp alignment, data hashes and horizons `1/5/15/30/60/120/240` are unchanged.
- Synthetic SHORT/zero-cost terminal returns are not executable net PnL. No MFE/MAE or stop/target/cost/borrow/option/futures implementation was added.

Earlier endpoint details: `docs/research/R1A_ENDPOINT_METHOD_REVIEW_20260912.md` and `docs/ops/evidence/r1a_endpoint_diagnostic_20260912/`. All prior receipt directories remain evidence, not competing current task instructions.

## Data and reproduction

Actual data: `data/r1a_carrier_prices/cloud_pack_v1/`, 10 annual OHLCV CSVs plus 2 action CSVs, 583,943 price rows. No DataHub/private dependency. The robustness stage reads pinned endpoint ledgers and hash-verified original index bytes; it does not generate a new ETF sample.

```bash
PYTHONPATH=src:. python research/r1a_endpoint_robustness/study.py --output /tmp/r1a-robustness-new
PYTHONPATH=src:. python -m pytest -q tests/test_r1a_*.py
```

Fresh output directories only. Old full-path and endpoint runners continue to reproduce their own immutable results.

`BLACKBOX_query_count=3`; no query #4; `production_authority=false`; `fresh_oos=false`. R1/R2 mechanism certifications remain; closed R1_B, R2-directional and MO payoff identities remain closed. No holding horizon selected.
