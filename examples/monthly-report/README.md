# Repeatable monthly sales report

This example uses newly authored fictional data. It contains no company, customer or internal figures. September and October use the same five-scene presentation structure: title, executive summary, channel mix, weekly timeline and conclusion.

Generate both months and both languages:

```sh
python tools/build_monthly_report.py
```

Generate only a new month after adding `examples/monthly-report/YYYY-MM.json`:

```sh
python tools/build_monthly_report.py --month YYYY-MM
```

The command also creates a matching `YYYY-MM.xlsx`, bilingual presentation JSON and offline HTML. Review the workbook and JSON together before publishing. Do not reuse a prior month's totals.

## Numeric verification

| Item | September | October | Evidence |
|---|---|---|---|
| Unit | Passed | Passed | Revenue and AOV use KRW; orders use count. Korean displays KRW ÷ 10,000 as 만원; English displays KRW ÷ 1,000,000 as KRW M. |
| Denominator | Passed | Passed | AOV = total revenue ÷ total orders. Channel share = channel revenue ÷ monthly revenue. |
| Filter / range | Passed | Passed | `Sales!A1:D13`; four week labels and three channels, 12 rows per month. |
| Rounding | Passed | Passed | Raw integers are aggregated first. Money is rounded to one decimal only for display; raw KRW remains in source text. |
| Provenance | Passed | Passed | Every scene names `YYYY-MM.xlsx / Sales!A1:D13`. |
| Motion off / print | Passed by shared player tests | Passed by shared player tests | All titles, values, descriptions and sources are HTML text in the final reveal and print copies. Saved-PDF layout remains a separate visual check. |

Reviewed totals: September has **1,218 orders**, **KRW 70,995,000 revenue** and **KRW 58,288.18 AOV**. October has **1,471 orders**, **KRW 91,607,000 revenue** and **KRW 62,275.32 AOV**. Workbook-to-JSON and generated-output agreement are covered by the test suite.

[September HTML](../../docs/monthly-report-2026-09.en.html) · [October HTML](../../docs/monthly-report-2026-10.en.html) · [한국어 설명](README.ko.md)
