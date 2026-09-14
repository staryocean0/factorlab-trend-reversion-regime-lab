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

2026-09-14 用户显式授权独立的 Post-V1 **Cross-Profile Invariance & Calibration Study**。它不是自动 M10，不修改 V1。

当前研究进度：

- X1 source/profile inventory — **COMPLETE**
- X2 distributional invariance + preregistered sensitivity — **COMPLETE**
- X3 state-dynamics invariance — **COMPLETE**
- X4 calibration-family decision — **`INSUFFICIENT_EVIDENCE` / NO V1 CHANGE**
- X5 five-carrier 5m replication — **COMPLETE**
- X5B 5m source robustness — **COMPLETE**
- X5C five-carrier 15m/60m + long-window 60m — **COMPLETE**
- X5D static interval-specific T1 vs static robust normalization — **COMPLETE / `INSUFFICIENT_EVIDENCE`**
- X6 representation version decision — **HOLD / NOT READY**

V1 release pointer `release/trend-regime-v1.0.0` 必须继续固定在 `5a563d87d1628379e0d9a04aa7c5500bc30c4bc2`；Post-V1 research commits 不得移动它。

## 接管必读

- `docs/ROADMAP.md`
- `docs/governance/TREND_CROSS_PROFILE_INVARIANCE_PROTOCOL_V1.json`
- `docs/governance/TREND_X5C_15M_60M_CROSS_CARRIER_PROTOCOL_V1.json`
- `docs/governance/TREND_X5C_SINA_15M_60M_SOURCE_RECEIPT_V1.json`
- `docs/governance/TREND_X5C_15M_60M_CROSS_CARRIER_RESULT_V1.json`
- `docs/governance/TREND_X5D_INTERVAL_CALIBRATION_COMPARISON_PROTOCOL_V1.json`
- `docs/governance/TREND_X5D_DEVELOPMENT_CALIBRATION_METHOD_V1.json`
- `docs/governance/TREND_X5D_DEVELOPMENT_CALIBRATION_RECEIPT_V1.json`
- `docs/governance/TREND_X5D_INTERVAL_CALIBRATION_COMPARISON_RESULT_V1.json`
- `docs/governance/TREND_X4_POST_X5D_UPDATE_V1.json`
- `docs/governance/TREND_M7_CONSUMER_CONTRACT_V1.json`
- `docs/governance/TREND_M9_RELEASE_GOVERNANCE_V1.json`

## V1 正式产品

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

入口：`query_regime(symbol, as_of, bar_interval, profile_id=None)`。

Runtime admission 仍只有 `000852.SH` / `000688.SH` 的 1m official 与 5m offset0；Post-V1 public/native-clock 研究数据不获得 admission。

## 现在真正知道什么

### 5m

5m 是目前最稳的一层：五指数 cross-carrier replication 中 SIDEWAYS occupancy range ≈ **3.13pp**，one-step self-transition range ≈ **1.23–1.87pp**。Sina vs Eastmoney 在 CSI1000/STAR50 上 slope_t Pearson ≈ **0.9999994**，三桶状态 **100% 一致**。

因此目前没有证据要求 5m carrier-specific / phase-specific / provider-specific T1。

### 15m

X5C 五指数 15m external replication 有 63 个完整交易日、每 carrier 989 measurements。固定 V1 `20-bar slope_t / T1=2` 时：

- abs(slope_t) q90 cross-carrier range ≈ **1.26**；
- SIDEWAYS occupancy range ≈ **4.65pp**；
- directional survival5 range ≈ **7.8–9.0pp**。

15m 仍比 60m 稳定得多。

### 60m

X5C 五指数 60m 使用 2026-01-05 至 2026-09-14，170 个完整交易日、每 carrier 661 measurements；所有预注册 directional metric 最小 origins = **181**，早先的 UP underpower 已解除。

但 heterogeneity 仍明显：

- abs(slope_t) q90 range ≈ **3.37**；
- SIDEWAYS occupancy range ≈ **12.41pp**；
- survival5 range：DOWN ≈ **14.75pp**、UP ≈ **10.44pp**。

因此 60m 的问题是真实存在的，不再能主要归因于样本太短。

## X5D 得到了什么

X5D 参数只从 2020 Development exact-view 数据拟合，2026 五指数仅做外部 evaluation，没有读取交易收益。

Development 拟合：

```text
interval-specific T1:
5m  ≈ 1.9989
15m ≈ 1.9351
60m ≈ 1.2225

median-abs normalization equivalent raw T1:
5m  = 2.0000
15m ≈ 2.0717
60m ≈ 1.2701
```

两种方法在 Development 上都认为 60m 数值标尺不同，但在 2026 外部样本上没有形成全面优势：

- interval-specific T1：16 个语义 dispersion 指标 **9 改善 / 7 恶化**；
- primary median-abs normalization：**10 改善 / 5 恶化 / 1 持平**；
- MAD normalization：**9 / 7**；
- q75 normalization：**7 / 9**；
- 任意候选之间都没有严格 Pareto dominance。

静态 60m calibration 会把 SIDEWAYS carrier dispersion 从约 **12.4pp** 降到约 **6.8pp**，但会恶化若干 persistence/reversal 指标；例如 DOWN opposite-entry10 dispersion 从 V1 约 **5.2pp** 上升到约 **11%–12%**。同时约 **10%–15%** 的 60m 状态会被改写。

q75 normalization 对数值 strength scale 很有效：cross-interval strength-level range 从 raw ≈ **0.506** 降到 ≈ **0.157**；但 state semantics 并未同步改善，因此不能把它直接升级成产品 strength 定义。

## 当前结论

```text
UNIVERSAL_FIXED_T1          = current V1 baseline, not a proven universal law
STATIC_INTERVAL_SPECIFIC_T1 = not supported for adoption
PROFILE_SPECIFIC_T1         = not supported as default
STATIC_NORMALIZED_SCORE     = not supported for adoption
NORMALIZED_STRENGTH_SCALE   = promising diagnostic only
CURRENT_DECISION            = INSUFFICIENT_EVIDENCE
X6                           = HOLD / NOT READY
```

60m 剩余问题现在应理解为：**interval scale + temporal/regime nonstationarity + clock/source identity**，不是简单“把 T1 从 2 改成 1.2”就能解决。

## 下一研究边界

如果继续 normalization：

1. 分开研究 state-boundary normalization 与 strength-scale normalization；
2. 必须 causal / out-of-time，不得拿 2026 evaluation 重新拟合静态阈值；
3. 不能通过强制固定 SIDEWAYS occupancy 抹掉真实 regime 信息；
4. 优先获得更多 governed/exact 60m clock 证据，或预注册新的因果 normalization protocol。

## 仍然禁止

- 重跑 M5 primary / T2 sensitivity / STAR50 replication；
- 打开旧 M4/M5 2025 Holdout；
- 修改冻结的 M6/M7/M8/M9 semantics；
- 把 public/native-clock research source 写成 runtime admitted 或 DataHub exact identity；
- 输出 `global_state`、BUY/SELL、position/order、strategy selection/routing；
- 把 `production_authority=false` 或 `fresh_oos=false` 改成 true。

历史 V1 snapshots 永不原地改写。未来任何 T1、lookback、estimator、strength semantics 改动都必须经过新的版本化 representation decision。
