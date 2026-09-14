# 趋势状态 Consumer：当前 Gap List（M0–M9 已收口）

> **M9 PASS。** Stable component `factorlab.layer2.trend_regime@1.0.0` 的 compatibility、migration、evidence lineage、known limitations 与 release governance 已冻结。当前没有自动进入的新研究里程碑。

## 1. 完整路径

```text
M2/M3 measurement + profiles
        +
M4/M5 evidence
        +
M6 three-bucket + continuous strength
        +
M7 stable consumer + snapshot lifecycle
        +
M8 integration-boundary validation
        +
M9 release/version/governance
        ↓
versioned maintenance / future separately-governed changes
```

## 2. 已解决项

| ID | Gap | 解决状态 |
|---|---|---|
| G01–G04 | entrypoint / consumer / snapshot / expiry | M7 RESOLVED |
| G05 | caller/component 参数所有权 | M3/M7 RESOLVED |
| G06/G07 | 三桶数学/completed-bar/T1 | M2 RESOLVED |
| G08 | 多周期 profile engineering registry | M3 RESOLVED |
| G09 | 五桶市场证据收口 | M5 RESOLVED |
| G11/G12 | snapshot identity/history + conformance | M7 RESOLVED |
| G13 | release lifecycle / migration / changelog / compatibility | **M9 RESOLVED** |
| G14 | 多调用者/上层集成边界未证明 | M8 RESOLVED WITH SCOPE LIMIT |
| G15/G16 | cadence / global trend 歧义 | M3 RESOLVED |
| G18–G24 | preregistration/evidence | M4/M5 RESOLVED |
| G25 | representation 未裁决 | M6 RESOLVED |
| G26 | M6 representation 未进入 snapshot | M7 RESOLVED |
| G27 | 上层可能误把 state/strength 当交易动作 | M8 RESOLVED |
| G29 | component semantic version 与仓库 package version 易混淆 | **M9 RESOLVED**：component=`1.0.0`，repository distribution=`0.1.0`，后者不是 component SemVer authority |

## 3. M9 release governance

Machine authority：`docs/governance/TREND_M9_RELEASE_GOVERNANCE_V1.json`。

Stable component identity：`factorlab.layer2.trend_regime@1.0.0`。

M9 已冻结：

- stable public call/schema matrix；
- patch/minor/major compatibility rules；
- pre-M7 internal usage → V1 migration；
- M2→M9 evidence lineage；
- `docs/RELEASE.md`、`docs/API_EXAMPLES.md`、`CHANGELOG.md`；
- known limitations；
- release gate 与 forbidden release actions。

语义变化必须新 schema/version identity；历史 V1 snapshot 永不原地改写。

## 4. 明确保留为 limitation / upstream ownership 的项目

这些不是“遗漏未做完”，而是 V1 明确不拥有的边界：

| ID | Boundary | V1 状态 | 未来若改变 |
|---|---|---|---|
| G10 | provider/source admission 范围 | 仅两指数 1m official / 5m offset0 | 需要新 exact source admission receipt + 至少 minor version governance |
| G17 | 完整交易日 completeness authority | Layer2 不猜交易日，由 Layer1/provider receipt 负责 | 由上游 authority 解决，不得 Layer2 本地补造 |
| G28 | STAR50 external strategy caller | 当前没有被证明存在 connected external caller | 后续可做独立 integration/deployment work，但不能回写 M8 历史结论 |
| G30 | live/production certification | 未认证；`production_authority=false` | 必须独立 production governance，不能由 component release 自动获得 |
| G31 | fresh OOS certification | `fresh_oos=false`，2025 protocol Holdout 未打开 | 必须独立预声明的新证据流程 |

## 5. V1 稳定边界

当前正式产品只有：

```text
DOWN | SIDEWAYS | UP
+ directional_score
+ continuous strength
```

当前不属于 V1 stable product：

- formal T2 / `STRONG_UP` / `STRONG_DOWN`；
- 15m/60m runtime admission；
- phase profile runtime admission；
- `global_state`；
- trend+risk fused state；
- BUY/SELL、position/order、strategy selection/routing；
- live/production authority。

因此 M9 收口后没有“自动 M10”。未来变更必须从 M9 的 SemVer、source admission 和 authority 规则重新立项。
