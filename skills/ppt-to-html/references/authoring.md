# Bundled tools and scene authoring

Use these helpers when a portable starter presentation meets the brief. Resolve paths relative to this skill's directory. They use Python's standard library and do not call an AI API.

## Read a PPTX

```text
python <skill-directory>/scripts/extract_pptx.py <input.pptx> --output <work/source.json>
```

The extractor follows presentation relationship order, not slide filenames. It reads shape text, preserves paragraph-internal line breaks, reads tables and speaker notes, flags hidden slides and inventories linked media. It does not copy media into the output. SmartArt relationships are listed with a warning; their text is not extracted. Treat notes as private input: use them as evidence (definitions, qualifications, intended message) and cite them as "speaker notes, slide N", but do not copy note text onto audience-facing scenes unless the user agrees. Do not automatically put hidden slides into the audience's presentation. Confirm their intended use if relevant. It cannot render slides, perform OCR, interpret chart workbooks, read legacy PPT, or open encrypted/DRM sources. Obtain an owner-exported accessible source when required; do not claim that raw extraction preserves visual hierarchy.

## Author scene JSON

The AI reads the extracted material and authors the outline; the builder does not autonomously decide the narrative. Store the brief, source trace and editable JSON in the user's working folder.

On Windows, preserve UTF-8 when transferring Korean or other non-ASCII text through PowerShell. Do not pipe a non-ASCII Python program into Python under the default console encoding. Write a UTF-8 script file, use ASCII `\uXXXX` escapes, or explicitly set the pipe encoding first. After text edits, read the saved JSON and HTML back and compare the requested string exactly; a successful build alone does not detect replacement `?` characters.

```json
{
  "title": "Presentation title",
  "settings": {"width":1600,"height":900,"font":"system","motion":"key","playback":"both","end":"stop"},
  "scenes": [{
    "id":"overview",
    "eyebrow":"01 / Overview",
    "title":"One clear message",
    "lead":"Why this matters",
    "layout":"flow",
    "motion":"lines",
    "motion_caption":"Illustrative process",
    "items":[{"label":"Start","body":"Source-supported explanation"},{"label":"Finish","body":"Source-supported explanation"}],
    "message":"The audience's takeaway",
    "source":"Source slide 2",
    "duration":7
  }]
}
```

- `font`: `system` (system Korean sans-serif), `serif` (system serif), or `story` (bundled Story Sans review subset derived from Pretendard). The subset covers the current public example; other characters fall back to system fonts. Use a suitably licensed complete font for arbitrary documents needing consistent typography. Custom font packaging requires adapting the source and checking redistribution permission; the dropdown request alone does not install a font.
- `motion`: `none`, `key` (diagram motion), `rich` (also animate cards). These settings drive card scenes. Composed scenes animate through classes the player sets on every `[data-step]` element — `on` (revealed), `focus` (current step), `dim` (later, spotlight) and `pending` (later, build) — so write finite transitions or `@keyframes` on those classes in the deck `css`, with a `prefers-reduced-motion` fallback. Scene motion is `none`, `points`, `lines`, or `planes`. Other custom motion requires additional implementation.
- `playback`: `manual`, `both`, `auto`. All support visible previous/next controls. `end` is `stop` or explicitly requested `loop`.
- The bundled player builds its Contents panel from scene titles and item labels. Each item is a directly addressable reveal step. Question bookmarks store the exact flat step index in memory for the current page session; opening a sandboxed supporting resource does not rebuild the player or clear those marks.
- Each scene contains 1–4 concise items. Each item is one reveal step. Split dense material into scenes without omitting source qualifications. Title and message are required. Optional textual fields must be plain strings, not HTML.
- The player offers a small set of layouts, not a general-purpose PPT renderer. `cards` and `flow` use a list with an optional diagram; `compare` uses a two-column card grid. Design and implement additional layouts when the brief requires them.
- Use a `chart` for any scene whose message is a numeric comparison, trend, funnel or share. Text cards alone undersell numeric slides; a motion diagram is not a chart.
- Treat 1600×900 as the supplied starter's design basis. Alternate ratios, long text and other fonts require visual checking and may require CSS changes.
- `duration` is seconds per reveal step, from 3 to 120. It must be long enough to read that step.

## Chart scenes

Add an optional `chart` to a scene. It replaces the motion diagram on the right; the item cards stay on the left.

```json
"chart": {
  "type": "bar",
  "title": "Revenue by channel (KRW 10k)",
  "unit": "",
  "data": [{"label":"Store","value":5200,"display":"5,200"},{"label":"App","value":3100,"display":"3,100"}],
  "note": "Total 8,300. Bars start at zero."
}
```

| Type | Use for | Points |
|---|---|---|
| `bar` | comparing categories | 2–8 |
| `line` | a trend over ordered periods | 2–8 |
| `funnel` | stages that narrow; stage-to-stage rates are computed and shown | 2–6 |
| `donut` | parts of one whole; shares are computed and shown; optional `center` text | 2–6, each > 0 |

