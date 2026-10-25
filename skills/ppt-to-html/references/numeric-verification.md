# Numeric verification before delivery

Compare the output to the authorized workbook and its metric definitions. Generated metadata describes the implemented starter, not proof of source agreement. Never mark an item Passed just because the HTML builds or contains definitions. If source definitions or browser evidence are unavailable, use Needs review and identify what is missing.

| Item | Verify against the source |
|---|---|
| Units | KRW / thousand KRW / million KRW / % / x, counts, chart axes and export headers. When display units differ, show the conversion and verify the underlying value. |
| Denominators | Match the intended population: all records, channel-specific, market-specific, etc. ROAS here is revenue / spend; purchase conversion is orders / clicks, not impressions. Sum numerator and denominator in the same group before division. Zero denominators are unavailable. |
| Filters and ranges | Match sheet/range, periods, channels, markets, exclusion rules and aggregation grain. Check all records, a single row, a subset and an empty selection. Keep source and hypothetical results separate. |
| Rounding | Aggregate unrounded values; apply precision only for display. Compare totals before rounding and disclose any displayed-parts versus displayed-total gap. Never change source totals to hide it. |
| Provenance | Preserve the workbook sheet/range (e.g. Campaign!A1:H25) beside the value or on its evidence screen, including shared/offline output. |

Final reports must have one row for **each** item: **Item / Passed or Needs review / Evidence or unresolved issue** (Korean: **항목 / 통과 또는 확인 필요 / 근거·남은 확인**). A missing status is not a pass. Distinguish source calculation tests from browser observations; JSON/XML checks do not prove Excel desktop or saved-PDF behavior.

## Campaign starter metadata

`build_analysis.py` embeds `metricMetadata` inside `script#analysis-data`: source units, rate numerators/denominators, same-group aggregation, scope/filter rules, language-dependent display divisors/precision and rounding policy. It does not mutate the input config and rejects conflicting supplied metadata. Changing a definition requires a separately tested model/formatter adapter, not just a new label.

The evidence dialog shows units/conversions, denominator definitions, selected scope/row count, rounding and source. Saved HTML retains the metadata with its current filters. For the fictional marketing fixture, compare all 24 rows to Campaign!A2:H25 and cached totals, then check an exact filtered row. Workbook definition text is agent-reviewed evidence; the starter does not parse arbitrary workbook definitions automatically.
