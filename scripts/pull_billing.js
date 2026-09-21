// 在 kimi.com 控制台运行：拉取全部订阅流水（分页）
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
  console.log(JSON.stringify(out));
})()
