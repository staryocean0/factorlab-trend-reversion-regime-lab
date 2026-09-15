# 从这里接管

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> 当前：固定日来源对账已完成；现有数据仅限明确约束的历史观察。
> R1_A当前价格版本储备、主动开发暂停；没有新的本地交付任务或已授权实证候选。
> `BLACKBOX_query_count=3`；`production_authority=false`；`fresh_oos=false`。
> 机器状态：`FIXED_DAY_FIELD_ACCOUNTING_COMPLETE_CONSUMER_RESTRICTED_NO_VENDOR_BUCKET_CERTIFICATION`。
> [状态源](docs/REPOSITORY_STATE.json) · [最新研究解释](docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md)
<!-- END GENERATED STATUS -->

## 当前状态

本仓是 Layer 2 趋势状态识别组件，不是交易策略。**M0–M9 PASS**，V1 release 已冻结。

Component：`factorlab.layer2.trend_regime@1.0.0`。

Post-V1 Cross-Profile Invariance & Calibration Study 是独立研究线，不是自动 M10，不修改 V1。

当前研究进度：

- X1–X3 — **COMPLETE**
- X4 — **`INSUFFICIENT_EVIDENCE` / NO V1 CHANGE**
- X5 / X5B — **5m replication + source robustness COMPLETE**
- X5C — **15m/60m cross-carrier COMPLETE**
- X5D — **static calibration COMPLETE / NO ADOPTION**
- X5E — **causal rolling normalization COMPLETE / NO ADOPTION**
- X5F — **60m carrier × common-time decomposition COMPLETE / DIAGNOSTIC ONLY**
- X5G — **dynamic common + slow carrier COMPLETE / DIAGNOSTIC ONLY**
- X5H — **dual blend became prospective research candidate, NO ADOPTION**
- X5I — **independent-source prospective validation COMPLETE / NO CANDIDATE PASSES TURNOVER-AWARE GATES**
- X5J — **turnover-regularized scale COMPLETE / NO GATE-QUALIFIED CANDIDATE**
- X5K — **sparse / hysteretic scale update COMPLETE / NO GATE-QUALIFIED CANDIDATE**
- X6 — **HOLD / NOT READY**

V1 release pointer `release/trend-regime-v1.0.0` 必须继续固定在 `5a563d87d1628379e0d9a04aa7c5500bc30c4bc2`。

## 接管必读

- `docs/ROADMAP.md`
- `docs/governance/TREND_X5K_SPARSE_HYSTERETIC_STRENGTH_SCALE_PROTOCOL_V1.json`
- `docs/governance/TREND_X5K_SPARSE_HYSTERETIC_STRENGTH_SCALE_RESULT_V1.json`
- `docs/governance/TREND_X5K_POSTHOC_EVENT_SIZE_DIAGNOSTIC_V1.json`
- `docs/governance/TREND_X4_POST_X5K_UPDATE_V1.json`
- `docs/governance/TREND_X5J_TURNOVER_REGULARIZED_STRENGTH_SCALE_RESULT_V1.json`
- `docs/governance/TREND_X5I_PROSPECTIVE_FAST_VS_ADAPTIVE_STRENGTH_SCALE_RESULT_V1.json`
- `docs/governance/TREND_M7_CONSUMER_CONTRACT_V1.json`
- `docs/governance/TREND_M9_RELEASE_GOVERNANCE_V1.json`

## V1 正式产品

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

入口：`query_regime(symbol, as_of, bar_interval, profile_id=None)`。

Runtime admission 仍只有 `000852.SH` / `000688.SH` 的 1m official 与 5m offset0；Post-V1 public/native-clock research 数据不获得 admission。

## 到 X5J 已知什么

X5I 在独立 Tencent native 60m provider 上 prospectively 复制了 short-memory scale 的好处，也正式确认了 turnover 风险：fast 5/20 与 dual blend 均有约 93%+ 的 cross-carrier range reduction、约 23% 的 temporal improvement，但 median turnover 约为 slow 的 3.2×–3.4×，q95 约 2.1×–2.2×，因此在 turnover-aware gate 下失败。

X5J 随后测试 `CAP_0.06` 与 `EWMA α=0.35`：cap 降低了尾部 turnover，却几乎每根都打满 cap，造成明显响应滞后；EWMA 保留 scale alignment，并把 q95 turnover 压低到约 1.34× slow，但 median turnover 仍约 3.46×。因此连续型 regularization 没有产生全 gate candidate。

## X5K：Sparse / Hysteretic Strength Scale Update

