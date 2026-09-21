#!/usr/bin/env python3
"""从 Kimi Work 会话 wire.jsonl 提取 usage 记录并去重。
用法：python3 scripts/analyze_wire.py <wire.jsonl>
输出：去重后的 usage 记录与合计。usage 字段映射：
  miss = inputOther (+inputCacheCreation), cache = inputCacheRead, out = output"""
import json, sys
def find_usage(o, out):
    if isinstance(o, dict):
        for k,v in o.items():
            if k=='usage' and isinstance(v,dict) and 'output' in v:
                out.append(v)
            else: find_usage(v,out)
    elif isinstance(o, list):
        for v in o: find_usage(v,out)
seen=set(); rows=[]
for line in open(sys.argv[1]):
    try: d=json.loads(line)
    except: continue
    us=[]; find_usage(d,us)
    for u in us:
        miss=(u.get('inputOther') or 0)+(u.get('inputCacheCreation') or 0)
        key=(miss,u.get('inputCacheRead'),u.get('output'))
        if key in seen: continue
        seen.add(key)
        rows.append({'miss':miss,'cache':u.get('inputCacheRead'),'out':u.get('output')})
print(json.dumps(rows,ensure_ascii=False,indent=1))
print(f'# {len(rows)} 条去重; 合计 miss={sum(r["miss"] for r in rows)} cache={sum(r["cache"] or 0 for r in rows)} out={sum(r["out"] for r in rows)}', file=sys.stderr)
