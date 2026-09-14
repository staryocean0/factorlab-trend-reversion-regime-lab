# M8 Strategy-Layer Integration Validation

Status: **PASS with an explicit STAR50 external-caller gap**.

M8 validates integration boundaries only. It does not modify M7 consumer semantics, M6 representation, external repositories, market data, M5 outcomes, or the unopened Holdout.

## Validated external boundaries

### CSI1000

`staryocean0/csi1000-timing-strategy-private` already has a read-only Layer2 consumer adapter and a generic Layer3 orchestration kernel. The adapter declares read-only delivery with no value transformation, threshold mutation, strategy mutation, or production authority. Layer3 owns state adaptation, owner-waterfall composition, and conflict arbitration.

M8 therefore validates M7 trend snapshots as compatible read-only inputs to that ownership boundary. It does **not** install a new strategy plugin or create production wiring.

### STAR50 risk-state side

`staryocean0/factorlab-star50-filter-lab/research/state_degree_consumer_d5/consumer.py` is a real append-only Layer2 risk-state consumer with no-fallback semantics. Its own `example_consumer.py` explicitly reports `actual_external_consumer_connected=False`.

M8 therefore treats it as a real **parallel Layer2 risk provider**, not as an already connected strategy caller. Trend and risk can be passed upward under separate namespaces; no fused state or trade action is created in Layer2.

## Synthetic integration cases

The M8 conformance suite verifies:

- CSI1000 `1m=UP` and `5m=DOWN` remain distinct upper-layer inputs;
- STAR50 trend `DOWN` and risk `UNSAFE` remain separate inputs;
- latest expired trend remains `UNAVAILABLE`, with no fallback or SIDEWAYS substitution;
- unadmitted 15m fails before strategy composition;
- stable trend snapshots contain no T2, strong/five-bucket state, global state, action, position, order, route, or selected-strategy field.

## Frozen ownership rule

Layer2 supplies read-only measurements/state. Layer3 or a higher strategy layer owns cross-interval composition, risk/trend composition, conflict arbitration, selection, and any eventual action mapping. No M8 result grants production authority.

Machine authority: `TREND_M8_STRATEGY_INTEGRATION_V1.json`.

Next milestone: **M9 release/version/documentation/governance only**.
