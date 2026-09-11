# AI entry

Read in this order:

1. `CONTINUE_HERE.md`
2. `docs/research/INDEX_PRICE_VALIDITY_STUDY_20260911.md`
3. `PROMPT.md`
4. `AGENTS.md`

Current empirical state:

`R1_PRICE_EDGE_SUPPORTED_R2_DIRECT_DIRECTIONAL_PRICE_EDGE_NOT_SUPPORTED`

The frozen cash-index price study supports R1 directional price information, including delayed R1_B transport from CSI1000 to STAR50. It does **not** select a trading horizon or establish ETF/futures/options executability.

Both R1_B MO payoff identities remain closed as instrument-mapping failures. Do not create option v3/v4 from observed outcomes.

Current frontier: ETF/index-carrier price transport for R1 after ETF minute data are admitted and frozen. R2 direct directional implementation is not supported by the current price layer.

`BLACKBOX_query_count=3`.
`production_authority=false`.
