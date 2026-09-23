# data/ — 数据说明

| 文件 | 内容 | 来源 |
|---|---|---|
| `ledger_2026-09-21.json` | 当日全部 995 条订阅扣费流水（ts/feature/amountRatio） | ListBalanceActions API |
| `counter_snapshots.json` | 官方计数器读数快照（19.5%/22.22%/25.35%/2.26%），各标注来源 | GetSubscriptionStats / 用户侧截图 |
| `morning_work_usage.json` | 上午 Work 任务 254 条去重 usage 记录（1ms 容差去重） | wire.jsonl 提取 |
| `work_billing_pairs.json` | 234 对 Work usage↔流水配对 | 秒级时间戳配对 |
| `work_controlled_table.json` | Work 受控实验 11 行表（转录自 REPORT §5.5） | 受控实验 |
| `work_controlled_billing.json` | 其中前 8 个观测的原始流水条目（其余在主流水中） | ListBalanceActions |
| `code_organic_usage.json` | 194 条 Code 有机调用 usage | DSH 会话日志 |
| `code_billing_entries.json` | 225 条 Code 通道流水 | ListBalanceActions |
| `code_controlled_raw.json` | Code 受控实验块 A/B/D 原始记录 | 02_experiments |
| `work_controlled_wire_stats.json` | Work 受控实验 14 步 wire 统计指标（时间戳/token 纯数值，无文本） | 审计脚本复算支撑 |

**未发布**：wire.jsonl 原文（含任务内容，不可脱敏）与调研目录其余工作文件；usage/流水已提取为上述无内容字段的子集。
