# Continue here — K-line recognizer v8 closeout

Date: 2026-09-09

## Canonical champion rule

Read these first:
- `docs/research/KLINE_RECOGNIZER_CHAMPION.md`
- `experiments/kline_recognizer_champion.json`

The current promoted recognizer is **v5 probability hysteresis** at immutable result commit:

`e4ddffd3c190ba18739587aabf73844b3daa2230`

A research version is only a challenger. Failure never changes the champion pointer.

## Completed challengers

- v6 type-specific confirmation policy: failed promotion.
- v7 Markov persistence filter: failed promotion.
- v8 learned switch gate: failed promotion.

V8 formal result:
- result commit: `dee1e5fd6feda8ad27ec86f64f5786b3b6d886f3`;
- candidate count: 18;
- no point-eligible candidate;
- `promoted_over_v5_pre2025 = false`;
- 2025 was not used to rescue v8;
- one-shot v8 workflow removed after completed replay.

## What the failures mean

Do not add another post-classifier switch/filter layer merely to reduce churn. V6, v7 and v8 tested three materially different post-processing approaches and none beat the current champion under the frozen pre-2025 promotion gates.

The next challenger should improve the **primary state model itself** by giving it causal temporal context instead of attempting to repair single-bar classifications afterward.

## Next challenger: v9

Direction:
- keep the frozen v3 benchmark / labels;
- keep 5-minute causal data and no future information;
- build temporal-context features from the existing v4 causal feature surface only;
- train the primary four-state classifier directly on current + lagged/change summaries;
- keep candidate menu small and frozen before outcomes;
- rolling selection remains pre-2025;
- v5 is the comparison champion;
- only a preregistered pre-2025 promotion pass may update the champion registry;
- otherwise leave v5 untouched.

No fresh-OOS, trading-profitability or production claim is implied.
