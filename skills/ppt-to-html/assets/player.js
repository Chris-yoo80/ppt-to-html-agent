/* Offline player. Deck content is data, never executable markup. */
(() => {
  'use strict';
  const deck = JSON.parse(document.getElementById('deck-data').textContent);
  const settings = {width:1600,height:900,motion:'key',playback:'manual',font:'system',end:'stop',...deck.settings};
  const english=deck.language==='en';
  const stage = document.getElementById('stage');
  const viewport = document.getElementById('viewport');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  // Resolve player controls once, before any scene content exists, so scene ids can never shadow them.
  const ui = {};
  ['chapter-nav','prev','next','position','announcement','play','replay','open-outline','outline-dialog','outline-close','outline-list',
   'bookmark-current','open-bookmarks','bookmarks-dialog','bookmarks-close','bookmarks-list','return-bookmark','return-origin',
   'fullscreen','print','print-confirm','print-close','print-pages','supplements-dialog'].forEach(id=>{ui[id]=document.getElementById(id);});
  const byId = id => ui[id];
  // Card scenes reveal items; composed scenes reveal their named steps.
  const labelsOf = scene => scene.items ? scene.items.map(item => item.label) : scene.steps;
  const plain = value => value.split('**').length%2 ? value.split('**').join('') : value;
  // Backup scenes sit after the main sequence: reachable by chapter tab, contents or data-goto, never by Next.
  const order = deck.scenes.map((_, index) => index).sort((a, b) => Number(Boolean(deck.scenes[a].backup)) - Number(Boolean(deck.scenes[b].backup)) || a - b);
  const steps = order.flatMap(sceneIndex => labelsOf(deck.scenes[sceneIndex]).map((_, itemIndex) => ({sceneIndex, itemIndex})));
  const mainCount = steps.filter(step => !deck.scenes[step.sceneIndex].backup).length;
  const firstStep = id => steps.findIndex(step => deck.scenes[step.sceneIndex].id === id);
  let position = 0, timer = null, playing = false, returnTo = null;
  // Optional editor support: data provenance of rendered nodes, refreshed every render.
  const view = {editing:false, revealAll:false, targets:[], hooks:[]};
  const track = (node, ref, editable) => view.targets.push({node, ref, editable});
  const chapterTabs = [];
  const bookmarks=[];
  const text = (tag, className, value) => {
    const node = document.createElement(tag); node.className = className; node.textContent = value || ''; return node;
  };
  const svgNode = (tag, attrs) => {
    const node = document.createElementNS('http://www.w3.org/2000/svg', tag);
    Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value)); return node;
  };
  function fit() {
    const rect = viewport.getBoundingClientRect();
    const scale = Math.min(rect.width/settings.width, rect.height/settings.height);
    stage.style.width = settings.width + 'px'; stage.style.height = settings.height + 'px';
    stage.style.transform = `translate(${(rect.width-settings.width*scale)/2}px,${(rect.height-settings.height*scale)/2}px) scale(${scale})`;
  }
  function diagram(scene, visibleCount) {
    const box = text('div', 'motion-box', '');
    const svg = svgNode('svg', {viewBox:'0 0 600 360',role:'img','aria-label':scene.motion_caption || scene.title});
    const colors = ['#355b37','#3158db','#7f9e53','#b5c886'];
    const count = scene.items.length;
    scene.items.forEach((item, index) => {
      const x = count === 1 ? 300 : 80+index*(440/(count-1));
      const on = index < visibleCount;
      const state = (on?' on':'')+(index===visibleCount-1?' active':'');
      if (scene.motion === 'lines' && index > 0) {
        svg.append(svgNode('path',{d:`M ${x-440/(count-1)+25} 175 H ${x-25}`,stroke:'#3158db','stroke-width':4,fill:'none',class:'motion-link'+state}));
      }
      if (scene.motion === 'planes') {
        svg.append(svgNode('rect',{x:x-50,y:95+index*12,width:100,height:150-index*10,rx:14,fill:colors[index],class:'motion-plane'+state}));
      } else {
        svg.append(svgNode('circle',{cx:x,cy:175,r:scene.motion==='points'?26:20,fill:colors[index],class:'motion-point'+state}));
      }
      const label=svgNode('text',{x,y:285,'text-anchor':'middle',class:'motion-label'});
      label.textContent=item.label; svg.append(label);
    });
    box.append(svg,text('p','motion-caption',scene.motion_caption || '개념 예시 · 실측 수치 아님'));
    return box;
  }
  // Charts are data, not decoration: linear scales from zero, exact labels in
  // text nodes, and full visibility whenever motion is reduced or printed.
  // Show every source decimal (up to 6) so labels stay exact; ticks pass their own precision.
  const decimals = value => Math.min(6,(String(value).split('.')[1]||'').length);
  const numberFormat = (value,digits=decimals(value)) => Number(value).toLocaleString(english?'en-US':'ko-KR',{maximumFractionDigits:digits});
  const percent = value => (Math.round(value*10)/10).toFixed(1)+'%';
  function niceMax(value){
    if(value<=0) return 1;
    const power=10**Math.floor(Math.log10(value)), unit=value/power;
    return ([1,1.2,2,2.4,3,4,5,6,8,10].find(step=>unit<=step))*power; // each divides evenly into 4 ticks
  }
  function svgText(svg, x, y, value, className, anchor='middle'){
    const node=svgNode('text',{x,y,'text-anchor':anchor,class:className}); node.textContent=value; svg.append(node); return node;
  }
  function chart(scene, visibleCount, entering, currentStep=Infinity) {
    const spec=scene.chart, data=spec.data, linked=Boolean(scene.items)&&data.length===scene.items.length;
    // spec.steps maps each datum to a composed-scene step; otherwise data follow card items when counts match.
    const stepOf=Array.isArray(spec.steps)?index=>spec.steps[index]:null;
    const shown=index=>stepOf?stepOf(index)<=currentStep:!linked || index<visibleCount;
    const active=index=>stepOf?stepOf(index)===currentStep:linked&&index===visibleCount-1;
    const state=index=>(shown(index)?' on':'')+(active(index)?' active':'');
    const highlight=new Set((spec.highlight||[]).map(value=>typeof value==='number'?value:data.findIndex(item=>item.label===value)));
    const tone=index=>highlight.has(index)?' is-highlight':'';
    const display=item=>item.display || numberFormat(item.value)+(spec.unit||'');
    // Linked charts animate the newly revealed datum; unlinked charts animate once on scene entry.
    const box=text('figure',`chart-box chart-type-${spec.type}${!linked&&entering?' enter':''}`,'');
    if(spec.title) box.append(text('figcaption','chart-title',spec.title));
    const svg=svgNode('svg',{viewBox:'0 0 640 380',role:'group','aria-label':spec.title || scene.title});
    const notes=[];
    if(spec.type==='bar' || spec.type==='line' || spec.type==='waterfall'){
      // Waterfall: totals stand on zero, deltas float from the running total.
      let running=0;
      const spans=data.map((item,index)=>{
        const total=(item.kind || (index===0?'total':'delta'))==='total', from=total?0:running, to=total?item.value:running+item.value;
        running=to; return {from,to,kind:total?'total':item.value>=0?'up':'down'};
      });
      const peak=spec.type==='waterfall'?Math.max(...spans.map(span=>Math.max(span.from,span.to))):Math.max(...data.map(item=>item.value));
      const max=niceMax(peak), left=56, right=616, top=36, bottom=300;
      const y=value=>bottom-(value/max)*(bottom-top), step=(right-left)/data.length;
      for(let tick=0;tick<=4;tick++){
        const value=max*tick/4;
        svg.append(svgNode('path',{d:`M ${left} ${y(value)} H ${right}`,class:'chart-grid'}));
        svgText(svg,left-10,y(value)+5,numberFormat(value,Math.max(0,2-Math.floor(Math.log10(max)))),'chart-axis','end');
      }
      if(spec.type==='line'){
        const points=data.map((item,index)=>[left+step*(index+.5),y(item.value)]);
        svg.append(svgNode('path',{d:`M ${points[0][0]} ${bottom} `+points.map(p=>`L ${p[0]} ${p[1]}`).join(' ')+` L ${points.at(-1)[0]} ${bottom} Z`,class:'chart-area'+(data.every((_,i)=>shown(i))?' on':'')}));
        points.slice(1).forEach((point,index)=>svg.append(svgNode('path',{d:`M ${points[index][0]} ${points[index][1]} L ${point[0]} ${point[1]}`,class:'chart-line'+state(index+1)})));
        points.forEach((point,index)=>svg.append(svgNode('circle',{cx:point[0],cy:point[1],r:9,class:'chart-dot'+state(index)})));
        points.forEach((point,index)=>svgText(svg,point[0],point[1]-20,display(data[index]),'chart-value'+state(index)));
      } else if(spec.type==='waterfall'){
        const width=Math.min(76,step*.6);
        spans.forEach((span,index)=>{
          const x=left+step*(index+.5), high=Math.max(span.from,span.to), item=data[index];
          svg.append(svgNode('rect',{x:x-width/2,y:y(high),width,height:Math.max(Math.abs(y(span.from)-y(span.to)),1),rx:4,style:`--i:${index}`,class:`chart-bar wf-${span.kind}`+state(index)}));
          if(index<spans.length-1) svg.append(svgNode('path',{d:`M ${x+width/2} ${y(span.to)} H ${x+step-width/2}`,class:'chart-connector'+state(index+1)}));
          const label=item.display || (span.kind==='total'?'':item.value>=0?'+':'')+numberFormat(item.value)+(spec.unit||'');
          svgText(svg,x,y(high)-12,label,'chart-value'+state(index));
        });
      } else {
        const width=Math.min(84,step*.62);
        data.forEach((item,index)=>{
          const x=left+step*(index+.5), height=bottom-y(item.value);
          svg.append(svgNode('rect',{x:x-width/2,y:y(item.value),width,height:Math.max(height,0),rx:6,style:`--i:${index}`,class:'chart-bar series-0'+tone(index)+state(index)}));
          svgText(svg,x,y(item.value)-12,display(item),'chart-value'+state(index));
        });
      }
      data.forEach((item,index)=>svgText(svg,left+step*(index+.5),bottom+30,item.label,'chart-label'+state(index)));
      svg.append(svgNode('path',{d:`M ${left} ${bottom} H ${right}`,class:'chart-baseline'}));
    } else if(spec.type==='funnel'){
      const max=Math.max(...data.map(item=>item.value)), rowHeight=Math.min(84,340/data.length), barLeft=150, barWidth=330;
      let clamped=false;
      data.forEach((item,index)=>{
        const top=20+index*rowHeight, exact=max?item.value/max:0, ratio=Math.max(exact,.015);
        if(ratio>exact) clamped=true;
        const width=barWidth*ratio, x=barLeft+(barWidth-width)/2;
        svg.append(svgNode('rect',{x,y:top,width,height:rowHeight*.62,rx:5,style:`--i:${index}`,class:'chart-funnel series-0'+tone(index)+state(index)}));
        svgText(svg,barLeft-14,top+rowHeight*.42,item.label,'chart-label'+state(index),'end');
        svgText(svg,barLeft+barWidth+14,top+rowHeight*.42,display(item),'chart-value'+state(index),'start');
        if(index>0 && data[index-1].value>0) svgText(svg,barLeft+barWidth+14,top-rowHeight*.12,'↓ '+percent(item.value/data[index-1].value*100),'chart-rate'+state(index),'start');
      });
      if(clamped) notes.push(english?'Bar widths are to scale; very small values use a minimum visible width.':'막대 너비는 실제 비율입니다. 아주 작은 값은 보이도록 최소 너비로 표시했습니다.');
    } else if(spec.type==='donut'){
      const total=data.reduce((sum,item)=>sum+item.value,0), cx=190, cy=190, radius=140, inner=86;
      let angle=-Math.PI/2;
      const point=(r,a)=>`${cx+r*Math.cos(a)} ${cy+r*Math.sin(a)}`;
      data.forEach((item,index)=>{
        const sweep=item.value/total*Math.PI*2, end=angle+sweep, large=sweep>Math.PI?1:0;
        const d=`M ${point(radius,angle)} A ${radius} ${radius} 0 ${large} 1 ${point(radius,end)} L ${point(inner,end)} A ${inner} ${inner} 0 ${large} 0 ${point(inner,angle)} Z`;
        svg.append(svgNode('path',{d,class:`chart-slice series-${index%6}`+state(index)}));
        // Label and value sit on separate lines so long labels never collide with numbers.
        const legendY=64+index*Math.min(72,290/data.length);
        svg.append(svgNode('rect',{x:372,y:legendY-14,width:16,height:16,rx:4,class:`chart-key series-${index%6}`+state(index)}));
        svgText(svg,398,legendY,item.label,'chart-label'+state(index),'start');
        svgText(svg,398,legendY+26,`${display(item)} · ${percent(item.value/total*100)}`,'chart-value'+state(index),'start');
        angle=end;
      });
      if(spec.center) svgText(svg,cx,cy+10,spec.center,'chart-center');
    }
    box.append(svg);
    for(const note of [spec.note,...notes].filter(Boolean)) box.append(text('p','chart-note',note));
    return box;
  }
  function setPlaying(value) {
    clearTimeout(timer); timer=null;
    const last = position>=mainCount ? steps.length-1 : mainCount-1;
    playing = value && !reduced.matches && (position < last || (settings.end === 'loop' && position < mainCount));
    const button = byId('play');
    button.disabled=reduced.matches;
    button.textContent=playing?(english?'Pause':'일시 정지'):(english?'Autoplay':'자동 재생'); button.setAttribute('aria-pressed',String(playing));
    if (playing) timer=setTimeout(next,deck.scenes[steps[position].sceneIndex].duration*1000 || 7000);
  }
  // Rebuild a validated composed-scene tree with DOM calls only; collect step, chart and jump hooks.
  function buildTree(nodes, parent, inSvg, hooks, path=[]){
    nodes.forEach((node,index)=>{
      if(typeof node==='string'){parent.append(document.createTextNode(node));return;}
      const [tag,attrs,children]=node, svg=inSvg||tag==='svg', here=[...path,index];
      const element=svg?document.createElementNS('http://www.w3.org/2000/svg',tag):document.createElement(tag);
      for(const [name,value] of Object.entries(attrs)) element.setAttribute(name,value);
      if(attrs['data-step']) hooks.stepped.push([element,Number(attrs['data-step'])]);
      if(attrs['data-chart']) hooks.charts.push([element,JSON.parse(attrs['data-chart'])]);
      if(attrs['data-goto']){element.setAttribute('type','button');element.addEventListener('click',()=>{if(!view.editing)jump(attrs['data-goto']);});}
      // Elements are memo targets; plain-text HTML leaves are editable text.
      track(element,{path:here},!svg&&!attrs['data-chart']&&children.length>0&&children.every(child=>typeof child==='string'));
      buildTree(children,element,svg,hooks,here); parent.append(element);
    });
  }
  function composed(scene, itemIndex, showAll){
    const reveal=scene.reveal || 'spotlight';
    const body=text('div',`scene-body composed reveal-${reveal}`,''), hooks={stepped:[],charts:[]};
    buildTree(scene.body,body,false,hooks);
    const current=showAll||reveal==='none'?Infinity:itemIndex+1;
    hooks.charts.forEach(([element,spec])=>element.append(chart({chart:spec,title:scene.title},Infinity,false,current)));
    // Spotlight keeps later panels readable but dimmed; build hides them until their step.
    hooks.stepped.forEach(([element,step])=>{
      if(step<current) element.classList.add('on');
      else if(step===current){element.classList.add('on');element.classList.add('focus');}
      else element.classList.add(reveal==='build'?'pending':'dim');
      if(reveal==='build') element.setAttribute('aria-hidden',String(step>current));
    });
    return body;
  }
  function buildChapters(){
    const nav=byId('chapter-nav'); if(!nav) return;
    nav.replaceChildren(); chapterTabs.length=0; const seen=new Set(); let divided=false;
    order.forEach(sceneIndex=>{
      const scene=deck.scenes[sceneIndex]; if(!scene.chapter || seen.has(scene.chapter)) return;
      seen.add(scene.chapter);
      if(scene.backup&&!divided){divided=true;nav.append(text('span','chapter-divider',english?'Backup':'자료실'));}
      const button=text('button','chapter-tab'+(scene.backup?' backup':''),scene.chapter);button.type='button';
      chapterTabs.push([button,scene.chapter]);
      button.addEventListener('click',()=>{setPlaying(false);navigate(firstStep(scene.id));});
      nav.append(button);
    });
    document.body.classList.toggle('has-chapters',nav.children.length>0);
  }
  function jump(id){
    const target=firstStep(id); if(target<0) return;
    if(returnTo===null) returnTo=position;
    setPlaying(false); go(target);
  }
  function navigate(index){returnTo=null;go(index);}
  function returnToOrigin(){
    if(returnTo===null) return;
    const target=returnTo; returnTo=null; go(target);
  }
  function render() {
    const {sceneIndex,itemIndex}=steps[position], scene=deck.scenes[sceneIndex];
    view.targets=[];
    const labels=labelsOf(scene), inBackup=position>=mainCount;
    const hasChart = Boolean(scene.chart);
    const motionEnabled = !scene.body && !hasChart && settings.motion!=='none' && scene.motion && scene.motion!=='none';
    stage.replaceChildren(); stage.className=(settings.font==='serif'?'serif':'')+(scene.body?' composed-scene':'');
    stage.setAttribute('data-scene',scene.id); // lets deck css style one scene: [data-scene="id"]
    document.body.classList.toggle('motion-none',settings.motion==='none');
    document.body.classList.toggle('motion-rich',settings.motion==='rich');
    const top=text('div','deck-top',''); const mark=text('span','deck-mark','');
    mark.append(document.createElement('i'),document.createTextNode(deck.title));
    const trail=[scene.chapter,`${itemIndex+1}/${labels.length} ${english?'steps':'단계'}`].filter(Boolean).join(' · ');
    top.append(mark,text('span','breadcrumb',trail),...(deck.version?[text('span','version-tag',deck.version)]:[]),text('span','page-count',inBackup?(english?'Backup':'자료'):`${String(order.indexOf(sceneIndex)+1).padStart(2,'0')} / ${String(order.filter(i=>!deck.scenes[i].backup).length).padStart(2,'0')}`));
    // **word** in a title marks emphasis; everything else stays plain text.
    const title=text('h1','scene-title','');
    const parts=scene.title.split('**');
    if(parts.length%2===0||view.editing) title.append(document.createTextNode(scene.title));
    else parts.forEach((part,index)=>{if(part) title.append(index%2?text('em','',part):document.createTextNode(part));});
    stage.append(top);
    if(scene.eyebrow){const eyebrow=text('p','eyebrow',scene.eyebrow);stage.append(eyebrow);track(eyebrow,{field:'eyebrow'},true);}
    stage.append(title); track(title,{field:'title'},true);
    if(scene.lead){const lead=text('p',scene.body?'lead summary':'lead',scene.lead);stage.append(lead);track(lead,{field:'lead'},true);}
    const showAll=reduced.matches||settings.motion==='none'||view.revealAll;
    if(scene.body){
      stage.append(composed(scene,itemIndex,showAll));
    } else {
    const body=text('div',`scene-body ${scene.layout || 'cards'}${hasChart?' has-chart':motionEnabled?'':' no-motion'}`,'');
    const list=text('div','item-list','');
    scene.items.forEach((item,index)=>{
      const visible=showAll||index<=itemIndex;
      const card=text('section','item'+(visible?' on':'')+(index===itemIndex?' active':''),'');
      card.setAttribute('aria-hidden',String(!visible));
      card.append(text('span','item-index',String(index+1).padStart(2,'0')));
      const content=document.createElement('div');
      if(item.value){const value=text('strong','item-value',item.value);content.append(value);track(value,{field:'items',index,key:'value'},true);}
      const label=text('h2','',item.label), itemBody=text('p','',item.body);
      content.append(label,itemBody);card.append(content); list.append(card);
      track(label,{field:'items',index,key:'label'},true); if(item.body) track(itemBody,{field:'items',index,key:'body'},true);
    });
    const visibleCount=showAll?scene.items.length:itemIndex+1;
    body.append(list);
    if(hasChart) body.append(chart(scene,visibleCount,!showAll&&itemIndex===0)); else if(motionEnabled) body.append(diagram(scene,visibleCount));
    stage.append(body);
    }
    const bottom=text('footer','scene-bottom',''), message=text('p','message','');
    if(scene.message_label) message.append(text('span','message-label',scene.message_label));
    const messageText=text('span','message-text',scene.message); message.append(messageText);
    track(messageText,{field:'message'},true);
    bottom.append(message,text('p','source',scene.source || ''));
    stage.append(bottom);
    const lastMain=mainCount-1, atEnd=inBackup?position===steps.length-1:position===lastMain;
    byId('prev').disabled=position===0||position===mainCount;
    byId('next').disabled=atEnd && (inBackup || settings.end==='stop');
    byId('position').textContent=inBackup?`${english?'Backup':'자료'} · ${plain(scene.title)}`:`${position+1} / ${mainCount} ${english?'steps':'단계'}${position===lastMain?(english?' · End':' · 끝'):''}`;
    byId('announcement').textContent=`${plain(scene.title)}. ${labels[itemIndex]}`;
    view.hooks.forEach(hook=>hook({scene,sceneIndex,itemIndex}));
    if(returnTo===position) returnTo=null;
    const back=byId('return-origin'); if(back) back.hidden=returnTo===null;
    for(const [tab,chapter] of chapterTabs){
      const on=chapter===scene.chapter; tab.classList.toggle('active',on);
      if(on) tab.setAttribute('aria-current','true'); else tab.removeAttribute('aria-current');
    }
    fit(); setPlaying(playing);
  }
  function go(index){position=Math.max(0,Math.min(steps.length-1,index));render();}
  function next(){
    if(position>=mainCount){if(position<steps.length-1)go(position+1);else setPlaying(false);return;}
    if(position<mainCount-1)go(position+1);else if(settings.end==='loop')go(0);else setPlaying(false);
  }
  function previous(){go(Math.max(position>=mainCount?mainCount:0,position-1));}
  function openDialog(id){
    setPlaying(false);
    const dialog=byId(id);
    if(typeof dialog.showModal==='function')dialog.showModal();else dialog.open=true;
    const first=dialog.children?.[0]?.children?.find?.(node=>node.tagName==='button') || dialog.children?.[0]?.children?.[1];
    first?.focus?.();
  }
  function closeDialog(id,returnId){
    const dialog=byId(id);
    if(typeof dialog.close==='function')dialog.close();else dialog.open=false;
    byId(returnId)?.focus();
  }
  function bookmarkLabel(index){
    const step=steps[index],scene=deck.scenes[step.sceneIndex],labels=labelsOf(scene);
    return `${String(order.indexOf(step.sceneIndex)+1).padStart(2,'0')} · ${plain(scene.title)} · ${step.itemIndex+1}/${labels.length} ${labels[step.itemIndex]}`;
  }
  function updateBookmarks(){
    const root=byId('bookmarks-list');root.replaceChildren();
    if(!bookmarks.length)root.append(text('p','empty-bookmarks',english?'No questions marked yet.':'표시한 질문이 없습니다.'));
    bookmarks.forEach((stepIndex,index)=>{
      const row=text('div','bookmark-row','');
      const jump=text('button','bookmark-jump',bookmarkLabel(stepIndex));jump.type='button';
      jump.setAttribute('aria-label',(english?'Return to ':'질문 위치로 이동: ')+bookmarkLabel(stepIndex));
      jump.addEventListener('click',()=>{navigate(stepIndex);closeDialog('bookmarks-dialog','open-bookmarks');});
      const remove=text('button','bookmark-remove',english?'Remove':'삭제');remove.type='button';
      remove.setAttribute('aria-label',(english?'Remove ':'질문 표시 삭제: ')+bookmarkLabel(stepIndex));
      remove.addEventListener('click',()=>{bookmarks.splice(index,1);updateBookmarks();});
      row.append(jump,remove);root.append(row);
    });
    byId('return-bookmark').disabled=!bookmarks.length;
    byId('open-bookmarks').textContent=(english?'Question list':'질문 목록')+(bookmarks.length?` (${bookmarks.length})`:'');
  }
  function markQuestion(){
    setPlaying(false);
    if(!bookmarks.includes(position))bookmarks.push(position);
    updateBookmarks();
    byId('announcement').textContent=(english?'Question marked: ':'질문 표시: ')+bookmarkLabel(position);
  }
  function returnToLatest(){
    if(!bookmarks.length)return;
    setPlaying(false);navigate(bookmarks[bookmarks.length-1]);
  }
  function buildOutline(){
    const root=byId('outline-list');root.replaceChildren();
    let stepIndex=0, divided=false;
    order.forEach((sceneIndex,orderIndex)=>{
      const scene=deck.scenes[sceneIndex];
      if(scene.backup&&!divided){divided=true;root.append(text('h2','outline-divider',english?'Backup and reference':'자료실 · 백업'));}
      const group=text('section','outline-scene'+(scene.backup?' backup':''),'');
      group.append(text('h2','',`${String(orderIndex+1).padStart(2,'0')} · ${plain(scene.title)}`));
      const list=text('div','outline-steps','');
      labelsOf(scene).forEach((label,itemIndex)=>{
        const target=stepIndex++;
        const button=text('button','outline-step',`${itemIndex+1}. ${label}`);button.type='button';
        button.setAttribute('aria-label',(english?'Go to ':'이동: ')+bookmarkLabel(target));
        button.addEventListener('click',()=>{navigate(target);closeDialog('outline-dialog','open-outline');});list.append(button);
      });
      group.append(list);root.append(group);
    });
  }
  // Build one complete scene per printed page, independent of the current reveal.
  function preparePrint(){
    setPlaying(false);
    const original=position, editing=view.editing, revealAll=view.revealAll;
    view.editing=false; view.revealAll=false;
    let root=byId('print-pages');
    if(!root){root=text('div','','');root.id='print-pages';document.body.append(root);ui['print-pages']=root;}
    root.replaceChildren();
    let end=-1;
    try{
      for(const sceneIndex of order){
        end+=labelsOf(deck.scenes[sceneIndex]).length;position=end;render();
        const page=text('article','print-page','');
        const copy=stage.cloneNode(true);copy.removeAttribute('id');copy.className+=' print-stage';
        const scale=Math.min(1046/settings.width,699/settings.height);
        copy.style.width=settings.width+'px';copy.style.height=settings.height+'px';
        // zoom shrinks the layout box too; transform alone leaves a 1600×900 box that print pagination clips.
        if(globalThis.CSS?.supports?.('zoom','0.5')){copy.style.zoom=String(scale);copy.style.transform='none';}
        else copy.style.transform=`scale(${scale})`;
        page.append(copy);root.append(page);
      }
    }finally{position=original;view.editing=editing;view.revealAll=revealAll;render();}
  }
  addEventListener('beforeprint',preparePrint);
  byId('print')?.addEventListener('click',()=>{
    preparePrint();document.body.classList.add('print-preview');
    byId('print-confirm').focus();
  });
  byId('print-confirm')?.addEventListener('click',()=>window.print());
  byId('print-close')?.addEventListener('click',()=>{
    document.body.classList.remove('print-preview');byId('print').focus();fit();
  });
  byId('prev').addEventListener('click',previous);
  byId('return-origin')?.addEventListener('click',returnToOrigin);
  byId('next').addEventListener('click',next);
  byId('play').addEventListener('click',()=>setPlaying(!playing));
  byId('play').hidden=settings.playback==='manual';
  byId('replay').addEventListener('click',()=>{setPlaying(false);returnTo=null;go(0);});
  byId('open-outline').addEventListener('click',()=>openDialog('outline-dialog'));
  byId('outline-close').addEventListener('click',()=>closeDialog('outline-dialog','open-outline'));
  byId('bookmark-current').addEventListener('click',markQuestion);
  byId('open-bookmarks').addEventListener('click',()=>{updateBookmarks();openDialog('bookmarks-dialog');});
  byId('bookmarks-close').addEventListener('click',()=>closeDialog('bookmarks-dialog','open-bookmarks'));
  byId('return-bookmark').addEventListener('click',returnToLatest);
  byId('fullscreen').addEventListener('click',async()=>{
    try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}
    catch{byId('announcement').textContent='이 환경에서는 전체 화면을 사용할 수 없습니다.';}
  });
  addEventListener('keydown',event=>{
    if(document.body.classList.contains('print-preview')){
      if(event.key==='Escape')byId('print-close').click();return;
    }
    if(byId('supplements-dialog')?.open)return;
    if(byId('outline-dialog').open||byId('bookmarks-dialog').open){
      if(event.key==='Escape'){
        if(byId('outline-dialog').open)closeDialog('outline-dialog','open-outline');
        if(byId('bookmarks-dialog').open)closeDialog('bookmarks-dialog','open-bookmarks');
      }
      return;
    }
    if(event.altKey||event.ctrlKey||event.metaKey||event.target.closest('input,textarea,select,[contenteditable]'))return;
    // Arrow navigation still works after clicking a control. Space/Enter keep
    // their native button/link activation instead of triggering two actions.
    if(event.target.closest('button,a')&&[' ','Enter'].includes(event.key))return;
    if(['ArrowRight','PageDown',' '].includes(event.key)){event.preventDefault();next();}
    else if(['ArrowLeft','PageUp'].includes(event.key)){event.preventDefault();previous();}
    else if(event.key==='Home'){event.preventDefault();navigate(0);}
    else if(event.key==='End'){event.preventDefault();go(mainCount-1);}
    else if(event.key==='Backspace'&&returnTo!==null){event.preventDefault();returnToOrigin();}
    else if(event.key.toLowerCase()==='a'&&settings.playback!=='manual')setPlaying(!playing);
    else if(event.key.toLowerCase()==='g'){event.preventDefault();openDialog('outline-dialog');}
    else if(event.key==='B'){event.preventDefault();updateBookmarks();openDialog('bookmarks-dialog');}
    else if(event.key.toLowerCase()==='b'){event.preventDefault();markQuestion();}
    else if(event.key.toLowerCase()==='r'){event.preventDefault();returnToLatest();}
    else if(event.key==='Escape')setPlaying(false);
  });
  document.addEventListener('visibilitychange',()=>{if(document.hidden)setPlaying(false);});
  addEventListener('ppt-open-supplement',()=>setPlaying(false));
  addEventListener('resize',fit); reduced.addEventListener('change',()=>{setPlaying(false);render();});
  function stepFromHash(){
    const params={};
    for(const pair of String(globalThis.location?.hash||'').replace(/^#/,'').split('&')){const [key,value='']=pair.split('=');try{params[key]=decodeURIComponent(value);}catch{}}
    const first=firstStep(params.scene||''); if(first<0) return null;
    const scene=deck.scenes[steps[first].sceneIndex], step=Math.min(Math.max(1,Number(params.step)||1),labelsOf(scene).length);
    return first+step-1;
  }
  view.hooks.push(({scene,itemIndex})=>{
    const hash=`#scene=${encodeURIComponent(scene.id)}&step=${itemIndex+1}`;
    try{if(globalThis.location&&globalThis.location.hash!==hash)globalThis.history?.replaceState?.(null,'',hash);}catch{}
  });
  addEventListener('hashchange',()=>{const target=stepFromHash();if(target!==null&&target!==position){setPlaying(false);go(target);}});
  globalThis.__pptPlayer={deck,view,render,setPlaying,go,current:()=>({...steps[position],position}),labelsOf,firstStep,
    steps:()=>steps.map(({sceneIndex,itemIndex})=>({scene:deck.scenes[sceneIndex].id,step:itemIndex+1,backup:Boolean(deck.scenes[sceneIndex].backup)}))};
  const linked=stepFromHash(); if(linked!==null) position=linked;
  buildChapters();buildOutline();updateBookmarks();render(); if(settings.playback==='auto')setPlaying(true);
})();
