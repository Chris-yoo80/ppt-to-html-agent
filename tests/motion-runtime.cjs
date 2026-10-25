/* Execute the real motion runtime with DOM/SVG doubles. Not a layout renderer. */
const fs=require('fs'),path=require('path'),vm=require('vm');
const root=path.join(__dirname,'..'),M=require('../skills/ppt-to-html/assets/motion-math.js');
class Node{
 constructor(tag='div'){this.tagName=tag;this.children=[];this.attributes={};this.listeners={};this.style={};this.dataset={};this.textContent='';this.hidden=false;const s=new Set();this.classList={add:v=>s.add(v),remove:v=>s.delete(v),contains:v=>s.has(v)};}
 append(...nodes){this.children.push(...nodes);}
 insertBefore(node,before){const i=this.children.indexOf(before);if(i<0)this.append(node);else this.children.splice(i,0,node);}
 replaceChildren(...nodes){this.children=nodes;}
 setAttribute(k,v){this.attributes[k]=String(v);}
 addEventListener(type,fn){this.listeners[type]=fn;}
 querySelectorAll(selector){return selector==='button'?this.children.filter(n=>n.tagName==='button'):[];}
 click(){if(!this.disabled)this.listeners.click?.({target:this});}
 closest(){return null;}
 focus(){this.focused=true;}
 getTotalLength(){return 100;}
 getPointAtLength(value){return {x:value,y:value};}
}
function launch({language='ko',reduced=false}={}){
 const html=fs.readFileSync(path.join(root,`docs/demo${language==='en'?'.en':''}.html`),'utf8');
 const config=JSON.parse(html.split('<script id="stories-data" type="application/json">')[1].split('</script>')[0]);
 const ids=Object.fromEntries(['stories-data','story-svg','story-panel','story-eyebrow','story-title','story-lead','story-note','metric-value','metric-label','timeline','timecode','phase-label','phase-number','prev-phase','next-phase','toggle-play','restart','story-status','motion-mode','print-stories','story-print-confirm','story-print-close'].map(id=>[id,new Node(id)]));
 ids['stories-data'].textContent=JSON.stringify(config);
 const tabs=new Node(),phase=new Node(),span=new Node('span');tabs.append(span);
 const summaries=[...html.matchAll(/<section class="story-summary"([^>]*)>([\s\S]*?)<\/section>/g)].map(m=>{
  const n=new Node('section');n.dataset.story=m[1].match(/data-story="([^"]+)"/)[1];n.hidden=m[1].includes(' hidden');
  n.textContent=m[2].replace(/<[^>]*>/g,' ').replaceAll('&amp;','&').replaceAll('&lt;','<').replaceAll('&gt;','>');return n;
 });
 const docEvents={},events={},raf=new Map();let serial=0,intersection;
 const media={matches:reduced,addEventListener(type,fn){this[type]=fn;}};
 const document={body:new Node('body'),hidden:false,
  getElementById:id=>ids[id],
  querySelector:selector=>selector==='.story-tabs'?tabs:selector==='.story-tabs span'?span:selector==='.phase-nav'?phase:ids[selector.slice(1)],
  querySelectorAll:selector=>selector==='.story-summary'?summaries:selector==='.phase-nav button'?phase.querySelectorAll('button'):selector==='.story-tabs button'?tabs.querySelectorAll('button'):[],
  createElement:tag=>new Node(tag),createElementNS:(_,tag)=>new Node(tag),addEventListener:(type,fn)=>docEvents[type]=fn};
 const context={document,MotionMath:M,matchMedia:()=>media,
  requestAnimationFrame:fn=>{raf.set(++serial,fn);return serial;},cancelAnimationFrame:id=>raf.delete(id),
  addEventListener:(type,fn)=>events[type]=fn,window:{print(){},scrollTo(){}},
  IntersectionObserver:class{constructor(fn){intersection=fn;}observe(){}}};
 // Use the built localized runtime, so tests also exercise the English output.
 const runtime=html.split('<script id="stories-data"')[1].split('<script>')[1].split('</script>')[0];
 vm.runInNewContext(runtime,context);
 return {config,ids,summaries,document,events,raf,tabs,phase,
  visible(value){intersection([{isIntersecting:value}]);},
  setReduced(value){media.matches=value;media.change();},
  tick(now){const first=raf.entries().next().value;if(first){raf.delete(first[0]);first[1](now);}},
  seek(value){ids.timeline.value=String(value);ids.timeline.listeners.input({target:ids.timeline});},
  key(key){docEvents.keydown({key,target:new Node(),preventDefault(){}});}};
}
module.exports={launch};
