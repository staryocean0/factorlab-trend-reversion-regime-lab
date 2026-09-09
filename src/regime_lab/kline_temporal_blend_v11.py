"""V11 local refinement of the promoted v10 temporal blend."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from regime_lab.kline_temporal_blend_v10 import (
    aggregate_fold_metrics,
    safety_veto_2025,
    score_blend_period,
)


@dataclass(frozen=True, slots=True)
class V11BlendCandidate:
    alpha: float
    horizon: int = 6
    auxiliary_C: float = 0.1

    def __post_init__(self) -> None:
        if self.alpha not in {0.35, 0.40, 0.45}:
            raise ValueError("v11 alpha outside frozen grid")
        if self.horizon != 6:
            raise ValueError("v11 horizon is frozen at 6")
        if self.auxiliary_C != 0.1:
            raise ValueError("v11 auxiliary C is frozen at 0.1")

    @property
    def candidate_id(self) -> str:
        return f"v11_h6_a{self.alpha:.2f}"

    def to_dict(self) -> dict[str, object]:
        return {
            "alpha": float(self.alpha),
            "horizon": 6,
            "auxiliary_C": 0.1,
        }


def frozen_v11_menu() -> tuple[V11BlendCandidate, ...]:
    return tuple(V11BlendCandidate(alpha) for alpha in (0.35, 0.40, 0.45))


def candidate_is_promotable(
    aggregate: Mapping[str, float],
    champion: Mapping[str, float],
) -> bool:
    noninferior = (
        float(aggregate["min_balanced_accuracy"]) >= float(champion["min_balanced_accuracy"])
        and float(aggregate["min_macro_f1"]) >= float(champion["min_macro_f1"])
        and float(aggregate["min_transition_f1"]) >= float(champion["min_transition_f1"])
        and float(aggregate["max_false_transitions_per_day"])
        <= float(champion["max_false_transitions_per_day"])
    )
    material = (
        float(aggregate["min_balanced_accuracy"]) >= float(champion["min_balanced_accuracy"]) + 0.01
        or float(aggregate["min_macro_f1"]) >= float(champion["min_macro_f1"]) + 0.01
        or float(aggregate["min_transition_f1"]) >= float(champion["min_transition_f1"]) + 0.01
        or float(aggregate["max_false_transitions_per_day"])
        <= float(champion["max_false_transitions_per_day"]) - 0.05
    )
    return bool(noninferior and material)


def select_v11_candidate(
    rows: list[tuple[V11BlendCandidate, Mapping[str, float]]],
    champion: Mapping[str, float],
) -> tuple[V11BlendCandidate | None, Mapping[str, float] | None]:
    eligible = [(c, a) for c, a in rows if candidate_is_promotable(a, champion)]
    if not eligible:
        return None, None
    return max(
        eligible,
        key=lambda item: (
            float(item[1]["min_transition_f1"]),
            -float(item[1]["max_false_transitions_per_day"]),
            float(item[1]["min_balanced_accuracy"]),
            float(item[1]["min_macro_f1"]),
            -float(item[0].alpha),
        ),
    )


__all__ = [
    "V11BlendCandidate",
    "aggregate_fold_metrics",
    "candidate_is_promotable",
    "frozen_v11_menu",
    "safety_veto_2025",
    "score_blend_period",
    "select_v11_candidate",
]
