const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const M=require('../skills/ppt-to-html/assets/analysis-model.js');
const data=JSON.parse(fs.readFileSync(path.join(__dirname,'../examples/marketing-analysis/data.json'),'utf8'));
test('campaign totals and rates use weighted source sums',()=>{
 M.validate(data.records);const a=M.sum(data.records);
 for(const key of ['spend','revenue','orders','clicks'])assert.equal(a[key],data.expected[key]);
 assert.equal(a.roas,197711000/33661480);assert.equal(a.cvr,3383/72906);
 const average=data.records.reduce((s,r)=>s+r.revenue/r.spend,0)/data.records.length;assert.notEqual(a.roas,average);
});
test('period, channel and market slicers select the exact original row',()=>{
 const rows=M.select(data.records,{week:'2026-09-07',region:'Domestic',channels:['Search']});
 assert.equal(rows.length,1);assert.equal(rows[0].spend,2592000);assert.equal(rows[0].revenue,7946000);assert.equal(M.sum(rows).orders,137);
 assert.equal(M.select(data.records,{week:'all',region:'all',channels:[]}).length,0);
});
test('empty denominators are unavailable and zero spend never creates infinite ROAS',()=>{
 const empty=M.sum([]);assert.equal(empty.roas,null);assert.equal(empty.cvr,null);
 assert.equal(M.sum([{spend:0,revenue:5,impressions:0,clicks:0,orders:0}]).roas,null);
 assert.equal(M.scenario(empty,100,100,100),null);
});
test('scenario multiplies reviewed assumptions without mutating source records',()=>{
 const before=JSON.stringify(data.records),a=M.sum(data.records),s=M.scenario(a,200,100,100);
 assert.equal(s.spend,a.spend*2);assert.ok(Math.abs(s.revenue-a.revenue*2)<1e-6);assert.ok(Math.abs(s.roas-a.roas)<1e-12);assert.equal(JSON.stringify(data.records),before);
 assert.throws(()=>M.scenario(a,NaN,100,100));assert.throws(()=>M.scenario(a,201,100,100));
});
test('channel grouping preserves aggregate totals and rejects malformed funnels',()=>{
 const groups=M.group(data.records,'channel');assert.equal(groups.length,3);assert.equal(groups.reduce((s,r)=>s+r.revenue,0),data.expected.revenue);
 assert.throws(()=>M.validate([{...data.records[0],orders:999999}]));assert.throws(()=>M.validate([{...data.records[0],spend:-1}]));
});
