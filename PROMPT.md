# 本地执行模型接管提示 — R1_A ETF 公共数据交付

仓库：`staryocean0/factorlab-trend-reversion-regime-lab`。先读 `CONTINUE_HERE.md`，安全 fetch/fast-forward main。

## 已完成

1. **公共字节包** `data/r1a_carrier_prices/cloud_pack_v1/`：2021–2025 全量 1m OHLCV（含零成交量）、除权除息表、manifest、校验清单；与 `private/` **字节相同**。
2. **588000.SH** 描述性 transport 与公开账本审计已完成。
3. **512100.SH** 数据已交付，但 2021 正成交量覆盖率 **94.478738% < 95%**；源审计：`TRUE_ZERO_VOLUME_ON_INDEX_CLOCK`（`r1a_carrier_source_audit_20260912`）。
4. 总状态 **`PARTIAL_CARRIER_TRANSPORT`**。

## 云端命令（无需 DataHub / private）

```bash
git clone https://github.com/staryocean0/factorlab-trend-reversion-regime-lab.git
cd factorlab-trend-reversion-regime-lab
PYTHONPATH=src:. python -m pytest -q \
  tests/test_r1a_carrier_transport.py \
  tests/test_r1a_public_delivery_audit.py \
  tests/test_r1a_delivered_ledger_regression.py \
  tests/test_r1a_cloud_pack_delivery.py
PYTHONPATH=src:. python research/r1a_carrier_transport/transport.py \
  --manifest-dir data/r1a_carrier_prices/cloud_pack_v1 \
  --output /tmp/r1a-cloud-replay-new
```

## 不可改变

原配对、七周期、95% 门槛、`BLACKBOX_query_count=3`、`production_authority=false`。不要把工程通过写成策略 PASS。
