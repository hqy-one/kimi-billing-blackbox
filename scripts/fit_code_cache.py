#!/usr/bin/env python3
"""Code 通道缓存价：有机调用 usage↔流水 ±3s 配对 + OLS。
数据：data/code_organic_usage.json（t, in, cache, out）+ data/code_billing_entries.json（ts, amt）。
用法：python3 scripts/fit_code_cache.py"""
import json, datetime
def ue(s): return datetime.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
U=json.load(open('data/code_organic_usage.json'))
B=json.load(open('data/code_billing_entries.json'))
pairs=[]
for u in U:
    t0=u['t']
    t=ue(t0) if isinstance(t0,str) else (t0/1000 if t0>1e12 else t0)
    cands=[b for b in B if abs(ue(b['ts'])-t)<=3 and b['f']=='FEATURE_CODING']
    if len(cands)==1: pairs.append((u,cands[0]))
print(f'配对 {len(pairs)}/{len(U)}')
import math
n=len(pairs)
def sx(f): return sum(f(p) for p in pairs)
A=[[sx(lambda p,a=a,b=b: p[0][a]*p[0][b]/1e12) for a in('in','cache','out')] for b in('in','cache','out')]
Bv=[sum(p[0][a]/1e6*(p[1]['amt']*1000) for p in pairs) for a in('in','cache','out')]  # 1%≡¥10 ⇒ amt×1000=¥
M=[A[i]+[Bv[i]] for i in range(3)]
for c in range(3):
    p=max(range(c,3),key=lambda i:abs(M[i][c])); M[c],M[p]=M[p],M[c]
    for i in range(3):
        if i!=c:
            f=M[i][c]/M[c][c]
            for j in range(4): M[i][j]-=f*M[c][j]
sol=[M[i][3]/M[i][i] for i in range(3)]
rmse=math.sqrt(sum((sol[0]*p[0]['in']/1e6+sol[1]*p[0]['cache']/1e6+sol[2]*p[0]['out']/1e6-p[1]['amt']*1000)**2 for p in pairs)/n)
print(f'OLS: Pin=¥{sol[0]:.2f}/M  Pc=¥{sol[1]:.3f}/M  Pout=¥{sol[2]:.1f}/M  RMSE=¥{rmse:.4f}  n={n}')
