# Kimi 会员计费黑箱实测

> **被计费的模型，测量了计费它自己的系统。**
> 本仓库全部测量与主报告由 Kimi K3 模型在 DeepSeek Harness 中执行完成（校准证书 No. 2026-0921-K3）。

## 📊 先看这个 → [可视化数据看板](https://hqy-one.github.io/kimi-billing-blackbox/)（[PDF 版](kimi-billing-certificate.pdf)）

Kimi Allegretto（¥199/月）只给用户一根百分比进度条。2026-09-21，我们把它逆向成了价目表。

| 发现 | 数值 |
|---|---|
| 月度额度池锚点（实测推算） | 100% ≡ 官方 API 标价 **¥1,000**（1% ≡ ¥10） |
| 同一 K3 模型的双通道缓存价差 | **≈22×**（Code ¥0.08/M vs Work ¥1.82/M） |
| Work 通道输出加价 | **2.6×** 官方 API 价 |
| 一次 41.9 分钟 Work 任务的消耗 | **≈19.5%** 月度额度（官方自估同类任务 5–10%） |

## 文档

- **[REPORT.md](REPORT.md)** — 主报告 v2.3（结论、证据、行业坐标、免责声明）
- **[TECHNICAL.md](TECHNICAL.md)** — 技术附录（拟合方法与推导，数值以 REPORT 为准）
- **[METHOD.md](METHOD.md)** — 10 分钟自行验证（拉你自己的计费流水）
- `data/` — 脱敏数据（仅时间戳/token 数/百分比）｜ `scripts/` — 复现脚本 ｜ `research/` — 外部事实核验与两轮独立审计记录（DeepSeek V4.1 Flash）

## 免责

个人消费计量研究：所有数值为 2026-09-21 单账号实测推算，非官方口径，不构成指控。接口路径此前已有社区记录；我们的增量是受控实验费率卡、双通道发现与口径校准。详见 [REPORT.md](REPORT.md) 免责节。

---

**EN**: Black-box measurement of Kimi (Moonshot AI) membership billing, performed by the Kimi K3 model itself inside DeepSeek Harness. **[View the dashboard](https://hqy-one.github.io/kimi-billing-blackbox/)** — findings, rate cards, and replication guide inside. Single-account single-day estimates, not accusations.

## License

文档与数据 CC-BY-4.0 ｜ 脚本 MIT