- `value` is the source number (finite, ≥ 0). `display` is the exact label to show; copy the source's formatting. Without `display`, the player formats `value` and appends `unit`.
- Charts are drawn to scale from zero. Do not rescale, truncate axes or invent data to make a chart look better. If a value is too small to see in a funnel, the player keeps a minimum width and states it under the chart.
- Bars and funnel stages share one colour (one measure, one hue). Mark the data the audience should look at with `"highlight": [index or label, …]`; do not colour every bar differently. Donut slices and waterfall totals/increases/decreases keep distinct colours because they encode categories or direction.
- In a composed scene, link a chart to the steps with `"steps": [1, 1, 2, 3]` (one step number per data point): data appear and are emphasised on their step and stay visible afterwards.
- When `data` has the same length as `items`, each reveal step highlights the matching datum. Otherwise the whole chart appears when the scene opens.
- Charts are content, not motion: they stay fully visible with motion off, reduced motion and print. Entrance animation is finite and ends in the same static chart.
- The palette uses the CSS variables `--chart-1` … `--chart-6`, so a design reference can restyle charts without changing the data.
- Recompute every chart value from the source before building and report it in numeric verification.

## Composed scenes (recommended for business reports)

Card scenes (`items`) suit short talks. For reports, reviews and proposals, write each scene body yourself: two or three panels per screen, each with the visual that fits its evidence. The player still provides navigation, steps, contents, question bookmarks, backup jumps, print and offline packaging.

```json
{
  "id": "investment",
  "chapter": "2 투자",
  "eyebrow": "2 · 투자 규모",
  "title": "총투자 32.4억 — **기존 견적 대비 +6.4억**",
  "lead": "기존 26.0 + 설비 4.2 + 시스템 1.6 + 인프라 1.2 − 예비비 0.6 = 32.4억",
  "steps": ["증감 구조", "상세 내역"],
  "reveal": "spotlight",
  "html": "<div class='k-grid cols-2'><section class='k-panel' data-step='1'>…</section><section class='k-panel' data-step='2'>…</section></div>",
  "message": "견적 기준은 동일하고 증가분은 설비 대수에 연동됩니다.",
  "message_label": "Key Message",
  "source": "원본 p.12"
}
```

- `title`: the conclusion, not a topic. Wrap key words in `**…**` to color them.
- `lead`: one line of key figures; it renders as a summary bar.
- `steps`: one label per reveal step (1–12). Every number 1…N must appear on at least one `data-step` element.
- `reveal`: `spotlight` (default; the current step gets an outline, later steps stay readable but dimmed), `build` (later steps hidden) or `none`.
- `message` + `message_label`: the bottom bar, e.g. `Key Message` or `시사점`.
- `chapter`: label for the chapter tab bar. Consecutive scenes with the same chapter share a tab.
- `backup: true`: the scene is outside the main Next sequence and appears under 자료실/Backup. Link to it with `<button data-goto="scene-id">label</button>`; the player shows a Back control that returns to the exact step.
- Deck level: `settings.theme` is `default`, `consulting` (dense panels, index tabs on top, solid key-message bar) or `executive` (storytelling, spotlight, chapter tabs at the bottom). `version` and `css` are optional. Put a client's exact brand colors in `css` by overriding the variables below; do not edit the bundled presets.

### Allowed markup

The builder converts `html` into a validated element tree, so only these are accepted:

- HTML: `div span p h2–h5 ul ol li dl dt dd table thead tbody tfoot tr th td caption col colgroup strong em b i u s small sup sub mark br hr figure figcaption section article header footer aside blockquote`, `button` (only with `data-goto`), `img` (only `data:image/` sources).
- SVG: `svg g path rect circle ellipse line polyline polygon text tspan defs linearGradient radialGradient stop clipPath mask pattern marker title desc use symbol`.
- Attributes: anything except `on*` handlers. Links and `href` may only point to `#ids`; no remote URLs anywhere, including `style` and `css`.
- Not allowed: `script style iframe object embed link meta form input video audio a`. Interaction comes from the player.
- A scene may hold up to 4,000 elements and 400 KiB. Move detail into a backup scene.

### Your own design (preferred) and the optional kit

Design the deck for its content first (see "Design each deck for its content" in SKILL.md). Write your own classes in the deck `css` and use them in scene HTML; target one scene with `[data-scene="scene-id"] …`. Use host design skills when available. The kit below is a shortcut for common parts, not a required look.

Deck and inline CSS run offline and are validated: no `@import`, `@font-face`, remote `url()`, `image-set()`, backslash escapes or comments. Write characters literally (`content:"—"`, not `"\2014"`), embed images as `data:image/…`, and keep `@keyframes` finite with a `@media (prefers-reduced-motion: reduce)` fallback.

### Component kit

All classes use CSS variables (`--k-accent --k-accent-dark --k-accent-2 --k-soft --k-ink --k-muted --k-line --k-panel --k-bg --k-warn --k-good --k-bad --k-radius`, charts `--chart-1…6`).

