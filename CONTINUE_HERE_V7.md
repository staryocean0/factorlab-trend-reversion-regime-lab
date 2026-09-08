# Continue here — K-line recognizer Markov filter v7

V7 starts from the completed v6 research state but returns the active recognizer baseline to v5 because v6 was not useful.

Goal: improve recognizer A itself using a causal learned Markov persistence filter over the locked linear classifier probabilities.

Read first:
- `CONTINUE_HERE_V6.md`
- `docs/research/KLINE_RECOGNIZER_MARKOV_FILTER_V7_PROTOCOL.md`

Execution order:
1. implement pooled pre-validation 4x4 transition-matrix fitting and causal forward filter;
2. add no-future/day-reset/transition-count tests;
3. run 12 frozen Markov candidates plus v5 baseline on rolling 2022-2024 folds;
4. promote only if pre-2025 gates beat/match v5 as preregistered;
5. run 2025 diagnostic only after selection is locked;
6. preserve failure without candidate expansion.
