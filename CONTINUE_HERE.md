# Continue here — reversal / mean-reversion bucket

## Current authority

Certified mechanisms remain R1 `rmr_cross_scale_pullback_parent_integrity_v2` and R2 `rmr_range_boundary_parent_integrity_v2`.

`BLACKBOX_query_count=3` exactly: R1 PASS, R5-C FAIL, R2 PASS. No query #4. `production_authority=false`, `fresh_oos=false`.

## Current frontier — R1_A ETF delivery / admission

**`BLOCKED_CARRIER_DATA_NOT_ADMITTED`**

The user authorized R1_A carrier price transport. Its contract has now been frozen, the implementation tested, the original index input and matched-pair identities verified in the cloud, and the source acquisition audit executed. **ETF returns have not been measured**, because neither fixed ETF has an admitted historical minute delivery.

Do not say the ETF study passed or failed. The engineering run passed; the empirical step is data-blocked.

Read first:

1. `docs/research/R1A_CARRIER_TRANSPORT_STATUS_20260912.md`
2. `docs/governance/R1A_CARRIER_PRICE_TRANSPORT_FREEZE@1.0.json`
3. `research/r1a_carrier_transport/README.md` — exact delivery request, manifest shape and commands
4. `docs/ops/evidence/r1a_carrier_transport_20260912/transport_receipt.json`
5. `docs/ops/evidence/r1a_carrier_transport_20260912/source_inventory_receipt.json`

Cloud preflight run `34621777306`, job `103337245006`: SUCCESS; 33 synthetic boundary tests passed. This is not ETF alpha PASS.

Verified inventory:

| Index | Frozen ETF | Original R1_A event/control pairs | Verified index rows |
|---|---|---:|---:|
| `000852.SH` | `512100.SH` | 1,296 | 641,441 |
| `000688.SH` | `588000.SH` | 1,802 | 317,280 |

49,568 index-clock anchor rows (44,578 unique carrier/timestamp keys) are retained. They are timestamps to be priced by ETF data, not acquired ETF prices. `ETF_outcomes_read=false`; no signal refit, rematching or horizon selection occurred.

### Exact next action

Acquire/admit full, non-event-conditioned **2021-01-01 .. 2025-12-31** minute OHLCV for the fixed ETFs, plus source timestamp/adjustment/volume semantics and a complete split/distribution ex-date ledger. Existing legitimately accessible local DataHub or broker exports are acceptable candidates; no particular paid provider is mandatory.

Use the existing implementation, not another redesign:

```bash
PYTHONPATH=src:. python -m pytest -q tests/test_r1a_carrier_transport.py
PYTHONPATH=src:. python research/r1a_carrier_transport/transport.py --output /tmp/r1a-new-delivery
```

Source manifests belong at `data/r1a_carrier_prices/512100.SH.json` and `588000.SH.json`. Paid/nonpublic raw bytes default to the Git-ignored `data/r1a_carrier_prices/private/`. Do not expose credentials, nonpublic URLs or unauthorized raw data in public Git. Preserve the existing blocked receipt; use a new output directory for each delivery version.

The fixed replay keeps BOTH the original event and matched control. It uses exact index timestamps and the entire `1/5/15/30/60/120/240` observed-index-bar surface. No next-available ETF price, forward fill, interpolation, control rematching or holding-period selection. Corporate-action crossings and missing paths are explicitly excluded and counted; index comparisons use the identical common sample.

This is zero-cost synthetic LONG/SHORT price transport. MO Level-2 data, borrow access, broker fees and an actual trading account are not requirements of this layer.

### Acquisition findings — do not overstate

Five public FactorLab default-branch data trees were inventoried. The only ETF-named candidate was an overseas daily ASHS/ASHR/FXI/MCHI/SPY pack in the overnight repository, not the required domestic minute tape. Its rejection is recorded in `source_candidate_review.json`.

The two Eastmoney probes were disconnected, which is not proof of general data absence. Official AKShare ETF-minute documentation limits 1-minute output to recent five trading days. Tushare documents a historical `etf_mins` route but the cloud run had no configured authorized token. No paid order or credential circumvention occurred. Other local/private sources are not claimed to have been exhausted.

## Existing scientific evidence — unchanged

The pure index study reports favorable raw R1 price responses but no supported R2 direct directional response. The subsequent matched-parent attribution makes R1_A the lead historical price-alpha lane.

CSI1000 R1_A, 2021-2025:

- 15 observed bars: event +4.80bp, matched control +0.95bp, increment +3.85bp; pointwise event-day bootstrap 95% interval [+0.80,+6.88]bp; positive annual increment 4/5 years.
- 30 observed bars: event +6.80bp, control +0.72bp, increment +6.07bp; interval [+1.38,+10.66]bp; positive annual increment 5/5 years.
- LONG/SHORT increments were positive at those locations. **No 15/30-bar holding period is selected.**

STAR50 R1_A is weaker and did not satisfy the full prior strong-incremental flag. R1_B has positive raw delayed returns but no supported advantage over the frozen matched-parent controls (CSI1000 240-bar +23.43bp versus +34.63bp, increment -11.20bp). R2 direct directional translation remains unsupported.

These are observational historical findings conditional on the original matching design, not causal identification, familywise statistical proof or fresh independent OOS. Carrier transport cannot automatically upgrade those claims.

Retained scientific sources:

- `docs/research/R1_INCREMENTAL_ALPHA_PROGRAM_DECISION_20260911.md`
- `docs/research/R1_INCREMENTAL_ALPHA_ATTRIBUTION_20260911.md`
- `docs/governance/R1_INCREMENTAL_ALPHA_ATTRIBUTION_FREEZE@1.0.json`
- `docs/ops/evidence/r1_incremental_alpha_20260911/attribution_receipt.json`
- `docs/research/INDEX_PRICE_VALIDITY_STUDY_20260911.md`
- `docs/ops/evidence/index_price_validity_20260911/price_validity_receipt.json`

## Closed — no rescue

Still closed under their own definitions: R1 structural economic translations v1/v2/v3, R2 direct economic identity, unified router, R1_B temporal impulse completion, R1_B single-long ATM MO, R1_B 1x2 adjacent-OTM MO backspread, probability/threshold/sizing rescues, R3/R4/R5-B1/R5-C and broad automatic R8/R9 lanes.

No option, strike, DTE, ratio, exit, stop, target, side/year/regime/clock filter or horizon search is authorized by the ETF data-blocked state. Existing failures stay preserved. No BLACKBOX query #4 and no production promotion.

## Index data

Verified index data stay under `data/market/`, loaded through `src/regime_lab/market_data.py` with manifest/hash checks:

- `000852.SH` 1m: 2015-01-05 .. 2025-12-31;
- `000688.SH` 1m: 2020-07-23 .. 2025-12-31.

The separate `data/r1b_research/` pack remains infrastructure for already-closed MO research; it is not ETF price data.
