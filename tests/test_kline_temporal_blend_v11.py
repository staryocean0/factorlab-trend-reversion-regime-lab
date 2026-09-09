from regime_lab.kline_temporal_blend_v11 import (
    V11BlendCandidate,
    candidate_is_promotable,
    frozen_v11_menu,
    select_v11_candidate,
)


def test_v11_menu_is_exactly_three_local_weights():
    menu = frozen_v11_menu()
    assert [c.alpha for c in menu] == [0.35, 0.40, 0.45]
    assert all(c.horizon == 6 and c.auxiliary_C == 0.1 for c in menu)


def test_v11_rejects_architecture_drift():
    try:
        V11BlendCandidate(0.35, horizon=3)
    except ValueError:
        pass
    else:
        raise AssertionError("v11 must not change horizon")


def test_v11_promotion_requires_champion_noninferiority_and_material_gain():
    champion = {
        "min_balanced_accuracy": 0.755,
        "min_macro_f1": 0.759,
        "min_transition_f1": 0.198,
        "max_false_transitions_per_day": 1.207,
    }
    good = {
        "min_balanced_accuracy": 0.756,
        "min_macro_f1": 0.760,
        "min_transition_f1": 0.209,
        "max_false_transitions_per_day": 1.19,
    }
    too_small = {
        "min_balanced_accuracy": 0.756,
        "min_macro_f1": 0.760,
        "min_transition_f1": 0.202,
        "max_false_transitions_per_day": 1.19,
    }
    assert candidate_is_promotable(good, champion)
    assert not candidate_is_promotable(too_small, champion)


def test_v11_selection_prefers_transition_f1():
    champion = {
        "min_balanced_accuracy": 0.75,
        "min_macro_f1": 0.75,
        "min_transition_f1": 0.18,
        "max_false_transitions_per_day": 1.30,
    }
    a = V11BlendCandidate(0.35)
    b = V11BlendCandidate(0.40)
    agg_a = {
        "min_balanced_accuracy": 0.76,
        "min_macro_f1": 0.76,
        "min_transition_f1": 0.20,
        "max_false_transitions_per_day": 1.20,
    }
    agg_b = {
        "min_balanced_accuracy": 0.76,
        "min_macro_f1": 0.76,
        "min_transition_f1": 0.21,
        "max_false_transitions_per_day": 1.22,
    }
    selected, _ = select_v11_candidate([(a, agg_a), (b, agg_b)], champion)
    assert selected == b
