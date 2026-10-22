# Verification record

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
| Claude Code and Codex complete PPT-to-HTML sessions | Not verified |
| Claude source review | Received a read-only review of four public source files. Confirmed issues in keyboard routing, line breaks and hidden/SmartArt handling were corrected; browser behavior still requires verification. Reported garbled text was a command-pipe encoding issue rather than damage to the UTF-8 source files. |
| GitHub repository and Pages deployment | Public repository created on 2026-10-22. GitHub Pages build and deployment succeeded from main/docs. Korean and English landing pages and motion galleries included. |
| GitHub Actions checks | Initial run passed tool tests and artifact validation; ZIP byte reproducibility differed across Windows/Linux. Packaging now fixes ZIP platform attributes and uses stored entries. Follow-up CI result is recorded in the repository Actions tab. |
| Public-site browser QA | Not completed: opening the public origin was denied by the browser approval gate; no workaround attempted. |
| English localization | Landing page, starting prompt, motion-story text and controls, plus license explanation localized. English motion build checked for remaining Korean text. |

The sample source is independently authored Markdown. The synthetic extractor fixture is not presented as a real PowerPoint or a full conversion example. A new fictional PPTX and permitted browser QA are still required for broader release claims.

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
