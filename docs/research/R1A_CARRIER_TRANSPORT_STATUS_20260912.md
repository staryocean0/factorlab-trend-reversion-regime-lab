# R1_A carrier price transport — execution status

Session date: 2026-09-12. GitHub execution timestamps are retained as returned by GitHub; this document's date is not a relabeling of source history.

## Decision

**`BLOCKED_CARRIER_DATA_NOT_ADMITTED`**

The frozen price-transport implementation and the real index-clock preflight have executed. Actual ETF outcome measurement has **not** executed because neither fixed carrier has an admitted 2021-2025 minute-price delivery. This is neither an alpha PASS nor an alpha FAIL.

`ETF_outcomes_read=false`, `signal_refitted=false`, `control_rematched=false`, `horizon_selected=false`, `fresh_oos=false`, `BLACKBOX_query_count=3`, `production_authority=false`.

## Executed, not merely designed

Freeze: `docs/governance/R1A_CARRIER_PRICE_TRANSPORT_FREEZE@1.0.json`.

Freeze commit: `b9a1a69a17dffe328360a69586065292c077f960`, before carrier outcomes.

Freeze SHA256: `7c3b08847a873132df36c97b4c8c8e84c251c4b9c56568260ffbbb90ce99142b`.

Verified cloud run: `34621777306`, job `103337245006`, code commit `03aafcd07ad498e55e4a61dc4efc6f0465363eb3`.

The run completed package installation, the 33 synthetic boundary tests, a five-public-repository source inventory, bounded historical endpoint probes, frozen index-input checks, clock-anchor generation, explicit blocked-state serialization, evidence commit, and artifact upload.

| Reference index | Fixed ETF | Frozen R1_A event/control pairs | Index rows verified | ETF outcome state |
|---|---|---:|---:|---|
| `000852.SH` | `512100.SH` | 1,296 | 641,441 | NOT OPENED |
| `000688.SH` | `588000.SH` | 1,802 | 317,280 | NOT OPENED |

The existing matched-pairs file was byte-identity checked against its frozen Git blob. Its SHA256 is `e4f5977919077e39935adfd5f7f0db0ff41c640de60470c757bf754c457da23c`.

49,568 clock-anchor rows were generated, representing 3,098 pairs × 2 legs × 8 endpoints (entry plus seven horizons). There are 44,578 unique carrier/timestamp keys. These are verified **index-reference timestamps**, not acquired ETF prices.

Anchor CSV SHA256: `2b82ccf2a0a1b58d3b43f1354217033fcaf55d01f81f099862f7a7206d4ac8b0`; bytes: 4,657,643.

## Source findings

The five public FactorLab default branches were scanned without truncation. Four had no ETF-named data blobs in their data trees. The overnight repository's candidate was inspected through its manifest and rejected: it contains **daily overseas ASHS/ASHR/FXI/MCHI/SPY**, not domestic `512100.SH`/`588000.SH` minute prices. See `source_candidate_review.json`.

The two bounded Eastmoney historical kline probes ended in `RemoteDisconnected`. This is recorded as `PROBE_UNAVAILABLE_NOT_DATA_ABSENCE_PROOF`; it does not prove the vendor has no data. Separately, the official AKShare `fund_etf_hist_min_em` documentation limits 1-minute output to the recent five trading days, which is not the frozen 2021-2025 history.

Tushare's official `etf_mins` documentation describes the required historical frequency, but this cloud run had no configured `TUSHARE_TOKEN`. The route was therefore `NOT_ATTEMPTED_AUTH_NOT_CONFIGURED`, not a successful download and not a claim that the user has no subscription elsewhere. No token was guessed, borrowed, displayed, or purchased.

These checks do not exhaust every commercial provider, private local data store, nondefault branch, or unlabeled binary file. The narrow verified conclusion is that **no usable ETF delivery was acquired and admitted in this run**.

## Implementation boundary

`research/r1a_carrier_transport/transport.py` uses the original event and matched-control indices unchanged, joins ETF prices at exact index timestamps, and reports every frozen `1/5/15/30/60/120/240` horizon. It never shifts to the next available ETF bar or picks a best holding period.

The data gate checks provenance, hashes, source time/adjustment/volume semantics, valid OHLCV, duplicates, full-year coverage and a common complete-pair sample. Both event and control must be covered; same-sample index comparators are recomputed. Missing minutes, zero-volume observations and paths crossing documented split/distribution ex-dates remain explicit exclusions rather than invented fills or fitted adjustments.

The price layer uses zero cost and synthetic SHORT. It does not need an options tape, Level-2 quotes, a fee schedule or borrow access to define its research returns. Actual trading feasibility remains a later, separate question.

## Initial CI issue and correction

Run `34621221643` passed all 33 tests and generated the correct blocked receipt, but Bash's inherited `-e` exited at the intentional return code 2 before the evidence-commit step. Its artifact `10272059807` retained the initial receipts.

The workflow wrapper was corrected to capture that exit code inside an explicit `if` before checking the receipt. No research definition, input pairing, coverage threshold or outcome was changed. The subsequent cloud run above succeeded and committed the decisive receipts. Engineering SUCCESS remains distinct from ETF research BLOCKED.

## Next concrete dependency

Deliver or authorize access to the full non-event-conditioned 2021-2025 minute OHLCV tape for `512100.SH` (primary) and `588000.SH` (secondary), together with the timestamp/adjustment dictionary and complete split/distribution ex-dates. Existing local DataHub/broker exports are acceptable candidates when their identity, semantics and research rights can be verified. Neither a specific vendor purchase nor a new signal design is required.

Exact manifest shape, data request, commands and privacy boundary are in `research/r1a_carrier_transport/README.md`. Paid/nonpublic bytes default to the Git-ignored `data/r1a_carrier_prices/private/` directory. Use a new output directory for each future delivered-data version; preserve this blocked receipt.

ETF transport remains unmeasured. The R1_A index findings remain historical leads conditional on the original matching design, not causal proof or fresh independent OOS. R1_B, R2 and option closeouts are unchanged.

## Decisive evidence

- `docs/ops/evidence/r1a_carrier_transport_20260912/transport_receipt.json`
- `docs/ops/evidence/r1a_carrier_transport_20260912/frozen_index_clock_anchors.csv`
- `docs/ops/evidence/r1a_carrier_transport_20260912/source_inventory_receipt.json`
- `docs/ops/evidence/r1a_carrier_transport_20260912/source_candidate_review.json`

## Primary external references

- ETF historical minute API and permission: https://tushare.pro/document/2?doc_id=387
- AKShare ETF-minute coverage: https://akshare.akfamily.xyz/data/fund/fund_public.html
- Fixed CSI1000 ETF identity: https://www.sse.com.cn/disclosure/announcement/general/c/c_20201021_5237291.shtml
- Fixed STAR50 ETF identity: https://www.chinaamc.com/fund/588000/
