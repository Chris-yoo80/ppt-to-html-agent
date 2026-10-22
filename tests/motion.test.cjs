const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const M=require('../skills/ppt-to-html/assets/motion-math.js');
const config=JSON.parse(fs.readFileSync(path.join(__dirname,'../examples/motion-stories/stories.json'),'utf8'));
const story=config.stories.find(s=>s.id==='delivery');
test('each prescribed route plan serves each fictional stop once',()=>{
  for(const key of ['before','after'])assert.deepEqual(story[key].flat().sort((a,b)=>a-b),Array.from({length:12},(_,i)=>i));
});
test('displayed geometric route reduction is based on those routes',()=>{
  const old=M.totalLength(story,story.before),next=M.totalLength(story,story.after);
  assert.ok(next<old);assert.ok(old>0);
  console.log('Fictional coordinate reduction:',Math.round((1-next/old)*100)+'%');
});
test('vehicles stay on the route and have stable endpoint states',()=>{
  const points=[[0,0],[10,0],[10,20]];
  assert.deepEqual(M.pointAt(points,0),[0,0]);assert.deepEqual(M.pointAt(points,1),[10,20]);
  assert.deepEqual(M.pointAt(points,1/3),[10,0]);assert.deepEqual(M.pointAt(points,2/3),[10,10]);
});
test('timeline end stays on the last phase',()=>{
  assert.equal(M.phase(0,24),0);assert.equal(M.phase(6,24),1);assert.equal(M.phase(24,24),3);assert.equal(M.phase(30,24),3);
});
