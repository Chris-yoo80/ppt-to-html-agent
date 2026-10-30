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
  const buttons=['play','prev','next','replay','fullscreen','print','print-confirm','print-close','open-outline','outline-close','bookmark-current','open-bookmarks','bookmarks-close','return-bookmark','return-origin'];
  const dialogs=['outline-dialog','bookmarks-dialog'];
  const ids=Object.fromEntries(['deck-data','stage','viewport','position','announcement','outline-list','bookmarks-list','chapter-nav',...dialogs,...buttons].map(id=>[id,new Node(buttons.includes(id)?'button':dialogs.includes(id)?'dialog':'div')]));
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
const chartFixture=()=>JSON.parse(fs.readFileSync(path.join(root,'examples/chart-scenes/deck.json'),'utf8'));
const chartMarks=(stage,kind)=>collect(stage).filter(n=>(n.attributes?.class||'').split(' ').includes(kind));
const isOn=n=>n.attributes.class.split(' ').includes('on');
test('chart scenes reveal data with their linked steps and keep exact labels as text',()=>{
  const deck=chartFixture(),p=launch(deck),bars=()=>chartMarks(p.ids.stage,'chart-bar');
  assert.equal(bars().length,4);assert.deepEqual(bars().map(isOn),[true,false,false,false]);
  p.ids.next.click();assert.deepEqual(bars().map(isOn),[true,true,false,false]);
  const texts=collect(p.ids.stage).map(n=>n.textContent);
  for(const point of deck.scenes[0].chart.data)assert.ok(texts.includes(point.display),'missing '+point.display);
  assert.ok(texts.includes(deck.scenes[0].chart.note));
});
test('charts stay complete with motion off, reduced motion and in every printed page',()=>{
  const deck=chartFixture();
  for(const [data,options] of [[{...deck,settings:{...deck.settings,motion:'none'}},{}],[deck,{reduced:true}]]){
    const p=launch(data,options);
    for(const scene of data.scenes){
      const box=collect(p.ids.stage).find(n=>(n.className||'').includes('chart-box'));
      assert.ok(box,'chart missing for '+scene.id);assert.ok(!box.className.includes('enter'));
      const marks=collect(box).filter(n=>/chart-(bar|funnel|slice|dot)\b/.test(n.attributes?.class||''));
      assert.ok(marks.length>=scene.chart.data.length&&marks.every(isOn),scene.id);
      for(let i=0;i<scene.items.length;i++)p.ids.next.click();
    }
  }
  const p=launch(deck);p.ids.print.click();
  const pages=p.doc.body.children.find(n=>n.id==='print-pages').children;
  assert.equal(pages.length,deck.scenes.length);
  pages.forEach((page,i)=>{const texts=collect(page).map(n=>n.textContent);for(const point of deck.scenes[i].chart.data)assert.ok(texts.some(t=>t.startsWith(point.display||point.value.toLocaleString('ko-KR'))),deck.scenes[i].id+' '+point.label);});
});
test('funnel and donut derive rates and shares from the data, not from hand-typed text',()=>{
  const deck=chartFixture(),p=launch(deck,{reduced:true});
  for(let i=0;i<7;i++)p.ids.next.click(); // first step of the funnel scene
  const funnel=collect(p.ids.stage).map(n=>n.textContent);
  for(const rate of ['↓ 45.0%','↓ 23.3%','↓ 42.9%'])assert.ok(funnel.includes(rate),rate);
  p.key('End');const donut=collect(p.ids.stage).map(n=>n.textContent);
  for(const share of ['1,000만 · 50.0%','600만 · 30.0%','400만 · 20.0%'])assert.ok(donut.includes(share),share);
});
test('chart labels keep source decimals and axis ticks stay readable',()=>{
  const deck=chartFixture();deck.scenes=[{...deck.scenes[0],chart:{type:'bar',data:[{label:'A',value:0.012},{label:'B',value:1.4}]},items:deck.scenes[0].items.slice(0,2)}];
  const p=launch(deck,{reduced:true}),texts=collect(p.ids.stage).map(n=>n.textContent);
  assert.ok(texts.includes('0.012'),'exact small value');assert.ok(texts.includes('1.4'));
  for(const tick of ['0','0.5','1','1.5','2'])assert.ok(texts.includes(tick),'tick '+tick);
});
// Composed scenes: the builder turns agent HTML into a validated tree; tests use the same conversion.
const {execFileSync}=require('node:child_process');
const composedFixture=()=>JSON.parse(execFileSync('python',['-c',"import json,sys;sys.path.insert(0,'skills/ppt-to-html/scripts');from build_deck import runtime_deck;sys.stdout.reconfigure(encoding='utf-8');print(json.dumps(runtime_deck(json.load(open('examples/composed-report/deck.json',encoding='utf-8'))),ensure_ascii=False))"],{cwd:root,encoding:'utf8'}));
const stepped=stage=>collect(stage).filter(n=>n.attributes?.['data-step']).map(n=>[Number(n.attributes['data-step']),['on','focus','dim','pending'].filter(c=>n.classList.contains(c)).join(' ')]);
test('composed scenes spotlight the current step and keep later panels visible but dimmed',()=>{
  const deck=composedFixture(),p=launch(deck);
  assert.ok(!JSON.stringify(deck).includes('"html"'),'raw html never reaches the player');
  assert.deepEqual(stepped(p.ids.stage),[[1,'on focus'],[2,'dim'],[3,'dim']]);
  p.ids.next.click();assert.deepEqual(stepped(p.ids.stage),[[1,'on'],[2,'on focus'],[3,'dim']]);
  assert.equal(p.ids.announcement.textContent,'부품센터 자동화는 투자 32.4억, 회수 3.6년으로 추진 가능. 기대 효과');
  const title=collect(p.ids.stage).find(n=>n.className==='scene-title');assert.ok(title.children.some(n=>n.tagName==='em'&&n.textContent==='투자 32.4억, 회수 3.6년'));
});
test('composed scenes show every panel with reduced motion and render embedded charts',()=>{
  const deck=composedFixture(),p=launch(deck,{reduced:true});
  assert.deepEqual(stepped(p.ids.stage),[[1,'on'],[2,'on'],[3,'on']]);
  const texts=collect(p.ids.stage).map(n=>n.textContent);
  for(const share of ['18.0억 · 55.6%','8.2억 · 25.3%','3.6억 · 11.1%','2.6억 · 8.0%'])assert.ok(texts.includes(share),share);
});
test('backup scenes sit outside Next, open by data-goto and return to the exact step',()=>{
  const deck=composedFixture(),p=launch(deck),main=deck.scenes.filter(s=>!s.backup).reduce((n,s)=>n+s.steps.length,0);
  for(let i=0;i<7;i++)p.ids.next.click();
  const origin=p.ids.position.textContent;assert.equal(origin,`8 / ${main} 단계`);
  const button=collect(p.ids.stage).find(n=>n.attributes?.['data-goto']==='b1-cost');
  assert.equal(button.attributes.type,'button');button.listeners.click();
  assert.match(p.ids.position.textContent,/^자료 · 설비 단가/);assert.equal(p.ids['return-origin'].hidden,false);
  assert.equal(p.ids.next.disabled,true);assert.equal(p.ids.prev.disabled,true);
  p.ids['return-origin'].click();assert.equal(p.ids.position.textContent,origin);assert.equal(p.ids['return-origin'].hidden,true);
  p.key('End');assert.equal(p.ids.position.textContent,`${main} / ${main} 단계 · 끝`);assert.equal(p.ids.next.disabled,true);
  p.ids.next.click();assert.equal(p.ids.position.textContent,`${main} / ${main} 단계 · 끝`);
});
test('chapter tabs jump to their first step and mark the active chapter; contents lists backups separately',()=>{
  const deck=composedFixture(),p=launch(deck),tabs=p.ids['chapter-nav'].children.filter(n=>n.tagName==='button');
  assert.deepEqual(tabs.map(n=>n.textContent),['Summary','1 현황','2 투자','3 운영','4 일정','B1']);
  assert.ok(tabs[0].classList.contains('active'));
  tabs[2].click();assert.equal(p.ids.position.textContent,'7 / 13 단계');assert.ok(tabs[2].classList.contains('active'));assert.ok(!tabs[0].classList.contains('active'));
  p.key('g');const outline=p.ids['outline-list'].children;
  assert.ok(outline.some(n=>n.className==='outline-divider'));assert.ok(outline.at(-1).className.includes('backup'));
});
test('printing a composed deck includes backup scenes with no dimmed panels',()=>{
  const deck=composedFixture(),p=launch(deck);p.ids.print.click();
  const pages=p.doc.body.children.find(n=>n.id==='print-pages').children;
  assert.equal(pages.length,deck.scenes.length);
  pages.forEach(page=>{const states=stepped(page);assert.ok(states.every(([,s])=>!/dim|pending/.test(s)),JSON.stringify(states));});
  assert.equal(p.ids.position.textContent,'1 / 13 단계');
});
test('review regressions: scene ids cannot shadow controls; Back clears; autoplay and chapter tabs respect regions',()=>{
  const deck=composedFixture();
  // Defense in depth: even if a tree carried a control id, the player keeps its own references.
  deck.scenes[0].body.push(['span',{id:'position'},['fake']]);
  const p=launch(deck);
  p.ids.next.click();assert.equal(p.ids.position.textContent,'2 / 13 단계');
  for(let i=0;i<6;i++)p.ids.next.click();
  collect(p.ids.stage).find(n=>n.attributes?.['data-goto']==='b1-cost').listeners.click();
  assert.equal(p.ids['return-origin'].hidden,false);p.key('Home');assert.equal(p.ids['return-origin'].hidden,true);
  const withRepeat=composedFixture();withRepeat.scenes[3].chapter='1 현황';
  const q=launch(withRepeat),tabs=q.ids['chapter-nav'].children.filter(n=>n.tagName==='button').map(n=>n.textContent);
  assert.equal(tabs.filter(t=>t==='1 현황').length,1);
  const auto=composedFixture();auto.settings.playback='both';const r=launch(auto);
  r.key('End');r.ids.play.click();assert.equal(r.ids.play.attributes['aria-pressed'],'false');assert.equal(r.timers.size,0);
  const odd=composedFixture();odd.scenes[0].title='a**b';const s=launch(odd);
  assert.ok(!collect(s.ids.stage).some(n=>n.tagName==='em'));assert.match(s.ids.announcement.textContent,/^a\*\*b\./);
});
