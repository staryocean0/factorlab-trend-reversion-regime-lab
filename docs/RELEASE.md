# Layer 2 趋势状态组件 V1 发布说明

> 发布对象是 **Layer 2 trend-regime component**，不是交易策略，也不是对本仓全部历史研究模块的稳定性承诺。

## 1. 发布身份

- component id：`factorlab.layer2.trend_regime`
- component version：`1.0.0`
- planned Git tag：`trend-regime-v1.0.0`
- machine authority：`docs/governance/TREND_M9_RELEASE_GOVERNANCE_V1.json`
- `production_authority=false`
- `fresh_oos=false`

`pyproject.toml` 中仓库 distribution 仍为 `0.1.0`。该 distribution 包含大量历史研究、回放和维护代码，因此 **不是** trend component 的 semantic-version authority；M9 不把这些非趋势模块一并宣称为 1.0 stable。

## 2. V1 稳定调用面

```text
query_regime(symbol, as_of, bar_interval, profile_id=None)
```

正式返回语义：

```text
state             = DOWN | SIDEWAYS | UP
directional_score = frozen M2 slope_t
strength          = abs(directional_score)
```

稳定 schema：

- consumer：`regime_state_consumer_v1`
- snapshot：`trend_regime_snapshot@1.0`
- representation：`trend_regime_three_bucket_plus_continuous_strength@1.0`
- state scheme：`trend_regime_three_bucket@1.0`
- strength definition：`absolute_log_close_ols_slope_t@1.0`

V1 不包含 T2、`STRONG_UP/STRONG_DOWN`、five-bucket state、`global_state`、BUY/SELL、position、order、strategy selection 或 routing。

## 3. 当前 runtime admission

当前 V1 provider registry 只接纳：

- symbols：`000688.SH`, `000852.SH`
- `trend_1m_official_v1`
- `trend_5m_offset0_v1`

15m、60m 与其他 phase profiles 仍属于 M3 engineering registry，但 **不是 V1 runtime admitted surface**。未准入 profile 必须 fail closed 为 `STATE_NOT_ADMITTED`；发布动作不得扩张这个边界。

## 4. Compatibility / SemVer

### Patch（1.0.x）

只允许不改变公共语义的文档澄清、测试/CI 加固、内部重构。Public schema、required fields、状态边界、expiry/no-fallback 和 query 含义必须保持不变。

### Minor（1.x）

只允许向后兼容的增量能力。例如新增 profile/provider admission 时，必须先有新的 exact source admission receipt，且现有 caller 行为不能改变。可忽略的 optional metadata 也可作为 minor，但不能改变旧字段含义。

### Major（x.0）

以下变化必须新 major identity：状态枚举或 T1 边界、estimator/directional score、strength 定义、query 必需参数、snapshot identity、expiry/no-fallback、正式 T2/STRONG state、Layer2 global state、策略选择/路由/交易动作，或 authority 模型的根本变化。

任何语义变化都必须有新的 schema/version identity；历史 V1 snapshot 永不原地改写。

## 5. Migration

从 M7 之前的内部调用方式迁移到 V1：

1. 通过 `TrendRegimeConsumer.query_regime(...)` 读取，而不是直接依赖内部 measurement object。
2. `UNAVAILABLE` 是缺失状态，不是 `SIDEWAYS`。
3. latest expired / latest explicit unavailable 均不允许 fallback 到更旧 snapshot。
4. caller 不能传 lookback、estimator、T1/T2、provider admission、validity policy 或 strategy action。
5. 多周期组合、trend+risk 组合、策略选择与最终动作全部留在 Layer3/更上层。

M4/M5 five-bucket 文件从未成为 stable product API，因此不存在“从正式五桶 API 迁移到 V1”的兼容承诺；它们只保留为历史研究审计材料。

## 6. Evidence lineage

V1 的可追溯链为：

`M2 baseline math → M3 profile/view binding → M4 preregistration → M5 empirical closeout → M6 representation → M7 stable consumer → M8 caller-boundary validation → M9 release governance`

对应 machine authorities 已逐项登记在 `TREND_M9_RELEASE_GOVERNANCE_V1.json`。

## 7. Known limitations

- 15m/60m 和 phase profiles 尚未进入 V1 runtime admission。
- M5 strength/persistence 证据只覆盖 admitted 1m/5m、CSI1000 与 STAR50。
- STAR50 有真实 parallel risk-state provider，但没有被证明存在已连接 external strategy caller。
- M8 是 interface/ownership compatibility validation，不是 live deployment certification。
- 2025 protocol Holdout 未打开；`fresh_oos=false`。
- Layer2 不自行声明完整交易日日历 authority；它依赖 admitted provider/source receipts。
- 本发布不授予生产、交易动作、策略选择或路由 authority。

## 8. Release gate

只有在以下全部成立时才可创建 `trend-regime-v1.0.0` tag/release：

- repository consistency PASS；
- M2–M9 默认 contract tests PASS；
- M6/M7/M8 frozen semantics 未改变；
- `new_market_outcomes_computed=false`；
- M5 outcome jobs 仍 disabled/skipped；
- historical/full replay 没有因发布而自动触发；
- release notes 明示 `production_authority=false`、`fresh_oos=false` 和当前 runtime admission 限制。

发布不是研究重跑，也不是生产授权。
