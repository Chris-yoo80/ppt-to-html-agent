/* Player logic in a minimal DOM double. This is not browser/layout verification. */
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.join(__dirname,'..');
class Node {
  constructor(tag='div'){this.tagName=tag;this.children=[];this.attributes={};this.style={};this.listeners={};this.textContent='';this.className='';this.classList={toggle(){}};}
  append(...children){this.children.push(...children);}
  replaceChildren(...children){this.children=children;}
  setAttribute(k,v){this.attributes[k]=v;}
  addEventListener(k,v){this.listeners[k]=v;}
  getBoundingClientRect(){return {width:1600,height:900};}
  closest(selector){return selector.includes(this.tagName)?this:null;}
  click(){if(!this.disabled)this.listeners.click?.({target:this});}
}
function launch(deck){
  const ids=Object.fromEntries(['deck-data','stage','viewport','play','prev','next','position','announcement','replay','fullscreen'].map(id=>[id,new Node(['play','prev','next','replay','fullscreen'].includes(id)?'button':'div')]));
  ids['deck-data'].textContent=JSON.stringify(deck);
  const events={},docEvents={},timers=new Map();let seq=0;
  const doc={body:new Node(),documentElement:new Node(),hidden:false,getElementById:id=>ids[id],createElement:tag=>new Node(tag),createElementNS:(_,tag)=>new Node(tag),createTextNode:text=>({textContent:text}),addEventListener:(type,fn)=>docEvents[type]=fn};
  const ctx={document:doc,matchMedia:()=>({matches:false,addEventListener(){}}),addEventListener:(type,fn)=>events[type]=fn,setTimeout:fn=>{timers.set(++seq,fn);return seq;},clearTimeout:id=>timers.delete(id)};
  vm.runInNewContext(fs.readFileSync(path.join(root,'skills/ppt-to-html/assets/player.js'),'utf8'),ctx);
  return {ids,doc,docEvents,timers,key(key,target=new Node()){let prevented=false;events.keydown({key,target,preventDefault(){prevented=true;}});return prevented;},tick(){const [id,fn]=timers.entries().next().value||[];if(fn){timers.delete(id);fn();}}};
}
const fixture=()=>JSON.parse(fs.readFileSync(path.join(root,'examples/library/deck.json'),'utf8'));
test('every reveal has deterministic forward/back navigation and stops at end',()=>{
  const deck=fixture(),p=launch(deck),steps=deck.scenes.flatMap(s=>s.items.map(i=>`${s.title}. ${i.label}`));
  for(let i=0;i<steps.length;i++){
    assert.equal(p.ids.announcement.textContent,steps[i]);
    if(i<steps.length-1)p.ids.next.click();
  }
  assert.equal(p.ids.next.disabled,true);p.ids.next.click();assert.equal(p.ids.announcement.textContent,steps.at(-1));
  for(let i=steps.length-2;i>=0;i--){p.ids.prev.click();assert.equal(p.ids.announcement.textContent,steps[i]);}
  assert.equal(p.ids.prev.disabled,true);
});
test('keyboard arrows still navigate after button focus; native space is not doubled',()=>{
  const p=launch(fixture());p.key('ArrowRight',p.ids.next);assert.match(p.ids.position.textContent,/^2 \/ /);
  assert.equal(p.key(' ',p.ids.next),false);assert.match(p.ids.position.textContent,/^2 \/ /);
  p.key('End');assert.equal(p.ids.next.disabled,true);p.key('Home');assert.equal(p.ids.prev.disabled,true);
});
test('autoplay replaces one timer per step and clears it at the terminal step',()=>{
  const deck=fixture();deck.settings.playback='both';deck.settings.end='stop';
  const p=launch(deck),count=deck.scenes.reduce((sum,s)=>sum+s.items.length,0);
  p.ids.play.click();assert.equal(p.timers.size,1);
  for(let i=1;i<count;i++)p.tick();
  assert.equal(p.timers.size,0);assert.equal(p.ids.play.attributes['aria-pressed'],'false');assert.equal(p.ids.next.disabled,true);
});
test('hidden tab pauses playback and replay returns to the first reveal',()=>{
  const deck=fixture();deck.settings.playback='both';const p=launch(deck);
  p.ids.play.click();p.tick();p.doc.hidden=true;p.docEvents.visibilitychange();assert.equal(p.timers.size,0);
  p.ids.replay.click();assert.equal(p.ids.prev.disabled,true);assert.equal(p.timers.size,0);
});
