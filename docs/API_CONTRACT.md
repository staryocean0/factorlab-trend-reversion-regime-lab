# 趋势状态识别组件 API 合同（M1）

> 状态：**M1 接口合同已冻结；实现尚未进入 M7。**
>
> 本文冻结的是调用边界、时间语义、参数所有权和失败语义，不冻结 M2 的三桶数学公式、M3 的多周期 profile、M4–M6 的五桶研究结论，也不授予 production authority。

## 1. 合同目标

本组件是 Layer 2 的**趋势状态识别 consumer**。上层策略给出证券、查询时点和一个有版本的配置 profile，组件返回在该时点**已经可知且仍有效**的趋势状态快照。

组件回答：

> 在 `symbol + as_of + profile` 这个查询坐标下，当前是否存在可用状态；若存在，它是什么状态、由什么测量产生、何时发布、何时失效？

组件不回答买卖、仓位、订单、策略路由或应选择哪个交易工具。

## 2. 与现有 Layer 2 measurement plane 的关系

当前 `src/factor_lab/market_state/timing_layer2_measurement_plane.py` 已经定义：

- `Layer2MeasurementCoordinate`：测量坐标、`observation_time`、`available_at`、来源/估计器版本和 receipt identity；
- `Layer2Capability`：能力覆盖、状态和 known gaps；
- measurement authority 为真；
- strategy selection、parameter selection、routing、production authority 为假；
- 输出不得带 `position`、`action`、`selected_*`、`tool_owner`、`responsible_tool` 等策略字段。

因此本合同**不替换 measurement plane**。目标结构是：

```text
Layer 1 / market data
        ↓
Layer 2 measurement providers
        ↓
existing timing_layer2_measurement_plane
        ↓
Regime Snapshot Builder          ← M2/M3/M6 决定状态语义
        ↓
Regime Consumer / as_of facade   ← 本文冻结公开边界，M7 实现
        ↓
strategy callers
```

measurement plane 负责“能测什么、测量来自哪里”；consumer 负责“某个 `as_of` 时刻调用者能安全看到什么”。

## 3. 参考范式

接口语义参考 `staryocean0/factorlab-star50-filter-lab` 的 `state_degree_consumer_d5`：

- snapshot 不可变；
- 只允许按发布时间/接收时间向前追加；
- `as_of` 查询只看到当时已发布内容；
- 最新快照过期时**不得悄悄回退到更老快照**；
- 缺失、过期和不可用显式返回；
- consumer 本身不拥有交易 authority。

本组件只借鉴上述消费合同，不复制风险工具的 shock、recovery probability、风险持续时间等业务字段。

## 4. V1 逻辑调用面

M1 冻结以下**逻辑接口**；Python 类名和部署方式留到 M7：

```text
query_regime(
    symbol,
    as_of,
    profile,
) -> RegimeQueryResult
```

### 4.1 调用者必须提供

| 字段 | 要求 | 所有权 |
|---|---|---|
| `symbol` | 非空、属于该 profile 支持的 carrier/symbol 集合 | caller selects |
| `as_of` | timezone-aware datetime | caller selects |
| `profile` | 不可变、有版本的公开 profile ID | caller selects from component registry |

### 4.2 调用者不得通过稳定接口直接指定

下列参数可以存在于 profile 内部，但**不得作为稳定 consumer API 的任意自由参数**：

- 原始 lookback/window；
- 价格变换方式；
- slope / trend estimator 实现；
- normalization 公式；
- `T1/T2` 阈值；
- 三桶/五桶内部裁决版本；
- bar completion / session handling 规则；
- source/provider 优先级；
- publication / validity 规则。

理由：若每个策略都能临时传一套阈值和算法，本组件就不再有统一、可版本化的状态语义。

### 4.3 K 线级别的处理

`bar_interval` 是必须出现在返回快照中的消费维度，但 **M1 不提前冻结支持集合或 profile 与 bar_interval 的绑定方式**。

M3 将决定：

- profile 是否一对一绑定 `bar_interval`；
- 是否允许 `profile + bar_interval` 两级选择；
- 首批正式支持哪些周期。

在 M3 之前，调用者不能假定 `1m/5m/15m/60m` 已经全部可用。

