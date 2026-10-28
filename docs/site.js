(() => {
  'use strict';
  const form = document.getElementById('brief-form');
  const preview = document.getElementById('prompt-preview');
  const status = document.getElementById('copy-status');
  const english = document.documentElement.lang === 'en';

  function update() {
    const data = new FormData(form);
    const reference = data.get('reference').trim() || (english ? 'none / recommend a preset' : '없음 / 적합한 프리셋 추천');
    const referenceUse = data.get('reference-use');
    if (english) {
      preview.textContent = `Use the PPT to HTML skill to turn the attached PPT into an interactive HTML presentation.\n\n• Purpose and audience: ${data.get('purpose').trim() || '[Enter purpose and audience]'}\n• Length: ${data.get('time')}\n• Screen: ${data.get('size')}\n• Typeface: ${data.get('font')}\n• Motion frequency: ${data.get('motion')}\n• Playback: ${data.get('playback')}\n• Point, line and plane motion: ${data.get('graphics')}\n• Design reference: ${reference}\n• Reference use: ${referenceUse}\n• Deliverables: one offline HTML file, editable source and design-reference.json\n\nPreserve the original figures and meaning. Show the outline and one representative screen first. If the reference is accessible, inspect it and extract visual rules only. Do not copy branding, text, images, icons, sample data, DOM or CSS. Record what was applied and excluded, along with permission and license details. Do not add runtime network dependencies. Ask only for missing settings. MP4 export is not needed.`;
      status.textContent = 'Generated only in this browser.';
      return;
    }
    preview.textContent = `PPT to HTML 스킬로 첨부한 PPT를 발표용 HTML로 재구성해주세요.\n\n• 목적·청중: ${data.get('purpose').trim() || '[목적과 청중을 입력해주세요]'}\n• 발표 시간: ${data.get('time')}\n• 화면: ${data.get('size')}\n• 글꼴: ${data.get('font')}\n• 움직임 빈도: ${data.get('motion')}\n• 진행 방식: ${data.get('playback')}\n• 점·선·면 모션: ${data.get('graphics')}\n• 디자인 레퍼런스: ${reference}\n• 레퍼런스 적용 범위: ${referenceUse}\n• 산출물: 오프라인 단일 HTML + 편집용 소스 + design-reference.json\n\n원문 수치와 의미는 보존하고, 전체 구성과 대표 화면을 먼저 보여주세요. 레퍼런스에 접근할 수 있으면 시각 규칙만 분석해주세요. 브랜드, 문구, 이미지, 아이콘, 예제 데이터, DOM, CSS는 복사하지 마세요. 적용·제외 항목과 권한·라이선스 근거를 기록하고 실행 중 네트워크 의존성을 추가하지 마세요. 필요한 추가 설정만 질문해주세요. MP4 출력은 필요하지 않습니다.`;
    status.textContent = '현재 브라우저 안에서만 생성됩니다.';
  }

  form.addEventListener('input', update);
  form.addEventListener('change', update);
  form.addEventListener('submit', event => event.preventDefault());
  document.getElementById('copy-prompt').addEventListener('click', async () => {
    if (!form.reportValidity()) return;
    try {
      await navigator.clipboard.writeText(preview.textContent);
      status.textContent = english ? 'Copied. Use this with your PPT in your AI environment.' : '복사했습니다. 설치한 AI 환경에 PPT와 함께 전달하세요.';
    } catch {
      status.textContent = english ? 'Automatic copying is unavailable. Select and copy the prompt above.' : '자동 복사를 사용할 수 없습니다. 위 요청문을 선택해서 복사해주세요.';
      preview.focus();
      const range = document.createRange();
      range.selectNodeContents(preview);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
    }
  });
  update();
})();
