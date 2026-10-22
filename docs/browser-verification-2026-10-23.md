# Real-browser verification: supporting marketing HTML

Date: 2026-10-23 (Asia/Seoul). Browser: the user's installed Microsoft Edge, controlled through the browser extension. Tests loaded the application from an explicit localhost server serving only the public `docs/` directory. This is actual browser interaction, distinct from Node DOM-double tests.

## Delivered scope

The marketing analysis is supporting HTML within a presentation, not a separate hosted AI conversion application. Additional resources contains the analysis and the matching Korean/English HTML guide. A standalone analysis file is also supplied. The published dataset contains 24 independently authored fictional campaign records and a matching sample XLSX; no company workbook or private operating model is included.

## Observed checks

| Check | Browser observation |
|---|---|
| Initial brief | Setup dialog showed purpose, priority metrics, viewing context, typeface and CSV controls. Applying it opened the analysis. |
| Brief changes | Selecting serif and conversion priority applied the serif class and highlighted the conversion KPI. The final saved HTML retained those settings and the bilingual text catalog. |
| Desktop composition | Left-side controls/slicers; right-side KPIs, trend chart, funnel counts and channel comparison. Actual desktop page width was 1897 CSS pixels with no document-level horizontal overflow. |
| Full-source totals | 24 records; source ad spend KRW 33,661,480; revenue KRW 197,711,000; ROAS 5.87×; conversion 4.64%. |
| Slicer intersection | First week + Search + Domestic showed one source record: KRW 2,592,000 spend, KRW 7,946,000 revenue, 137 purchases / 3,600 clicks, ROAS 3.07×, conversion 3.81%. |
| Empty selection | Clearing the remaining channel showed an explicit no-records message, unavailable KPI markers and zero detail rows. |
| Scenario slider | Enabling assumptions and setting spend to 200% retained source spend/revenue and separately showed KRW 5,184,000 / 15,892,000 scenario values for that one record. Source ROAS stayed unchanged. |
| Optional detail | Detail toggle showed the exact selected source row; reset restored all 24 source records and default assumptions. |
| Data export controls | CSV export was disabled by default and enabled only after the setup choice. Hiding these buttons is not a data-removal mechanism. |
| Real CSV download | Browser produced the source CSV. A separate filesystem check compared all 24 rows and each value with the original reviewed JSON. |
| English UI | Language switch translated controls, headings, metric labels and disclosures; source numeric metrics stayed consistent. |
| Save HTML | Browser produced a standalone English HTML containing the selected Domestic filter and full legal notice. Saved bytes were inspected independently. Browser-extension elements were excluded from the saved document. |
| Parent presentation | Opening Additional resources while playing changed autoplay from true to false. Embedded analysis displayed ROAS 5.87×. Closing returned to step 2 / 9 and remained paused. |
| HTML guide | The guide opened as another additional-HTML tab inside the presentation. |
| State persistence | Selecting Domestic, switching to the guide and back retained 12 records and did not repeat the setup dialog. Closing/reopening resources retained the same analysis state. |
| Escape | Escape closed the supporting dialog and returned to the same presentation step. |
| Responsive layout | Real-browser iframe QA used outer frames of 390×844 and 1600×900 CSS pixels. Actual content widths after scrollbars were 375 and 1585 pixels, with equal scroll widths (no document-level horizontal overflow). Narrow controls reflowed and KPIs stacked. This is iframe layout testing, not a physical mobile-device test. |

The advertised top-level viewport override did not change the observed Edge page width. Responsive tests therefore used explicitly sized, real-browser iframes and recorded their actual content widths, rather than claiming device emulation.

## Corrections made during testing

- Supporting iframe reloads originally discarded the brief and filters. Each resource now keeps its own sandboxed frame for the current presentation session.
- The initial narrow layout stretched Reset and scaled chart tick labels too small. Reset alignment and the chart coordinate/font sizing were corrected.
- Saving a live DOM could copy browser-extension elements and omit an outside-document license comment. Saved HTML now keeps only the application's known elements and retains an embedded license template.
- Exported rate checks use floating-point tolerance; row values and counts are checked exactly.

## Automated evidence

- Nine Python tests cover existing extraction/build behavior plus supporting-HTML isolation, campaign build validation and every sample XLSX row/cached formula total against reviewed JSON.
- Five Node campaign tests cover weighted metrics, exact slicer intersections, empty denominators, immutable scenarios and grouping/invalid data.
- Existing four motion-geometry tests and four player DOM-double tests remain separate from actual browser observations.
- Release checks compare generated HTML, bilingual guides and portable skill ZIP entries with their sources.

## Explicitly unverified

- Direct browser inspection of the deployed `chris-yoo80.github.io` origin was denied by a saved site-permission policy. No alternate fetch/control path was used to bypass it. GitHub's checks and Pages deployment for runtime commit `dd89c6a` both succeeded; these backend signals are distinct from opening the live URL in a browser.
- Opening the downloaded file through `file://` was denied by the browser URL policy (HTTP/HTTPS only). No alternate control path or serving of the downloaded file was used to bypass that block. Real direct-file/offline reopening remains unverified, although saved content/state and self-contained resources were checked.
- Native PowerPoint/Excel execution, Safari/Firefox, physical mobile devices, exhaustive accessibility and arbitrary workbook formulas/macros/external connections.
- The old motion-gallery's complete continuous timeline and all fullscreen cases are not certified by this marketing-specific check.

Screenshot: [actual desktop Edge capture](assets/marketing-dashboard.jpg). Source records and workbook are in `examples/marketing-analysis/`. No raw host logs, local paths or authentication output are included as public evidence.
