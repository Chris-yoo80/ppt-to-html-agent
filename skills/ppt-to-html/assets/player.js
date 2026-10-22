/* Offline player. Deck content is data, never executable markup. */
(() => {
  'use strict';
  const deck = JSON.parse(document.getElementById('deck-data').textContent);
  const settings = {width:1600,height:900,motion:'key',playback:'manual',font:'system',end:'stop',...deck.settings};
  const english=deck.language==='en';
  const stage = document.getElementById('stage');
  const viewport = document.getElementById('viewport');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const steps = deck.scenes.flatMap((scene, sceneIndex) => scene.items.map((_, itemIndex) => ({sceneIndex, itemIndex})));
  let position = 0, timer = null, playing = false;
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
  function setPlaying(value) {
    clearTimeout(timer); timer=null;
    playing = value && (position < steps.length-1 || settings.end === 'loop');
    const button = document.getElementById('play');
    button.textContent=playing?(english?'Pause':'일시 정지'):(english?'Autoplay':'자동 재생'); button.setAttribute('aria-pressed',String(playing));
    if (playing) timer=setTimeout(next,deck.scenes[steps[position].sceneIndex].duration*1000 || 7000);
  }
  function render() {
    const {sceneIndex,itemIndex}=steps[position], scene=deck.scenes[sceneIndex];
    const motionEnabled = settings.motion!=='none' && scene.motion && scene.motion!=='none';
    stage.replaceChildren(); stage.className=settings.font==='serif'?'serif':'';
    document.body.classList.toggle('motion-none',settings.motion==='none');
    document.body.classList.toggle('motion-rich',settings.motion==='rich');
    const top=text('div','deck-top',''); const mark=text('span','deck-mark','');
    mark.append(document.createElement('i'),document.createTextNode(deck.title));
    top.append(mark,text('span','',`${String(sceneIndex+1).padStart(2,'0')} / ${String(deck.scenes.length).padStart(2,'0')}`));
    stage.append(top,text('p','eyebrow',scene.eyebrow || 'INTERACTIVE PRESENTATION'),text('h1','scene-title',scene.title));
    if(scene.lead) stage.append(text('p','lead',scene.lead));
    const body=text('div',`scene-body ${scene.layout || 'cards'}${motionEnabled?'':' no-motion'}`,'');
    const list=text('div','item-list','');
    scene.items.forEach((item,index)=>{
      const card=text('section','item'+(index<=itemIndex?' on':'')+(index===itemIndex?' active':''),'');
      card.setAttribute('aria-hidden',String(index>itemIndex));
      card.append(text('span','item-index',String(index+1).padStart(2,'0')));
      const content=document.createElement('div');
      if(item.value) content.append(text('strong','item-value',item.value));
      content.append(text('h2','',item.label),text('p','',item.body));card.append(content); list.append(card);
    });
    body.append(list); if(motionEnabled) body.append(diagram(scene,itemIndex+1)); stage.append(body);
    const bottom=text('footer','scene-bottom',''); bottom.append(text('p','message',scene.message),text('p','source',scene.source || ''));
    stage.append(bottom);
    document.getElementById('prev').disabled=position===0;
    document.getElementById('next').disabled=position===steps.length-1 && settings.end==='stop';
    document.getElementById('position').textContent=`${position+1} / ${steps.length} ${english?'steps':'단계'}${position===steps.length-1?(english?' · End':' · 끝'):''}`;
    document.getElementById('announcement').textContent=`${scene.title}. ${scene.items[itemIndex].label}`;
    fit(); setPlaying(playing);
  }
  function go(index){position=Math.max(0,Math.min(steps.length-1,index));render();}
  function next(){if(position<steps.length-1)go(position+1);else if(settings.end==='loop')go(0);else setPlaying(false);}
  document.getElementById('prev').addEventListener('click',()=>go(position-1));
  document.getElementById('next').addEventListener('click',next);
  document.getElementById('play').addEventListener('click',()=>setPlaying(!playing));
  document.getElementById('play').hidden=settings.playback==='manual';
  document.getElementById('replay').addEventListener('click',()=>{setPlaying(false);go(0);});
  document.getElementById('fullscreen').addEventListener('click',async()=>{
    try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}
    catch{document.getElementById('announcement').textContent='이 환경에서는 전체 화면을 사용할 수 없습니다.';}
  });
  addEventListener('keydown',event=>{
    if(document.getElementById('supplements-dialog')?.open)return;
    if(event.altKey||event.ctrlKey||event.metaKey||event.target.closest('input,textarea,select,[contenteditable=true]'))return;
    // Arrow navigation still works after clicking a control. Space/Enter keep
    // their native button/link activation instead of triggering two actions.
    if(event.target.closest('button,a')&&[' ','Enter'].includes(event.key))return;
    if(['ArrowRight','PageDown',' '].includes(event.key)){event.preventDefault();next();}
    else if(['ArrowLeft','PageUp'].includes(event.key)){event.preventDefault();go(position-1);}
    else if(event.key==='Home'){event.preventDefault();go(0);}
    else if(event.key==='End'){event.preventDefault();go(steps.length-1);}
    else if(event.key.toLowerCase()==='a'&&settings.playback!=='manual')setPlaying(!playing);
    else if(event.key==='Escape')setPlaying(false);
  });
  document.addEventListener('visibilitychange',()=>{if(document.hidden)setPlaying(false);});
  addEventListener('ppt-open-supplement',()=>setPlaying(false));
  addEventListener('resize',fit); reduced.addEventListener('change',render);
  render(); if(settings.playback==='auto')setPlaying(true);
})();
