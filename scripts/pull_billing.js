// 在 kimi.com 控制台运行：拉取当前计数器快照与全量订阅流水（分页）
(async()=>{
  const token = localStorage.getItem('access_token');
  if (!token) {
    console.error('未在 localStorage 找到 access_token，请确认已登录 kimi.com');
    return;
  }
  const H = {
    'connect-protocol-version': '1',
    'content-type': 'application/json',
    'authorization': 'Bearer ' + token
  };

  // 1. 获取计数器快照 (GetSubscriptionStats)
  let stats = null;
  try {
    const sRes = await fetch('/apiv2/kimi.gateway.membership.v2.MembershipService/GetSubscriptionStats', {
      method: 'POST',
      headers: H,
      body: '{}'
    });
    stats = await sRes.json();
  } catch (e) {
    console.warn('获取 GetSubscriptionStats 失败:', e);
  }

  // 2. 分页拉取扣费流水 (ListBalanceActions)
  let actions = [], cursor = '';
  for (let i = 0; i < 50; i++) {
    const r = await fetch('/apiv2/kimi.gateway.membership.v2.MembershipService/ListBalanceActions', {
      method: 'POST',
      headers: H,
      body: JSON.stringify({
        page_size: 20,
        pageToken: cursor,
        filter: { unit: 'UNIT_CREDIT', balance_types: ['SUBSCRIPTION'] }
      })
    });
    const d = await r.json();
    if (!d.actions || d.actions.length === 0) break;
    actions.push(...d.actions.map(a => ({
      ts: a.timestamp,
      f: a.feature,
      t: a.title,
      amt: a.items.reduce((s, item) => s + parseFloat(item.amountRatio || 0), 0)
    })));
    if (!d.nextPageToken) break;
    cursor = d.nextPageToken;
  }

  const result = { stats, actions };
  const totalAmt = actions.reduce((s, a) => s + (a.amt || 0), 0);
  const counterRatio = stats?.subscriptionBalance?.amountUsedRatio;

  console.log(`[Kimi Billing] 抓取完成: 共 ${actions.length} 条流水，流水累计扣费 = ${(totalAmt * 100).toFixed(2)}% (${(totalAmt * 10000).toFixed(0)} credits)`);
  if (counterRatio !== undefined) {
    console.log(`[Kimi Billing] 官方计数器读数 amountUsedRatio = ${(counterRatio * 100).toFixed(2)}%`);
  }
  console.log(JSON.stringify(result));
})()
