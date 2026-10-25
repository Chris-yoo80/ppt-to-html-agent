# Fictional unit verification

[한국어](README.ko.md)

All 14 comparisons in `checks.json` are newly authored fictional values. That JSON is the source; the `sourceRef` JSON pointers refer to its own rows and packing definition. No real workbook or company data is included. These examples validate declared comparisons, not automatic extraction from Excel.

```text
python skills/ppt-to-html/scripts/unit_audit.py examples/unit-verification/checks.json --output examples/unit-verification/report.json
```

| Comparison | Result |
|---|---|
| 1.25 m → 1,250 mm | Passed |
| 2 m² → 20,000 cm² | Passed; scale factor is squared |
| 2.5 L → 0.0025 m³ | Passed |
| 1,200 kg → 1.2 t | Passed |
| 90 min → 1.5 h | Passed |
| 36 km/h → 10 m/s | Passed |
| 720 item/h → 12 item/min | Passed |
| 800 KRW/kg → 0.8 KRW/g | Passed |
| 1 kWh → 3,600,000 J | Passed |
| 3 boxes → 24 items with a fictional 8-items-per-box definition and reference | Passed |
| 1 m → 1 m² | Needs review: incompatible dimensions |
| 3 boxes → 24 items without a packing definition | Needs review: missing definition |
| crate → crate | Needs review: unsupported business unit, even though the labels match |
| °C → K | Needs review: affine temperature conversion is unsupported |

Overall report: **Needs review**, intentionally. Inspect every row, not just the CLI exit code. Values, unit labels, dimensions, conversion factors and definition references are retained. A Passed result covers arithmetic with declared inputs only; source extraction and semantic agreement still require review. Calendar months, exchange rates, density-dependent conversion and unknown units are not inferred.

To add these comparisons to a campaign HTML, put the list under the optional `unitChecks` key in its reviewed JSON. `build_analysis.py` computes and embeds `unitAudit` and the evidence dialog displays the results. It does not turn the KRW campaign charts into length/mass charts. Saved HTML retains the audit. Use a separately tested adapter for a different chart/data model.
