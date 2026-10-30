# Design sources

Use these to choose a visual direction that fits the content. Two kinds of source exist, and they are handled differently:

- **Look only**: study layout, hierarchy, color and rhythm, then rebuild with newly authored HTML/CSS/SVG. Never copy text, images, icons, templates, DOM or CSS from these.
- **Reuse under license**: code, icons, palettes or data can be embedded if the license allows it. Before reusing, open the source, confirm the current license, and record it in `design-reference.json` (Reference Design Mode). Keep required notices in the deck. Licenses below were correct when written; the source is authoritative.

Prefer installed design skills first (for example frontend-design for the overall direction, ui-ux-pro-max for style/palette/type options, dataviz for chart choice and color). Then use this list for anything they do not cover.

## Look only

| Need | Where to look |
|---|---|
| Presentation layouts and pacing | Pitch, Gamma and Beautiful.ai template galleries; Slidesgo; SlidesCarnival |
| Web/UI composition and type | Dribbble, Behance, Awwwards, Land-book, Godly |
| Report and consulting style | Public reports from consulting firms and research institutes; The Economist and Financial Times graphics |
| The user's own decks | Files the user provides; follow their confidentiality and keep them out of public repositories |

## Reuse under license

| Need | Source | License (verify before use) |
|---|---|---|
| Chart choice | Financial Times Visual Vocabulary (chart-doctor) | check the repository; use as guidance |
| Chart patterns | Apache ECharts examples | Apache-2.0 |
| Chart patterns | Vega-Lite examples | BSD-3-Clause |
| Design systems | IBM Carbon (including data-visualization guidance) | Apache-2.0 |
| Design systems | Material components | Apache-2.0 |
| UI patterns | shadcn/ui, Tabler | MIT |
| Icons (inline SVG) | Lucide | ISC |
| Icons (inline SVG) | Tabler Icons, Heroicons | MIT |
| Illustrations | unDraw | unDraw license (free, no attribution) |
| Illustrations | Storyset | free with attribution |
| Slide-engine themes | Reveal.js, Slidev | MIT |
| Color palettes | Coolors, Adobe Color | color values are free to use |
| Fonts | Google Fonts, Pretendard | mostly SIL OFL 1.1 |

## Constraints in this player

- Composed scenes accept inline SVG, so licensed icons and illustrations can be pasted as SVG markup. Remove scripts, event handlers and external `href`s first; the validator rejects them.
- Deck CSS cannot load fonts (`@font-face` is blocked). Use system fonts, or the bundled `story` font setting. For a specific typeface, ask the user and say it is not embedded yet.
- Everything stays in one offline file: no CDN links, remote images or web fonts.
- Name the sources and skills used in the final report: Reference / Inspected / Applied / Excluded / License or permission.
