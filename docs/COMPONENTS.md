# 文件组件与生命周期

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](REPOSITORY_STATE.json) · [最新研究解释](research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

当前维护工具和生成文档受统一门禁保护；历史源码保留导入闭包，历史研究不自动执行。

| 模块 | 状态 | 解释 | 复现工作流 |
|---|---|---|---|
| [etf_day_reconciliation](../research/etf_day_reconciliation/README.md) | `READ_ONLY_SOURCE_CONSUMER` | [报告](research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md) | [手动复现](../.github/workflows/etf-day-reconciliation.yml) |
| [etf_one_day_review](../research/etf_one_day_review/README.md) | `COMPLETED_SOURCE_AUDIT_REPLAY_ONLY` | [报告](research/ETF_ONE_DAY_CLOUD_REVIEW_20260912.md) | [手动复现](../.github/workflows/etf-one-day-observation.yml) |
| [etf_upstream_review](../research/etf_upstream_review/README.md) | `COMPLETED_SOURCE_AUDIT_REPLAY_ONLY` | [报告](research/ETF_UPSTREAM_CLOUD_REVIEW_20260912.md) | [手动复现](../.github/workflows/etf-upstream-delivery.yml) |
| [etf_source_repair](../research/etf_source_repair/README.md) | `COMPLETED_KNOWN_ACTION_REPAIR_REPLAY_ONLY` | [报告](research/ETF_SOURCE_REPAIR_IMPACT_REVIEW_20260912.md) | [手动复现](../.github/workflows/etf-source-repair.yml) |
| [etf_index_measurability](../research/etf_index_measurability/README.md) | `COMPLETED_MEASUREMENT_REPLAY_ONLY` | [报告](research/ETF_INDEX_MEASURABILITY_REVIEW_20260912.md) | [手动复现](../.github/workflows/etf-index-measurability.yml) |
| [r1a_evidence_closeout](../research/r1a_evidence_closeout/README.md) | `RESERVE_DISPOSITION_READ_ONLY_AUDIT` | [报告](research/R1A_EVIDENCE_CLOSEOUT_REVIEW_20260912.md) | [手动复现](../.github/workflows/r1a-evidence-closeout.yml) |
| [r1a_walkforward_prediction](../research/r1a_walkforward_prediction/README.md) | `RESERVED_HISTORICAL_REPLAY_ONLY` | [报告](research/R1A_WALKFORWARD_PREDICTION_REVIEW_20260912.md) | [手动复现](../.github/workflows/r1a-walkforward-prediction.yml) |
| [r1a_control_design](../research/r1a_control_design/README.md) | `CLOSED_DESIGN_NO_SELECTED_OUTCOMES` | [报告](research/R1A_CAUSAL_CONTROL_DESIGN_REVIEW_20260912.md) | [手动复现](../.github/workflows/r1a-control-design.yml) |
| [r1a_development_noise](../research/r1a_development_noise/README.md) | `COMPLETED_DEVELOPMENT_REPLAY_ONLY` | [报告](research/R1A_DEVELOPMENT_NOISE_REVIEW_20260912.md) | [手动复现](../.github/workflows/r1a-development-noise-regression.yml) |
| [r1a_confirmation_feasibility](../research/r1a_confirmation_feasibility/README.md) | `COMPLETED_PLANNING_NO_NEW_PROBES` | [报告](research/R1A_CONFIRMATION_FEASIBILITY_REVIEW_20260912.md) | [手动复现](../.github/workflows/legacy-price-statistics-replay.yml) |
| [r1a_method_calibration](../research/r1a_method_calibration/README.md) | `COMPLETED_SYNTHETIC_REPLAY_ONLY` | [报告](research/R1A_METHOD_CALIBRATION_REVIEW_20260912.md) | [手动复现](../.github/workflows/legacy-price-statistics-replay.yml) |
| [r1a_endpoint_robustness](../research/r1a_endpoint_robustness/README.md) | `COMPLETED_RETROSPECTIVE_REPLAY_ONLY` | [报告](research/R1A_ENDPOINT_ROBUSTNESS_REVIEW_20260912.md) | [手动复现](../.github/workflows/legacy-price-statistics-replay.yml) |
| [r1a_carrier_transport](../research/r1a_carrier_transport/README.md) | `RESERVED_LEGACY_PRICE_REPLAY_ONLY` | [报告](research/R1A_EVIDENCE_CLOSEOUT_REVIEW_20260912.md) | [手动复现](../.github/workflows/legacy-price-statistics-replay.yml) |
| [index_price_validity](../research/index_price_validity/README.md) | `COMPLETED_HISTORICAL_REPLAY_ONLY` | [报告](research/INDEX_PRICE_VALIDITY_STUDY_20260911.md) | [手动复现](../.github/workflows/legacy-price-statistics-replay.yml) |
| [r1_incremental_alpha_attribution](../research/r1_incremental_alpha_attribution/README.md) | `COMPLETED_HISTORICAL_REPLAY_ONLY` | [报告](research/R1_INCREMENTAL_ALPHA_ATTRIBUTION_20260911.md) | [手动复现](../.github/workflows/legacy-price-statistics-replay.yml) |
| [r1b_mo_data_admission](../research/r1b_mo_data_admission/README.md) | `RETIRED_ACQUISITION_RETAINED_FOR_DEPENDENCIES` | [报告](research/R1B_MO_OUTCOME_STUDY_20260911.md) | [手动复现](../.github/workflows/legacy-price-statistics-replay.yml) |
| [r1b_mo_pre_execution](../research/r1b_mo_pre_execution/README.md) | `CLOSED_OPTION_IDENTITY_REPLAY_ONLY` | [报告](research/R1B_MO_PRE_EXECUTION_FREEZE_20260911.md) | [手动复现](../.github/workflows/legacy-price-statistics-replay.yml) |
| [r1b_mo_outcome](../research/r1b_mo_outcome/README.md) | `CLOSED_OPTION_IDENTITY_REPLAY_ONLY` | [报告](research/R1B_MO_OUTCOME_STUDY_20260911.md) | [手动复现](../.github/workflows/legacy-price-statistics-replay.yml) |
| [r1b_mo_backspread](../research/r1b_mo_backspread/README.md) | `CLOSED_OPTION_IDENTITY_REPLAY_ONLY` | [报告](research/R1B_MO_RATIO_BACKSPREAD_OUTCOME_STUDY_20260911.md) | [手动复现](../.github/workflows/legacy-price-statistics-replay.yml) |

所有原始data、决定性evidence、历史报告与冻结文件按[基线清单](maintenance/BASELINE_COMPONENTS.json)受保护。归档副本保存清理前字节。新增文件也必须属于已注册组件；新research目录不会自动取得权限。

上游白皮书位于data交付包；迁移策略白皮书位于docs/archive，均为来源/历史快照。本仓当前规范白皮书为[WHITEPAPER](WHITEPAPER.md)。
