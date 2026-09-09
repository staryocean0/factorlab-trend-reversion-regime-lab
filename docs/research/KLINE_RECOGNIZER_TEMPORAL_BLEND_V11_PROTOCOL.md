# K-line recognizer temporal-blend v11 — local refinement protocol

Date frozen: 2026-09-09

Goal: refine the successfully integrated temporal contribution in the current v10 champion without changing architecture, features, auxiliary horizon, models, or decoder.

## Authority boundary

Current champion is `v10_temporal_blend` at immutable result commit `723404633fccb0a52181d2090cadbca3114dcc67`.

V11 is a challenger only. The champion registry is read-only during v11 execution and changes only in a separate governance action if v11 passes promotion.

## Fixed champion structure

Keep all v10 components fixed:
- primary head: pooled multinomial linear classifier, `C=1.0`, 12 current causal K-line features;
- temporal auxiliary: six-bar temporal-context linear classifier, `C=0.1`;
- temporal fallback: primary only when temporal context is unavailable;
- probability fusion: log-probability blend;
- decoder: unchanged v5 hysteresis, switch margin `0.05`, minimum probability `0.45`, confirmation `4` bars.

Only the temporal blend weight may change.

## Frozen local menu

Exactly three challengers:
- `alpha=0.35`;
- `alpha=0.40`;
- `alpha=0.45`.

Horizon is fixed at six bars and auxiliary `C=0.1`.

No other alpha, horizon, model, feature or decoder parameter may be added after results.

## Rolling evaluation

Same folds:
- train through 2021 -> validate 2022;
- train through 2022 -> validate 2023;
- train through 2023 -> validate 2024.

Compare against the v10 champion.

V10 champion pre-2025 worst-cell authority:
- min balanced accuracy `0.7553851080081395`;
- min macro F1 `0.7591912321042829`;
- min transition F1 `0.19843342036553524`;
- max false transitions/day `1.2066115702479339`.

For champion promotion, v11 must be noninferior on all four metrics and show at least one material improvement:
- min balanced accuracy +`0.01`, or
- min macro F1 +`0.01`, or
- min transition F1 +`0.01`, or
- max false transitions/day -`0.05`.

Selection among promotable candidates:
1. highest min transition F1;
2. lowest max false transitions/day;
3. highest min balanced accuracy;
4. highest min macro F1;
5. smaller alpha.

If no candidate passes, v10 remains champion.

## Contribution retention

Failure to become champion does not imply zero contribution. After the immutable result is produced, a v11 effect may be entered into the Contribution Ledger if it demonstrates a clear repeatable trade-off or local improvement useful for a later integrated challenger. Contribution retention is a separate governance action and never changes the champion by itself.

## 2025 safety diagnostic

Only after a pre-2025 candidate qualifies for promotion:
- refit fixed heads through 2024;
- compare v11 against the same-period v10 champion once on 2025;
- 2025 cannot select alpha or rescue a failed pre-2025 candidate.

Safety veto on either asset if:
- balanced accuracy lower by more than `0.01`;
- macro F1 lower by more than `0.01`;
- transition F1 lower by more than `0.01`;
- false transitions/day higher by more than `0.05`.

2025 remains already-consumed diagnostic evidence, not fresh OOS.

## Forbidden

- changing architecture;
- changing six-bar temporal horizon;
- changing either classifier C;
- changing v5 decoder;
- adding a postprocessor;
- asset-specific alpha;
- post-result alpha expansion;
- 2025-based selection or rescue;
- P&L-based selection;
- runner mutation of champion or contribution authority files.
