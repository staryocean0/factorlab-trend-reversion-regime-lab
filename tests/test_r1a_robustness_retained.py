import json
from pathlib import Path
import pandas as pd
from research.r1a_endpoint_robustness.study import sha, HORIZONS, SPECS

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/ops/evidence/r1a_endpoint_robustness_20260912'


def test_retained_robustness_files_and_scope():
    r=json.loads((OUT/'robustness_receipt.json').read_text())
    assert r['decision']=='RETROSPECTIVE_ENDPOINT_ROBUSTNESS_COMPLETED_NO_PRODUCTION'
    assert sha(ROOT/'docs/governance/R1A_ENDPOINT_ROBUSTNESS_FREEZE@1.0.json')==r['freeze_sha256']
    assert r['BLACKBOX_query_count']==3
    for k in ['production_authority','fresh_oos','signal_refitted','horizon_selected','old_protocols_changed','missing_ETF_outcomes_imputed','primary_common_cohort_opened','research_history_multiplicity_corrected']:
        assert r[k] is False
    for s in r['output_csvs']:
        p=OUT/s['path']
        assert p.stat().st_size==s['bytes'] and sha(p)==s['sha256']
    for carrier, info in r['carriers'].items():
        assert set(map(int,info['horizons']))==set(HORIZONS)
        for cell in info['horizons'].values():
            assert len(cell['inference'])==len(SPECS)
            assert set(cell['missing_sensitivity'])=={'pooled','2021','2022','2023','2024','2025'}
    assert r['primary_family14_positive_cells']==[]
    assert r['all_four_family56_positive_cells']==[]


def test_retained_complete_family_and_scenarios_not_horizon_selection():
    cells=pd.read_csv(OUT/'all_56_inference_cells.csv')
    assert len(cells)==56 and not cells.duplicated(['carrier','horizon','spec']).any()
    assert set(cells.horizon)==set(HORIZONS)
    scenarios=pd.read_csv(OUT/'missing_residual_scenarios_NOT_ESTIMATES.csv')
    assert len(scenarios)==14*6*11
    assert not scenarios.missing_returns_imputed.any()
    thinning=pd.read_csv(OUT/'clock_disjoint_selection_audit.csv')
    assert len(thinning)==(1296+1802)*7
    assert (thinning.retained_for_sensitivity == (thinning.clock_selected_before_eligibility & thinning.endpoint_eligible)).all()
