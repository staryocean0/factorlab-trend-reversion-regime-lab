# K-line recognizer learned switch gate v8 — result card

V8 modifies only recognizer A by adding a causal learned switch head. The state classifier, causal K-line feature surface, and frozen benchmark remain unchanged.

## Pre-2025 promotion decision

Switch gate promoted over v5: **False**

V5 frozen rolling-CV baseline:
- minimum transition F1: `0.179`
- maximum false transitions/day: `1.240`
- minimum balanced accuracy: `0.754`
- minimum macro F1: `0.756`

No switch-gate candidate satisfied the preregistered pre-2025 promotion gate. V5 remains the active recognizer; 2025 was not used to rescue v8.

## Boundary

2025 was already consumed by earlier development and is diagnostic only. This is chart-state recognition research, not a trading-profitability or fresh-OOS claim.
