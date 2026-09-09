# Continue here — temporal-blend v10

V10 is a contribution-integration challenger, not a replacement baseline by assumption.

Current champion remains v5. V10 integrates only the retained v9 temporal-context contribution by blending a small temporal auxiliary probability head into the v5 primary probability head while keeping the v5 decoder unchanged.

Read first:
- `docs/research/KLINE_RECOGNIZER_AUTHORITY.md`
- `docs/research/KLINE_RECOGNIZER_CHAMPION.md`
- `experiments/kline_recognizer_contributions.json`
- `docs/research/KLINE_RECOGNIZER_TEMPORAL_BLEND_V10_PROTOCOL.md`

Execution order:
1. create the v10 research branch from this governance state;
2. implement the six frozen blend challengers;
3. add causality/blend/champion-read-only tests;
4. run immutable market validation and full pytest;
5. run 2022-2024 rolling comparison against the v5 champion;
6. run 2025 safety diagnostic only if a pre-2025 candidate qualifies;
7. update the champion registry only in a separate governance step if the complete v10 result is eligible and not vetoed.
