# R1_A local delivery — cloud evidence audit

Delivery commit: `b656b4b8cda266800b33a374d5a5c98360c51837`

Decision: `PUBLIC_LEDGER_AUDIT_PASS_RAW_ETF_REPLAY_NOT_PERFORMED`

This audit recalculates the public ledger summaries and index comparators. It does not rerun private ETF price generation, independently approve upstream source semantics, or open the blocked primary carrier.

588000.SH: 1791/1802 complete pairs; 12537 rows; 2128 summary leaves verified.

| Index bars | n | ETF event bp | Index event bp | ETF increment bp | Index increment bp | Return correlation |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1791 | +0.067 | +0.350 | +0.557 | +0.502 | 0.8407 |
| 5 | 1791 | +1.643 | +1.285 | +1.784 | +1.179 | 0.9424 |
| 15 | 1791 | +3.600 | +3.011 | +3.019 | +2.074 | 0.9582 |
| 30 | 1791 | +5.160 | +3.908 | +3.727 | +2.015 | 0.9711 |
| 60 | 1791 | +3.759 | +2.323 | +1.618 | -0.442 | 0.9839 |
| 120 | 1791 | +2.316 | +0.732 | +1.605 | -0.284 | 0.9864 |
| 240 | 1791 | +6.018 | +3.005 | +4.763 | +1.217 | 0.9877 |

512100.SH remains unmeasured: 2021 valid-minute coverage is 94.478738% versus frozen 95%. No year exclusion, zero-volume fill, carrier switch or gate relaxation is performed.

All seven horizons are reported. The secondary carrier does not replace primary CSI1000 evidence. Close-price synthetic returns are not bid/ask execution profits.

## Remaining source-level checks

- Raw source-to-canonical verification requires private bytes; hashes in a manifest are not the bytes themselves.
- Exporter interprets Z-suffixed strings as Shanghai wall-clock under its source claim; upstream dictionary/provenance is not independently verified by this public-ledger audit.
- Exporter drops duplicate timestamps keeping the last row without a before/after duplicate-count receipt; occurrence or nonoccurrence in this delivery cannot be established here.
- Corporate-action completeness is asserted in local manifests; this audit does not independently establish the complete source ledger.

`BLACKBOX_query_count=3`; `production_authority=false`; `fresh_oos=false`.
