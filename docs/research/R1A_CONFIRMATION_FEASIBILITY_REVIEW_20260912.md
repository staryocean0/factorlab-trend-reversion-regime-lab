# R1_A confirmation feasibility — completed, not ready to launch confirmation

## Decision

**`CONFIRMATION_FEASIBILITY_COMPLETED_NOT_READY_TO_START`**.

The authorized power/sample-size, estimator-null-calibration and candidate-data-role checks have actually executed. Retain R1_A as a historical lead; do not infer that the effect is zero or close the mechanism. Do not launch a costly confirmation on the premise that a few additional months will settle a 2-6bp edge under the unchanged measurement design.

Three distinct findings:

1. At the inherited paired-return noise and event rate, the information needed to reliably detect small effects is large.
2. The previous graph/t estimator is model-dependent: adding serial dependence between its calendar blocks produces excessive null rejection in the declared stress model. It is not validated for prospective confirmation by the earlier green engineering CI.
3. A relevant 2026 CSI1000 minute file exists in another repository, but its metadata records repeat-validation use and fresh_oos=false. No genuinely unused, source-admitted R1_A confirmation package has been established.

This stage did not freeze the final confirmation protocol, start an observation clock, read new confirmation prices, place trades, request a purchase or ask for a repeat transfer of existing history.

## Execution and scope

Baseline: `8b1cb1e69123712be3fbefb909ae382e2a1104c3`.
Freeze: `docs/governance/R1A_CONFIRMATION_FEASIBILITY_FREEZE@1.0.json`.
Freeze commit: `4c1b30995e02e00d335b83a050a45e9cb309d502`.
Decisive compute commit: `25cf8ffa9d45995b8d24c63184d3dd8b73af1c00`.
Decisive Actions run: `34661221824`, job `103463958578`: SUCCESS.

Outputs live under `docs/ops/evidence/r1a_confirmation_feasibility_20260912/`.
There are 28 fixed layer/index/horizon designs, 112 historical-noise specifications, 2,688 sample-size scenarios, 6,720 fixed-budget scenarios, 112 null-calibration rows (224,000 simulated datasets) and 140 annual pair-rate rows. All seven horizons and both indices/ETFs are retained, not only the short locations illustrated below.

INDEX noise uses all original frozen pairs, irrespective of ETF availability. ETF noise uses the already admitted horizon-specific observed endpoint pairs. The ETF estimand remains conditional on future endpoint observability; it is not all-event or executable alpha. Neither layer's historical observed mean is treated as a true effect for sample planning.

## What the sample-size calculation means

The assumed true incremental effects are 2/4/6bp, not fitted estimates or economically sufficient profit thresholds. For a positive lower bound of a two-sided family-adjusted interval, the normal plug-in planning formula is

`D_needed = ceil(D_hist * (SE_hist / delta)^2 * (z[1-alpha/(2m)] + z[target_power])^2)`.

It assumes the future mean variance scales as `SE_hist^2 * D_hist / D_future`, with unchanged long-run noise, original matching/observation structure and pair rate. `D_hist=1,212` trading dates over the five historical calendar years. Expected pair counts use the observed paired-cohort rate, NOT every detected raw signal and NOT a claim of independent observations.

The main reporting envelope is 14 comparisons within each layer. Single-test, 7-comparison and combined 28-comparison alternatives are also fully reported for planning transparency; none is chosen because its sample requirement is convenient. Target power is per contrast, not the probability that every horizon succeeds simultaneously.

### CSI1000 index layer: 80% positive detection, primary variance, family 14

| Assumed true increment | h15 expected pairs | h15 trading days | h30 expected pairs | h30 trading days |
|---:|---:|---:|---:|---:|
| 2bp | 19,429 | 18,169 | 52,246 | 48,859 |
| 4bp | 4,858 | 4,543 | 13,062 | 12,215 |
| 6bp | 2,159 | 2,019 | 5,806 | 5,429 |

At the old data's information rate, the 4bp cases correspond to about 18.74/50.39 information-equivalent years. These are **not recommended waiting periods, completion forecasts or a claim that markets stay stationary for decades**. They diagnose an inefficient confirmation plan for a small effect. The ETF cases are comparable or larger: 4bp at h15/h30 requires approximately 5,260/14,996 observed pairs (5,027/14,436 trading days; 20.74/59.55 information-equivalent years).

A fixed 243-day budget in the index layer has conditional positive-detection probability only 2.04% at h15 and 0.86% at h30 for a true 4bp effect with the 14-comparison criterion. The corresponding 80%-power detectable effects are about 17.29bp and 28.36bp. These are model-based planning probabilities, not real-world success forecasts or proof that a small effect is absent.

Even those projections omit uncertainty about the nuisance variance, future regimes and missingness. The subsequent calibration findings are a further reason not to treat the computed day counts as an approved confirmatory sample size. Existing observations cannot simply be added to a new confirmation test as though unused.

## Null calibration: the old approximate method is not a validated confirmation test