X5K 进一步把 **update frequency** 正式纳入 gate，同时用 mean absolute `Δlog(scale)` 和 q95 jump 约束 turnover，避免“稀疏但巨跳”的方案被错误判优。

预注册候选：

```text
EVENT_DEADBAND_0P12_FULL
EVENT_PERSIST2_0P10_FULL
HYSTERETIC_EWMA_ENTRY0P16_EXIT0P06_A0P50
```

保留 slow 20/120 和 fast 5/20 为 baseline。必须同时满足：

```text
cross-carrier range reduction >= 75%
temporal improvement           >= 15%
breadth                       >= 4/5
interaction improvement        >= 20%
mean turnover                 <= 2.0x slow
q95 turnover                  <= 2.0x slow
update fraction               <= 35%
```

Tencent 主结果：

```text
EVENT_DEADBAND_0P12_FULL
  range reduction      93.77%
  temporal improvement 23.59%
  breadth              5/5
  interaction improve  38.41%
  mean / q95 turnover  2.65x / 2.11x
  update fraction      55.2%
  result               FAIL

EVENT_PERSIST2_0P10_FULL
  range reduction      94.35%
  temporal improvement 19.00%
  breadth              4/5
  interaction improve  35.32%
  mean / q95 turnover  2.66x / 3.20x
  update fraction      34.7%
  result               FAIL

HYSTERETIC_EWMA_ENTRY0P16_EXIT0P06_A0P50
  range reduction      93.81%
  temporal improvement 23.18%
  breadth              4/5
  interaction improve  30.14%
  mean / q95 turnover  2.43x / 1.60x
  update fraction      84.6%
  result               FAIL
```

Sina replication 几乎逐项一致，因此：

```text
TENCENT_QUALIFIED_CANDIDATES        = []
SINA_QUALIFIED_CANDIDATES           = []
CROSS_PROVIDER_QUALIFIED_CANDIDATES = []
SELECTED_CANDIDATE                  = NONE
```

### X5K 机制解释

`PERSIST2` 是第一个真正达到 sparse update-frequency gate 的方案（约 34.7%），但它并没有消除 turnover，而是把许多小更新积累成更大的单次跳跃。Post-hoc event-size diagnostic：

```text
FAST target
  update events         = 1148
  conditional mean jump ≈ 0.197
  conditional q95       ≈ 0.520

PERSIST2
  update events         = 451
  conditional mean jump ≈ 0.483
  conditional q95       ≈ 0.969
```

Deadband 0.12 的 update fraction 仍高达约 55.2%，不够稀疏；hysteretic EWMA 则约 84.6% 的时点仍在更新，本质上仍接近连续控制。

因此现在问题已经进一步收敛：**下一步不能只是提高 deadband 或增加 persistence 次数。** 更合理的是研究 `partial reset / anchored event update / cooldown-based stateful control`：触发事件后只释放部分累积误差，并明确限制 cooldown、单次 jump 与总 variation；同时继续禁止在同一 outcomes 上做阈值网格搜索。

## 当前结论

```text
SHORT_MEMORY_SCALE_BENEFIT                = REPLICATED
SCALE_TURNOVER_CONCERN                    = PROSPECTIVELY CONFIRMED
SIMPLE_CHANGE_RATE_CAP                    = NOT SUPPORTED
SIMPLE_EWMA                               = NOT SUPPORTED
SIMPLE_DEADBAND                           = NOT SUPPORTED
PERSISTENCE_ONLY_SPARSE_UPDATE            = NOT SUPPORTED
SIMPLE_HYSTERETIC_EWMA                    = NOT SUPPORTED
STABLE_TEMPORAL_PRODUCT_STRENGTH          = NOT ESTABLISHED
CURRENT_DECISION                          = INSUFFICIENT_EVIDENCE
V1                                        = NO CHANGE
X6                                        = HOLD / NOT READY
```

## 仍然禁止

- 重跑 M5 primary / T2 sensitivity / STAR50 replication；
- 打开旧 M4/M5 governed 2025 Holdout；
- 修改冻结的 M6/M7/M8/M9 semantics；
- 把 public/native-clock research source 写成 runtime admitted 或 DataHub exact identity；
- 输出 `global_state`、BUY/SELL、position/order、strategy selection/routing；
- 把 `production_authority=false` 或 `fresh_oos=false` 改成 true。

历史 V1 snapshots 永不原地改写。未来任何 T1、lookback、estimator、strength semantics 改动都必须经过新的版本化 representation decision。
