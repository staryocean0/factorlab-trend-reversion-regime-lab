# RESULT CARD — H1 Overnight-Gap Mechanism Audit v0.12

Date: 2026-09-07  
Status: **first materially stronger candidate mechanism; still development evidence**  
Run: `34102914428`  
Artifact: `reversal-overnight-gap-v0-12`  
Artifact ID: `10011213909`  
Artifact digest: `sha256:bd27e321d63f7a07acd291a7205a2c168c17f51e491cd1a9ce7777cad40aec99`

## Question

Does the relatively stable CSI1000 `09:30–10:00` robust-reentry effect identified in v0.11 mainly represent **fading the overnight gap**, or is the gap relation irrelevant?

## Frozen definitions

No entry family or numeric threshold changed from v0.11:

- robust residual re-entry signal computed on completed 5m bars, threshold 2.0;
- H1 = 09:30–10:00;
- supplied 1m path used only after the completed 5m signal;
- next-1m-open entry, previously audited to equal next-5m-open;
- symmetric 10bps target/stop;
- 5/10/30m caps;
- 2020-07-23 through 2024-12-31 only;
- 2025 unopened.

The only new coordinate is sign of the already-known overnight gap:

- `GAP_FADE`: reversal trade direction is opposite the previous-close -> current-open gap;
- `GAP_FOLLOW`: reversal trade direction is with the gap.

No gap magnitude threshold is searched.

## Audit

H1 signals:

| Symbol | H1 signals | Gap fade | Gap follow | Median |gap| |
|---|---:|---:|---:|---:|
| STAR50 | 389 | 288 | 101 | 28.40 bps |
| CSI1000 | 339 | 265 | 74 | 20.03 bps |

All 339 CSI1000 H1 signals have a defined non-zero gap relation.

Seed validation passed and pytest remained **42 passed**.

## CSI1000 pooled first-passage result

### GAP_FADE

| Cap | Side | Events | Clean target share | Symmetric hit imbalance |
|---:|---|---:|---:|---:|
| 5m | ALL | 265 | 57.14% | +1.17 bps |
| 5m | LONG | 162 | **60.58%** | **+1.79 bps** |
| 5m | SHORT | 103 | 51.25% | +0.19 bps |
| 10m | ALL | 265 | 55.78% | +1.09 bps |
| 10m | LONG | 162 | **58.97%** | **+1.73 bps** |
| 10m | SHORT | 103 | 50.53% | +0.10 bps |
| 30m | ALL | 265 | 54.92% | +0.98 bps |
| 30m | LONG | 162 | **58.64%** | **+1.73 bps** |
| 30m | SHORT | 103 | 49.02% | -0.19 bps |

### GAP_FOLLOW

The corresponding pooled LONG clean target share is below 50% at all three caps:

- 5m: 45.95%;
- 10m: 48.78%;
- 30m: 48.78%.

Therefore the H1 effect is not simply a generic property of all opening-half-hour re-entry signals.

## Year transport — CSI1000 GAP_FADE LONG

At the 10m cap, clean target share by year:

- 2020 partial: 58.33% (12 events);
- 2021: 63.89% (38);
- 2022: 56.41% (39);
- 2023: 65.71% (39);
- 2024: 50.00% (34).

Thus 4 yearly slices are above 50% and the fifth is exactly 50%; none is below 50% at 10m. The 30m cap has the same 4-positive / 0-negative / 1-equal pattern.

The 5m cap is slightly less stable: 4 positive years and 1 negative.

2020 is only a partial common-sample year and must be down-weighted conceptually.

## Key interpretation

The strongest lead found so far is no longer “CSI1000 mean reverts” or even “09:30–10:00 mean reverts.” It is much more specific:

> **After a negative overnight gap, a CSI1000 long robust-reentry event during 09:30–10:00 has shown a materially higher probability of reaching +10bps before -10bps than the generic reversal baselines.**

This is development evidence, discovered after a sequence of failed and localized tests. It is not fresh OOS and should not be enlarged with more filters.

The asymmetry is also direction-specific: short `GAP_FADE` events do not show the same pooled edge. That directional asymmetry is itself part of the mechanism and must not be averaged away.

The supplied paper pack contains prior evidence linking Chinese overnight returns to the T+1 trading environment and separate evidence of intraday reversal/momentum differences by clock. Those papers make this mechanism economically plausible but do not validate this exact index event rule.

## Decision

**Freeze here. Do not add another development filter before confirmation.**

The next research action should be a preregistered 2025 project-local historical confirmation of the exact candidate:

- CSI1000 only for the primary candidate;
- negative overnight gap;
- H1 09:30–10:00;
- LONG robust-reentry signal threshold 2.0;
- next-1m-open entry;
- 10bps symmetric target/stop;
- primary cap 10m;
- 5m and 30m reported only as frozen robustness caps;
- conservative treatment of any same-1m-bar target/stop ambiguity;
- no new threshold, clock, side or gap-magnitude search after seeing 2025.

2025 remains consumed historical material, not fresh OOS, even if it passes.