| Need | Markup |
|---|---|
| Panel layout | `k-grid cols-2 / cols-3 / cols-4 / cols-2-1 / cols-1-2`, `rows-2`, `span-2`, `row-span-2`; `k-stack`, `k-row`, `k-fill` |
| Panel | `<section class="k-panel">` (+ `soft`, `dark`, `accent`), header `<h3 class="k-panel-head"><span class="k-icon">↗</span>Title<small>note</small></h3>` |
| Big number | `k-hero` tile; `k-kpis` > `k-kpi` with `k-kpi-label`, `k-kpi-value` (+ `k-kpi-unit`), `k-delta up/down` |
| Table | `<table class="k-table">`; `th/td.num` right-aligned numbers; `tr.hl` highlight; `tr.total` total row |
| Labels | `k-chips` > `k-chip`, `k-tag`, `k-badge`, `k-note`, `k-list` (bulleted), `k-insight` (`<b>시사점</b> text`) |
| Status timeline | `k-timeline` > `k-tl-item` (`now`, `next`) with `k-tl-date` and `k-tl-body` |
| Gantt | `<div class="k-gantt" style="--cols:10">` then header `k-gantt-h` cells (first cell empty), rows of `k-gantt-label` + `k-gantt-bar` placed with `style="grid-column:3/6"` (column 2 = first period); bar variants `alt`, `soft`, `milestone` |
| Process | `k-flow` > `k-flow-step` (`active`) with `<b>` and `<small>` |
| Progress | `<div class="k-progress"><i style="--v:62%"></i></div>` |
| Chart | `<div class="k-fill" data-chart='{"type":"bar","data":[…]}'></div>` — any chart type above, plus `waterfall` |

Waterfall data starts with a total and continues with signed deltas: `{"label":"기존","value":26.0,"kind":"total"}, {"label":"설비","value":4.2}, {"label":"예비비","value":-0.6}, {"label":"최종","value":32.4,"kind":"total"}`. The running total may not go below zero. Recompute the closing total yourself; the validator does not know which total is intended.

Draw custom diagrams (buildings, layouts, flows) directly in inline SVG. Keep text in `<text>` elements so it stays searchable and printable.

### Quality bar for composed scenes

- One conclusion per screen; every panel supports it with different evidence (trend, table, breakdown, status).
- The deck should not look like one template repeated: vary composition, scale and density by what each scene has to prove.
- Numbers in the title, summary bar, panels and charts must match each other and the source. Report them in numeric verification.
- Use steps for the order of explanation: what happened → why → what we propose. Do not split a screen into steps that carry no new point.
- Check every step at 1600×900 in a browser: no clipped tables, no overlapping chart labels, no empty half-panels.

## Review in the browser: edit and memo modes

Every built deck includes a review toolbar (set `settings.review` to `false` for a read-only deck):

- **Edit (E)**: shows every step and turns text into plain-text fields. Reviewers can change titles, summary bars, panel text, card labels and the key message in place. Structure, styles and chart data stay locked.
- **Memo (M)**: click any element to leave a change request ("shorten this", "check the source", "use a bar chart"). A numbered badge marks it.
- **Review**: lists edits and memos, flags edits that changed numbers, and offers **Save edited HTML** (a new offline file that reopens with the edits and memos) and **Export changes (JSON)** (`deck-edits.json`).

When the user returns a `deck-edits.json`:

```text
python <skill-directory>/scripts/apply_edits.py work/deck.json deck-edits.json --notes work/review-notes.md
```

- Text edits are applied only where the source still holds the text the reviewer saw; others are reported as conflicts. Resolve conflicts by asking the user.
- Address each memo in `review-notes.md`, then rebuild.
- An edit that changed digits does not update charts, bar widths or totals. Re-run numeric verification, update the related chart data yourself, and report it as Needs review until checked.
- Tell the user which edits were applied, which memos were addressed, and what still needs their decision.

## Build and check

Every step has a link: `presentation.html#scene=<scene-id>&step=<n>` opens that step directly (also useful for sharing "look at this" links).

```text
python <skill-directory>/scripts/build_deck.py <work/deck.json> --output <output/presentation.html>
```

The builder validates data and embeds CSS, player JavaScript and JSON into one UTF-8 HTML file. It treats content as text rather than executable HTML and does not import source images or notes automatically. The delivered source and media still require appropriate review for the intended audience.

Check syntax and model validity first, then capture every step:

```text
python <skill-directory>/scripts/capture_steps.py <output/presentation.html> --out <output/shots> [--reduced] [--pdf <output/presentation.pdf>]
```

It opens each step in a local Edge/Chrome/Chromium (standard library only), saves PNGs, prints the deck to PDF on request and lists elements that leave the slide or are clipped inside a panel in `report.json`. Look at every PNG yourself; an empty issue list does not prove the layout is right.

Then open the HTML through an authorized browser workflow. Inspect every step at the actual target size; check for clipping and errors. Exercise direct jumps from Contents, multiple question bookmarks, latest-mark return, bookmark-list selection and keyboard-only operation. Open and close each supporting resource after marking a question, then confirm the exact reveal and marks remain. Browser verification is not provided by these scripts. Print / PDF previews all scenes with every item visible, one scene per A4 landscape page. Reduced-motion and explicit motion=none show all items in the current scene while preserving its navigation step. A saved PDF still needs separate rendering/page-count inspection. MP4 export is deferred.
