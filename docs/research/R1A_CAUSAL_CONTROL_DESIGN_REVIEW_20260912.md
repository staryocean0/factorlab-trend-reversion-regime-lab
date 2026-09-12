# R1_A event-time control allocation — completed design gate

## Decision

**CONTROL_ALLOCATION_DESIGN_SCREEN_COMPLETED_NO_OUTCOMES**.

The proposed `rmr_R1A_past_mature_caliper_interval_exclusive_design_v1` fails its fixed coverage and event-population retention screen. It is not advanced to return analysis. This is a rejected comparison design, **not** a rejected R1_A signal, proof of zero incremental return, or a new test of historical alpha.

Freeze commit: `6ebbb80e93cd0e5d783438c41f6fe310381a3e68`.
Decisive code commit: `6b453cef4546890a4576c79ef77f51b40a5cb905`.
Actions: `34666939631`, job `103480639603`, SUCCESS.
Evidence: `docs/ops/evidence/r1a_control_design_20260912/`.

The engineering success means the predeclared rules were executed and audited. It does not turn the design failure into a strategy PASS or FAIL.

## 1. Scope and what was actually changed

The original Development R1_A population is unchanged: CSI1000 2015-2020 has 1,752 events; STAR50 July-December 2020 has 156 events and remains short context, not a full replication. All original event identities and pre-entry features were checked against the pinned Development pair file. The source compiler reproduced 144,733 / 7,673 candidate control rows respectively.

Only the seven manifest-verified pre2021 index partitions were read. No ETF, Validation 2021-2025 or 2026 candidate prices/return ledgers were present in the decisive checkout. The original structural engine uses historical close prices and first-passage logic to reproduce its already-established event clocks. Accordingly, the boundary is **no newly assigned paired-return computation**, not the literally impossible assertion that a historical causal feature stream can be compiled without accessing price rows after earlier events.

The new allocator receives only event/control identity, date, clock, direction and four declared covariates. No price, payoff, severity, outcome or standard error enters its API. The original Validation pairs and all prior outcomes remain unchanged. New controls are stored under a separate identity.

One primary allocation was frozen, with two diagnostic shadows, not a parameter sweep:

1. PAST_NEAREST: same-year/direction/30-minute-bucket nearest control whose complete 240-bar path ends by event confirmation; replacement allowed, no quality bound. It measures available historical support, not an authorized fallback.
2. PAST_CALIPER: additionally require every covariate gap to be within 0.5 of its event-time robust prefix scale; replacement still allowed. It measures individual admissibility before competition for intervals.
3. PAST_CALIPER_EXCLUSIVE: the only proposed design; additionally prevent overlap of any allocated inclusive [c,c+240] price intervals, including shared endpoints.

Events are processed chronologically. Prefix median/MAD scales use only the same-year control paths already mature at that event's information cutoff, not the future year's pool. Ties use the earliest control index. No future allocation optimization, post-control-treatment exclusion, year deletion, extra-control-count search or caliper retuning is performed. The 240-bar rule supports one allocation across all seven horizons; it is a restrictive design choice, not a universal requirement for short-horizon inference.

## 2. Coverage losses are large before capacity constraints

| Symbol | Original events | Past nearest | Plus quality bound | Plus exclusive intervals |
|---|---:|---:|---:|---:|
| CSI1000 | 1,752 | 1,645 (93.89%) | 414 (23.63%) | 241 (13.76%) |
| STAR50 short context | 156 | 122 (78.21%) | 27 (17.31%) | 17 (10.90%) |

CSI1000's mutually exclusive primary no-match reasons are 107 without a mature exact-stratum candidate, 1,231 without a candidate inside the fixed quality bound, and 173 whose quality-compatible intervals were already occupied. Together with the 241 matched cases these sum exactly to 1,752. STAR50 has 34 / 95 / 10 losses plus 17 matches.

Thus, in this frozen design, **lack of sufficiently similar historical controls is the biggest loss, not interval reuse alone**. The 23.63% CSI1000 PAST_CALIPER coverage is an upper bound for any allocator restricted to the same candidate pool, causal scales and quality rule. Rearranging capacity reservations cannot create an admissible candidate for the other 1,338 events. This is not a claim that every sensible covariate metric or control baseline lacks support.

Every original event is in the allocation ledger, including the unmatched ones. Primary CSI1000 year coverages are 5.43%, 9.20%, 32.29%, 23.92%, 25.37% and 16.00% for 2015-2020. Both direction groups and every required year/direction group also fail the 80% coverage criterion. Nothing has been redefined as zero-return or hidden from the denominator.

## 3. Good balance inside the selected pairs hides a different event population

For the CSI1000 primary selected sample, pooled event-control standardized differences are all smaller than 0.02 in absolute value. But the selected-event population differs sharply from the original full-event population:

| Covariate | Selected event minus its control / original event SD | Selected events minus all original events / original event SD |
|---|---:|---:|
| Parent absolute drift | -0.0178 | -0.5322 |
| Parent efficiency | -0.0062 | -0.6568 |
| Log(1+parent age) | -0.0028 | +0.6815 |
| Local volatility 30/240 ratio | -0.0002 | -0.3214 |

The selected events are older in parent-state age and have lower parent drift/efficiency and lower short/long volatility ratios on these pooled measures. They are not representative of the original event population under the predeclared retention check. We cannot compute returns on these 241 cases and silently call the result an estimate for all 1,752 original events.

