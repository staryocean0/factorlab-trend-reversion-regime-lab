# Continue here — low-weight persistence prior v13

Current champion remains v10 temporal blend.

V13 integrates exactly one audited contribution: v7 persistence information, converted into a one-step low-weight probability prior. It does not recreate the old Markov decoder.

Read first:
- `docs/research/KLINE_RECOGNIZER_AUTHORITY.md`
- `docs/research/KLINE_RECOGNIZER_CHAMPION.md`
- `experiments/kline_recognizer_contributions.json`
- `docs/research/KLINE_RECOGNIZER_PERSISTENCE_PRIOR_V13_PROTOCOL.md`

Execution order:
1. create v13 branch from completed v12 governance state;
2. implement rho={0.05,0.10,0.15}, fixed eta=2;
3. test day reset, one-step-only prior, no recursion, prefix causality and authority read-only guards;
4. run immutable data validation and full pytest;
5. run 2022-2024 rolling comparison against v10;
6. run 2025 safety diagnostic only if a pre-2025 rho qualifies;
7. update champion only in a separate governance action if the complete v13 challenger passes.
