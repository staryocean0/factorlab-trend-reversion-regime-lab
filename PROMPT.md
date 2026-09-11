# 接管提示 — ETF数据已完成交付，转回云端处理

仓库：`staryocean0/factorlab-trend-reversion-regime-lab`。先读 CONTINUE_HERE.md。安全同步 main，不覆盖本地未提交工作。

## 不再需要重复搬数据

用户提交 `9abe7046e50b5eeb6299848eccf6039f7af55647` 已把实际文件交付到公共 Git：

`data/r1a_carrier_prices/cloud_pack_v1/`

共12个CSV：10个年度行情文件、2个除权除息表；583,943行行情。云端 Actions 34628912555 在无 private/、无 DataHub 环境中完成逐文件校验和原协议复算。

588000 的12,537行收益明细、1,802行覆盖明细与本地结果字节一致，2,128个汇总值复核一致。数据交付与复算已经完成，不要再次把清单当数据、要求用户传同一批文件或声称只能本地计算。

## 当前研究状态

`PARTIAL_CARRIER_TRANSPORT`

588000：保持原描述性结果；这次复现不是新增独立验证。

512100：文件已取得，但原协议未准入；2021有58,320个指数时钟记录，其中3,220个volume=0，55,100个volume>0，有效覆盖94.478738%<95%。按原240-bar完整事件/对照路径规则，配对覆盖率仅65.2778%（846/1,296），2021仅4.8387%。未计算它的收益。

源数据记零，不等于已经独立证明交易所真实无成交。本地源审计对此保留UNKNOWN。下一阶段在云端审查观测口径与数据语义，而不是修改门槛凑PASS。必要的外部核验应说明确切缺口，不默认要求本地重新交付已有数据。

## 云端复现

```bash
PYTHONPATH=src:. python -m pytest -q tests/test_r1a_*.py
PYTHONPATH=src:. python research/r1a_carrier_transport/verify_cloud_replay.py --output /tmp/r1a-cloud-acceptance-new
```

验收器要求新输出目录且无private/依赖。直接原协议回放：

```bash
PYTHONPATH=src:. python research/r1a_carrier_transport/transport.py \
  --manifest-dir data/r1a_carrier_prices/cloud_pack_v1 \
  --output /tmp/r1a-public-replay-new
```

PARTIAL的返回码2是预期研究状态，不是数据未上传或程序崩溃。

## 不可改变

保留原信号、事件与对照、指数时钟、完整七周期、95%年度门槛和80%配对门槛。不补零成交量、不删年份、不换ETF、不自动选择短周期。另行改变估计对象或采样方法，必须独立论证并冻结新协议，不能篡改v1历史。

不重开R1_B/R2或旧期权身份。不覆盖旧manifest/receipt。`BLACKBOX_query_count=3`，`production_authority=false`，`fresh_oos=false`。
