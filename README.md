# FactorLab Trend–Reversion Regime Lab

Reversal / mean-reversion research, keeping mechanism, price response, observation quality, noise, inference and execution distinct.

## Current completed stage

**`DEVELOPMENT_NOISE_ACCOUNTING_COMPLETED_NOT_ALPHA_TEST`**.

Real pre2021 index noise accounting has executed. For CSI1000 h15/h30, individual event SD is 70.745/99.850bp versus control SD 49.940/68.887bp; event-control correlation is only 0.0943/0.1113. Individual-pair dispersion is not mainly a noisy control. However, when the same legs are aggregated on their actual price calendar, reused and overlapping controls produce concentrated exposures: control contributions are 82.68%/79.30% of daily difference variance, with negative covariance offsets. Pair dispersion, calendar contribution variance and uncertainty of a mean are different quantities.

CSI1000 uses its original 2015-2020 Development period (1,752 pairs); STAR50 only its short 2020 context (156 pairs). No 2021-2025, ETF, MO or 2026 prices were read by this study. Original signals and the retrospective matching algorithm were reused without tuning; previous Validation pairs and outcomes are unchanged.

This identifies a control-allocation issue worth reviewing, not an achieved variance reduction, new alpha certificate or validated inference method. No historical p-value was retested. The previous finite estimator screen stays closed. R1_A remains a lead, not disproved and not production-ready.

## Entry points

- [Current handoff](CONTINUE_HERE.md)
- [Actual noise interpretation](docs/research/R1A_DEVELOPMENT_NOISE_REVIEW_20260912.md)
- [Full Development evidence](docs/ops/evidence/r1a_development_noise_20260912/REPORT.md)
- [Frozen decomposition contract](docs/governance/R1A_DEVELOPMENT_NOISE_DECOMPOSITION_FREEZE@1.0.json)
- [Runner and reproduction](research/r1a_development_noise/README.md)

A possible next task is a separately frozen, event-time-available control-baseline design, addressing exact/overlapping reuse while preserving coverage and balance. It is not implemented by the noise receipt. No new confirmation sample is opened.

## Preserved data and history

Historical ETF data are already cloud-readable in `data/r1a_carrier_prices/cloud_pack_v1/`; no routine local transfer is outstanding. Both ETF endpoint diagnostics remain completed. The original full-path v1 retains its separate PARTIAL_CARRIER_TRANSPORT status. All original source bytes, freezes, ledgers and closed identities remain intact.

The known 2026 CSI1000 file is still a metadata-only candidate with unresolved R1_A holdout status. It is not automatically fresh because of its year. R1/R2 mechanism certifications and closed R1_B/R2-directional/MO lineages are unchanged.

`BLACKBOX_query_count=3`; no query #4; `production_authority=false`; `fresh_oos=false`; `confirmation_protocol_frozen=false`; `horizon_selected=false`.