## 5. `regime_state_consumer_v1` 最小返回 envelope

M1 冻结以下 envelope 形状。M2/M3 可以补全测量语义和枚举，但不得破坏这里的时间、安全和 authority 语义。

```json
{
  "schema": "regime_state_consumer_v1",
  "symbol": "000852.SH",
  "as_of": "2026-09-14T10:15:00+08:00",
  "profile": "<versioned-profile-id>",
  "status": "AVAILABLE | UNAVAILABLE",
  "reason": "<reason-code>",
  "snapshot": null,
  "production_authority": false
}
```

`AVAILABLE` 时，`snapshot` 至少包含：

```json
{
  "snapshot_id": "<content-or-event identity>",
  "symbol": "000852.SH",
  "profile": "<versioned-profile-id>",
  "bar_interval": "<profile-resolved interval>",
  "decision_time": "<timezone-aware datetime>",
  "observation_time": "<timezone-aware datetime>",
  "published_at": "<timezone-aware datetime>",
  "valid_until": "<timezone-aware datetime>",
  "state_scheme_version": "<version>",
  "state": "<M2/M6-governed state>",
  "measurement": {
    "estimator_id": "<id>",
    "estimator_version": "<version>",
    "raw_value": "<number or structured value>",
    "normalized_value": "<number or null>",
    "strength": "<number or null>"
  },
  "source_identity": {
    "source_id": "<id>",
    "source_version": "<version>",
    "source_receipt_sha256": "<sha256>",
    "bar_authority": "<authority>"
  },
  "authority": {
    "measurement": true,
    "strategy_selection": false,
    "parameter_selection": false,
    "routing": false,
    "production": false
  }
}
```

### 5.1 M1 明确冻结的字段

冻结字段名及含义：

- identity：`schema/snapshot_id/symbol/profile/bar_interval`；
- clock：`as_of/decision_time/observation_time/published_at/valid_until`；
- availability：`status/reason`；
- state envelope：`state_scheme_version/state/measurement`；
- provenance：`source_identity`；
- authority：measurement-only、`production_authority=false`。

### 5.2 M1 明确不冻结的内容

以下留给后续 Gate：

- `state` 最终是三桶还是五桶；
- slope 的最终数学定义；
- `raw_value/normalized_value/strength` 的量纲与公式；
- 具体 profile ID 和 bar interval 清单；
- `valid_until` 的具体周期规则。

因此 M1 冻结的是**容器与安全语义**，不是研究公式。

## 6. availability 与失败语义

`status` 只允许：

- `AVAILABLE`
- `UNAVAILABLE`

`UNAVAILABLE` 必须带机器可读 `reason`。V1 至少预留：

| reason | 含义 |
|---|---|
| `NO_PUBLISHED_SNAPSHOT` | `as_of` 之前没有任何已发布快照 |
| `LATEST_SNAPSHOT_EXPIRED` | 最新已发布快照已经失效；不得回退更老记录 |
| `INSUFFICIENT_HISTORY` | 当前 profile 所需历史不足 |
| `SOURCE_UNAVAILABLE` | 所需上游数据/receipt 不可用 |
| `UNSUPPORTED_SYMBOL` | profile 不支持该 symbol/carrier |
| `UNSUPPORTED_PROFILE` | profile 未注册或已退役 |
| `OUTSIDE_SUPPORTED_TIME` | 查询处于该 profile 不服务的交易/时间区域 |
| `MEASUREMENT_INVALID` | provider 产出未通过测量合同或完整性校验 |
| `STATE_NOT_ADMITTED` | 测量存在，但尚未被当前 state scheme 接纳为可发布状态 |

禁止用 `SIDEWAYS`、`DOWN`、`UP` 代替“数据缺失/不可用”。不可用是一种消费状态，不是一种市场状态。

## 7. as-of 与因果时间合同

### 7.1 可见性

一个 snapshot 只有在：

```text
published_at <= as_of < valid_until
```

且其所有输入在 `decision_time` 已经可知时，才能返回 `AVAILABLE`。

### 7.2 禁止未来信息

