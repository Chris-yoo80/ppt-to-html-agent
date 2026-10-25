const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const M=require('../skills/ppt-to-html/assets/motion-math.js');
const {launch}=require('./motion-runtime.cjs');
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

function assertSummary(summary,story){
 assert.ok(summary);
 for(const value of [story.title,story.lead,story.note,...story.phases])assert.ok(summary.textContent.includes(value),'missing '+value);
 const expected={delivery:['12','3','34%'],marketing:['1,200','360','72','24','6.0%'],warehouse:['4']};
 for(const value of expected[story.id])assert.ok(summary.textContent.includes(value),'missing numeric fact '+value);
}
function assertFacts(p,index){
 const story=p.config.stories[index],summary=p.summaries.find(s=>s.dataset.story===story.id);
 assertSummary(summary,story);assert.equal(summary.hidden,false);assert.equal(p.ids['story-title'].textContent,story.title);
}
for(const language of ['ko','en']){
 test(`${language}: reduced-motion startup retains all stories' essential facts without running frames`,()=>{
  const p=launch({language,reduced:true});p.visible(true);
  for(let i=0;i<3;i++){p.tabs.querySelectorAll('button')[i].click();assertFacts(p,i);assert.equal(p.raf.size,0);assert.equal(p.ids['toggle-play'].disabled,true);}
 });
 test(`${language}: final states retain earlier headline numbers in nonanimated summaries`,()=>{
  const p=launch({language});
  for(let i=0;i<3;i++){p.tabs.querySelectorAll('button')[i].click();p.seek(p.config.duration);assertFacts(p,i);}
 });
 test(`${language}: enabling reduced motion or manual motion-off preserves time and stops frames`,()=>{
  const p=launch({language});p.visible(true);assert.equal(p.raf.size,1);p.tick(0);p.tick(1200);
  const before=p.ids.timeline.value;p.setReduced(true);assertFacts(p,0);assert.equal(p.ids.timeline.value,before);assert.equal(p.raf.size,0);
  p.setReduced(false);assert.equal(p.raf.size,0);p.ids['motion-mode'].click();assert.equal(p.ids['toggle-play'].disabled,true);
  p.ids.restart.click();assert.equal(p.ids.timeline.value,'0');assert.equal(p.raf.size,0);
  for(let i=0;i<4;i++){p.phase.querySelectorAll('button')[i].click();assert.equal(Number(p.ids.timeline.value),i*p.config.duration/4);assertFacts(p,0);}
  p.seek(7.5);assert.equal(p.ids.timeline.value,'7.5');assertFacts(p,0);
 });
 test(`${language}: print preview retains three complete summaries and restores story/time paused`,()=>{
  const p=launch({language});p.tabs.querySelectorAll('button')[1].click();p.seek(7.5);
  const before=p.ids.timeline.value;p.ids['print-stories'].click();assert.equal(p.document.body.classList.contains('stories-print-preview'),true);
  assert.equal(p.summaries.length,3); // Print CSS shows even summaries hidden on interactive screen.
  for(let i=0;i<3;i++){
   const story=p.config.stories[i],node=p.summaries.find(n=>n.dataset.story===story.id);
   assertSummary(node,story);
  }
  p.events.beforeprint();assert.equal(p.raf.size,0);p.key('Escape');assert.equal(p.document.body.classList.contains('stories-print-preview'),false);
  assert.equal(p.ids.timeline.value,before);assertFacts(p,1);
 });
}
