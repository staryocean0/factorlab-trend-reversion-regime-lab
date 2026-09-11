# R1_A endpoint dependence / selection robustness

Decision: `RETROSPECTIVE_ENDPOINT_ROBUSTNESS_COMPLETED_NO_PRODUCTION`

Retrospective inference on already observed means. NOT new independent confirmation, causal proof, or live profitability.

Freeze commit: `f098e4702c03a6374dfd8332fcfc1ee10882cced`; code commit: `c7365dcd6111c248dcb6ab833306bb7a58c7e265`; run: `34658568504`.

## Primary 20-trading-day calendar-exposure specification

The graph connects any event/control paths sharing a calendar block, including cross-role shared controls. Means and per-horizon samples are unchanged. Intervals use an approximate graph sandwich with an IID-SE floor and a heuristic t reference; displayed family correction covers 14 contrasts only.

| ETF | h | n | Increment bp | SE bp | Pointwise 95% interval | 14-family interval | Positive in all four 56-family checks |
|---|---:|---:|---:|---:|---|---|---|
| 512100.SH | 1 | 1271 | -0.861 | +0.551 | [-1.964, +0.241] | [-2.534, +0.811] | False |
| 512100.SH | 5 | 1268 | +0.984 | +1.208 | [-1.431, +3.400] | [-2.679, +4.648] | False |
| 512100.SH | 15 | 1268 | +4.368 | +2.169 | [+0.029, +8.707] | [-2.211, +10.948] | False |
| 512100.SH | 30 | 1259 | +7.074 | +3.676 | [-0.279, +14.427] | [-4.077, +18.224] | False |
| 512100.SH | 60 | 1261 | +6.976 | +5.077 | [-3.179, +17.131] | [-8.423, +22.375] | False |
| 512100.SH | 120 | 1265 | +7.026 | +6.533 | [-6.042, +20.094] | [-12.791, +26.843] | False |
| 512100.SH | 240 | 1261 | +4.131 | +7.529 | [-10.928, +19.191] | [-18.705, +26.968] | False |
| 588000.SH | 1 | 1802 | +0.630 | +0.575 | [-0.519, +1.780] | [-1.113, +2.374] | False |
| 588000.SH | 5 | 1802 | +1.922 | +0.967 | [-0.012, +3.855] | [-1.011, +4.854] | False |
| 588000.SH | 15 | 1802 | +3.118 | +2.851 | [-2.585, +8.821] | [-5.529, +11.766] | False |
| 588000.SH | 30 | 1801 | +3.963 | +3.697 | [-3.432, +11.358] | [-7.251, +15.177] | False |
| 588000.SH | 60 | 1801 | +1.560 | +5.988 | [-10.417, +13.537] | [-16.602, +19.722] | False |
| 588000.SH | 120 | 1802 | +2.127 | +7.048 | [-11.970, +16.225] | [-19.250, +23.505] | False |
| 588000.SH | 240 | 1801 | +6.462 | +13.197 | [-19.936, +32.861] | [-33.568, +46.493] | False |

Primary-family positive cells: `[]`.
All-four/56-family positive cells: `[]`.

No positive adjusted lower bound means insufficient evidence under that check, NOT proof the effect is zero or negative.

## Influence / concentration checks (descriptive, not substitute winners)

| ETF | h | Distinct controls | Max reuse | Equal-control increment bp | Clock-disjoint n | Clock-disjoint increment bp | Minimum leave-year-out increment bp |
|---|---:|---:|---:|---:|---:|---:|---:|
| 512100.SH | 1 | 1180 | 4 | -0.445 | 1130 | -0.475 | -1.310 |
| 512100.SH | 5 | 1178 | 4 | +0.888 | 1036 | +0.660 | +0.659 |
| 512100.SH | 15 | 1177 | 4 | +3.780 | 901 | +2.816 | +2.600 |
| 512100.SH | 30 | 1170 | 4 | +6.356 | 759 | +6.405 | +4.995 |
| 512100.SH | 60 | 1170 | 4 | +5.704 | 644 | -0.953 | +3.558 |
| 512100.SH | 120 | 1174 | 4 | +5.783 | 515 | -0.221 | +0.735 |
| 512100.SH | 240 | 1171 | 4 | +4.143 | 396 | +0.508 | -2.808 |
| 588000.SH | 1 | 1625 | 5 | +0.284 | 1515 | +0.181 | +0.161 |
| 588000.SH | 5 | 1625 | 5 | +1.578 | 1297 | +1.488 | +1.179 |
| 588000.SH | 15 | 1625 | 5 | +2.010 | 1048 | +1.384 | +1.082 |
| 588000.SH | 30 | 1624 | 5 | +2.427 | 847 | +1.910 | +0.796 |
| 588000.SH | 60 | 1624 | 5 | +0.686 | 666 | -2.164 | -5.190 |
| 588000.SH | 120 | 1625 | 5 | +0.930 | 500 | -8.392 | -3.523 |
| 588000.SH | 240 | 1625 | 5 | +3.851 | 383 | +0.831 | -4.692 |

The disjoint subset is selected on ALL original clocks before endpoint eligibility, not by return. It does not guarantee independence from serial dependence. All leave-year-out results and 56 inference rows remain in the receipt.

## Missing-outcome tipping points (NOT estimates)

Let missing ETF-minus-index mean residual differ from the observed mean residual by gamma. Only as a sensitivity assumption: all-pair mean = full-index mean + observed residual mean + missing_fraction*gamma. No missing ETF return is filled. Pooled and each-year gamma grids [-100,-50,-25,-10,-5,0,5,10,25,50,100] bp are all retained.

| ETF | h | Missing ETF paired mean needed for zero, pooled bp | Residual gamma needed for zero, pooled bp |
|---|---:|---:|---:|
| 512100.SH | 1 | +43.792 | +45.554 |
| 512100.SH | 5 | -44.578 | -47.775 |
| 512100.SH | 15 | -197.824 | -199.958 |
| 512100.SH | 30 | -240.700 | -231.914 |
| 512100.SH | 60 | -251.348 | -257.927 |
| 512100.SH | 120 | -286.713 | -269.755 |
| 512100.SH | 240 | -148.847 | -134.840 |
| 588000.SH | 1 | UNQUANTIFIED | UNQUANTIFIED |
| 588000.SH | 5 | UNQUANTIFIED | UNQUANTIFIED |
| 588000.SH | 15 | UNQUANTIFIED | UNQUANTIFIED |
| 588000.SH | 30 | -7137.607 | -7108.466 |
| 588000.SH | 60 | -2808.927 | -3107.738 |
| 588000.SH | 120 | UNQUANTIFIED | UNQUANTIFIED |
| 588000.SH | 240 | -11638.881 | -10813.456 |

A tipping point is not evidence about actual missing outcomes or a validated plausible range. No unrestricted all-event mean sign is identified when outcomes are missing.

## Boundaries

- Graph-sandwich dependence neighborhoods and t calibration are approximations, not finite-sample guarantees.
- Displayed-family multiplicity does not correct prior signal/identity exploration or repeated historical reuse.
- Eligibility conditions on future observed endpoints; missingness need not be random.
- Missingness grids are algebraic assumptions, not imputed returns or identified all-event effects.
- Canonical source assumptions inherited; no bid/ask, costs, borrow, path-risk or production claim.

Old full-path and endpoint receipts are untouched; no failed common-primary cohort has been opened. No horizon selected. `BLACKBOX_query_count=3`; `production_authority=false`; `fresh_oos=false`.

Method references and exact formulas are in `docs/governance/R1A_ENDPOINT_ROBUSTNESS_FREEZE@1.0.json`.
