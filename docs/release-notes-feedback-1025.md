# Feedback update release notes (draft)

Branch: `feat/feedback-1025`  
Status: local commits only; not pushed, merged or deployed.

## What changed

- Numeric review now covers money, physical and compound/business units, denominator definitions, filter scope, display rounding and source sheet/range. Final agent reports must mark each check Passed or Needs review with evidence.
- Motion-off, reduced-motion and Print/PDF states retain essential titles, figures and explanations in the delivery, marketing, warehouse and presentation examples.
- The player adds a full scene/step Contents dialog and multiple exact-step question bookmarks. Shortcuts: `G` Contents, `B` mark, `Shift+B` list and `R` return.
- Korean and English READMEs and landing pages now show a three-step first-use path, correct Claude Code/Codex skill locations and tested limitations.
- A repeatable fictional monthly sales workflow adds two months of JSON and `.xlsx` source data, one shared five-scene generator, bilingual presentation JSON and four offline HTML outputs.
- A complete seven-scene fictional presentation demonstrates contents → overview → body → timeline → conclusion.

## Validation

- 23 Python tests passed.
- 30 Node tests passed: 12 motion and 18 player/analysis.
- All six required Development checks passed.
- Release validation passed for 22 HTML pages, 64 local references, deterministic motion output and 35 portable-skill ZIP entries.
- Skill validation passed.
- The revised monthly summary and timeline were visually checked in headless Microsoft Edge at 1600×900 after fixing overlap and clipping.

## Remaining limits

- Saved multipage PDFs, broad cross-browser behavior and physical mobile devices still need separate visual review.
- The extractor does not provide pixel-perfect PPT reconstruction, image OCR or arbitrary chart/workbook interpretation.
- Legacy `.ppt`, password-protected/DRM files, MP4 export and regular ChatGPT/Claude web-chat execution are unsupported.
- Numeric metadata and automated arithmetic do not replace comparison with the authorized source workbook.

## Commits

- `41416ab` — feedback#1: verify numeric units, denominators, filters and provenance
- `f8da506` — feedback#1: audit physical, compound and business unit conversions
- `9554469` — feedback#2: retain essential facts without motion and in print previews
- `d3ba474` — feedback#2: add a complete presentation showcase
- `88e5104` — feedback#3: add scene jumps and question bookmarks
- `a20f61b` — feedback#4: add a three-step quick start
- `24c103e` — feedback#5: add repeatable monthly sales reports

[한국어 릴리스 노트](release-notes-feedback-1025.ko.md)
### Reference Design Mode

- Added website, repository, local HTML/image, named-style, and preset references to the intake flow.
- Added four offline presets and a `design-reference.json` manifest with explicit applied/excluded rules.
- Added a license gate for code reuse; visual inspiration remains the default.
