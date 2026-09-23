# METHOD.md — 10 分钟自行验证

> 原则：不采信本文任何数字，用你自己的账号复算。证据分级（实测/反演/推测）见 [REPORT.md](./REPORT.md) 开头约定。

## 3 步复现

1. **打开计费接口**：登录 kimi.com → F12 控制台；
2. **拉你自己的流水**：粘贴运行 [`scripts/pull_billing.js`](scripts/pull_billing.js)（读取 `localStorage.access_token`，调用 GetSubscriptionStats / ListBalanceActions，导出自己的计数器读数与全量扣费流水）；
3. **对照**：把流水按 `feature` 分组求和，与本报告同结构（Work/iFinD/Code/Search）对比。

## 进阶：费率卡复算

- Work 卡：`python3 scripts/fit_work_card.py`（14 方程 OLS + 区间交集）；
- Code 卡：`python3 scripts/fit_code_cache.py`（有机配对 OLS；精确复现需过滤 0.01% 取整点）；
- wire 提取：`python3 scripts/analyze_wire.py <wire.jsonl>`；
- 思考口径审计：`python3 scripts/audit_reasoning_anchor.py`。

## 可证伪点

- 连发微调用时官方计数器（`amountUsedRatio`）增量与流水同步（即跳动非零格数）→「后台无保底连续计费、流水为 ceil 伪影」的结论被推翻；
- 任何人复现 Code 缓存单价显著高于 [0.05, 0.09] 区间 → 缓存近免费结论被推翻；
- 官方公布费率卡与本报告不符 → 以官方为准，本报告勘误。

## 边界

本方法依赖网页会话内的内部接口，接口可能随时变更；仅测量你自己账号的数据。
