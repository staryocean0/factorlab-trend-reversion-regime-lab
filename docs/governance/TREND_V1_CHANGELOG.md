# Trend Regime Component Changelog

This changelog tracks the **Layer 2 trend-regime component** stable release line. It does not claim semantic-version stability for every historical research or maintenance module in this repository.

## [1.0.0] - 2026-09-14

### Stable product surface

- Freeze `factorlab.layer2.trend_regime` as component version `1.0.0`.
- Stable query: `query_regime(symbol, as_of, bar_interval, profile_id=None)`.
- Stable consumer schema: `regime_state_consumer_v1`.
- Stable snapshot schema: `trend_regime_snapshot@1.0`.
- Stable representation: `trend_regime_three_bucket_plus_continuous_strength@1.0`.
- Formal state remains `DOWN / SIDEWAYS / UP`.
- `directional_score` remains the frozen M2 `slope_t`.
- `strength = abs(directional_score)`.

### Runtime admission

- Admitted symbols: `000688.SH`, `000852.SH`.
- Admitted profiles: `trend_1m_official_v1`, `trend_5m_offset0_v1`.
- 15m/60m and other phase profiles remain fail-closed under V1 runtime admission.

### Lifecycle guarantees

- Immutable snapshots and deterministic identity.
- Append-only ingest.
- Publication/receipt causal visibility.
- Latest-expired and latest-explicit-unavailable no-fallback.
- Unavailable is never silently converted to `SIDEWAYS`.

### Integration boundary

- CSI1000 real Layer2 read-only adapter / Layer3 orchestration ownership boundary validated.
- STAR50 parallel risk-state provider acknowledged without claiming a connected external strategy caller.
- Multi-interval trend states and trend/risk namespaces remain separate at Layer2.

### Governance

- Add component SemVer policy, migration rules, evidence lineage, known limitations and release gate.
- Add V1 API examples.
- Preserve `production_authority=false` and `fresh_oos=false`.
- Do not reopen M5 outcomes or read the 2025 protocol Holdout.
- Do not promote T2 or five-bucket research semantics into the stable V1 product.

### Not included

- No BUY/SELL, position, order, routing or strategy-selection semantics.
- No live/production integration certification.
- No expansion of provider/profile admission.
- No claim that 15m/60m have 1m/5m-equivalent empirical certification.
- No package-wide `1.0.0` stability claim for the repository's Python distribution; `pyproject.toml` remains `0.1.0` because its scope is broader than this component release.
