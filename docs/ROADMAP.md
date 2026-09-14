# 趋势状态识别组件路线图

> 本路线图定义执行顺序。组件是 Layer 2 市场状态基础设施，不是交易策略。
>
> 执行纪律：一次会话只推进当前里程碑；通过 Gate 后也不自动进入下一里程碑。

## 当前进度

- **M0 — PASS**：产品定位、白皮书与路线图。
- **M1 — PASS**：consumer 审计、API 合同与 Gap List。
- **M2 — PASS**：20-bar log-close OLS signed slope t-score 三桶基线，`T1=2.0`。
- **M3 — PASS**：versioned interval/profile registry、view/cadence/as-of 边界。
- **M4 — PASS**：五桶研究协议在 outcome 前冻结。
- **M5 — PASS**：CSI1000 primary、T2 sensitivity、STAR50 replication 收口；原 extreme-slope exhaustion H1 被稳健反驳。
- **M6 — PASS**：正式表示为三桶 + 连续 strength。
- **M7 — PASS**：stable consumer、immutable snapshot、append-only lifecycle、expiry/no-fallback 与 provider admission。
- **M8 — PASS（scope-limited）**：真实外部边界 + synthetic integration 验证完成；STAR50 没有被虚构成已连接的策略 caller。
- **唯一下一步：M9 — 发布、版本与治理。**

## M6 正式表示

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

schema：`trend_regime_three_bucket_plus_continuous_strength@1.0`。V1 stable API 不包含 T2、`STRONG_UP/STRONG_DOWN`、five-bucket state 或 `global_state`。

## M7 Stable Consumer（PASS）

Machine authority：`docs/governance/TREND_M7_CONSUMER_CONTRACT_V1.json`。

正式调用面：`query_regime(symbol, as_of, bar_interval, profile_id=None)`。当前 V1 provider admission 仅两指数的 `trend_1m_official_v1` 与 `trend_5m_offset0_v1`；其余 M3 engineering profiles fail closed。Consumer 保持 immutable/append-only、receipt-causal、latest-expired/unavailable no-fallback、`production_authority=false`。

## M8 策略层调用集成验证（PASS）

Machine authority：`docs/governance/TREND_M8_STRATEGY_INTEGRATION_V1.json`。

验证边界：

- CSI1000 私仓存在真实 read-only Layer2 adapter 与 Layer3 orchestration kernel；M7 snapshot 与该“Layer2 只读输入 → Layer3 组合/仲裁”边界兼容；
- STAR50 仓存在真实 append-only risk-state consumer，但其示例明确 `actual_external_consumer_connected=False`，因此 M8 只把它作为并行 Layer2 risk provider，不声称已有外部策略接线；
- synthetic integration 验证 1m/5m 可保持不同状态、trend/risk 保持独立 namespace、expired 不回退/不变 SIDEWAYS、15m 在上层之前 fail closed；
- Layer2 不产生 `global_state`、BUY/SELL、position/order、strategy selection 或 route；
- 外部仓库未修改，没有 market outcome、M5 reopen 或 Holdout read。

M8 的 PASS 是**接口与所有权边界验证**，不是 live/production integration certification，也没有安装新的策略 plugin。

## M9 — 发布、版本与治理（唯一下一步）

负责稳定版本、migration/changelog、API 示例、证据追踪、兼容性矩阵与发布治理。M9 不得借发布流程扩大当前 provider admission、重开 M5 outcome 或赋予 production authority。

## 全程不变原则

1. 组件不是交易策略。
2. 状态绑定 symbol / as_of / interval / profile / version。
3. V1 是三桶方向 + 连续强度。
4. 当前 runtime source admission 只有两指数 1m official / 5m offset0。
5. 研究阈值不得静默升级为产品语义。
6. `production_authority=false`，直到未来独立治理明确改变。