The frozen primary graph/t estimator was applied to zero-mean simulated data on each historical exposure geometry. No historical p-value was searched or repaired. Each design/DGP used 2,000 replicates and retained Wilson Monte Carlo intervals plus invalid-variance frequencies.

| Imposed data-generating model | Nominal 5% marginal rejection range, 28 designs | Severe warnings: Wilson lower bound >7.5% |
|---|---:|---:|
| Independent Gaussian | 2.95%-4.85% | 0 |
| Shared independent calendar-block Gaussian effects | 4.60%-7.45% | 0 |
| Shared independent calendar-block t5 effects | 3.20%-7.25% | 0 |
| Calendar-block effects with AR(1) correlation 0.6 | 6.80%-22.20% | 26 |

The last model deliberately allows dependence that the old graph excludes. It is a stress scenario, not an estimated description of the real market. Therefore we cannot say the actual false-positive rate is 22.20%; we can say the procedure is vulnerable to this declared off-graph dependence. Absence of severe warnings in the easier models is not a calibration certificate either.

The simulated random effects are unsigned outcome-level loadings fitted to historical variance, not a structural model of signed event/control prices. Their role is diagnostic. The sparse inclusion-exclusion implementation was tested against the exact old adjacency quadratic so this is not a hidden new estimator. Invalid-variance replicates cannot reject and their counts are reported. Joint familywise error across the 14 correlated contrasts was NOT simulated; the corresponding marginal adjusted tests were.

Consequence: before a real confirmatory claim, an inference design must be justified for serial/calendar and event-control dependence and calibrated on predeclared synthetic cases. Do not shop estimator/block choices on the real R1_A means until something becomes significant. The previous non-promotion decision remains unchanged.

## Unused-data audit: a concrete candidate, not a fresh-data certificate

Five public default-branch trees were inspected, along with 37 bounded metadata files and branch names. No candidate price or strategy-outcome table was opened. The overnight repository had 34 metadata candidates and the fixed scan limit read 12; limitations and blob hashes are explicitly retained.

Relevant candidate:

- Repository: `staryocean0/factorlab-overnight-open-lab`.
- File: `data/gap_fill_repeat_2026/csi1000_1m_20260105_to_20260821.parquet`.
- Metadata-declared instrument/window: `000852.SH`, 2026-01-05 through 2026-08-21, 154 trading days, 36,960 rows.
- Manifest Git blob: `7a229bcb8a793806f31e7e7d014315e314cedaaf`.
- Manifest declares `fresh_oos=false` and use by the gap-fill repeat-validation evaluator.

Thus **2026 index data are not universally absent**. The candidate is retained as `KNOWN_REPEAT_USE_NOT_CERTIFIED_R1A_HOLDOUT`. Another study's use is not, by itself, proof of R1_A contamination, but an R1_A-specific exposure history and admission have not been established. A matching admitted 2026 ETF package has not been established either. Raw price bytes were not read or copied into this repository in this stage.

The numeric-only target-path flag missed the `csi1000` text alias; the supplementary candidate review resolves its actual instrument identity without discarding it. Other 2026-named paths include unrelated daily/industry data and version-date names; those are not automatically 2026 minute observations for the target.

The old 2015-2025 material is explicitly consumed. Prospective status would begin only after a later finalized confirmation freeze, not this feasibility calculation. No prospective timer, scheduled monitoring or collection was started.

## Program action

**Do not start or fund a formal R1_A confirmation campaign yet.** Keep the historical lead and existing files; no identity rescue or production promotion.

The next limited research task should be a method-only calibration/measurement review using synthetic data and the already disclosed nuisance geometry, with an explicit resource budget. It must address cross-block serial dependence and whether the planned matching/observation design can supply useful information. Any substantive estimand or matching change is a new disclosed design, not a rewrite of old success/failure states.

Keep the 2026 candidate at metadata-only status until that design and data role are fixed. Do not spend the limited potentially confirmatory data merely to produce another inconclusive or miscalibrated p-value. No routine local model transfer is needed for the historical pack.

## Engineering note

The first run `34661134488` stopped in synthetic tests: at zero simulated rejections, floating arithmetic produced a Wilson lower endpoint around 3.5e-18 instead of exactly zero. It read no new candidate or feasibility outcomes. The boundary was corrected to its exact 0/1 value and committed before the successful run; no frozen statistical rule, family, effect scenario, seed or sample was changed.

## References

- Sample-size/power assumptions and normal planning: https://www.itl.nist.gov/div898/handbook/prc/section2/prc222.htm
- Finite-family adjustment: https://www.itl.nist.gov/div898/handbook/prc/section4/prc473.htm
- Shared-member dependence: https://arxiv.org/abs/1312.3398
- Network dependence conditions: https://arxiv.org/abs/1903.01059
- Ordered-node dependence as motivation for the serial stress, not automatic validation of our method: https://arxiv.org/abs/2605.28349
- Existing-data preregistration and exposure disclosure: https://www.cos.io/initiatives/prereg

`BLACKBOX_query_count=3`; `production_authority=false`; `fresh_oos=false`; `confirmation_protocol_frozen=false`; `confirmation_clock_started=false`.