- `observation_time` 不能晚于该测量实际可观察的市场信息时点；
- `available_at/published_at` 不能早于产生该测量所需的最后信息；
- 调用者不能覆盖 component/source clocks；
- 未完成 K 线是否可用由 profile 的冻结规则决定，不能在调用时临时切换。

### 7.3 最新过期不回退

若 `as_of` 之前最新发布的 snapshot 已经过期：

```text
status = UNAVAILABLE
reason = LATEST_SNAPSHOT_EXPIRED
snapshot = null
```

不得为了“给调用者一个值”而返回更早但已经过时的状态。

### 7.4 时区

`as_of`、snapshot clocks 全部必须 timezone-aware。中国市场 profile 的内部标准时区预计为 `Asia/Shanghai`；最终 source clock 映射仍服从 Layer 1 authority 和 profile 合同。

## 8. 快照不可变与版本身份

- 已发布 snapshot 必须具有稳定 `snapshot_id`；
- 相同 `snapshot_id` 对应内容不得发生变化；
- 新估计器、阈值、状态方案或 profile 必须产生新版本身份，而不是改写旧历史；
- query 返回副本/只读视图，调用者不能经由返回对象修改 consumer 历史；
- future M7 实现应采用 append-only 或等价不可变存储语义。

## 9. 参数所有权

### Caller-owned selection

调用者拥有：

- `symbol`
- `as_of`
- 从注册表选择 `profile`
- M3 若批准后，可拥有显式 `bar_interval` 选择

### Component-owned semantics

组件拥有并版本化：

- 数据/载体适配；
- K 线完成规则；
- estimator；
- lookback；
- normalization；
- threshold；
- state scheme；
- validity；
- provenance；
- supported profile registry。

### Strategy-owned semantics

组件之外的策略拥有：

- 看到 `UP/DOWN/SIDEWAYS/...` 后做什么；
- 是否交易；
- 买卖方向；
- 仓位；
- stop/take-profit；
- 多周期状态如何组合；
- 趋势状态如何与风险组件联合使用。

## 10. 禁止输出的交易语义

稳定 consumer 不得输出或暗示：

- `BUY/SELL/HOLD`；
- `position/target_position`；
- `action/order`；
- `selected_strategy/selected_tool`；
- `responsible_tool/tool_owner`；
- “当前应顺势/反转/减仓”等推荐性字段。

若未来需要策略路由，应在 Layer 3/4 或独立 strategy layer 处理，不得污染 Layer 2 schema。

## 11. Provider admission：注册能力不等于可调用实现

当前 measurement-plane capability matrix 是一个冻结能力分母，其中部分 `source_refs` 在本裁剪仓的当前 checkout 并不存在，且多项 capability 明确标为 `partial/compatibility`。

因此 consumer 不得仅因某个 `asset_id` 出现在 capability registry 就发布状态。一个 provider 至少需要满足：

1. 实现/冻结 artifact 当前可解析；
2. source identity 可验证；
3. 能映射到 `Layer2MeasurementCoordinate` 或等价因果坐标；
4. 所需 clocks 完整；
5. provider-specific acceptance 通过；
6. 已被目标 profile 明确接纳。

不满足时必须 fail closed，而不是从历史 source ref、旧文档或近似实现推断当前状态。

## 12. 与 M2–M7 的边界

- **M2**：冻结三桶基线公式、K 线完成规则、阈值和可复现样例；补全 `state` 和 `measurement` 语义。
- **M3**：冻结 profile / bar interval 参数化。
- **M4–M6**：研究并裁决五桶是否获得正式状态语义。
- **M7**：实现本文 consumer、snapshot store/index、conformance tests。

M1 不允许通过实现细节提前决定上述研究结论。

## 13. M1 Gate

本合同通过 M1 Gate，因为：

- 调用者无需知道任何具体策略逻辑即可理解并使用接口；
- consumer schema 不包含交易动作；
- caller/component/strategy 参数所有权已经分离；
- as-of、published、valid、missing、expired 和 no-fallback 语义已明确；
- snapshot/provenance/authority 可以追溯；
- 未把三桶公式、多周期支持或五桶猜想伪装成已完成实现。

现有实现差距见 [API_GAP_ANALYSIS.md](API_GAP_ANALYSIS.md)。
