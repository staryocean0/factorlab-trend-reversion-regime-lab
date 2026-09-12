# R1_A control allocation design screen

Current result: `CONTROL_ALLOCATION_DESIGN_SCREEN_COMPLETED_NO_OUTCOMES`.
The only proposed design, `PAST_CALIPER_EXCLUSIVE`, fails coverage and event-population retention. Its new paired returns have not been calculated. The two shadow stages locate losses, not fallback candidates.

Read `docs/research/R1A_CAUSAL_CONTROL_DESIGN_REVIEW_20260912.md` and the frozen contract `docs/governance/R1A_CAUSAL_CONTROL_DESIGN_FREEZE@1.0.json`.

## Actual input and boundary

The original Development event identities in `docs/ops/evidence/r1a_development_noise_20260912/development_pairs.csv` are immutable. CSI1000 has 1,752 events in 2015-2020; STAR50 has 156 events in its short 2020 context. The compiler verifies their identity and features, reads only seven pre2021 index partitions, and recreates the original control feature pool.

The allocator API accepts only symbol, observed clock indices/dates, year, direction, 30-minute clock bucket and four causal covariates. Additional columns are refused. It receives neither prices nor returns. The original structural feature compiler does access historical closes and structural resolution logic; this boundary does not claim that all historical price rows are unknown.

At event information index e-1, a candidate requires c+240<=e-1. Robust scaling comes from the same-year matured control prefix, never full-year future normalization. One fixed componentwise 0.5 scale caliper is used. The primary scheme selects nearest matches chronologically, and no allocated inclusive [c,c+240] control intervals may share a price observation.

Both the original event denominator and every unmatched reason are retained. Covariate matching balance and selected-vs-original event composition are reported separately. Geometry tables compare old and new controls on identical retained event IDs; unit incidence is not a realized-return variance estimator.

## Reproduce; never overwrite decisive evidence

```bash
PYTHONPATH=src:. python -m pytest -q \
  tests/test_r1a_control_design.py tests/test_control_design_retained.py

OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=src:. \
  python research/r1a_control_design/study.py --output /tmp/r1a-control-design-new

PYTHONPATH=src:. python research/r1a_control_design/verify_replay.py \
  --reference docs/ops/evidence/r1a_control_design_20260912 \
  --replay /tmp/r1a-control-design-new \
  --output /tmp/r1a-control-design-new-audit.json
```

Use directories that do not exist before each run. The read-only workflow enforces source isolation, tests prefix invariance and exact allocation constraints, reproduces the six tables, and checks all identities/counts/flags exactly. Numerical tolerance is restricted to named continuous columns; the pinned original receipts and bytes never change.

`packing_implication` separately derives an optimistic capacity bound from the decisive price-row/event counts. Same-year disjoint inclusive 240-bar intervals imply at most sum_year min(events_year,floor(price_rows_year/241)) matches: 1,230/1,752 for CSI1000, before quality constraints. This is a post-run analytical implication of the fixed design, not a new gate or a search over horizons.

## Stop rule

Do not widen the caliper, lower coverage, remove 2015, pick a shorter horizon, switch to a shadow stage, or compute returns only for selected pairs to relabel this design as successful. It is a closed feasibility result for one restrictive scheme, not proof that all baselines or R1_A itself are invalid. An offline attribution baseline also need not be an online trade input; these targets require explicit separation.

No routine local data delivery is needed. No post2020/ETF/MO/2026 prices, new p-values, source repairs, or confirmation clock are part of this stage. `BLACKBOX_query_count=3`, `production_authority=false`, `fresh_oos=false`.
