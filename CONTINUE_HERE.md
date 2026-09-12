# Continue here — known ETF source correction and impact audit complete

## Latest authorized task: actually completed

**`KNOWN_ACTION_REPAIRED_PUBLISHED_MEMBERSHIP_UNCHANGED_SOURCE_SEMANTICS_PENDING`**.

Read first:
1. `docs/research/ETF_SOURCE_REPAIR_IMPACT_REVIEW_20260912.md`
2. `docs/governance/ETF_ACTION_SOURCE_OVERLAY_V2_20260912.json`
3. `data/etf_source_actions_v2/manifest.json`
4. `docs/ops/evidence/etf_source_repair_20260912/receipt.json`
5. `research/etf_source_repair/README.md`

The missing 512100 2022-09-02 share consolidation/suspension is now in a separate versioned known-action inventory. The originally proposed 2022-08-03 split was CANCELLED and is not an effective adjustment. Original price/action bytes, manifests and study receipts are preserved.

Decisive source impact run `34677079296`, code `7b66fa290ddeea363323bcb89fdc15f12a896384`; 125 baseline inputs pinned. All 3,098 original pairs and 21,686 event/control horizon windows checked under the original rules. Existing published rows checked: 46,594. No new signal, fit, return population, p-value or 2026 price was opened.

## Impact is now quantified — do not repeat the earlier unknown-impact claim

No included endpoint cohort changed, across both carriers and all seven horizons. Two original primary pairs generate three added action-crossing reasons (one at h120, two at h240); all were ALREADY excluded for missing event exits on the halted day. There is no original price window bridging the pre-consolidation and resumed valid-price units.

All 112 recomputed published mean groups have zero change. Full-path counts remain 846/1296 (512100, blocked) and 1791/1802 (588000, measured). All-horizon common endpoint counts remain 1192/1296 (blocked) and 1799/1802. No previously blocked outcome was opened.

Minute-measurement eligible counts remain 281,354 / 288,418, with zero change in preserved gaps. For 512100, 238 halted-day comparison opportunities move from missing-endpoint reason to known-action reason; data and samples do not change.

The earlier `ETF_SOURCE_QUALITY_ADVISORY_20260912.json` is preserved historical evidence. Its unquantified-impact field is superseded ONLY by this new scoped impact audit, not by a blanket claim that all sources are now valid.

## What is still unresolved

`full_source_qualification_complete=false`; `microstructure_research_admitted=false`.

The v2 correction does NOT certify an exhaustive 2021-2025 action/suspension calendar. 588000's empty known-action CSV is not proof of no action. Old corporate_actions_complete=true must never be used alone to admit NEW research.

Source contracts remain incomplete: zero-volume nonflat OHLC semantics, timestamp labels versus exchange publication, index causal fills and available_at meanings. Exporter behavior has been inspected (numeric volume conversion only, Z stripping/localization, keep-last), but referenced upstream contract documents were not obtained. No fabricated repairs.

Exact minimal source-document request: `docs/ops/ETF_UPSTREAM_SEMANTICS_HANDOFF_20260912.md`. No repeat five-year CSV delivery is needed. After source qualification, a separately authorized, small non-event-conditioned timestamped quote/reference sample may be considered; this task did not purchase or acquire it.

## Current research limits

The separate ETF/index measurement screen remains `MEASUREMENT_SCREEN_COMPLETED_MICROSTRUCTURE_IDENTIFICATION_BLOCKED`. Minute relative price changes are not NAV premiums, quote spreads or verified reversion. No lead-lag/half-life/threshold/repair-profit experiment follows automatically.

R1_A remains **R1A_CURRENT_PRICE_FORMULATION_RESERVED_ACTIVE_DEVELOPMENT_PAUSED**. Its closeout and original R1/R2 mechanism records are unchanged. No model/matching/horizon/side/year/cost/option rescue. The failed strict-control selected-pair outcomes and failed primary common-cohort outcomes remain unopened. Known 2026 candidate stays metadata-only.

`BLACKBOX_query_count=3`, no #4; `production_authority=false`; `fresh_oos=false`; no confirmation clock or selected horizon.

## Maintenance

Read-only current verification:

```bash
PYTHONPATH=src:. python -m pytest -q tests/test_etf_source_repair.py tests/test_etf_source_repair_retained.py
PYTHONPATH=src:. python research/etf_source_repair/verify_retained.py
```

This validates retained evidence and pinned input bytes, not a new independent experiment. Full source-impact reproduction remains available using a fresh directory, per module README. Never overwrite original evidence or run the obsolete exporter as a newly qualified source.
