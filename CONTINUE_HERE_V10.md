# Continue here — temporal-blend v10

Date: 2026-09-09

## Outcome

V10 successfully integrated a retained contribution from failed challenger v9 and is now the promoted champion.

Immutable v10 result commit:
`723404633fccb0a52181d2090cadbca3114dcc67`

Selected configuration:
- primary head: v5 pooled multinomial linear classifier, `C=1.0`;
- temporal auxiliary: 6-bar v9 context classifier, `C=0.1`;
- log-probability blend alpha: `0.30`;
- decoder: unchanged v5 hysteresis (`0.05`, `0.45`, `4`).

Pre-2025 worst-cell metrics:
- min balanced accuracy `0.7553851080`;
- min macro F1 `0.7591912321`;
- min transition F1 `0.1984334204`;
- max false transitions/day `1.2066115702`.

2025 consumed-data safety diagnostic passed with no veto. This is not fresh OOS.

## Authority state

Current champion: **v10 temporal blend**.
Previous champion: **v5 probability hysteresis**, preserved with immutable result commit `e4ddffd3c190ba18739587aabf73844b3daa2230`.

Canonical authority files:
- `docs/research/KLINE_RECOGNIZER_AUTHORITY.md`
- `docs/research/KLINE_RECOGNIZER_CHAMPION.md`
- `experiments/kline_recognizer_champion.json`
- `experiments/kline_recognizer_contributions.json`
- `experiments/kline_recognizer_promotion_log.json`

The v9 six-bar temporal-context contribution is now marked successfully integrated into champion v10.

## Next contribution refinement

V10's own frozen candidate surface showed that, for the successful six-bar auxiliary, increasing alpha from `0.10 -> 0.20 -> 0.30` improved transition behavior while the `0.20-0.30` region still preserved point-state floors. The selected alpha `0.30` sat at the top edge of the frozen v10 menu.

The next challenger should therefore be a narrow local refinement, not a new architecture:
- keep the entire v10 champion structure fixed;
- keep six-bar temporal context fixed;
- keep auxiliary `C=0.1` fixed;
- keep v5 primary head and decoder fixed;
- test only slightly higher temporal blend weights in a new version;
- champion remains v10 unless the complete refinement challenger passes promotion.
