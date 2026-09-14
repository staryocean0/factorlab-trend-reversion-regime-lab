# M5-3 Development Seal

状态：**PASS — SEALED BEFORE PRIMARY VALIDATION**。

本文件只解释 `TREND_M5_DEVELOPMENT_SEAL_V1.json`；机器 receipt 是 authority。

## 已封存

M5-3 固定了 M4 协议、M5-1 source/profile admission、M5-2 Development adequacy receipt，以及 Development 实际依赖的计算/读取代码：M5-2 entrypoint/core、M2 slope baseline、M3 profile registry、Layer-1 clock contract、market-data reader。

同时固定：

- 本地 `data/manifest.json` Git blob；
- DataHub export `factorlab_unified_index_kline_v3_20260824`；
- `1m_official` 与 `5m_offset_0` 的 source SHA256；
- Development run `34812469153`、head、artifact ID 与 artifact digest；
- Development split `2020-07-23`–`2022-12-30`；
- `runtime_available_at = bar_end` 的历史回放时钟适配。

15m/60m 仍然 `NOT_ADMITTED`，不得因进入 Validation 阶段而补采、重采样或换 profile。

## Primary family 不缩小

M4 的 planned primary family 固定为 `4 intervals × 2 directions = 8`。当前只有 1m/5m 的 4 个 contrasts 可执行；15m/60m 的 4 个 planned contrasts 仍保留，并按预注册规则 `p=1.0` 进入 Holm。禁止在 source admission 以后把 family 从 8 缩成 4。

## Seal 的含义

后续 primary Validation 必须使用 seal 中完全相同的协议、source identity、profile identity 与底层计算语义。修改任一 sealed path 都会使 seal regression 失败；若确需改变，必须建立新版本并重新开始协议流程，不能把修改后的结果冒充本次预注册 Validation。

## 本轮明确未做

M5-3 没有读取 Validation/Holdout 数据，没有计算 survival、reversal、return、transition、MFE/MAE、bootstrap 或 p-value，也没有裁决 H1。

## 唯一下一步

**M5-4：一次性的 primary `T2=4` Validation，仅执行已 admitted 的 1m/5m anchors；Holm family 仍为 8。** Holdout 继续锁定，协议与 sealed code 不得修改。
