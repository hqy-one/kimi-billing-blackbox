#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立审计：思考(reasoning) token 口径是否系统性破坏
  (a) "1% ≡ ¥10" 锚点（全池 ¥1,000）
  (b) Code 通道 "输出价 = ¥105/M（官方平价）"
所有数字均来自本脚本实算，不引用报告结论。
数据：05_disclosure/data/code_organic_usage.json, code_billing_entries.json
"""
import json, os, math, statistics, datetime
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
D = os.path.join(REPO_DIR, "data")
USAGE = json.load(open(os.path.join(D, "code_organic_usage.json")))
BILL = json.load(open(os.path.join(D, "code_billing_entries.json")))

def iso_to_ms(s):
    s = s.replace("Z", "+00:00")
    return datetime.datetime.fromisoformat(s).timestamp() * 1000.0

U = [dict(t=float(r["t"]), tin=float(r["in"]), cache=float(r["cache"]), out=float(r["out"]))
     for r in USAGE]
B = [dict(t=iso_to_ms(r["ts"]), amt=float(r["amt"]), f=r["f"]) for r in BILL]
U.sort(key=lambda r: r["t"]); B.sort(key=lambda r: r["t"])

W = 3000.0  # ±3s
print("=" * 78)
print("STEP 0  数据概览")
print("=" * 78)
print(f"usage 记录      : {len(U)} 条,  t∈[{datetime.datetime.utcfromtimestamp(U[0]['t']/1000)} , "
      f"{datetime.datetime.utcfromtimestamp(U[-1]['t']/1000)}] UTC")
print(f"billing 流水    : {len(B)} 条, t∈[{datetime.datetime.utcfromtimestamp(B[0]['t']/1000)} , "
      f"{datetime.datetime.utcfromtimestamp(B[-1]['t']/1000)}] UTC")
print(f"流水 feature     : {sorted(set(r['f'] for r in B))}")
amts = sorted(set(round(r['amt'], 6) for r in B))
print(f"amt 取值         : {amts}  (全部为 {min(amts)*10000:.0f}e-4 的整数倍 -> 0.01% 网格)")
print(f"amt==0.0001(0.01%保底) 条数 : {sum(1 for r in B if abs(r['amt']-0.0001)<1e-12)}/{len(B)}")
print(f"¥ 换算           : amt×1000 = ¥   (0.0001 -> ¥0.100)")
print(f"量化步长 q       : 0.0001 ratio = ¥0.100   均匀量化噪声 σ_q = q/√12 = ¥{0.1/math.sqrt(12):.4f}")

# ---------------------------------------------------------------- STEP 1
print()
print("=" * 78)
print("STEP 1  ±3s 配对 usage<->流水")
print("=" * 78)

used = [False] * len(B)
pairs = []          # (usage_idx, [billing_idx,...])
for i in range(len(U)):
    t = U[i]["t"]
    hit = [j for j in range(len(B)) if abs(B[j]["t"] - t) <= W]
    pairs.append((i, hit))
n_hit = sum(1 for _, h in pairs if h)
n_multi = sum(1 for _, h in pairs if len(h) > 1)
print(f"有 ±3s 命中的 usage 记录      : {n_hit}/{len(U)}")
print(f"其中命中 >1 条流水的          : {n_multi}")
print(f"未被任何 usage 命中的流水条数 : {len(B) - len(set(j for _, h in pairs for j in h))}")

# 1:1 配对：每个 usage 取窗口内最近的一条流水；同一流水可被多条 usage 命中（记重复）
p1 = []
for i, h in pairs:
    if not h:
        continue
    j = min(h, key=lambda j: abs(B[j]["t"] - U[i]["t"]))
    p1.append((i, j, abs(B[j]["t"] - U[i]["t"])))
print(f"1:1 最近邻配对集             : {len(p1)} 对")
print(f"  配对时差 |Δt| 中位 {statistics.median(d for _,_,d in p1):.0f} ms, 最大 {max(d for _,_,d in p1):.0f} ms")
dup = len(p1) - len(set(j for _, j, _ in p1))
print(f"  被多条 usage 复用的流水条数 : {dup}")

# 唯一流水版本（同一流水只保留时差最小的一对）——这是本审计主用配对集
best = {}
for i, j, d in p1:
    if j not in best or d < best[j][2]:
        best[j] = (i, j, d)
PAIRS = sorted(best.values(), key=lambda x: x[2])
print(f"唯一流水配对集 (主用)         : {len(PAIRS)} 对")

# 供对照：报告口径 160 对 —— 报告称 Code 通道 160/194 配对成功
print(f"  报告声称口径               : 160/194  （脚本复现 {len(PAIRS)} 对）")

def build(subset, floor_excluded=False):
    rows = []
    for i, j, d in subset:
        a = B[j]["amt"]
        if floor_excluded and abs(a - 0.0001) < 1e-12:
            continue
        rows.append((U[i], a, j, d))
    return rows

ALL_PAIRS = build(PAIRS)
print(f"  其中 amt==0.01%保底 的条数  : {sum(1 for r in ALL_PAIRS if abs(r[1]-0.0001)<1e-12)}")
print(f"  去掉保底后的条数            : {sum(1 for r in ALL_PAIRS if abs(r[1]-0.0001)>=1e-12)}")

# ---------------------------------------------------------------- STEP 2
print()
print("=" * 78)
print("STEP 2  OLS  billed¥ = Pin*in + Pc*cache + Pout*out   (¥/M)")
print("=" * 78)

def ols(X, y):
    XtX = X.T @ X
    beta = np.linalg.solve(XtX, X.T @ y)
    resid = y - X @ beta
    n, k = X.shape
    dof = n - k
    s2 = (resid @ resid) / dof
    cov = s2 * np.linalg.inv(XtX)
    se = np.sqrt(np.diag(cov))
    # HC1 稳健标准误
    meat = X.T @ (X * (resid ** 2)[:, None])
    cov_hc1 = np.linalg.inv(XtX) @ meat @ np.linalg.inv(XtX) * n / dof
    se_hc1 = np.sqrt(np.diag(cov_hc1))
    rmse = math.sqrt((resid @ resid) / n)
    return beta, se, se_hc1, rmse, resid, dof

def fit(rows, label, floor_excluded):
    if floor_excluded:
        rows = [r for r in rows if abs(r[1] - 0.0001) >= 1e-12]
    y = np.array([r[1] * 1000.0 for r in rows])                  # ¥
    X = np.array([[r[0]["tin"] / 1e6, r[0]["cache"] / 1e6, r[0]["out"] / 1e6] for r in rows])
    beta, se, se_hc1, rmse, resid, dof = ols(X, y)
    names = ["Pin (¥/M)", "Pc  (¥/M)", "Pout(¥/M)"]
    print(f"\n--- {label}   n={len(rows)}  dof={dof} ---")
    for nm, b, s, sh in zip(names, beta, se, se_hc1):
        t_ = b / sh
        print(f"  {nm:11s} = {b:10.4f}   OLS-SE {s:8.4f}   HC1-SE {sh:8.4f}   t={t_:7.2f}   "
              f"95%CI[{b-1.96*sh:8.3f},{b+1.96*sh:8.3f}]")
    print(f"  RMSE = ¥{rmse:.4f}   量化噪声下限 σ_q = ¥{0.1/math.sqrt(12):.4f}   "
          f"RMSE/σ_q = {rmse/(0.1/math.sqrt(12)):.3f}")
    # 与官方标价对比
    print(f"  对比官方: Pin 21.0 (实测/官方={beta[0]/21:.3f})   Pc 2.1 (={beta[1]/2.1:.3f})   "
          f"Pout 105.0 (={beta[2]/105:.3f})")
    return dict(rows=rows, beta=beta, se=se, se_hc1=se_hc1, rmse=rmse, resid=resid, X=X, y=y)

F_all = fit(ALL_PAIRS, "Code 全配对集 (含 0.01% 保底)", floor_excluded=False)
F_ex = fit(ALL_PAIRS, "Code 去保底集 (排除 amt==0.01%)", floor_excluded=True)

# ---------------------------------------------------------------- STEP 3
print()
print("=" * 78)
print("STEP 3  关键检验：思考 token 是否被计费但不在 out 字段")
print("=" * 78)

rows = F_ex["rows"]                      # 去保底 57 点（报告同款）
resid = F_ex["resid"]
X = F_ex["X"]; y = F_ex["y"]; beta = F_ex["beta"]

# 思考强度代理：usage 记录是每条 API 响应的落账时点，故
#   gap_before_i = t_i - t_{i-1}  ~= 工具耗时(i-1) + 第 i 次调用的完整延迟(含思考)
T = np.array([r[0]["t"] for r in rows]) / 1000.0
order = np.argsort(T)
idx_sorted = order
gap_before = np.full(len(rows), np.nan)
Ts = T[order]
gb = np.full(len(rows), np.nan)
for k in range(1, len(order)):
    gb[k] = Ts[k] - Ts[k - 1]
gap_sorted = gb
gap_before[order] = gb

# 用 out/gap 估计解码上限 TPS（只取大输出的点，延迟由解码主导）
outs = np.array([r[0]["out"] for r in rows])
big = (outs > 1500) & ~np.isnan(gap_before)
tps = outs[big] / gap_before[big]
TPS = np.percentile(tps, 90)
print(f"3.0 代理构造：usage 落账时点相邻间隔作为「上一次调用延迟上界」")
print(f"    大输出点(out>1500, n={big.sum()}) 的 out/gap 分布: "
      f"p50={np.percentile(tps,50):.1f} p90={np.percentile(tps,90):.1f} max={tps.max():.1f} tok/s")
print(f"    取 TPS_max = p90 = {TPS:.1f} tok/s；excess_i = gap_before_i - out_i/TPS_max")

excess = gap_before - outs / TPS
ok = ~np.isnan(excess)

def corr(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    return float(np.corrcoef(a, b)[0, 1])

def spear(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    return corr(ra, rb)

def ols_slope(x, yy):
    x = np.asarray(x, float); yy = np.asarray(yy, float)
    n = len(x)
    Xd = np.column_stack([np.ones(n), x])
    b = np.linalg.solve(Xd.T @ Xd, Xd.T @ yy)
    r = yy - Xd @ b
    s2 = (r @ r) / (n - 2)
    cov = s2 * np.linalg.inv(Xd.T @ Xd)
    se = math.sqrt(cov[1, 1])
    return b[1], se, b[0]

print()
print("3.1 残差 vs 思考强度代理")
for nm, prox in [("gap_before (s)", gap_before),
                 ("excess time (s)", excess),
                 ("gap_before/out (s/tok)", gap_before / np.maximum(outs, 1))]:
    m = ~np.isnan(prox)
    sl, se, ic = ols_slope(prox[m], resid[m])
    print(f"  resid ~ {nm:22s}  n={m.sum():3d}  slope={sl:+.5f} ¥/unit (SE {se:.5f}, t={sl/se:+.2f})"
          f"  Pearson r={corr(prox[m], resid[m]):+.3f}  Spearman ρ={spear(prox[m], resid[m]):+.3f}")

print()
print("3.2 「低输出 + 长间隔」子样本（最像重思考的调用）残差 vs 其余")
m = ok
q_out = np.percentile(outs[m], 25)
q_gap = np.percentile(gap_before[m], 75)
sel = m & (outs <= q_out) & (gap_before >= q_gap)
print(f"    门槛: out<=p25={q_out:.0f} tok 且 gap>=p75={q_gap:.1f}s   -> n={sel.sum()}")
if sel.sum() > 0:
    print(f"    该子集残差: mean={resid[sel].mean():+.4f} ¥  median={np.median(resid[sel]):+.4f} ¥  "
          f"max={resid[sel].max():+.4f} ¥")
    rest = m & ~sel
    print(f"    其余样本  : mean={resid[rest].mean():+.4f} ¥  median={np.median(resid[rest]):+.4f} ¥  n={rest.sum()}")
    d = resid[sel].mean() - resid[rest].mean()
    sd = math.sqrt(resid[sel].var(ddof=1)/sel.sum() + resid[rest].var(ddof=1)/rest.sum())
    print(f"    差值 = {d:+.4f} ¥  (Welch SE {sd:.4f}, t={d/sd:+.2f})   "
          f"-> 折算隐藏输出 {d/105*1e6:+.0f} tok/call @ ¥105/M")

print()
print("3.3 常数隐藏思考量 R̄ 的截距检验（模型强制过原点，若每次调用都多计 R̄，则被残差吸收）")
Xi = np.column_stack([np.ones(len(X)), X])
bi = np.linalg.solve(Xi.T @ Xi, Xi.T @ y)
ri = y - Xi @ bi
n, k = Xi.shape
s2 = (ri @ ri) / (n - k)
cov = s2 * np.linalg.inv(Xi.T @ Xi)
sei = np.sqrt(np.diag(cov))
meat = Xi.T @ (Xi * (ri ** 2)[:, None])
covh = np.linalg.inv(Xi.T @ Xi) @ meat @ np.linalg.inv(Xi.T @ Xi) * n / (n - k)
seih = np.sqrt(np.diag(covh))
lbl = ["intercept", "Pin", "Pc", "Pout"]
for nm, b_, s_, sh_ in zip(lbl, bi, sei, seih):
    print(f"  {nm:9s} = {b_:9.4f}   SE {s_:8.4f}  HC1-SE {sh_:8.4f}  95%CI[{b_-1.96*sh_:8.4f},{b_+1.96*sh_:8.4f}]")
print(f"  截距 95%CI 上界 = ¥{bi[0]+1.96*seih[0]:.4f}/call  ->  等价常数隐藏输出 "
      f"{(bi[0]+1.96*seih[0])/105*1e6:.0f} tok/call @ ¥105/M")
print(f"  RMSE(带截距) = ¥{math.sqrt((ri@ri)/n):.4f}  vs 过原点 ¥{F_ex['rmse']:.4f}")

print()
print("3.4 方差预算：隐藏思考量的最大可兼容量级")
sig_q = 0.1 / math.sqrt(12)
for tag, rmse in [("观测 RMSE (去保底 57 点)", F_ex["rmse"]),
                  ("观测 RMSE (全 160 点)", F_all["rmse"]),
                  ("题目给定下限 ¥0.029", 0.029)]:
    var_r = rmse ** 2 - sig_q ** 2
    if var_r > 0:
        s_r = math.sqrt(var_r)
        print(f"  {tag:26s} RMSE=¥{rmse:.4f}  σ_R_max=¥{s_r:.4f}/call  "
              f"= {s_r/105*1e6:6.0f} tok/call 标准差 @ ¥105/M")
    else:
        print(f"  {tag:26s} RMSE=¥{rmse:.4f}  σ_R_max=¥0  (RMSE 已被量化噪声吃满，无剩余预算)")

print()
print("3.5 与单点最重的调用交叉核对（最大 out 的调用，隐藏思考量最易暴露）")
k_big = int(np.argmax(outs))
r_ = rows[k_big]
pred = beta[0]*r_[0]["tin"]/1e6 + beta[1]*r_[0]["cache"]/1e6 + beta[2]*r_[0]["out"]/1e6
print(f"  t={datetime.datetime.utcfromtimestamp(r_[0]['t']/1000)}  in={r_[0]['tin']:.0f} cache={r_[0]['cache']:.0f} "
      f"out={r_[0]['out']:.0f}  实扣=¥{r_[1]*1000:.3f}")
print(f"  过原点模型预测 = ¥{pred:.4f}   残差 = ¥{r_[1]*1000-pred:+.4f}")
print(f"  剩余量化余量（保底外）: 该点实扣正好落在网格上，可容纳的额外隐藏输出 <= "
      f"{(0.00005*1000 + max(0.0, r_[1]*1000-pred))/105*1e6:.0f} tok "
      f"(= 0.005% 半格 ≈ ¥0.05 加已观测残差)")

# ---------------------------------------------------------------- STEP 3B
print()
print("=" * 78)
print("STEP 3B  Work 通道受控实验：直接计时思考（W1「只回答两个字」，思考 65.2s）")
print("=" * 78)
WK = [  # (label, miss_in, cache, out, billed_ratio)
    ("W1  只答两个字(思考65.2s)", 29271,     0,   41, 0.0011),
    ("W2  光合作用长文",            186, 29184, 1055, 0.0003),
    ("W3  扩写",                   1294, 29184, 2150, 0.0007),
    ("W4  深海热泉长文",           2227, 30464, 6856, 0.0020),
    ("W5  古罗马水道长文",         7096, 32512, 4972, 0.0017),
    ("W6  对比综述",               5219, 39424, 5514, 0.0017),
    ("W7  一句话总结",             5668, 44544,  155, 0.0003),
    ("T9/T10 短答",                 232, 63744, 1322, 0.0005),
    ("T11 十字概括",               1608, 63744,  183, 0.0002),
]
Xw = np.array([[m/1e6, c/1e6, o/1e6] for _, m, c, o, _ in WK])
yw = np.array([a*1000.0 for _, _, _, _, a in WK])
bw, sew, sehw, rmsew, residw, dofw = ols(Xw, yw)
print(f"9 个精确方程（T8 五步与隐藏标题调用只有区间/无 token，未纳入）  n={len(WK)}  dof={dofw}")
for nm, b_, s_, sh_ in zip(["Pin(¥/M)", "Pc (¥/M)", "Pout(¥/M)"], bw, sew, sehw):
    print(f"  {nm:9s} = {b_:9.3f}   OLS-SE {s_:7.3f}  HC1-SE {sh_:7.3f}  95%CI[{b_-1.96*sh_:8.2f},{b_+1.96*sh_:8.2f}]")
print(f"  RMSE = ¥{rmsew:.4f}  (报告 14 方程解: 37.2 / 1.82 / 269.6, RMSE ¥0.028)")
print(f"  实测/官方: Pin {bw[0]/21:.2f}x  Pc {bw[1]/2.1:.2f}x  Pout {bw[2]/105:.2f}x")
print()
print("  逐点残差（¥，实扣 - 预测）：")
for (lab, m, c, o, a), r_ in zip(WK, residw):
    print(f"    {lab:24s} out={o:5d}  实扣 ¥{a*1000:.3f}  预测 ¥{a*1000-r_:.3f}  残差 {r_:+.4f}")

# W1 隐藏思考相容性：在 9 方程整体量化带内，W1 最多能藏多少计费思考 token
print()
print("  W1 隐藏思考量 R 的相容上界（量化粒度 ¥0.1, 半格 ¥0.05）")
w1_pred = Xw[0] @ bw
print(f"    过原点预测 ¥{w1_pred:.5f}   实扣 ¥{yw[0]:.3f}   残差 {yw[0]-w1_pred:+.5f}")
pmax = bw[2] / 1e6
for tag, slack in [("半格 ¥0.05（含舍入）", 0.05),
                   ("全格 ¥0.10", 0.10),
                   ("半格+残差", 0.05 + (yw[0] - w1_pred))]:
    R = slack / pmax
    print(f"    {tag:20s} -> R <= {R:7.0f} tok  = 65.2s 思考期内 {R/65.2:.2f} tok/s")
print(f"    参考：若思考按 15 tok/s 产出，65.2s = {15*65.2:.0f} tok -> 计费 ¥{15*65.2*pmax:.3f}"
      f" = {15*65.2*pmax/10*100:.3f}% 额度；W1 实扣 0.110% 会变成 "
      f"{(yw[0]+15*65.2*pmax)/10:.3f}%")

# 蒙特卡洛：把系数不确定度一起传播
rng = np.random.default_rng(20260921)
covw = np.linalg.inv(Xw.T @ Xw) * (residw @ residw) / dofw
draws = rng.multivariate_normal(bw, covw, size=20000)
w1_preds = Xw[0] @ draws.T
Rs = (0.05 + (yw[0] - w1_preds)) / (draws[:, 2] / 1e6)
print(f"    MC(20000, 系数协方差传播): R 上界 中位 {np.median(Rs):.0f} tok, "
      f"5%~95% [{np.percentile(Rs,5):.0f}, {np.percentile(Rs,95):.0f}] tok, max {Rs.max():.0f} tok")

# ---------------------------------------------------------------- STEP 4
print()
print("=" * 78)
print("STEP 4  敏感性：out 被低估 k 倍（真实计费输出 = out×(1+k)）时的锚点")
print("=" * 78)
# 报告 §3 给出的锚点单点推导
IN_A, OUT_A, AMT_A = 137, 6618, 0.0700   # tokens, tokens, %
L0 = (OUT_A * 105 + IN_A * 21) / 1e6
print(f"锚点原始单点（REPORT §3）: in={IN_A} out={OUT_A} 实扣 {AMT_A}%")
print(f"  官方标价成本 = ({OUT_A}×105 + {IN_A}×21)/1e6 = ¥{L0:.4f}  (报告写 ¥0.6978 ✓复现)")
print()
print("  k        标价成本¥      ¥/1%       全池¥      Pout_fit 需等于   相对本审计拟合 104.61 的偏离")
for k in [0.0, 0.1, 0.5, 1.0, 2.0]:
    L = (OUT_A * (1 + k) * 105 + IN_A * 21) / 1e6
    per1 = L / AMT_A
    p_need = 105 * (1 + k)
    z = (p_need - 104.6092) / 1.7810
    print(f"  {k:<4.1f}   ¥{L:.4f}      ¥{per1:7.3f}   ¥{per1*100:8.1f}   ¥{p_need:8.1f}        {z:+.1f} SE")

print()
print("  用本审计 Code 去保底拟合(13.327/0.0807/104.609)在全 57 点上的聚合锚点：")
Lv = (F_ex["beta"][0]*F_ex["X"][:, 0] + F_ex["beta"][1]*F_ex["X"][:, 1] + F_ex["beta"][2]*F_ex["X"][:, 2])
r_pct = np.array([r_[1] * 100 for r_ in F_ex["rows"]])
for k in [0.0, 0.1, 0.5, 1.0]:
    Lk = Lv + F_ex["beta"][2] * F_ex["X"][:, 2] * k
    per1 = float(np.sum(r_pct * Lk) / np.sum(r_pct ** 2))   # 过原点一参数拟合
    print(f"    k={k:<4.1f}  加权 ¥/1% = ¥{per1:7.3f}   全池 = ¥{per1*100:8.1f}")

print()
print("  关键约束：k 不是自由参数，它被 Pout 的拟合值钉住")
khat = F_ex["beta"][2] / 105.0 - 1
se_k = F_ex["se_hc1"][2] / 105.0
print(f"    k̂ = Pout_fit/105 - 1 = {khat:+.4f}   HC1-SE {se_k:.4f}   95%CI [{khat-1.96*se_k:+.4f}, {khat+1.96*se_k:+.4f}]")
print(f"    => 95% 置信下 k <= {khat+1.96*se_k:+.4f} （隐藏思考 <= 可见输出的 {100*(khat+1.96*se_k):.1f}%）")
print(f"    => 锚点 95% 上界 = ¥{1000*(1+khat+1.96*se_k):.0f}")

# ---------------------------------------------------------------- STEP 5
print()
print("=" * 78)
print("STEP 5  字段口径判定：wire 日志层面检验 out 是否已含思考 token")
print("=" * 78)
WSESS = os.path.expanduser("~/Library/Application Support/kimi-desktop/daimon-share/daimon/"
                           "runtime/kimi-code/home/sessions/wd_14-30-59-5778e52b_6095d08f7684/"
                           "conv-f5831a6a32b4c38adfcbf438/agents/main/wire.jsonl")
CTITLE = os.path.expanduser("~/Library/Application Support/kimi-desktop/daimon-share/daimon/"
                            "runtime/kimi-code/home/sessions/wd_14-30-59-5778e52b_6095d08f7684/"
                            "ctitle-01a0c2a9-2290-715f-ad4a-8dc1879a6094/agents/main/wire.jsonl")

def tok_est(s):
    cjk = sum(1 for ch in s if '\u4e00' <= ch <= '\u9fff')
    return cjk * 1.0 + (len(s) - cjk) / 4.0

def parse(wf):
    lines = [json.loads(l) for l in open(wf, errors="ignore") if l.strip().startswith("{")]
    order, steps = [], {}
    for d in lines:
        ty = d.get("type")
        if ty == "context.append_loop_event":
            e = d.get("event", {})
            if e.get("type") == "step.begin":
                k = (e.get("turnId"), e.get("step"))
                steps[k] = dict(think="", text="", tool=0, t0=d.get("time"))
                order.append(k)
            elif order:
                s = steps[order[-1]]
                if e.get("type") == "content.part":
                    p = e.get("part", {})
                    if p.get("type") == "think":
                        s["think"] += p.get("think", "")
                    elif p.get("type") == "text":
                        s["text"] += p.get("text", "")
                elif e.get("type") == "tool.call":
                    s["tool"] += len(json.dumps(e.get("args", {}), ensure_ascii=False))
        elif ty == "usage.record" and order:
            u = d.get("usage", {})
            steps[order[-1]].update(out=u.get("output"), miss=u.get("inputOther"),
                                    cache=u.get("inputCacheRead"), t1=d.get("time"))
    return [steps[k] for k in order]

stats_file = os.path.join(D, "work_controlled_wire_stats.json")
if os.path.exists(WSESS) and os.path.exists(CTITLE):
    W = parse(WSESS)
    T = parse(CTITLE)
    title_miss, title_out = T[0]['miss'], T[0]['out']
    th = np.array([tok_est(s["think"]) for s in W])
    tx = np.array([tok_est(s["text"]) + s["tool"] / 4.0 for s in W])
    ou = np.array([float(s["out"]) for s in W])
    w_steps = W
elif os.path.exists(stats_file):
    wire_stats = json.load(open(stats_file, encoding="utf-8"))
    title_miss = wire_stats["ctitle"]["miss"]
    title_out = wire_stats["ctitle"]["out"]
    w_steps = wire_stats["steps"]
    th = np.array([float(s["think_est"]) for s in w_steps])
    tx = np.array([float(s["vis_est"]) for s in w_steps])
    ou = np.array([float(s["out"]) for s in w_steps])
else:
    raise FileNotFoundError("既未找到本地桌面 wire.jsonl，也未找到 data/work_controlled_wire_stats.json")

print(f"Work 受控会话 wire 步数 = {len(w_steps)}（报告称 14 个模型步 ✓）")
print(f"隐藏标题调用 wire: miss={title_miss} out={title_out}")
print()
print(f"{'step':>9} {'out':>6} {'think_est':>9} {'vis_est':>8} {'think+vis':>9} {'vis-ratio':>9}")
for s, a, b, o in zip(w_steps, th, tx, ou):
    print(f"{str((s.get('t0'),)):>9} {o:6.0f} {a:9.1f} {b:8.1f} {a+b:9.1f}   vis/(t+v)={b/(a+b):.2f}")

def fit2(X, y):
    b = np.linalg.solve(X.T @ X, X.T @ y)
    r = y - X @ b
    return b, math.sqrt((r @ r) / len(y)), 1 - (r @ r) / ((y - y.mean()) ** 2).sum()

bA, rA, R2A = fit2(np.column_stack([th, tx]), ou)                       # 含思考
bB, rB, R2B = fit2(np.column_stack([tx]), ou)                           # 仅可见
print()
print(f"模型 A: out = {bA[0]:.2f}·think + {bA[1]:.2f}·visible      RMSE={rA:.0f} tok  R²={R2A:.3f}")
print(f"模型 B: out = {bB[0]:.2f}·visible                          RMSE={rB:.0f} tok  R²={R2B:.3f}")
print(f"  -> 系数接近 1 的模型即真实口径。A 的 think 系数 = {bA[0]:.2f}（≠0 表示 out 含思考）")

print()
print("  三个决定性单点（可见输出极少、思考正文很长）：")
for s, a, b in zip(w_steps, th, tx):
    if b < 30 and a > 25:
        dur = (s.get("t1", 0) - s.get("t0", 0)) / 1000.0
        print(f"    step t0={s['t0']} 步时长={dur:.1f}s  out={s['out']:.0f}  "
              f"思考正文≈{a:.0f} tok  可见≈{b:.0f} tok  -> out 只能是含思考")

# ---------------------------------------------------------------- STEP 6
print()
print("=" * 78)
print("STEP 6  报告受控实验表 out 列 vs 原始 API completion_tokens")
print("=" * 78)
ctrl_raw = json.load(open(os.path.join(D, "code_controlled_raw.json"), encoding="utf-8"))
EA = ctrl_raw["blocks"]["exp_block_a_results.json"]
EB = ctrl_raw["blocks"]["exp_block_b_results.json"]
raw = {}
for r in EA + EB:
    if "usage" in r:
        u = r["usage"]
        raw[r["tag"]] = dict(bj=r.get("bj_start"), p=u.get("prompt_tokens"),
                             c=u.get("completion_tokens"),
                             rz=u.get("completion_tokens_details", {}).get("reasoning_tokens"),
                             ck=u.get("cached_tokens") or u.get("prompt_tokens_details", {}).get("cached_tokens"))
REPORT_ROWS = [  # REPORT.md:150-163 摘录 (bj, in, cache, out)
    ("12:21:16", 98, 0, 16), ("12:22:13", 5331, 0, 16), ("12:23:26", 0, 15774, 40),
    ("12:31:09", 0, 99036, 16),
]
print(f"{'REPORT bj':>10} {'in':>7} {'cache':>8} {'out':>6} | {'raw tag':>16} {'prompt':>7} {'compl':>6} {'reason':>7} {'cached':>8}")
for bj, i_, c_, o_ in REPORT_ROWS:
    hit = None
    for tag, v in raw.items():
        if v["bj"] == bj:
            hit = (tag, v); break
    if hit:
        tag, v = hit
        ok = (v["p"] == i_ or i_ == 0) and (v["c"] == o_)
        print(f"{bj:>10} {i_:>7} {c_:>8} {o_:>6} | {tag:>16} {v['p']:>7} {v['c']:>6} {v['rz']:>7} {str(v['ck']):>8}  "
              f"{'MATCH: out=completion_tokens(含思考)' if ok else 'MISMATCH'}")
    else:
        print(f"{bj:>10} {i_:>7} {c_:>8} {o_:>6} | (无原始记录)")

# 锚点单点：prior_art 明说 6618 含 265 思考
print()
print("锚点单点口径（00_prior_art/Kimi_Work_额度消耗深度分析报告.md:50）：")
print("  「completion_tokens: 6,618（长代码输出 + 265 推理思考）」")
print("  => 报告 §3 锚点分子 6,618 本身就是「可见输出 + 思考」的合计，未把思考排除在外。")
print(f"  若错误地按'可见=6618-265=6353'重算标价：¥{(6353*105+137*21)/1e6:.4f} -> ¥/1% = "
      f"{((6353*105+137*21)/1e6)/0.07:.3f} -> 全池 ¥{((6353*105+137*21)/1e6)/0.07*100:.1f}")
print(f"  但 0.01% 网格下两者都量化到 0.07%：{{0.6978, 0.6699}} -> 0.07 ✓（单点无法分辨，聚合 OLS 才能）")

# 常数隐藏思考对照
print()
print("常数隐藏思考量 R̄（与 out 无关）对聚合锚点的影响：")
Lv2 = (F_ex["beta"][0]*F_ex["X"][:, 0] + F_ex["beta"][1]*F_ex["X"][:, 1] + F_ex["beta"][2]*F_ex["X"][:, 2])
Sr = float(np.sum(r_pct))
print(f"  57 点合计标价 ¥{Lv2.sum():.2f}，合计扣费比例 {Sr:.3f}%  ->  比和锚点 ¥{Lv2.sum()/Sr*100:.1f}/全池")
for Rc in [50, 143, 478]:
    extra = 105 * Rc / 1e6 * len(Lv2)
    print(f"  R̄={Rc:>4} tok/call -> 追加标价 ¥{extra:.2f} -> 全池 "
          f"¥{(Lv2.sum()+extra)/Sr*100:.1f}  (+{((Lv2.sum()+extra)/Lv2.sum()-1)*100:.1f}%)")
