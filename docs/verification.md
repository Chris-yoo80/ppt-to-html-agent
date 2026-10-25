# Verification record

Latest: [real Edge browser verification and marketing supporting HTML, 2026-10-23](browser-verification-2026-10-23.md). The dated table below preserves the earlier 2026-10-22 check scope; previously blocked browser items are superseded only where the new record explicitly reports an observation.

Local checks completed on 2026-10-22. This is an early preview, not an end-to-end compatibility certification.

| Check | Result |
|---|---|
| Skill frontmatter and basic structure | Passed bundled skill validator |
| PPTX relationship order, Unicode text, table data, notes separation, hidden-slide flag, SmartArt warnings and media inventory | Passed in-memory synthetic OOXML test |
| Paragraph-internal line breaks and tabs | Passed preservation test |
| Scene validation for invalid dimensions, duplicate IDs, empty items, nonfinite duration and unsupported layout | Passed |
| User text remains data rather than executable HTML | Passed inert-content generation test |
| Player and website JavaScript syntax | Passed Node.js syntax checks |
| Fictional library demo | Built from committed scene JSON; 3 scenes, 9 reveal steps |
| Local HTML links and resources | Website, motion gallery, library starter and license page checked for local targets |
| Skill ZIP | Public-source entries, license and bundled font notices are compared byte-for-byte by check_release.py |
| License propagation | Root, portable skill and website copies matched; generated HTML retained the notice and complete license |
| Typography | Website and demo use bundled Story Sans review subsets derived from Pretendard 1.3.9, with regular/bold font files and retained SIL OFL notices; browser appearance remains unverified |
| Motion-story data and geometry | Four Node tests passed: complete delivery coverage, computed fictional route-length reduction, route interpolation and terminal phase bounds |
| Motion build safety | Python tests check invalid route plans, inert labels and legal notices in the motion gallery |
| Motion scenes | Hand-authored delivery, marketing and warehouse presets built with 24-second timelines; browser rendering, actual playback and scrubbing have not been independently verified |
| Known internal company terms and paths | No matches in 29 public text files after license updates; this is a targeted scan, not proof of all possible sensitive-data absence |
| Browser rendering, clipping, controls and fullscreen | Not verified: local HTML navigation was blocked by browser tool policy; no bypass was attempted |
| Claude Code and Codex PPT-to-HTML CLI workflow | One fictional five-slide fixture completed in both CLIs, including intake, extraction, build, source fidelity and requested revision. See [the dated acceptance report](acceptance-2026-10-22.md) for the encoding repair, Claude continuation and unverified browser scope. |
| Claude source review | Received a read-only review of four public source files. Confirmed issues in keyboard routing, line breaks and hidden/SmartArt handling were corrected; browser behavior still requires verification. Reported garbled text was a command-pipe encoding issue rather than damage to the UTF-8 source files. |
| GitHub repository and Pages deployment | Public repository created on 2026-10-22. GitHub Pages build and deployment succeeded from main/docs. Korean and English landing pages and motion galleries included. |
| GitHub Actions checks | Initial run passed tool tests and artifact validation; ZIP byte reproducibility differed across Windows/Linux. Packaging now fixes ZIP platform attributes and uses stored entries. Follow-up CI result is recorded in the repository Actions tab. |
| Public-site browser QA | Not completed: opening the public origin was denied by the browser approval gate; no workaround attempted. |
| English localization | Landing page, starting prompt, motion-story text and controls, plus license explanation localized. English motion build checked for remaining Korean text. |

The sample source is independently authored Markdown. The synthetic extractor fixture is not presented as a real PowerPoint or a full conversion example. A new fictional PPTX and permitted browser QA are still required for broader release claims.

## Feedback 1: numeric verification

[한국어 검수 기록](verification.ko.md). This section records the 2026-10-25 review change; the older dated records below/above retain their own scope. Only task 1 is included. Tasks 2–5 await separate review.

Generated HTML carries `metricMetadata` with source units, denominators, scope, display divisors/precision and rounding policy. The evidence dialog exposes these definitions and the current filters. Metadata alone does not certify source agreement. Every final delivery report must use the checklist below, marking **Passed or Needs review**, with evidence for every row. Missing definitions or unperformed checks remain Needs review.

