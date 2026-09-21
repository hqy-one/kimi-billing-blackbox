# Kimi 会员计费黑箱实测 · Measuring Kimi's Membership Billing Black Box

**校准证书 No. 2026-0921-K3** — 被计费的模型，测量了计费它自己的系统。

本仓库的全部测量与主报告由 **Kimi K3 模型**（k3-agent）在 DeepSeek Harness 代理框架中亲自执行完成；受控实验的人类协助与审校由一位付费用户完成；外部价格事实核验由 DeepSeek V4.1 Flash 完成。

## 这是什么

Kimi Allegretto（¥199/月）会员只给用户一根 0~100% 的百分比进度条。官方公布档位间的相对倍率与粗略任务数估算，但不公布额度池的绝对大小、人民币折算与分项费率。

2026-09-21，我们把这根进度条逆向成了价目表：**18 个 Code 受控调用 + 2 个有机验证点 + 14 个 Work 受控回合 + 160 对有机调用秒级配对 + 995 条计费流水**。

## 核心发现

| 发现 | 数值 |
|---|---|
| 月度额度池锚点（实测推算） | 100% ≡ 官方 API 标价 **¥1,000**（1% ≡ ¥10） |
| 同一 K3 模型的双通道缓存价差 | **22×**（Code ≈¥0.08/M vs Work ¥1.82/M） |
| Work 通道输出加价 | **2.6×** 官方 API 价 |
| 一次 41.9 分钟 Work 任务的消耗 | **≈19.5%**（官方计数器口径；官方自估同类任务 5–10%） |

双口径说明：本报告所有 "¥" 金额为**标价口径**（池内记账单位，= 官方 API 标价折算），用户实付为固定 ¥199/月。

## 内容导航

- **`index.html`** — 计量校准证书式数据看板（单文件，浏览器直接打开）
- **`REPORT.md`** — 主报告 v2.3（结论、证据分级、行业坐标、免责声明）
- **`TECHNICAL.md`** — 详细技术分析（拟合方法、区间推导、量化机制）
- **`METHOD.md`** — 10 分钟复现指南（拉取你自己的计费流水）
- **`data/`** — 可脱敏原始数据子集与计数器快照（仅时间戳、token 数、百分比；会话原文等不可脱敏资产保留在本地）
- **`scripts/`** — 复现脚本
- **`research/`** — 外部事实核验记录（DeepSeek V4.1 Flash 执行）

## 免责声明

本仓库为**个人消费计量研究**：所有"费率/价格"均为 2026-09-21 当日、单一账号、单次会话的实测推算值，非官方口径；计费系统可能随时调整；不构成对任何主体的指控。详见 REPORT.md 免责节。

## English Summary

A black-box measurement of Kimi (Moonshot AI) Allegretto membership billing, performed by the Kimi K3 model itself inside DeepSeek Harness. We reverse-engineered the internal rate cards (reasoning tokens verified included in billed output) of the opaque monthly quota pool: pool anchor ¥1,000 (API list price), a 22× cache-price gap between the Code and Work channels for the same model, 2.6× output markup in Work, 0.01% quantization grid with ¥0.10 floor, and a per-conversation ≈0.11% "boot fee". All data sanitized and included; replication guide in METHOD.md. Findings are single-account, single-day measurements — estimates, not accusations.

## License

文档与数据 [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/)；脚本 [MIT](https://opensource.org/licenses/MIT)。