The high-coverage PAST_NEAREST shadow is not a satisfactory escape: its pooled parent-efficiency and parent-age matching standardized differences are +0.1983 and -0.1568, outside the fixed 0.1 criterion. Its existence does not authorize switching to it after seeing the failure.

Balance is a design diagnostic, not a significance test, evidence of unmeasured-confounder balance, or a proof of causal identification. The 0.1 limit has no universal status; it was a project-specific declared screen. Covariate variance ratios and all low-count groups are also retained rather than summarized away.

## 4. Exposure deconcentration works mechanically, not as demonstrated noise reduction

Every matched primary control is fully mature by its event cutoff, maximum exact reuse is one, and primary control-control inclusive overlap is zero. All seven horizon unit-incidence energy ratios equal one, as required by disjoint intervals. The old controls are also tabulated on the identical retained event IDs, so reduced sample count is not hidden in the comparison.

This verifies implementation and clock geometry. It does **not** show a reduction in realized return noise, the long-run variance of an estimator, or the variance of a tradable portfolio. Price weights and new returns were intentionally not used in this incidence calculation; cross-pair event/control exposures and serial market dependence can still remain. Disjoint intervals are not automatically independent observations.

## 5. A post-run analytical implication of the frozen constraints

A useful capacity contradiction can be derived without loading any further price or return data. An inclusive 240-bar control price interval occupies 241 observed timestamps. Because each selected control and its mature exit must be inside its event's calendar year, disjointness implies:

`selected_controls_year <= floor(observed_price_rows_year / 241)`.

Capping by the year's original event count and summing produces an optimistic bound. It ignores all maturity timing, exact strata, R1 exclusions and quality constraints, so it can only overstate feasible capacity:

| CSI1000 year | Price rows | Events | Optimistic selected-control bound |
|---|---:|---:|---:|
| 2015 | 58,560 | 645 | 242 |
| 2016 | 58,241 | 326 | 241 |
| 2017 | 58,560 | 96 | 96 |
| 2018 | 58,320 | 209 | 209 |
| 2019 | 58,560 | 201 | 201 |
| 2020 | 58,320 | 275 | 241 |
| Total | 350,561 | 1,752 | **1,230 (70.21%)** |

In particular, 2015 cannot exceed 242/645=37.52% under these constraints. Even deleting the quality bound would not make the full design reach 80% coverage. The short STAR50 window has the analogous upper bound 109/156=69.87%.

This is a derived implication, not a new threshold added after results. It is reproduced by `packing_implication` in the read-only replay auditor. The exhaustive greedy result is not claimed to be globally optimal; the separate packing bound is an optimistic impossibility result **only for this exact same-year, uniformly 240-bar, no-shared-observation conjunction**. It says nothing comparable about a design allowing honest dependence accounting or a different estimand.

In retrospect, this elementary capacity screen should precede implementation of future allocation designs. It prevents spending outcome samples on constraint sets that cannot satisfy their own population-coverage target.

## 6. Decision and research boundary

Close this fixed event-time, interval-exclusive design at the design stage. No new assigned-return table is opened, not even for the apparently well-balanced 241/17 selected pairs. Do not lower 80%, widen 0.5, drop 2015 or choose a shorter horizon in this run to manufacture PASS.

Two conceptual points must not get lost:

- An outcome-blind retrospective attribution baseline is not necessarily a live-trading input. Forcing all controls to predate the event was a condition of this proposed new design, not a theorem that invalidates all offline matching or changes the causal timing of the R1_A signal itself.
- Preserving an all-event price-prediction question is different from asking about a small, selectively matchable subgroup. Neither may be silently substituted for the other to obtain lower variance.

The next question, before another implementation, is whether an all-event parent-continuation baseline is identifiable under defensible explicit assumptions, and whether the intended object is retrospective attribution or an event-time forecast. Do not equate lower incidence energy with a statistically valid noise reduction. The generic estimator sweep and this fixed hard-pruning design are complete; no automatic next candidate or formal confirmation launch occurs here.

R1_A remains an unconfirmed historical lead. Existing raw price/ETF findings and their statistical limitations remain; R1/R2 mechanism certifications and closed R1_B/R2-directional/option identities are unchanged. The public historical ETF pack already exists; no routine local data transfer is required. The 2026 candidate remains unopened.

## Evidence and reproduction

Six deterministic CSV tables record 5,724 stage-event rows, all normalizers, every coverage group, covariate balance/selection shifts, all seven clock geometries and recompiled event features. The decisive receipt pins the source blobs and files. Replays require exact allocation IDs, counts, flags and decisions; tightly bounded float differences are reported, never used to overwrite the original evidence.

Run into a fresh directory using `research/r1a_control_design/study.py`; then use `verify_replay.py` against the committed reference directory. Source access in the retained workflow remains limited to seven pre2021 price files and excludes all outcome ledgers.

Primary method references (not sources for the project-specific temporal/capacity constraints):

- Austin (2009), Balance diagnostics: https://pmc.ncbi.nlm.nih.gov/articles/PMC3472075/
- Stuart (2010), Matching methods: https://pmc.ncbi.nlm.nih.gov/articles/PMC2943670/

`BLACKBOX_query_count=3`; `production_authority=false`; `fresh_oos=false`; `confirmation_protocol_frozen=false`; `confirmation_clock_started=false`; `horizon_selected=false`.
