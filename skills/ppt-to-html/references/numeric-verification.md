# Numeric verification before delivery

Compare the output to the authorized workbook and its metric definitions. Generated metadata describes the implemented starter, not proof of source agreement. Never mark an item Passed just because the HTML builds or contains definitions. If source definitions or browser evidence are unavailable, use Needs review and identify what is missing.

| Item | Verify against the source |
|---|---|
| Units | Verify all numeric quantities: length, area, volume, mass, time, speed, energy/power, currencies, %/x, counts, compound and business units, chart axes and export headers. Record source/display units, dimensional meaning, factor, rounding and definition source. Area/volume factors are squared/cubed. Unknown definitions remain Needs review. |
| Denominators | Match the intended population: all records, channel-specific, market-specific, etc. ROAS here is revenue / spend; purchase conversion is orders / clicks, not impressions. Sum numerator and denominator in the same group before division. Zero denominators are unavailable. |
| Filters and ranges | Match sheet/range, periods, channels, markets, exclusion rules and aggregation grain. Check all records, a single row, a subset and an empty selection. Keep source and hypothetical results separate. |
| Rounding | Aggregate unrounded values; apply precision only for display. Compare totals before rounding and disclose any displayed-parts versus displayed-total gap. Never change source totals to hide it. |
| Motion off / print retention | Verify every scene title, essential number, explanation and qualification without animation and in print preview. Check initial and mid-session reduced motion, all three story presets and the marketing presentation. Preserve current step/time on return; leave autoplay paused. Saved-PDF layout requires separate inspection. |
| Provenance | Preserve the workbook sheet/range (e.g. Campaign!A1:H25) beside the value or on its evidence screen, including shared/offline output. |

Final reports must have one row for **each** item: **Item / Passed or Needs review / Evidence or unresolved issue** (Korean: **항목 / 통과 또는 확인 필요 / 근거·남은 확인**). A missing status is not a pass. Distinguish source calculation tests from browser observations; JSON/XML checks do not prove Excel desktop or saved-PDF behavior.

## Generic unit comparisons

Use `scripts/unit_audit.py` for declared comparisons beyond the KRW-only campaign formatter. It checks dimensions and exact rational conversions using Python's standard library: m/mm/cm/km, m²/cm²/mm², m³/L/mL, g/kg/t, s/min/h, km/h↔m/s, item/h, KRW/kg, Wh/kWh/J, W/kW, %↔ratio and KRW/thousand/ten-thousand/million KRW. Products use `*` or `·`, one `/`, and exponents `2`, `3`, `^2`, `^3`, `²`, `³`. Units are case-sensitive; unknown symbols (even matching source/display labels) need review. No arbitrary expression execution.

```text
python <skill-directory>/scripts/unit_audit.py unit-checks.json --output unit-report.json
```

Input: `{"checks":[{"sourceValue":"1.25","sourceUnit":"m","displayValue":"1250","displayUnit":"mm","sourceRef":"Measurements!A2:D2"}]}`. Optional `displayDecimals` (0–12) declares display-only rounding, half away from zero. Otherwise conversion must match exactly. Numeric strings use decimal points, no thousands separators. Status is Passed or Needs review with reason codes. Empty reports never pass. A successful CLI run can still contain Needs review; inspect every row, not just exit code.

Box/item/pallet conversion needs `businessConversion: {"factor":"12","sourceRef":"Packing!B2"}`: 12 target units **per one source unit**, tied to that comparison. It cannot override standard conversion or incompatible dimensions (m→m², kg→L without density, kW→kWh without time, person→item). Unknown business units need a tested adapter. Exchange rates, Celsius/Fahrenheit offsets, calendar months, density-based conversion and ambiguous syntax remain Needs review. Never assume packing counts or a 30-day month.

`build_analysis.py` optionally accepts `unitChecks` with that list and embeds a fresh `unitAudit`; it never trusts a supplied pass. The evidence dialog shows these results when supplied. This does not turn KRW campaign charts into a generic units renderer. Passes cover declared arithmetic/dimensions only; compare extraction, meaning and definitions against the workbook separately. Denominator semantics still need review even when both ratios are dimensionless.

## Campaign starter metadata

`build_analysis.py` embeds `metricMetadata` inside `script#analysis-data`: source units, rate numerators/denominators, same-group aggregation, scope/filter rules, language-dependent display divisors/precision and rounding policy. It does not mutate the input config and rejects conflicting supplied metadata. Changing a definition requires a separately tested model/formatter adapter, not just a new label.

The evidence dialog shows units/conversions, denominator definitions, selected scope/row count, rounding and source. Saved HTML retains the metadata with its current filters. For the fictional marketing fixture, compare all 24 rows to Campaign!A2:H25 and cached totals, then check an exact filtered row. Workbook definition text is agent-reviewed evidence; the starter does not parse arbitrary workbook definitions automatically.
