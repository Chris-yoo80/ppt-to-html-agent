# Excel intake and English preview update

The actual fictional workbook is `examples/marketing-analysis/campaign-source.xlsx`. The automated workbook check compares every cell in its 24 source rows with the reviewed JSON records, then checks cached totals and ROAS. This check passed again with the other eight Python tests. Earlier workbook rendering/recalculation and browser checks are recorded in `browser-verification-2026-10-23.md`. Microsoft Excel desktop execution was not tested.

The skill now explicitly asks for the workbook attachment/local path, sheets/ranges, output placement (Additional resources, standalone HTML, or both), related presentation scene/topic, and resource tab label. This is a host-agent conversation instruction, not a website upload widget. The changed intake instruction has been inspected but has not been retested in a new Claude/Codex conversation. The bundled resources button is presentation-wide; scene-specific buttons need separate implementation.

Public marketing demo links and the shared preview image now use the English example. The replacement image was captured from the actual local Edge browser after applying the English initial setup. The controls, charts, 24-record count, ROAS 5.87 and conversion 4.64% appeared in English. Korean HTML manuals and optional Korean examples remain available.
