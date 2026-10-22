# Acceptance test: fictional PPTX and Excel workflows

Date: 2026-10-22. Local acceptance testing after the initial public preview.

## PPTX in Claude Code and Codex CLI

Both installed, authenticated CLIs were tested using the packaged skill ZIP in isolated project folders. The input was a newly authored five-slide Korean presentation with a native comparison table and a test-only speaker-note marker. No company deck or media was used.

| Check | Claude Code | Codex CLI |
|---|---|---|
| Discover the project-local skill and read its instructions | Passed | Passed |
| Ask required settings when they are absent; do not build yet | Passed | Passed |
| Extract five slides in order, the comparison table and separate notes | Passed | Passed |
| Build five HTML scenes with 17 reveal steps from the supplied brief | Passed | Passed |
| Retain table row associations, 120/90 km, 240/180 minutes, 12 stops, three vehicles, 60 parcels and the fictional 25% comparison | Passed | Passed |
| Retain exclusions and avoid treating fictional plans as measured improvement | Passed | Passed |
| Keep speaker notes out of audience JSON and HTML | Passed | Passed |
| Generated HTML exactly matches its editable JSON and bundled builder | Passed | Passed |
| Change the first title, disable motion and retain playback/end settings | Passed | Passed after an encoding repair |
| Outline and verification records delivered | Passed after continuation | Passed |

The build prompt supplied all settings and explicitly pre-approved the fixture outline and representative layout. This exercises that permitted shortcut; it does not establish that a separate representative-scene approval interaction works in every host.

The first Codex revision saved the Korean title as replacement question marks while claiming success. Independent read-back caught the mismatch. The authoring reference now explains UTF-8 PowerShell transfer and exact read-back checks. A second host revision preserved the exact requested title. This is a single observed repair, not proof against all encoding failures.

Claude's initial build hit the test runner's 16-turn limit after writing the result. A continuation completed the outline and checks; the later revision completed successfully. A clean one-pass conversion within that original budget is not claimed.

The new PPTX passed package, five-slide count, font and native-table structure validation and Artifact Tool re-import. All five source-slide renders were inspected. PowerPoint itself was not opened. Host inputs had the same text, table and note content as the finalized fixture; the source fixture's font metadata was corrected during preparation.

Four additional Node tests exercise the actual player JavaScript against a minimal DOM double: all forward/backward reveals, keyboard behavior after button focus, single-timer autoplay with end stop, hidden-tab pause and replay. They are logic tests, not browser, accessibility or layout verification.

## Current supplemental analysis

The public supplemental example is now fictional marketing analysis, with left-side controls and right-side visual results, embedded in a presentation together with bilingual HTML guides. See [the 2026-10-23 browser record](browser-verification-2026-10-23.md) for the actual observations and remaining limits.

Raw host transcripts remain in ignored local working folders. Only sanitized records and reusable tests are intended for publication.
