# R1_A confirmation feasibility — conditional planning only

No new confirmation sample or empirical significance claim. All 28 index/ETF/horizon designs and four variance specifications are retained.

## CSI1000 illustration: 80% positive detection, 14-comparison interval, primary variance

| Layer | bars | Assumed effect bp | Required trading days | Expected pairs | Information-equivalent years, NOT forecast |
|---|---:|---:|---:|---:|---:|
| INDEX_ALL_FROZEN_PAIRS | 15 | 2 | 18169 | 19429 | 74.95 |
| INDEX_ALL_FROZEN_PAIRS | 15 | 4 | 4543 | 4858 | 18.74 |
| INDEX_ALL_FROZEN_PAIRS | 15 | 6 | 2019 | 2159 | 8.33 |
| ETF_OBSERVED_ENDPOINTS | 15 | 2 | 20106 | 21035 | 82.95 |
| ETF_OBSERVED_ENDPOINTS | 15 | 4 | 5027 | 5260 | 20.74 |
| ETF_OBSERVED_ENDPOINTS | 15 | 6 | 2234 | 2338 | 9.22 |
| INDEX_ALL_FROZEN_PAIRS | 30 | 2 | 48859 | 52246 | 201.56 |
| INDEX_ALL_FROZEN_PAIRS | 30 | 4 | 12215 | 13062 | 50.39 |
| INDEX_ALL_FROZEN_PAIRS | 30 | 6 | 5429 | 5806 | 22.40 |
| ETF_OBSERVED_ENDPOINTS | 30 | 2 | 57743 | 59983 | 238.21 |
| ETF_OBSERVED_ENDPOINTS | 30 | 4 | 14436 | 14996 | 59.55 |
| ETF_OBSERVED_ENDPOINTS | 30 | 6 | 6416 | 6665 | 26.47 |

Required horizons are NOT chosen from this table. 2/4/6bp are assumptions, not historical effect estimates or economic profit hurdles. Years scale the historical pair/noise rate and must not be sold as a real-world completion schedule.

## Null calibration of the previous approximate graph/t estimator

| Assumed model | Designs | Marginal 5% rejection range | Severe warnings (MC lower bound >7.5%) |
|---|---:|---|---:|
| IID_GAUSSIAN | 28 | 2.95% to 4.85% | 0 |
| SHARED_BLOCK_GAUSSIAN | 28 | 4.60% to 7.45% | 0 |
| SHARED_BLOCK_T5 | 28 | 3.20% to 7.25% | 0 |
| OFF_GRAPH_AR1_0.6 | 28 | 6.80% to 22.20% | 26 |

These simulations use the historical exposure geometry but imposed random-effect models. They do not identify the true DGP. Correlated block shocks intentionally violate the assumed off-graph independence. Invalid-variance replicates are reported and cannot reject. Marginal Bonferroni tests were simulated; joint familywise error was NOT simulated.

## Deliverables and remaining boundary

All sample-size scenarios (families 1/7/14/28, target 80%/90%), fixed 60/120/243/486/1215-day power, index-versus-ETF noise, annual pair rates and 2000-repetition null diagnostics are separate CSVs. The pointwise and smaller-family alternatives are explanatory, not a chosen new test.

Data-role audit is separate. A later confirmation needs qualified data, a finalized missingness/observation contract, and an adequately justified inferential method. Neither the 95%/80% old gates nor failed common-primary ETF sample was changed. No new data transfer, live trading, options or BLACKBOX query is authorized.

Sources and exact planning/DGP formulas: docs/governance/R1A_CONFIRMATION_FEASIBILITY_FREEZE@1.0.json.

`production_authority=false`; `fresh_oos=false`; `confirmation_protocol_frozen=false`.
