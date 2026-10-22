(() => {
  'use strict';
  const form=document.getElementById('brief-form');
  const preview=document.getElementById('prompt-preview');
  const status=document.getElementById('copy-status');
  const english=document.documentElement.lang==='en';
  function update(){
    const data=new FormData(form);
    if(english){
      preview.textContent=`Use the PPT to HTML skill to turn the attached PPT into an interactive HTML presentation.\n\n• Purpose and audience: ${data.get('purpose').trim() || '[Enter purpose and audience]'}\n• Length: ${data.get('time')}\n• Screen: ${data.get('size')}\n• Typeface: ${data.get('font')}\n• Motion frequency: ${data.get('motion')}\n• Playback: ${data.get('playback')}\n• Point, line and plane motion: ${data.get('graphics')}\n• Deliverables: one offline HTML file and editable source\n\nPreserve the original figures and meaning. Show the outline and one representative screen first. Ask only for missing settings. MP4 export is not needed.`;
      status.textContent='Generated only in this browser.';return;
    }
    preview.textContent=`PPT to HTML 스킬로 첨부한 PPT를 발표용 HTML로 재구성해주세요.\n\n• 목적·청중: ${data.get('purpose').trim() || '[목적과 청중을 입력해주세요]'}\n• 발표 시간: ${data.get('time')}\n• 화면: ${data.get('size')}\n• 글꼴: ${data.get('font')}\n• 움직임 빈도: ${data.get('motion')}\n• 진행 방식: ${data.get('playback')}\n• 점·선·면 모션: ${data.get('graphics')}\n• 산출물: 오프라인 단일 HTML + 편집용 소스\n\n원문 수치와 의미는 보존하고, 전체 구성과 대표 화면을 먼저 보여주세요. 필요한 추가 설정만 질문해주세요. MP4 출력은 필요하지 않습니다.`;
    status.textContent='현재 브라우저 안에서만 생성됩니다.';
  }
  form.addEventListener('input',update);
  form.addEventListener('change',update);
  form.addEventListener('submit',event=>event.preventDefault());
  document.getElementById('copy-prompt').addEventListener('click',async()=>{
    if(!form.reportValidity())return;
    try{await navigator.clipboard.writeText(preview.textContent);status.textContent=english?'Copied. Use this with your PPT in your AI environment.':'복사했습니다. 설치한 AI 환경에 PPT와 함께 전달하세요.';}
    catch{status.textContent=english?'Automatic copying is unavailable. Select and copy the prompt above.':'자동 복사를 사용할 수 없습니다. 위 요청문을 선택해서 복사해주세요.';preview.focus();const range=document.createRange();range.selectNodeContents(preview);const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);}
  });
  update();
})();
