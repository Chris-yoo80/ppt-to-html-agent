# Supporting analysis as additional HTML

Treat an interactive analysis as supporting material for the presentation, not as a replacement for its narrative. Keep a standalone supporting HTML and optionally embed it in the presentation's Additional resources dialog. Closing it returns to the current scene and reveal step; opening it pauses presentation autoplay. The viewer must explicitly resume playback.

## Agree on the basics first

Ask missing answers together, reusing anything already supplied:

1. What decision, audience and question should the analysis support? For example, campaign comparison, budget review or conversion analysis.
2. Which workbook/sheets, periods, categories, units and metric definitions are authoritative? Clarify the denominator and grouping before computing ratios.
3. Which inputs and slicers belong on the left? Which KPIs, charts or diagrams belong on the right?
4. What screen size, aspect ratio, typeface and language will be used? Recommended: responsive supporting view, system font, original units, desktop and narrow-screen checks.
5. Is the first version source analysis only, or should it include hypothetical scenarios? Keep assumptions and scenario results visibly separate from source values.
6. Which additional materials may be shared? Source-file attachment is opt-in at build time. HTML needs its chart data embedded to work offline; hiding an export button does not remove that data. Review notes, hidden sheets, personal data, internal paths and credentials before sharing.
7. Where should the Excel-based analysis appear: in the presentation's Additional resources dialog, as a standalone HTML link, or both? Ask which scene/topic it supports and the resource tab label. Separately ask where the source workbook is available (chat attachment or an accessible local path) and which sheets/ranges to use. Never assume an upload destination or attach the raw workbook. The bundled player provides a presentation-wide resources button; an in-slide chart or scene-specific button requires an explicitly implemented and verified extension.

Propose the basic layout and one representative chart first. Let the user accept the recommended settings in one answer. After the base is agreed, add requested detail tables, comparison cases, assumptions, exports or new charts in separate iterations, with checks of affected results. Reference interaction patterns without copying private data or substituting the reference's subject for the requested example.

## Campaign starter

Ask whether PDF output is required for the deck, supporting analysis, or both. The deck prints every scene with all reveals visible, one scene per A4 landscape page. The analysis prints the current filters and selected optional sections as static results. Each resource is printed separately; automatic merging of arbitrary backup HTML is not included. Ask for different page formats or inclusion requirements before adapting them. Backup resources use the existing labeled resource tabs, with up to eight reviewed HTML resources per deck. Ask which files, related topics, tab names and output placement the user wants. Raw PPT/Excel attachments remain opt-in.

`scripts/build_analysis.py` renders reviewed JSON records into an offline supporting HTML. Declare `fictional` as true or false and include a `source` reference. Required dimensions: `week`, `channel`, `region`; slicer values are derived from those records. Required nonnegative numeric metrics: `spend`, `impressions`, `clicks`, `orders`, `revenue`; counts must satisfy orders <= clicks <= impressions. The starter's currency is KRW; other currencies need an explicitly adapted and tested formatter. The host inspects the authorized Excel file and prepares this data model with source references. This tool does not execute arbitrary Excel formulas, macros or external connections.

```text
python <skill-directory>/scripts/build_analysis.py reviewed-campaign.json --output marketing-analysis.html
python <skill-directory>/scripts/build_deck.py deck.json --supplement "Marketing analysis=marketing-analysis.html" --output presentation.html
```

Use source totals to calculate weighted rates: ROAS = SUM(revenue) / SUM(spend), purchase conversion = SUM(orders) / SUM(clicks). A zero denominator is unavailable, not zero. Keep source rows unchanged when filtering or applying a scenario. The starter's what-if controls assume constant cost per click and channel mix; they are not a forecast. Disclose these assumptions. Other workbook structures need a deliberate, separately tested data/model adapter.

The supporting page starts with a setup dialog. Its optional CSV control only enables/disables export buttons; the analysis data remains in the HTML. Save HTML retains the current brief, filters and scenario settings without a server. Korean and English UI are included. Raw original workbooks are not automatically embedded.

## Verify in a real browser

Units are not limited to money. For physical/compound units and packing counts, use the generic unit comparison workflow in [numeric-verification.md](numeric-verification.md). The campaign starter remains KRW-based; optional `unitChecks` add declared comparisons to its evidence dialog, not new chart formats.

Apply [numeric-verification.md](numeric-verification.md): units/conversions, denominators, filters/ranges, rounding and provenance. Compare source totals and an exact filtered row, reporting each item as Passed or Needs review with evidence. Embedded `metricMetadata` describes implementation, not automatic workbook certification.

Check setup, filters including an empty selection, weighted totals, charts, assumptions, reset, language, optional detail, save/reopen, narrow-screen layout and reduced motion. In the parent presentation, check pause-on-open, resource selection, Escape/close, focus return and preservation of the current reveal. Avoid parent navigation shortcuts firing while a supporting dialog is open. Keep static/unit checks distinct from these browser observations.
