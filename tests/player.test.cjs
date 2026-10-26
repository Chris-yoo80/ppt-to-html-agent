/* Player logic in a minimal DOM double. This is not browser/layout verification. */
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.join(__dirname,'..');
class Node {
  constructor(tag='div'){this.tagName=tag;this.children=[];this.attributes={};this.style={};this.listeners={};this.textContent='';this.className='';const classes=new Set();this.classList={add:v=>classes.add(v),remove:v=>classes.delete(v),toggle:(v,on)=>on?classes.add(v):classes.delete(v),contains:v=>classes.has(v)};}
  append(...children){this.children.push(...children);}
  replaceChildren(...children){this.children=children;}
  setAttribute(k,v){this.attributes[k]=v;}
  removeAttribute(k){delete this.attributes[k];}
  cloneNode(deep){const n=new Node(this.tagName);n.attributes={...this.attributes};n.style={...this.style};n.className=this.className;n.textContent=this.textContent;if(deep)n.children=this.children.map(c=>c.cloneNode?c.cloneNode(true):{...c});return n;}
  addEventListener(k,v){this.listeners[k]=v;}
  showModal(){this.open=true;}
  close(){this.open=false;}
  getBoundingClientRect(){return {width:1600,height:900};}
  closest(selector){return selector.includes(this.tagName)?this:null;}
  click(){if(!this.disabled)this.listeners.click?.({target:this});}
  focus(){}
}
function launch(deck,{reduced=false}={}){
  const buttons=['play','prev','next','replay','fullscreen','print','print-confirm','print-close','open-outline','outline-close','bookmark-current','open-bookmarks','bookmarks-close','return-bookmark'];
  const dialogs=['outline-dialog','bookmarks-dialog'];
  const ids=Object.fromEntries(['deck-data','stage','viewport','position','announcement','outline-list','bookmarks-list',...dialogs,...buttons].map(id=>[id,new Node(buttons.includes(id)?'button':dialogs.includes(id)?'dialog':'div')]));
  for(const [dialog,close] of [['outline-dialog','outline-close'],['bookmarks-dialog','bookmarks-close']]){const header=new Node('header');header.append(new Node('strong'),ids[close]);ids[dialog].append(header,dialog==='outline-dialog'?ids['outline-list']:ids['bookmarks-list']);}
  ids['deck-data'].textContent=JSON.stringify(deck);
  const events={},docEvents={},timers=new Map();let seq=0;
  const doc={body:new Node(),documentElement:new Node(),hidden:false,getElementById:id=>ids[id]||doc.body.children.find(n=>n.id===id),createElement:tag=>new Node(tag),createElementNS:(_,tag)=>new Node(tag),createTextNode:text=>({textContent:text}),addEventListener:(type,fn)=>docEvents[type]=fn};
  const media={matches:reduced,addEventListener(type,fn){this[type]=fn;}};
  const ctx={document:doc,window:{print(){}},matchMedia:()=>media,addEventListener:(type,fn)=>events[type]=fn,setTimeout:fn=>{timers.set(++seq,fn);return seq;},clearTimeout:id=>timers.delete(id)};
  vm.runInNewContext(fs.readFileSync(path.join(root,'skills/ppt-to-html/assets/player.js'),'utf8'),ctx);
  return {ids,doc,docEvents,timers,events,setReduced(value){media.matches=value;media.change();},key(key,target=new Node()){let prevented=false;events.keydown({key,target,preventDefault(){prevented=true;}});return prevented;},tick(){const [id,fn]=timers.entries().next().value||[];if(fn){timers.delete(id);fn();}}};
}
const fixture=()=>JSON.parse(fs.readFileSync(path.join(root,'examples/library/deck.json'),'utf8'));
const collect=n=>[n,...(n.children||[]).flatMap(collect)];
function assertContent(stage,scene){
 const nodes=collect(stage),texts=nodes.map(n=>n.textContent);
 for(const value of [scene.title,scene.lead,scene.message,scene.source,...scene.items.flatMap(i=>[i.label,i.body,i.value])].filter(Boolean))assert.ok(texts.includes(value),'missing '+value);
 const cards=nodes.filter(n=>n.className?.split(' ').includes('item'));
 assert.equal(cards.length,scene.items.length);assert.ok(cards.every(n=>n.attributes['aria-hidden']==='false'&&n.className.split(' ').includes('on')));
}
for(const lang of ['ko','en']){
 const deck=JSON.parse(fs.readFileSync(path.join(root,`examples/marketing-analysis/presentation.${lang}.json`),'utf8'));
 test(`marketing ${lang}: reduced motion and explicit motion=none retain every scene's facts`,()=>{
  for(const options of [{reduced:true},{reduced:false}]){
   const data=structuredClone(deck);if(!options.reduced)data.settings.motion='none';
   const p=launch(data,options);
   for(const scene of data.scenes){assertContent(p.ids.stage,scene);for(let i=0;i<scene.items.length;i++)p.ids.next.click();}
  }
 });
 test(`marketing ${lang}: normal/reduced print preview retains all titles values explanations and sources`,()=>{
  for(const reduced of [false,true]){
   const p=launch(deck,{reduced});p.ids.next.click();const before=p.ids.position.textContent;
   p.ids.print.click();const pages=p.doc.body.children.find(n=>n.id==='print-pages').children;
   assert.equal(pages.length,deck.scenes.length);pages.forEach((page,i)=>assertContent(page,deck.scenes[i]));
   p.events.beforeprint();assert.equal(p.doc.body.children.filter(n=>n.id==='print-pages').length,1);
   p.ids['print-close'].click();assert.equal(p.ids.position.textContent,before);assert.equal(p.timers.size,0);
  }
 });
}
test('enabling reduced motion mid-reveal exposes remaining facts and pauses without changing position',()=>{
 const deck=fixture();deck.settings.playback='both';const p=launch(deck);
 p.ids.play.click();const before=p.ids.position.textContent;assert.equal(p.timers.size,1);
 p.setReduced(true);assertContent(p.ids.stage,deck.scenes[0]);assert.equal(p.ids.position.textContent,before);assert.equal(p.timers.size,0);
 assert.equal(p.ids.play.disabled,true);p.setReduced(false);assert.equal(p.ids.play.disabled,false);assert.equal(p.timers.size,0);
});
test('printing includes every scene and hidden reveal, preserving current step and pausing playback',()=>{
 const deck=fixture();deck.settings.playback='both';const p=launch(deck);
 p.ids.next.click();const before=p.ids.position.textContent;p.ids.play.click();p.events.beforeprint();
 const pages=p.doc.body.children.find(n=>n.id==='print-pages').children;
 assert.equal(pages.length,deck.scenes.length);
 function collect(n){return [n,...(n.children||[]).flatMap(collect)];}
 pages.forEach((page,i)=>{
  const nodes=collect(page),cards=nodes.filter(n=>n.className?.split(' ').includes('item'));
  assert.equal(cards.length,deck.scenes[i].items.length);
  assert.ok(cards.every(n=>n.attributes['aria-hidden']==='false'));
  for(const item of deck.scenes[i].items)assert.ok(nodes.some(n=>n.textContent===item.label));
 });
 assert.equal(p.ids.position.textContent,before);assert.equal(p.timers.size,0);assert.equal(p.ids.play.attributes['aria-pressed'],'false');
});
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
test('contents panel jumps to any scene step and remains keyboard accessible',()=>{
  const deck=fixture(),p=launch(deck);
  p.key('g');assert.equal(p.ids['outline-dialog'].open,true);assert.equal(p.ids['outline-list'].children.length,deck.scenes.length);
  const secondSceneFirst=p.ids['outline-list'].children[1].children[1].children[0];
  secondSceneFirst.click();assert.equal(p.ids['outline-dialog'].open,false);
  assert.equal(p.ids.announcement.textContent,`${deck.scenes[1].title}. ${deck.scenes[1].items[0].label}`);
  p.key('G');assert.equal(p.ids['outline-dialog'].open,true);p.key('Escape');assert.equal(p.ids['outline-dialog'].open,false);
});
test('question bookmarks keep multiple exact steps and return after supporting-resource activity',()=>{
  const deck=fixture(),p=launch(deck);
  p.ids.next.click();const first=p.ids.announcement.textContent;p.key('b');
  p.ids.next.click();p.ids.next.click();const latest=p.ids.announcement.textContent;p.ids['bookmark-current'].click();
  assert.match(p.ids['open-bookmarks'].textContent,/2/);assert.equal(p.ids['return-bookmark'].disabled,false);
  p.events['ppt-open-supplement']();p.ids.next.click();p.ids['return-bookmark'].click();assert.equal(p.ids.announcement.textContent,latest);
  p.key('B');assert.equal(p.ids['bookmarks-dialog'].open,true);assert.equal(p.ids['bookmarks-list'].children.length,2);
  p.ids['bookmarks-list'].children[0].children[0].click();assert.equal(p.ids.announcement.textContent,first);assert.equal(p.ids['bookmarks-dialog'].open,false);
  p.ids['open-bookmarks'].click();p.ids['bookmarks-list'].children[0].children[1].click();assert.match(p.ids['open-bookmarks'].textContent,/1/);
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
