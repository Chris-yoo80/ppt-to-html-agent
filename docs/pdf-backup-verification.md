# PDF printing and backup resource verification

## Implemented behavior

- Initial intake asks whether PDF output is needed, which backup files to include, where they belong, their related topic/scene, and their tab labels. It reuses settings already supplied. The changed conversation instructions have not been rerun in a new host-agent conversation.
- Presentation Print / PDF opens a preview with every reveal visible, one complete scene per A4 landscape page. The next button invokes the browser print dialog; users choose its PDF destination. Opening the preview pauses playback and preserves the current step.
- Supporting analysis has its own print preview with the current period, market, channels and hypothetical multipliers recorded as text. It prints selected optional sections separately. Resources are not automatically merged into the deck PDF.
- The example now includes a real Backup: source & calculations tab with the 24 fictional source rows and the weighted-rate definitions. Both language manuals describe printing and backup selection. Raw PPT/Excel files are not attached automatically.
- Embedded resource sandboxes allow modal printing but retain their separate origin (no allow-same-origin permission).

## Actual local Edge observations

- Starting on presentation step 2/9 with autoplay enabled, opening print preview produced three scene pages and nine visible items. Every item had aria-hidden=false. Each scene's scroll dimensions matched its 1600 x 900 stage dimensions, without overflow. Playback was paused and the current step remained 2/9.
- The English print preview was visually inspected and captured in `assets/print-preview.jpg`.
- A Domestic analysis print preview displayed its exact filter context and 12 records, with spend KRW 21.72M and revenue KRW 127.46M. Its controls were replaced by a return/print toolbar.
- The backup tab contained 24 table rows. Switching back preserved the 12-record analysis; closing resources returned to step 2/9 with autoplay paused. Captured in `assets/backup-tabs.jpg`.
- Invoking native printing blocked browser DOM commands until the print dialog was dismissed/reloaded. The available browser surface does not expose the operating-system PDF save dialog or native print preview. Therefore actual saved PDF page count and final PDF rendering remain unverified; the three-page observation refers to the HTML print preview, not an inspected PDF file. Public-origin browser and file-protocol limitations from the earlier record still apply.

## Automated checks

The added player test checks all scenes/reveals, step preservation and playback pause when printing. All nine Python tests and fourteen Node tests passed locally. Static release/package checks also passed. These do not replace actual saved-PDF inspection.