| Item | Fictional marketing fixture result | Evidence / limits |
|---|---|---|
| Units and conversion | Passed: source money is KRW; counts are counts; rates are % and ROAS x. | Campaign!D1/H1 say KRW. All 24 rows match the JSON. Korean money ≥10,000 KRW uses /10,000 with max 1 decimal; English money ≥1,000,000 uses /1,000,000 with max 2 decimals. Below thresholds: whole KRW. Trend axes use those divisors with max 1 decimal. Rates: max 2 decimals. These are explicit display conversions, not identical unit labels. |
| Denominators | Passed for this fixture's implemented definitions. | ROAS = 197,711,000 / 33,661,480 = 5.873508829677126 (display 5.87x). Purchase conversion = 3,383 / 72,906 = 4.640221655282144% (display 4.64%). Each channel uses its own spend/clicks denominator. Zero denominator is unavailable. Workbook cached ROAS and source totals are compared; arbitrary workbook metric definitions still need review. |
| Filters / ranges | Passed for reviewed rows and model selections. | Campaign!A1:H25: four week-start labels (2026-09-07/14/21/28), three channels, two markets, 24 rows. 2026-09-07 + Search + Domestic selects one row: spend 2,592,000; revenue 7,946,000; clicks 3,600; orders 137; ROAS 3.07x, conversion 3.81%. Empty-selection and channel-group tests also run. Week labels are week starts, not inferred campaign end dates. |
| Rounding | Passed for source sums and tested display cases. | Aggregate raw values first. Total revenue displays as KRW 197.71M / 19,771.1만원. Channel revenue labels sum to those displayed totals in this fixture (104.37+61.83+31.51=197.71M). A new fictional edge case verifies that separately rounded parts can differ (2.30+4.10+1.40 vs total 7.81 million) without changing source totals. No forced reconciliation. |
| Source provenance | Passed in generated metadata and evidence output. | Source preserved as campaign-source.xlsx / Campaign!A1:H25. Metadata contains the source reference and cannot silently override the starter's numerator/denominator definitions. Conflicting metadata and hostile source strings are tested. |

Automated scope: Python source-row/cache, metadata/schema and inert-output checks; Node weighted sums, same-group denominators, filters, zero denominators and rounding checks. This is a controlled fictional fixture, not a universal workbook converter. Excel desktop execution and saved-PDF inspection were not performed. The new task-2 motion/print retention checks are not included in this task.

Local Edge observation: the new English evidence dialog showed all 24 records and exact source totals. Filtering to 2026-09-07 + Search + Domestic updated the evidence to one row (spend 2,592,000; revenue 7,946,000; orders 137; clicks 3,600). The Korean view showed the same row with the /10,000 display policy. Clearing all channels showed none / zero rows and zero source sums. The dialog was visually inspected; screenshot: [numeric review](assets/feedback1-numeric-review.jpg). These observations cover the new evidence UI, not a new full-browser regression suite. All six Development checks passed; the full local suite passed 11 Python + 15 Node tests. Static generated-output, local-link and 34-entry package checks passed. No push, merge or deployment was performed.

## Reproduce

From the repository root:

```text
python -m unittest discover -s tests -v
node --check skills/ppt-to-html/assets/player.js
node --check docs/site.js
python skills/ppt-to-html/scripts/build_deck.py examples/library/deck.json --output docs/library-demo.html
python tools/localize_site.py
python tools/package_skill.py
python tools/check_release.py
```

User working decks belong outside the public example tree. The release candidate contains newly authored guidance, code and fictional content, not copies of existing business presentations or embedded media.

## Feedback 1 extension: physical, compound and business units

The earlier marketing result table covers its currency/count/rate model only. The checklist now explicitly covers length, area, volume, mass, time, speed, energy/power and compound/business units. [New fictional unit cases](../examples/unit-verification/README.md) and [generated report](../examples/unit-verification/report.json) are paired with Korean documentation.

