/* Weighted campaign metrics and explicitly hypothetical scenarios. No formula eval. */
(function(root){
 'use strict';
 const fields=['spend','impressions','clicks','orders','revenue'];
 function validate(records){
  if(!Array.isArray(records)||!records.length||records.length>10000)throw new Error('1–10,000 records required');
  for(const r of records){for(const k of ['week','channel','region'])if(typeof r[k]!=='string'||!r[k].trim())throw new Error('Missing dimension: '+k);for(const k of fields)if(!Number.isFinite(r[k])||r[k]<0)throw new Error('Invalid metric: '+k);if(r.orders>r.clicks||r.clicks>r.impressions)throw new Error('Inconsistent funnel counts');}return records;
 }
 function sum(records){const totals=Object.fromEntries(fields.map(k=>[k,0]));for(const r of records)for(const k of fields)totals[k]+=r[k];return {...totals,roas:totals.spend?totals.revenue/totals.spend:null,cvr:totals.clicks?totals.orders/totals.clicks:null,ctr:totals.impressions?totals.clicks/totals.impressions:null,aov:totals.orders?totals.revenue/totals.orders:null};}
 function select(records,filters){return records.filter(r=>(filters.week==='all'||r.week===filters.week)&&(filters.region==='all'||r.region===filters.region)&&filters.channels.includes(r.channel));}
 function group(records,dimension){return [...new Set(records.map(r=>r[dimension]))].sort().map(label=>({label,...sum(records.filter(r=>r[dimension]===label))}));}
 function scenario(totals,budget,conversion,aov){
  if(![budget,conversion,aov].every(Number.isFinite)||budget<50||budget>200||conversion<70||conversion>130||aov<80||aov>120)throw new Error('Scenario controls outside supported range');
  if(totals.spend<=0||totals.clicks<=0||totals.orders<=0)return null;
  const rate=Math.min(1,totals.cvr*conversion/100),spend=totals.spend*budget/100,clicks=totals.clicks*budget/100,orders=clicks*rate,revenue=orders*totals.aov*aov/100;
  return {spend,clicks,orders,revenue,roas:revenue/spend,cvr:rate};
 }
 const api={validate,sum,select,group,scenario};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.AnalysisModel=api;
})(globalThis);
