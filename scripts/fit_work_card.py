#!/usr/bin/env python3
"""Work 通道费率卡：受控实验区间交集 + OLS。
数据：data/work_controlled_table.json（W1-W7, T11 为单步点）。
模型：billed¥ = Pin*miss + Pc*cache + Pout*out；1% ≡ ¥10；网格 0.01% ⇒ 带 ±¥0.05。
输出：区间交集 + OLS 点解 + RMSE。"""
import json, itertools
d=json.load(open('data/work_controlled_table.json'))
rows=[r for r in d['rows'] if isinstance(r['miss'],int)]
def band(b): return (b-0.005)*10, (b+0.005)*10  # ¥
# 区间交集（粗网格搜索）
best=None
for pin in [x/10 for x in range(300,450)]:
    for pc in [x/100 for x in range(0,400)]:
        for pout in [x for x in range(240,300)]:
            ok=True
            for r in rows:
                lo,hi=band(r['billed_pct'])
                v=pin*r['miss']/1e6 + pc*r['cache']/1e6 + pout*r['out']/1e6
                if not (lo<=v<hi): ok=False; break
            if ok: best=(pin,pc,pout)
print('区间交集非空示例点:', best)
# OLS
import math
n=len(rows)
sx=lambda f: sum(f(r) for r in rows)
# 正规方程 3x3
A=[[sx(lambda r,a=a,b=b: r[a]*r[b]/1e12) for a in('miss','cache','out')] for b in('miss','cache','out')]
y=[(r['billed_pct'])*10 for r in rows]
B=[sx(lambda r,a=a: r[a]/1e6)*0 for a in('miss','cache','out')]
B=[sum(r[a]/1e6*(r['billed_pct']*10) for r in rows) for a in('miss','cache','out')]
# 高斯消元
M=[A[i]+[B[i]] for i in range(3)]
for c in range(3):
    p=max(range(c,3),key=lambda i:abs(M[i][c])); M[c],M[p]=M[p],M[c]
    for i in range(3):
        if i!=c:
            f=M[i][c]/M[c][c]
            for j in range(4): M[i][j]-=f*M[c][j]
sol=[M[i][3]/M[i][i] for i in range(3)]
rmse=math.sqrt(sum((sol[0]*r['miss']/1e6+sol[1]*r['cache']/1e6+sol[2]*r['out']/1e6-r['billed_pct']*10)**2 for r in rows)/n)
print(f'OLS: Pin=¥{sol[0]:.1f}/M  Pc=¥{sol[1]:.2f}/M  Pout=¥{sol[2]:.1f}/M  RMSE=¥{rmse:.4f}  n={n}')
