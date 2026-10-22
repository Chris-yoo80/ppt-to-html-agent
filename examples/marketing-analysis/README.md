# Fictional campaign analysis supplement

All 24 records were independently authored for this project. No company workbook, customer data or business media was reused. Currency: KRW. Weeks begin 2026-09-07, 09-14, 09-21 and 09-28, spanning through 2026-10-04. The sample is not a measured campaign.

`campaign-source.xlsx` contains the same records on `Campaign!A1:H25`. Its SUM and ROAS formulas were recalculated with Artifact Tool and compared with an independent sum. `data.json` is the reviewed typed input to the supporting HTML builder. No arbitrary Excel formula execution is implemented.

The separate `presentation.ko.json` / `presentation.en.json` outlines are authored examples, not outputs of an automatic PPT conversion. Their generated presentation embeds the marketing HTML and a matching HTML user guide in Additional resources. It preserves the current reveal when closed and pauses autoplay when opened.

Rebuild from the repository root:

```text
python tools/build_guides.py
python tools/build_marketing_examples.py
```

The starter uses left-side period/channel/market controls and optional what-if assumptions. Right-side visuals show weighted totals, a trend, illustrative funnel widths with exact count labels and channel ROAS. Scenarios keep original records intact and are explicitly hypothetical. CSV export controls do not remove the data embedded in HTML.
