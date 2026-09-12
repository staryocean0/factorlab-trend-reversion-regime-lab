# FactorLab Trend–Reversion Regime Lab

Research separating mechanism, price response, counterfactual baseline, observation quality, noise, inference and execution.

## Latest completed gate

**CONTROL_ALLOCATION_DESIGN_SCREEN_COMPLETED_NO_OUTCOMES**.

The fixed event-time-available control design has executed on original pre2021 Development data and is closed without new return analysis. Only 241/1752 CSI1000 events and 17/156 STAR50 short-context events satisfy its combined maturity, covariate-caliper and exclusive-240-bar rules. Matched covariates look close inside the retained pairs, but the retained event population differs materially from the original population.

Loss decomposition is retained: CSI1000 1645 past-nearest -> 414 inside the fixed quality bound -> 241 interval-exclusive; STAR50 122 -> 27 -> 17. Shadows diagnose losses, not alternative trading candidates. Moreover, the same-year inclusive-240-bar disjoint constraints imply an optimistic CSI1000 capacity ceiling of 1230/1752=70.21%, below the 80% design gate even before similarity requirements.

This closes a restrictive comparison design, not R1_A. It does not prove zero alpha, achieve variance reduction, or authorize reopening historical significance searches. No newly assigned return, Validation/ETF/2026 outcome or confirmation clock was opened.

## Read first

- [Current handoff](CONTINUE_HERE.md)
- [Control design review and capacity proof](docs/research/R1A_CAUSAL_CONTROL_DESIGN_REVIEW_20260912.md)
- [Complete design evidence](docs/ops/evidence/r1a_control_design_20260912/REPORT.md)
- [Frozen design contract](docs/governance/R1A_CAUSAL_CONTROL_DESIGN_FREEZE@1.0.json)
- [Reproduction instructions](research/r1a_control_design/README.md)
- [Previous real-noise decomposition](docs/research/R1A_DEVELOPMENT_NOISE_REVIEW_20260912.md)

Before any replacement, distinguish offline attribution from event-time forecasting and state what identifies an all-event parent-continuation baseline. No replacement empirical candidate is currently authorized.

## Preserved research and data

R1_A remains an unconfirmed historical price lead. R1/R2 certifications and closed R1_B/R2-directional/MO identities remain unchanged. Both ETF endpoint diagnostics are complete; original full-path v1 separately remains PARTIAL_CARRIER_TRANSPORT. Old data, pairs, freezes, outcomes and statistical limitations are retained.

The real historical ETF pack is already cloud-readable under `data/r1a_carrier_prices/cloud_pack_v1/`; no routine local delivery remains. The known 2026 CSI1000 file is an unopened metadata-only candidate, not automatically fresh holdout.

BLACKBOX_query_count=3; no query #4; production_authority=false; fresh_oos=false; confirmation_protocol_frozen=false; horizon_selected=false.
