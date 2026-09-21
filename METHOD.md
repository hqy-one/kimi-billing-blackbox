# METHOD.md — 10 分钟复现指南

任何人都可以用自己的账号验证本报告的核心结论。你只需要一个 Kimi 会员账号和一个浏览器。

## 1. 拉取你的官方计数器（1 分钟）

浏览器登录 kimi.com，F12 打开控制台，粘贴：

```js
fetch('/apiv2/kimi.gateway.membership.v2.MembershipService/GetSubscriptionStats', {
  method: 'POST',
  headers: {'connect-protocol-version':'1','content-type':'application/json',
            'authorization':'Bearer '+localStorage.getItem('access_token')},
  body: '{}'
}).then(r=>r.json()).then(console.log)
```

读数：`subscriptionBalance.amountUsedRatio`（月度池水位）、`kimiCodeUsedRatio`、`ratelimitCode5h/7d`。

## 2. 拉取你的计费流水（3 分钟）

```js
(async()=>{
  const H={'connect-protocol-version':'1','content-type':'application/json',
           'authorization':'Bearer '+localStorage.getItem('access_token')};
  let out=[], cursor='';
  for(let i=0;i<50;i++){
    const r=await fetch('/apiv2/kimi.gateway.membership.v2.MembershipService/ListBalanceActions',
      {method:'POST',headers:H,body:JSON.stringify({page_size:20,pageToken:cursor,
        filter:{unit:'UNIT_CREDIT',balance_types:['SUBSCRIPTION']}})});
    const d=await r.json(); if(!d.actions)break;
    out.push(...d.actions.map(a=>({ts:a.timestamp, f:a.feature,
      amt:a.items.reduce((s,i)=>s+parseFloat(i.amountRatio||0),0)})));
    if(!d.nextPageToken)break; cursor=d.nextPageToken;
  }
  console.log(JSON.stringify(out)); // 复制保存
})()
```

## 3. 验证价差（5 分钟）

1. 在 **Kimi Code** 里发一个长输出请求，记下扣费百分比与输出 token 数；
2. 在 **Kimi Work**（桌面端）发一个同类请求，同样记录；
3. 用锚点换算：扣费% × 10 = 标价金额（¥），÷ token 数 = 单价；
4. 对比两者的缓存/输出单价——你应看到 Code 缓存近免费（≈¥0.08/M）而 Work 缓存 ≈¥1.8/M。

## 4. 证据分级约定

- **A 级**：接口直读 + 本地留存原始 JSON（本仓库 data/）
- **B 级**：受控实验 + 统计拟合（费率卡区间）
- **C 级**：单次观察/用户侧读数（标注来源）

## 5. 本报告的可证伪点

若官方公布费率卡、或你的复测得到系统性不同的数值，请以 issue 提出——所有原始数据与脚本在仓库内，结论可以被推翻。

## 6. 已知边界

- 流水合计 ≠ 官方计数器（量化膨胀 +2.6%，见 TECHNICAL.md §6）
- 单账户单日测量；计费系统可能随版本变化
- 子代理/插件的按次扣费（0.02%/次）在界面上无提示，需在流水中按 `feature` 过滤观察
