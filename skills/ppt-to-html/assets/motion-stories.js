/* Deterministic motion stories. All scenarios are fictional, not live models. */
(()=>{
  'use strict';
  const M=globalThis.MotionMath;
  const config=JSON.parse(document.getElementById('stories-data').textContent);
  const $=s=>document.querySelector(s), NS='http://www.w3.org/2000/svg';
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  const colors=['#9ebbf7','#c5e69b','#f1bd89'];
  let selected=0,time=0,playing=false,raf=null,last=null,draw=()=>{},activePhase=-1,viewed=false,manualReduced=false,printPreview=false;
  const motionReduced=()=>reduced.matches||manualReduced;
  function el(tag,attrs={},parent=$('#story-svg')){
    const n=document.createElementNS(NS,tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,String(v)));if(parent)parent.append(n);return n;
  }
  function label(x,y,value,cls='svg-label',parent){const n=el('text',{x,y,class:cls},parent);n.textContent=value;return n;}
  const path=points=>'M'+points.map(p=>p.join(',')).join(' L');
  const opacity=(node,value)=>node.setAttribute('opacity',M.clamp(value));
  const smooth=(t,start,end)=>M.ease((t-start)/(end-start));
  const format=t=>'0:'+String(Math.floor(t)).padStart(2,'0');
  function base(){
    const svg=$('#story-svg');svg.replaceChildren();
    const defs=el('defs');const filter=el('filter',{id:'soft-glow',x:'-100%',y:'-100%',width:'300%',height:'300%'},defs);
    el('feGaussianBlur',{stdDeviation:5},filter);
    for(let x=50;x<1280;x+=60)el('path',{d:`M${x} 210 V650`,class:'diagram-grid'});
    for(let y=230;y<650;y+=60)el('path',{d:`M45 ${y} H1235`,class:'diagram-grid'});
    return svg;
  }
  function delivery(story){
    base();
    const regions=el('g');
    [[[300,100],[715,100],[715,315],[300,315]],[[750,90],[1140,90],[1140,425],[750,425]],[[290,440],[1110,440],[1110,595],[290,595]]].forEach((points,i)=>{
      el('path',{d:path(points)+' Z',fill:colors[i],'fill-opacity':.09,stroke:colors[i],'stroke-opacity':.28,'stroke-dasharray':'5 8'},regions);
    });
    // Shift the map downward to keep labels and title in separate areas.
    const map=el('g',{transform:'translate(25 140) scale(.93 .72)'});
    regions.setAttribute('transform','translate(25 140) scale(.93 .72)');
    const before=el('g',{},map),after=el('g',{},map),routeNodes=[],trucks=[];
    story.before.forEach((ids,i)=>el('path',{d:path(M.route(story,ids)),fill:'none',stroke:colors[i],'stroke-width':2,'stroke-opacity':.25,'stroke-dasharray':'5 9'},before));
    story.after.forEach((ids,i)=>{
      const points=M.route(story,ids),len=M.length(points);
      const route=el('path',{d:path(points),fill:'none',stroke:colors[i],'stroke-width':4,'stroke-linejoin':'round','stroke-linecap':'round','stroke-dasharray':len,'stroke-dashoffset':len},after);
      routeNodes.push({node:route,len,points});
      const truck=el('g',{},map);
      el('circle',{r:21,fill:colors[i],'fill-opacity':.12},truck);
      el('rect',{x:-11,y:-8,width:20,height:15,rx:3,fill:colors[i],stroke:'#101622','stroke-width':2},truck);
      el('rect',{x:7,y:-4,width:9,height:11,rx:2,fill:colors[i]},truck);trucks.push(truck);
    });
    const dots=story.stops.map((p,i)=>{
      const g=el('g',{},map);el('circle',{cx:p[0],cy:p[1],r:15,fill:colors[Math.floor(i/4)],'fill-opacity':.1},g);
      const dot=el('circle',{cx:p[0],cy:p[1],r:6,fill:'#a3b3ca',stroke:'#101622','stroke-width':2},g);
      label(p[0]+14,p[1]+5,String(i+1).padStart(2,'0'),'svg-small',g);return dot;
    });
    const hub=el('g',{transform:`translate(${story.hub.join(' ')})`},map);
    el('circle',{r:46,fill:'#b9d7fb','fill-opacity':.06,stroke:'#7296c8','stroke-opacity':.3},hub);
    el('path',{d:'M-21 15 V-10 L0 -24 L21 -10 V15 Z',fill:'#c5d9f7'},hub);
    el('rect',{x:-6,y:0,width:12,height:15,fill:'#18273e'},hub);label(-27,70,'물류센터','svg-label',hub);
    label(865,590,'3 VEHICLES / 12 STOPS','svg-kicker');
    const old=M.totalLength(story,story.before),next=M.totalLength(story,story.after),gain=Math.round((1-next/old)*100);
    return t=>{
      opacity(regions,smooth(t,.20,.36));opacity(before,1-smooth(t,.38,.58));opacity(after,smooth(t,.36,.44));
      dots.forEach((dot,i)=>{dot.setAttribute('fill',t>.24?colors[Math.floor(i/4)]:'#a3b3ca');dot.setAttribute('r',t<.24?6+Math.sin(t*24+i)*1.7:6);});
      routeNodes.forEach((route,i)=>{route.node.setAttribute('stroke-dashoffset',route.len*(1-smooth(t,.37+i*.025,.66+i*.025)));const p=M.pointAt(route.points,((t-.64)*2+i*.23)%1);trucks[i].setAttribute('transform',`translate(${p[0]} ${p[1]})`);opacity(trucks[i],smooth(t,.65,.74));});
      $('#metric-value').textContent=t<.4?'12곳':'−'+Math.round(gain*smooth(t,.4,.77))+'%';
      $('#metric-label').textContent=t<.4?'가상 배송처':'가상 좌표의 총 경로 길이 비교';
    };
  }
  function marketing(story){
    base();
    const stages=['인지','관심','구매','재방문'],xs=[190,470,755,1040],heights=[230,185,140,102],panels=[];
    for(let i=0;i<4;i++){
      const g=el('g');const y=390-heights[i]/2;
      el('rect',{x:xs[i]-80,y,width:160,height:heights[i],rx:22,fill:colors[i%3],'fill-opacity':.09,stroke:colors[i%3],'stroke-opacity':.5},g);
      label(xs[i]-23,360,stages[i],'svg-label',g);label(xs[i]-48,408,story.counts[i].toLocaleString(),'svg-large',g);
      label(xs[i]-37,heights[i]/2+425,['도달','참여','전환','유지'][i]+' · 가상 인원','svg-small',g);panels.push(g);
      if(i<3)el('path',{d:`M${xs[i]+80} 390 C${xs[i]+145} 390 ${xs[i]+145} 390 ${xs[i+1]-80} 390`,stroke:'#748caf','stroke-opacity':.25,fill:'none','stroke-width':2,'stroke-dasharray':'4 8'});
    }
    const feedback=el('g');
    const retarget=el('path',{d:'M1040 464 C1040 615 470 610 470 505',stroke:'#c8e8a6','stroke-width':2,'stroke-dasharray':'5 8',fill:'none'},feedback);
    label(650,587,'RETENTION LOOP','svg-kicker',feedback);
    const channels=el('g');['콘텐츠','검색','이메일'].forEach((name,i)=>{el('rect',{x:110+i*126,y:215,width:106,height:32,rx:16,fill:'#1c2b40',stroke:'#ffffff13'},channels);label(134+i*126,236,name,'svg-small',channels);});
    const particles=Array.from({length:38},(_,i)=>el('circle',{r:i%5===0?4:2.7,fill:colors[i%3],'fill-opacity':.9}));
    const orbit=el('circle',{r:6,fill:'#d2f1ae'});
    return t=>{
      panels.forEach((panel,i)=>opacity(panel,.18+.82*smooth(t,i*.15,i*.15+.12)));
      opacity(channels,1-smooth(t,.25,.55));opacity(feedback,smooth(t,.65,.80));
      particles.forEach((particle,i)=>{const progress=((t*1.7+i/38)%1),x=100+progress*1060,amplitude=110*(1-progress)+15;particle.setAttribute('cx',x);particle.setAttribute('cy',390+Math.sin(i*2.4+progress*5)*amplitude);opacity(particle,smooth(t,.03,.13)*(progress>.62&&i%3!==0?.13:.8));});
      const f=M.clamp((t-.68)/.32),p=retarget.getPointAtLength(f*retarget.getTotalLength());orbit.setAttribute('cx',p.x);orbit.setAttribute('cy',p.y);opacity(orbit,smooth(t,.68,.76));
      $('#metric-value').textContent=t<.47?story.counts[0].toLocaleString()+'명':(story.counts[2]/story.counts[0]*100).toFixed(1)+'%';
      $('#metric-label').textContent=t<.47?'가상 캠페인 도달 인원':'가상 시나리오의 도달 대비 전환율';
    };
  }
  function warehouse(){
    base();
    const g=el('g',{transform:'translate(-70 65)'});
    const P=M.project;
    const poly=(points,attrs,parent=g)=>el('path',{d:path(points)+' Z',...attrs},parent);
    poly([P(0,0),P(880,0),P(880,520),P(0,520)],{fill:'#17283a',stroke:'#6686a7','stroke-width':1.5});
    for(let x=0;x<=880;x+=80)el('path',{d:path([P(x,0),P(x,520)]),stroke:'#799bc0','stroke-opacity':.13},g);
    for(let y=0;y<=520;y+=65)el('path',{d:path([P(0,y),P(880,y)]),stroke:'#799bc0','stroke-opacity':.13},g);
    const racks=[];
    function block(x,y,w,d,h,fill,parent=g){
      const group=el('g',{},parent);
      poly([P(x,y,h),P(x+w,y,h),P(x+w,y+d,h),P(x,y+d,h)],{fill,stroke:'#bbd2e0','stroke-opacity':.25},group);
      poly([P(x,y+d,0),P(x+w,y+d,0),P(x+w,y+d,h),P(x,y+d,h)],{fill:'#28465a',stroke:'#66899b','stroke-opacity':.3},group);
      poly([P(x+w,y,0),P(x+w,y+d,0),P(x+w,y+d,h),P(x+w,y,h)],{fill:'#20394b',stroke:'#66899b','stroke-opacity':.3},group);
      return group;
    }
    for(let row=0;row<3;row++)for(let col=0;col<5;col++)racks.push(block(235+col*100,95+row*105,65,65,44,'#3a6276'));
    const inbound=block(10,370,145,110,4,'#a6d0df'),outbound=block(760,20,110,115,4,'#c9dda0');
    const pi=P(20,505),po=P(865,30);label(pi[0]-50,pi[1]+28,'RECEIVING','svg-kicker',g);label(po[0]+8,po[1]+10,'SHIPPING','svg-kicker',g);
    const lanes=[[[80,430],[180,430],[180,250],[580,250]],[[580,250],[720,250],[720,90],[810,90]],[[300,360],[720,360],[720,90],[810,90]]].map(points=>points.map(p=>P(...p,8)));
    const routes=lanes.map((points,i)=>el('path',{d:path(points),fill:'none',stroke:colors[i],'stroke-width':3,'stroke-linejoin':'round','stroke-opacity':.65,'stroke-dasharray':'5 7'},g));
    const parcels=Array.from({length:12},(_,i)=>{
      const parcel=el('g',{},g);
      el('path',{d:'M0 -11 L13 -5 L0 2 L-13 -5 Z',fill:i%2?'#b8d7ef':'#d7e9ba'},parcel);
      el('path',{d:'M-13 -5 L0 2 V15 L-13 7 Z',fill:'#799bb6'},parcel);el('path',{d:'M0 2 L13 -5 V7 L0 15 Z',fill:'#4a738e'},parcel);return parcel;
    });
    const robot=el('g',{},g);el('ellipse',{rx:18,ry:9,fill:'#b5dcf5'},robot);el('rect',{x:-11,y:-10,width:22,height:10,rx:4,fill:'#71a4cb'},robot);
    return t=>{
      racks.forEach((rack,i)=>opacity(rack,.28+.72*smooth(t,.18+i*.012,.38+i*.012)));
      opacity(inbound,.5+.5*(1-smooth(t,.25,.5)));opacity(outbound,.35+.65*smooth(t,.65,.85));
      routes.forEach((route,i)=>opacity(route,smooth(t,.03+i*.22,.15+i*.22)));
      parcels.forEach((parcel,i)=>{const lane=i<6?0:(i<10?1:2),progress=((t*1.9+i*.13)%1),p=M.pointAt(lanes[lane],progress);parcel.setAttribute('transform',`translate(${p[0]} ${p[1]})`);opacity(parcel,smooth(t,lane*.20,lane*.20+.12));});
      const p=M.pointAt(lanes[2],(t*1.4)%1);robot.setAttribute('transform',`translate(${p[0]} ${p[1]})`);opacity(robot,smooth(t,.42,.56));
      $('#metric-value').textContent=['입고','적치','피킹','출고'][M.phase(t,1)];$('#metric-label').textContent='가상 공정 · 처리 성능을 뜻하지 않음';
    };
  }
  const builders={delivery,marketing,warehouse};
  function render(){
    const story=config.stories[selected],p=M.phase(time,config.duration);
    draw(time/config.duration);
    $('#timeline').value=String(time);
    $('#timecode').textContent=format(time)+' / '+format(config.duration);
    $('#timeline').setAttribute('aria-valuetext',`${p+1}단계 ${story.phases[p]}, ${Math.floor(time)}초`);
    if(p!==activePhase){activePhase=p;$('#phase-label').textContent=story.phases[p];$('#phase-number').textContent='CHAPTER '+String(p+1).padStart(2,'0')+' / 04';document.querySelectorAll('.phase-nav button').forEach((b,i)=>b.setAttribute('aria-current',i===p?'step':'false'));$('#story-status').textContent=story.label+' · '+story.phases[p];}
    $('#prev-phase').disabled=p===0;$('#next-phase').disabled=p===3;
  }
  function setPlaying(value){
    cancelAnimationFrame(raf);raf=null;last=null;
    playing=value&&!motionReduced()&&!printPreview&&time<config.duration;
    $('#toggle-play').textContent=motionReduced()?'모션 줄임':playing?'Ⅱ 일시 정지':'▶ 재생';$('#toggle-play').setAttribute('aria-pressed',String(playing));$('#toggle-play').disabled=motionReduced();
    $('#motion-mode').textContent=reduced.matches?'모션 줄임':manualReduced?'모션 켜기':'모션 끄기';$('#motion-mode').setAttribute('aria-pressed',String(motionReduced()));$('#motion-mode').disabled=reduced.matches;
    if(playing)raf=requestAnimationFrame(tick);
  }
  function tick(now){
    if(!playing)return;
    if(last!==null)time=Math.min(config.duration,time+(now-last)/1000);
    last=now;render();
    if(time>=config.duration)setPlaying(false);else raf=requestAnimationFrame(tick);
  }
  function seek(value){time=M.clamp(value,0,config.duration);activePhase=-1;last=null;render();}
  function select(index,autoplay=true){
    setPlaying(false);selected=index;time=0;activePhase=-1;
    const story=config.stories[index];
    document.querySelectorAll('.story-summary').forEach(n=>n.hidden=n.dataset.story!==story.id);
    $('#story-eyebrow').textContent=story.eyebrow;$('#story-title').textContent=story.title;$('#story-lead').textContent=story.lead;$('#story-note').textContent=story.note;
    document.querySelectorAll('.story-tabs button').forEach((b,i)=>{b.setAttribute('aria-selected',String(i===index));b.tabIndex=i===index?0:-1;});
    document.querySelectorAll('.phase-nav button').forEach((b,i)=>b.textContent=String(i+1).padStart(2,'0')+' '+story.phases[i]);
    draw=builders[story.id](story);render();
    if(autoplay&&!motionReduced())setPlaying(true);
  }
  config.stories.forEach((story,i)=>{const b=document.createElement('button');b.type='button';b.role='tab';b.textContent=story.label;b.setAttribute('aria-controls','story-panel');b.addEventListener('click',()=>select(i));$('.story-tabs').insertBefore(b,$('.story-tabs span'));});
  for(let i=0;i<4;i++){const b=document.createElement('button');b.type='button';b.addEventListener('click',()=>{setPlaying(false);seek(i*config.duration/4);});$('.phase-nav').append(b);}
  $('.story-tabs').addEventListener('keydown',event=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;event.preventDefault();const next=event.key==='Home'?0:event.key==='End'?2:(selected+(event.key==='ArrowRight'?1:2))%3;select(next);$('.story-tabs').querySelectorAll('button')[next].focus();});
  $('#toggle-play').addEventListener('click',()=>{if(time>=config.duration)seek(0);setPlaying(!playing);});
  $('#restart').addEventListener('click',()=>{seek(0);setPlaying(!motionReduced());});
  $('#motion-mode').addEventListener('click',()=>{manualReduced=!manualReduced;setPlaying(false);render();});
  $('#print-stories').addEventListener('click',()=>{printPreview=true;setPlaying(false);document.body.classList.add('stories-print-preview');$('#story-print-confirm').focus();window.scrollTo(0,0);});
  $('#story-print-confirm').addEventListener('click',()=>window.print());
  $('#story-print-close').addEventListener('click',()=>{printPreview=false;document.body.classList.remove('stories-print-preview');$('#print-stories').focus();});
  addEventListener('beforeprint',()=>setPlaying(false));
  $('#prev-phase').addEventListener('click',()=>{setPlaying(false);seek(Math.max(0,M.phase(time,config.duration)-1)*config.duration/4);});
  $('#next-phase').addEventListener('click',()=>{setPlaying(false);seek(Math.min(3,M.phase(time,config.duration)+1)*config.duration/4);});
  $('#timeline').max=String(config.duration);$('#timeline').addEventListener('input',event=>{setPlaying(false);seek(Number(event.target.value));});
  document.addEventListener('keydown',event=>{if(printPreview){if(event.key==='Escape')$('#story-print-close').click();return;}if(event.defaultPrevented||event.altKey||event.ctrlKey||event.metaKey||event.target.closest('button,input,select,textarea,a,[contenteditable=true]'))return;if(event.key===' '){event.preventDefault();$('#toggle-play').click();}else if(event.key==='ArrowRight')$('#next-phase').click();else if(event.key==='ArrowLeft')$('#prev-phase').click();else if(event.key==='Escape')setPlaying(false);});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)setPlaying(false);});
  reduced.addEventListener('change',()=>{setPlaying(false);render();});
  select(0,false);
  const observer=new IntersectionObserver(entries=>{if(entries[0].isIntersecting&&!viewed){viewed=true;if(!motionReduced())setPlaying(true);}else if(!entries[0].isIntersecting)setPlaying(false);},{threshold:.3});observer.observe($('#story-panel'));
})();
