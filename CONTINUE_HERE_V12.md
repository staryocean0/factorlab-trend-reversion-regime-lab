# Continue here — Shock-exit soft-inertia v12

Current champion remains v10 temporal blend.

V12 integrates exactly one audited historical contribution: v6 Shock-exit asymmetry, converted from hard confirmation counts into a small soft log-odds inertia while leaving the entire v10 model and ordinary decoder behavior unchanged.

Read first:
- `docs/research/KLINE_RECOGNIZER_AUTHORITY.md`
- `docs/research/KLINE_RECOGNIZER_CHAMPION.md`
- `experiments/kline_recognizer_contributions.json`
- `docs/research/KLINE_RECOGNIZER_HISTORICAL_CONTRIBUTION_AUDIT_V6_V9.md`
- `docs/research/KLINE_RECOGNIZER_SHOCK_EXIT_INERTIA_V12_PROTOCOL.md`

Execution order:
1. create v12 branch from this governance-complete v11 state;
2. implement exactly three gamma challengers;
3. add Shock-only/day-reset/no-future/champion-read-only tests;
4. run immutable data validation and full pytest;
5. run 2022-2024 rolling comparison against v10;
6. run 2025 safety diagnostic only if a pre-2025 gamma qualifies;
7. update champion only in a separate governance action if the complete v12 challenger passes.
