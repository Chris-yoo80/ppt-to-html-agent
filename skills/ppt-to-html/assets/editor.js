/* Optional in-browser review: edit text in place, leave memos for the author, save an updated HTML or export the changes.
   Text is edited as plain text only (contenteditable=plaintext-only); structure, styles and chart data stay locked. */
(() => {
  'use strict';
  const api = globalThis.__pptPlayer;
  if (!api) return;
  const {deck, view} = api;
  const english = deck.language === 'en';
  const t = (ko, en) => (english ? en : ko);
  const review = deck.review || (deck.review = {edits: [], memos: []});
  let memoMode = false, memoTarget = null;

  const make = (tag, className, textValue) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (textValue !== undefined) node.textContent = textValue;
    node.setAttribute('data-editor-ui', '');
    return node;
  };
  const sceneById = id => deck.scenes.find(scene => scene.id === id);
  const currentScene = () => deck.scenes[api.current().sceneIndex];
  const refKey = ref => ref.path ? 'path:' + ref.path.join('.') : ref.field === 'items' ? `items:${ref.index}:${ref.key}` : 'field:' + ref.field;
  const figures = value => String(value).match(/\d(?:[\d.,]*\d)?\s*[%A-Za-z가-힣$₩€]?/g) || [];

  // Read and write the deck value a rendered node came from.
  function treeNode(scene, path) {
    let node = null, list = scene.body;
    for (const index of path) { node = list[index]; list = node[2]; }
    return node;
  }
  function readValue(scene, ref) {
    if (ref.path) return treeNode(scene, ref.path)[2].join('');
    if (ref.field === 'items') return scene.items[ref.index][ref.key] || '';
    return scene[ref.field] || '';
  }
  function writeValue(scene, ref, value) {
    if (ref.path) treeNode(scene, ref.path)[2] = [value];
    else if (ref.field === 'items') scene.items[ref.index][ref.key] = value;
    else scene[ref.field] = value;
  }

  function commit(target, value) {
    const scene = currentScene(), key = refKey(target.ref);
    const before = readValue(scene, target.ref);
    if (before === value) return;
    writeValue(scene, target.ref, value);
    const index = review.edits.findIndex(edit => edit.scene === scene.id && edit.key === key);
    if (index < 0) review.edits.push({scene: scene.id, key, ref: target.ref, before, after: value});
    else review.edits[index].after = value;
    const edit = review.edits.find(item => item.scene === scene.id && item.key === key);
    if (edit.before === edit.after) review.edits.splice(review.edits.indexOf(edit), 1);
    else edit.numeric = JSON.stringify(figures(edit.before)) !== JSON.stringify(figures(edit.after));
    updateCounts();
  }

  // Controls
  // A separate top-right review bar keeps the playback controls uncluttered.
  const bar = make('div', 'editor-bar');
  bar.setAttribute('role', 'toolbar'); bar.setAttribute('aria-label', t('검토 도구', 'Review tools'));
  document.body.append(bar);
  const editButton = make('button', 'editor-toggle', t('편집', 'Edit'));
  const memoButton = make('button', 'editor-toggle', t('메모', 'Memo'));
  const reviewButton = make('button', 'editor-review', t('검토', 'Review'));
  for (const button of [editButton, memoButton, reviewButton]) { button.type = 'button'; button.setAttribute('aria-pressed', 'false'); }
  reviewButton.removeAttribute('aria-pressed');
  bar.append(editButton, memoButton, reviewButton);
  const banner = make('p', 'editor-banner');
  banner.setAttribute('role', 'status');
  document.body.append(banner);

  // Memo dialog
  const memoDialog = make('dialog', 'jump-dialog editor-dialog');
  memoDialog.id = 'memo-dialog';
  const memoHeader = make('header'), memoTitle = make('strong', '', t('수정 요청 메모', 'Change request'));
  const memoClose = make('button', '', '×'); memoClose.type = 'button'; memoClose.setAttribute('aria-label', t('닫기', 'Close'));
  memoHeader.append(memoTitle, memoClose);
  const memoTargetText = make('p', 'memo-target');
  const memoInput = make('textarea', 'memo-input');
  memoInput.setAttribute('rows', '4');
  memoInput.setAttribute('placeholder', t('예: 이 문장을 더 짧게, 수치 출처 확인, 차트를 막대로 바꾸기', 'e.g. shorten this, check the source, use a bar chart'));
  const memoActions = make('div', 'editor-actions');
  const memoSave = make('button', 'primary', t('메모 저장', 'Save memo')); memoSave.type = 'button';
  const memoDelete = make('button', '', t('메모 삭제', 'Delete memo')); memoDelete.type = 'button';
  memoActions.append(memoSave, memoDelete);
  memoDialog.append(memoHeader, memoTargetText, memoInput, memoActions);
  document.body.append(memoDialog);

  // Review dialog
  const reviewDialog = make('dialog', 'jump-dialog editor-dialog');
  reviewDialog.id = 'review-dialog';
  const reviewHeader = make('header'), reviewTitle = make('strong', '', t('수정과 메모', 'Edits and memos'));
  const reviewClose = make('button', '', '×'); reviewClose.type = 'button'; reviewClose.setAttribute('aria-label', t('닫기', 'Close'));
  reviewHeader.append(reviewTitle, reviewClose);
  const reviewList = make('div', 'review-list');
  const reviewActions = make('div', 'editor-actions');
  const saveHtmlButton = make('button', 'primary', t('수정본 HTML 저장', 'Save edited HTML')); saveHtmlButton.type = 'button';
  const exportButton = make('button', '', t('수정 내역 내보내기 (JSON)', 'Export changes (JSON)')); exportButton.type = 'button';
  reviewActions.append(saveHtmlButton, exportButton);
  const reviewNote = make('p', 'review-note', t('수정 내역 JSON을 작성자(AI)에게 전달하면 원본에 반영하고 숫자가 바뀐 항목은 다시 검수합니다.', 'Give the JSON to the author (AI) to apply the changes to the source; changed numbers are re-verified.'));
  reviewDialog.append(reviewHeader, reviewList, reviewActions, reviewNote);
  document.body.append(reviewDialog);

  const open = dialog => { api.setPlaying(false); if (typeof dialog.showModal === 'function') dialog.showModal(); else dialog.open = true; };
  const close = dialog => { if (typeof dialog.close === 'function') dialog.close(); else dialog.open = false; };

  function updateCounts() {
    const numeric = review.edits.filter(edit => edit.numeric).length;
    reviewButton.textContent = t('검토', 'Review') + (review.edits.length || review.memos.length ? ` (${review.edits.length + review.memos.length})` : '');
    banner.textContent = numeric ? t(`숫자가 바뀐 수정 ${numeric}건: 차트·합계와 맞는지 작성자 재검수가 필요합니다.`, `${numeric} edit(s) changed numbers: the author must re-verify charts and totals.`) : '';
    banner.hidden = !numeric;
  }

  function snippet(scene, ref) {
    const value = readValue(scene, ref) || '';
    return value.length > 60 ? value.slice(0, 60) + '…' : value;
  }
  function stepLabel() {
    const {sceneIndex, itemIndex} = api.current();
    return api.labelsOf(deck.scenes[sceneIndex])[itemIndex];
  }

  function openMemo(target) {
    const scene = currentScene();
    const existing = review.memos.find(memo => memo.scene === scene.id && memo.key === refKey(target.ref));
    memoTarget = {scene: scene.id, ref: target.ref, key: refKey(target.ref)};
    memoTargetText.textContent = `${scene.id} · ${stepLabel()} · ${snippet(scene, target.ref) || t('(요소)', '(element)')}`;
    memoInput.value = existing ? existing.note : '';
    memoDelete.hidden = !existing;
    open(memoDialog);
    memoInput.focus?.();
  }
  memoSave.addEventListener('click', () => {
    const note = memoInput.value.trim();
    if (!note || !memoTarget) { close(memoDialog); return; }
    const existing = review.memos.find(memo => memo.scene === memoTarget.scene && memo.key === memoTarget.key);
    if (existing) existing.note = note;
    else review.memos.push({...memoTarget, step: stepLabel(), target: snippet(sceneById(memoTarget.scene), memoTarget.ref), note});
    close(memoDialog); updateCounts(); api.render();
  });
  memoDelete.addEventListener('click', () => {
    const index = review.memos.findIndex(memo => memo.scene === memoTarget?.scene && memo.key === memoTarget?.key);
    if (index >= 0) review.memos.splice(index, 1);
    close(memoDialog); updateCounts(); api.render();
  });
  memoClose.addEventListener('click', () => close(memoDialog));
  reviewClose.addEventListener('click', () => close(reviewDialog));

  function renderReview() {
    reviewList.replaceChildren();
    if (!review.edits.length && !review.memos.length) reviewList.append(make('p', 'empty-bookmarks', t('아직 수정이나 메모가 없습니다. 편집(E) 또는 메모(M)를 켜고 화면을 클릭하세요.', 'No edits or memos yet. Turn on Edit (E) or Memo (M) and click the slide.')));
    for (const edit of review.edits) {
      const row = make('div', 'review-row' + (edit.numeric ? ' numeric' : ''));
      row.append(make('b', '', `${t('수정', 'Edit')} · ${edit.scene}${edit.numeric ? t(' · 숫자 변경', ' · number changed') : ''}`), make('span', 'before', edit.before), make('span', 'after', edit.after));
      reviewList.append(row);
    }
    for (const memo of review.memos) {
      const row = make('div', 'review-row memo');
      const jump = make('button', 'bookmark-jump', t('이동', 'Go')); jump.type = 'button';
      jump.addEventListener('click', () => { close(reviewDialog); api.go(api.firstStep(memo.scene)); });
      row.append(make('b', '', `${t('메모', 'Memo')} · ${memo.scene} · ${memo.step}`), make('span', 'after', memo.note), make('span', 'before', memo.target), jump);
      reviewList.append(row);
    }
  }

  function exportReview() {
    return {format: 'ppt-to-html-review', version: 1, deck: deck.title, exported: new Date().toISOString(),
      edits: review.edits.map(({scene, ref, before, after, numeric}) => ({scene, ...ref, before, after, numeric: Boolean(numeric)})),
      memos: review.memos.map(({scene, ref, step, target, note}) => ({scene, ...ref, step, target, note}))};
  }
  const safeJson = value => JSON.stringify(value).replace(/&/g, '\\u0026').replace(/</g, '\\u003c').replace(/>/g, '\\u003e');
  // A copy of this file with the edited deck data; runtime-rendered parts are cleared and rebuilt on open.
  function savedHtml() {
    const copy = document.documentElement.cloneNode(true);
    for (const selector of ['#stage', '#chapter-nav', '#outline-list', '#bookmarks-list', '#position', '#announcement']) copy.querySelector(selector)?.replaceChildren();
    copy.querySelectorAll('[data-editor-ui], #print-pages').forEach(node => node.remove());
    copy.querySelectorAll('dialog[open]').forEach(node => node.removeAttribute('open'));
    const body = copy.querySelector('body');
    body.className = [...document.body.classList].filter(name => name.startsWith('theme-')).join(' ');
    copy.querySelector('#deck-data').textContent = safeJson(deck);
    const head = [...document.childNodes].filter(node => node !== document.documentElement).map(node =>
      node.nodeType === 8 ? `<!--${node.data}-->` : node.nodeType === 10 ? '<!doctype html>' : '').join('\n');
    return head + '\n' + copy.outerHTML;
  }
  function download(name, content, type) {
    const blob = new Blob([content], {type});
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob); link.download = name;
    document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(link.href), 1000);
  }
  const baseName = () => deck.title.replace(/[\\/:*?"<>|]+/g, ' ').trim().slice(0, 60) || 'presentation';
  saveHtmlButton.addEventListener('click', () => download(`${baseName()}-${t('수정본', 'edited')}.html`, savedHtml(), 'text/html'));
  exportButton.addEventListener('click', () => download('deck-edits.json', JSON.stringify(exportReview(), null, 2), 'application/json'));

  function setEditing(on) {
    view.editing = on; view.revealAll = on;
    if (on && memoMode) setMemo(false);
    editButton.setAttribute('aria-pressed', String(on));
    document.body.classList.toggle('editing', on);
    api.setPlaying(false); api.render();
  }
  function setMemo(on) {
    memoMode = on;
    if (on && view.editing) setEditing(false);
    memoButton.setAttribute('aria-pressed', String(on));
    document.body.classList.toggle('memo-mode', on);
    api.setPlaying(false);
  }
  editButton.addEventListener('click', () => setEditing(!view.editing));
  memoButton.addEventListener('click', () => setMemo(!memoMode));
  reviewButton.addEventListener('click', () => { renderReview(); open(reviewDialog); });

  // After each render: make text editable, mark edits and memos.
  view.hooks.push(({scene}) => {
    for (const target of view.targets) {
      const key = refKey(target.ref);
      if (view.editing && target.editable) {
        target.node.setAttribute('contenteditable', 'plaintext-only');
        target.node.setAttribute('spellcheck', 'false');
        target.node.addEventListener('input', () => commit(target, target.node.textContent));
        target.node.addEventListener('keydown', event => { if (event.isComposing || event.keyCode === 229) return; if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); target.node.blur?.(); } });
      }
      if (review.edits.some(edit => edit.scene === scene.id && edit.key === key)) target.node.classList.add('was-edited');
      const memoIndex = review.memos.findIndex(memo => memo.scene === scene.id && memo.key === key);
      if (memoIndex >= 0) { target.node.classList.add('has-memo'); target.node.setAttribute('data-memo', String(memoIndex + 1)); }
    }
  });
  // In memo mode a click on the slide picks the nearest tracked element instead of activating it.
  document.getElementById('stage').addEventListener('click', event => {
    if (!memoMode) return;
    let node = event.target;
    while (node && node.id !== 'stage') {
      const target = view.targets.find(item => item.node === node);
      if (target) { event.preventDefault(); event.stopPropagation(); openMemo(target); return; }
      node = node.parentNode;
    }
  }, true);
  addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.target?.closest?.('input,textarea,select,[contenteditable]')) return;
    if (document.body.classList.contains('print-preview') || memoDialog.open || reviewDialog.open || document.querySelector?.('dialog[open]')) return;
    if (event.key.toLowerCase() === 'e') { event.preventDefault(); setEditing(!view.editing); }
    else if (event.key.toLowerCase() === 'm') { event.preventDefault(); setMemo(!memoMode); }
  });
  globalThis.__pptEditor = {exportReview, savedHtml, setEditing, setMemo, review};
  updateCounts();
  api.render();
})();
