# K-line transition recognition v2 — frozen protocol

Date frozen: 2026-09-08
Base evidence: completed `kline_state_recognition_v1` historical result bundle
Assets: CSI1000 `000852.SH`, STAR50 `000688.SH`
Primary clock: repository-verified `5m` K-line bars
Status: **preregistered before first v2 replay**

## 1. Why v2 exists

V1 produced a real Level-2 result. Its main failure modes were:

- the raw recognizer was often conservative: conditional accuracy when it emitted a concrete state was about 70%+, while concrete-state coverage was only about 51–52%;
- transition F1 was near zero;
- inspection of v1 transition events showed many online and oracle transitions with the same destination separated by about six 5-minute bars.

That six-bar offset is structurally expected because the v1 offline judge labels a center time using a fixed `+/-6` bar centered window. A judge label centered at time `t` is therefore not fully knowable until six eligible bars later. V1 scored the causal online event against the retrospective center timestamp, creating a systematic information-set mismatch.

V2 corrects that mismatch and adds one causal state-persistence decoder. It does **not** change the v1 feature formulas, state names, or numerical state thresholds.

V1 results remain immutable and are not overwritten.

## 2. Research question

Can the existing causal K-line recognizer, when evaluated against the offline judge at the time that judge label is actually fully observable, provide useful historical state and transition recognition?

Pipeline:

```text
v1 causal K-line features
-> v1 raw online state
-> causal persistent state decoder
-> availability-aligned offline state target
-> availability-aligned transition events
-> Level 2/3/4 historical recognition score
```

This is still chart/state recognition, not profitability research.

## 3. Frozen recognizer inputs and thresholds

V2 inherits v1 unchanged:

```text
clock = 5m
short window = 6 bars / 30m
primary online window = 12 bars / 60m
strict-prior reference = 480 finite observations
states = UpTrend / DownTrend / Range / Shock / Uncertain
```

Inherited state thresholds remain exactly:

```text
BDCI trend >= 60
BDCI range <= 40
trend efficiency >= 0.30
range efficiency <= 0.20
|DII| trend >= 1.25
shock RV rank >= 0.90
shock one-bar absolute-return rank >= 0.995
```

No threshold sweep, feature search, model-family search, or new market variable is allowed in v2.

## 4. Causal persistent decoder

The raw v1 recognizer remains the only source of new state evidence.

For each symbol and trading day separately:

1. reset stable state at the start of the day;
2. require the same new concrete raw state on `2` consecutive eligible bars to establish or switch the stable state;
3. before the first confirmed concrete state, output `Uncertain`;
4. once a stable concrete state exists, a raw `Uncertain` keeps the last stable state rather than erasing it;
5. a different concrete raw state becomes a pending candidate and must satisfy the same 2-bar confirmation rule before switching;
6. no state is carried overnight.

This adds no new numerical tuning parameter; it reuses the v1 frozen two-bar transition confirmation rule.

The decoded state is called `online_decoded_state`.

## 5. Availability-aligned offline target

The v1 offline judge uses a centered radius of six eligible 5-minute bars.

Therefore a judge label centered at eligible-bar sequence position `j` is fully observable only at sequence position:

```text
j + 6
```

For every trading day, first compute the v1 oracle state stream at its structural center timestamps, apply the same two-bar confirmation rule to obtain `oracle_confirmed_center_state`, and then shift that confirmed state forward by exactly six **eligible** bars.

At online decision time `t`, the primary target is:

```text
oracle_available_state(t) = oracle_confirmed_center_state(t - 6 eligible bars)
```

Rows without six prior eligible bars for this alignment are not scored.

This shift is fixed by the frozen judge geometry, not chosen from v1 performance.

## 6. Primary point-state metrics

Primary v2 point scoring compares:

```text
online_decoded_state(t)
vs
oracle_available_state(t)
```

Report separately for both assets:

```text
n_scored
concrete coverage
exact accuracy
conditional accuracy
balanced accuracy over 4 concrete states
macro F1 over 4 concrete states
per-state precision / recall / F1 / support
confusion matrix
yearly metrics
```

If a supported class is completely missed, its F1 is exactly zero.

Secondary diagnostics must also preserve:

- raw v1 same-center score;
- decoded same-center score;
- availability-aligned raw score.

Only the availability-aligned decoded score is primary for v2 maturity adjudication.

## 7. Availability-aligned transition scoring

Generate online transition events from `online_decoded_state`.

Generate oracle structural-center events from `oracle_confirmed_center_state`.

For each oracle event, map its center event to the same day's eligible-bar sequence and define:

```text
oracle_available_event_ordinal = oracle_center_event_ordinal + 6
```

An oracle event whose availability falls beyond the same day's eligible sequence is excluded from primary transition scoring and counted in an audit.

Match online to oracle one-to-one by:

- same symbol;
- same trading day;
- same destination concrete state;
- online event within `+/-3` eligible bars of the oracle **availability** event.

The `+/-3` tolerance is inherited unchanged from v1.

Report:

```text
transition precision
transition recall
transition F1
false transitions/day
median delay vs oracle availability
median delay vs structural center
```

A zero-match case has F1 = 0.

## 8. Capability rubric — unchanged from v1

### Level 2

End-to-end scoring exists but at least one Level-3 gate fails.

### Level 3

Both assets separately require:

```text
balanced_accuracy >= 0.55
transition_F1 >= 0.40
concrete coverage >= 0.60
every concrete state support >= 100
```

### Level 4

Both assets separately require:

```text
balanced_accuracy >= 0.70
transition_F1 >= 0.60
concrete coverage >= 0.75
at least 3 eligible yearly slices
yearly median balanced_accuracy >= 0.60
no eligible year balanced_accuracy < 0.50
```

### Level 5

Still unavailable because all supplied history is consumed development material. Independent/fresh evidence is required.

## 9. Candidate budget and anti-overfitting rule

V2 permits exactly one replay of the frozen design above.

After v2 results are observed:

- do not change the six-bar alignment;
- do not change two-bar confirmation;
- do not change thresholds;
- do not widen transition tolerance;
- do not add a new state;
- do not select a best asset/year subset.

If v2 still fails Level 3, preserve the null and preregister v3.

## 10. Required outputs

Write only under:

```text
experiments/kline_transition_recognition_v2/
```

Required files:

```text
RESULT_CARD.md
summary.json
input_identity.json
alignment_audit.json
state_timeseries.csv
transition_events.csv
confusion_matrix.csv
per_state_metrics.csv
yearly_metrics.csv
secondary_metrics.json
execution_receipt.json
```

## 11. Interpretation boundary

A positive v2 result would support only:

> the causal recognizer can identify a completed local K-line state and its transitions with useful historical accuracy once the offline centered reference is compared at its true information-availability time.

It does not establish:

- future-return prediction;
- profitable trading;
- optimal strategy frequency;
- production routing authority;
- fresh OOS validity.