`unit_audit.py` checks declared source/display values, dimensions, exact conversion factors, optional display rounding and required source references. There are 14 new fictional comparisons: ten supported arithmetic checks pass; four intentionally remain Needs review (m→m², missing box definition, unknown crate unit, temperature offset). The report's overall status is Needs review. These are JSON source values, not a fabricated Excel verification claim.

Tests additionally cover reverse length conversion, squared/cubed factors, energy versus power, person versus item, currency mismatch, months, malformed units, missing provenance, invalid values, explicit business definitions and caller-supplied false passes. Optional `unitChecks` are recomputed by the analysis builder; evidence output and saved HTML retain them. No unit checks supplied means no automated unit-audit claim.

Limits: whitelisted conversions only, not every possible unit. No inferred box size, density, month length, temperature offset or exchange rate. Campaign charts remain KRW-based; generic physical-quantity chart conversion needs a tested adapter. Arithmetic passes do not verify workbook extraction, definitions, filter scope, denominator semantics or final rendering. Each of those still needs its own evidence.

Extension checks passed: all six required Development checks, 19 Python tests and 15 Node tests, analysis UI syntax and generated artifacts/package consistency (35 skill entries). In local Edge, a temporary fictional UI fixture showed supported length/area/defined packing conversions as Passed, and dimension mismatch/missing definition/unknown crate/temperature as Needs review, in both Korean and English. The fixture HTML remains ignored test material. [Observed unit evidence](assets/feedback1-unit-review.jpg). No push, merge or deployment was performed; task 2 has not started.

## Feedback 2: essential content with motion off and in print

| Subject | Result | Evidence |
|---|---|---|
| Delivery story | Passed for static summary/runtime contract | 12 stops, 3 vehicles and the computed 34% fictional coordinate-length reduction remain alongside the title, explanation, four phases and qualifications at the start and final frame. |
| Marketing story | Passed for static summary/runtime contract | All four counts (1,200 / 360 / 72 / 24) and 6.0% reach-to-purchase conversion remain, including after the animated headline changes. A separately authored fixture checks new counts and 6.7% rather than hard-coded defaults. |
| Warehouse story | Passed for static summary/runtime contract | All four process steps and the title/explanation/fictional qualification remain. The summary does not invent measured throughput or capacity. |
| Marketing presentation (KO/EN) | Passed for tested scenes | Reduced-motion and motion=none expose all current-scene cards; tests cover every title, number, item explanation, message and source. Print preview contains all three scenes/all nine items in normal and reduced modes. |
| Playback and navigation | Passed in runtime tests; selected cases observed in Edge | Startup/mid-session reduced-motion stops frames/autoplay; phase jumps and timeline seek still work. Returning from print preserves story/time or step and stays paused. Removing reduced motion does not auto-resume. |

The checklist and final-report instructions now include a sixth item: **motion-off/print retention of essential figures and explanations**. The gallery adds a static Key facts summary, Turn motion off control and Print / PDF preview of all three summaries. These HTML text summaries print independently of SVG opacity and current timeline position. Korean/English guides, README and landing pages were regenerated from their sources.

Local Edge observations: manual motion-off, all marketing funnel counts at phase 1, all three summary blocks visible in print preview without horizontal overflow, preview starting at scroll position 0, and return to Marketing at 6 seconds with playback paused. A temporary ignored motion=none presentation showed all four KPI cards with opacity 1 and aria-hidden=false at step 3/9; its print preview retained every scene. Screenshot: [motion print preview](assets/feedback2-motion-print.jpg).

Limits: operating-system prefers-reduced-motion startup/change is simulated in the Node runtime tests, not a claim that the OS preference was changed in Edge. SVG geometry methods are stubbed in runtime tests; existing pure-geometry tests remain separate. Actual saved-PDF rendering/page count is still unverified. The three-summary/three-scene counts refer to HTML previews. A full cross-browser or physical mobile audit was not performed.

Local validation: all six required Development checks; 20 Python + 28 Node tests; JS syntax, generated-output consistency and 35-entry skill package checks. No push, merge or deployment. Task 3 awaits user review of task 2.
