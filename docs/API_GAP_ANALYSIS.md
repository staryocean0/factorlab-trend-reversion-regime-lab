# 趋势状态 Consumer：当前 Gap List（已吸收 M2–M8）

> **M8 PASS（scope-limited）。** M7 stable consumer 已通过真实外部边界 + synthetic integration 验证；当前唯一下一步是 M9 release/version/governance。

## 1. 当前路径

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
        ↓
M9 release/version/governance
```

## 2. 已解决项

| ID | Gap | 解决状态 |
|---|---|---|
| G01–G04 | entrypoint / consumer / snapshot / expiry | M7 RESOLVED |
| G05 | caller/component 参数所有权 | M3/M7 RESOLVED |
| G06/G07 | 三桶数学/completed-bar/T1 | M2 RESOLVED |
| G08 | 多周期 profile | M3 RESOLVED |
| G09 | 五桶市场证据收口 | M5 RESOLVED |
| G11/G12 | snapshot identity/history + conformance | M7 RESOLVED |
| G14 | 多调用者/上层集成边界未证明 | **M8 RESOLVED WITH SCOPE LIMIT**：CSI1000 real Layer2→Layer3 boundary + STAR50 parallel risk-provider boundary + synthetic composition tests |
| G15/G16 | cadence / global trend 歧义 | M3 RESOLVED |
| G18–G24 | preregistration/evidence | M4/M5 RESOLVED |
| G25 | representation 未裁决 | M6 RESOLVED |
| G26 | M6 representation 未进入 snapshot | M7 RESOLVED |
| G27 | 上层可能误把 state/strength 当交易动作 | **M8 RESOLVED**：Layer2 direct action mapping explicitly forbidden/tested |

## 3. M8 已验证的外部边界

Machine authority：`docs/governance/TREND_M8_STRATEGY_INTEGRATION_V1.json`。

### CSI1000

私仓的真实 read-only Layer2 adapter 固定 `value_transformation=false / thresholds=false / strategy_mutation=false`；真实 Layer3 orchestration kernel 负责 state adapter、owner waterfall 和 conflict arbitration，且本身不输出 position。M8 验证 M7 trend snapshot 可以作为该所有权模型中的只读输入，但没有修改外部仓或安装策略 plugin。

### STAR50

`state_degree_consumer_d5` 是真实并行 Layer2 risk provider，并具有 append-only/no-fallback 边界；但其仓内示例明确 `actual_external_consumer_connected=False`。因此 M8 **不声称存在已部署的 STAR50 策略 caller**，只验证 trend/risk 分离 namespace 的上层组合接口。

Synthetic conformance 同时确认：1m/5m 冲突状态保持独立；expired/unavailable 不变成 SIDEWAYS；15m 在进入策略层之前保持 `STATE_NOT_ADMITTED`；stable snapshot 不含 T2/strong/global/action/position/order/route。

## 4. 仍未解决 / 明确保留的边界

| ID | Gap | 当前状态 | 后续处理 |
|---|---|---|---|
| G10 | provider/source admission 范围不完整 | V1 runtime 仅两指数 1m official / 5m offset0 | 扩张必须新 exact receipt/version；M9 只能记录，不能擅自扩权 |
| G13 | release lifecycle / migration 尚未完整发布化 | M7/M8 machine contracts 已冻结 | **M9** changelog/migration/release policy |
| G17 | 完整交易日 completeness authority 不在 Layer2 | consumer 不猜交易日 | M9 文档化 Layer1 authority / future upstream work |
| G28 | STAR50 尚无已连接外部策略 caller | 仓内 evidence 明确为 false | 记录为 deployment/integration limitation；不是生产已完成声明 |

## 5. 唯一下一步：M9

M9 只做发布、版本、兼容性和治理收口：schema/version matrix、API examples、migration/changelog、evidence lineage、known limitations 与 release policy。

M9 不得借发布流程：

- 扩张当前 provider admission；
- 改 M6 representation 或 M7 lifecycle；
- 重跑 M5 / 打开 Holdout；
- 把 M8 interface validation 写成 live/production integration certification；
- 授予 production authority。
