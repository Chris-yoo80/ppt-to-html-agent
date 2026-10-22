# Bundled tools and scene authoring

Use these helpers when a portable starter presentation meets the brief. Resolve paths relative to this skill's directory. They use Python's standard library and do not call an AI API.

## Read a PPTX

```text
python <skill-directory>/scripts/extract_pptx.py <input.pptx> --output <work/source.json>
```

The extractor follows presentation relationship order, not slide filenames. It reads shape text, preserves paragraph-internal line breaks, reads tables and speaker notes, flags hidden slides and inventories linked media. It does not copy media into the output. SmartArt relationships are listed with a warning; their text is not extracted. Treat notes as private input and do not automatically put hidden slides into the audience's presentation. Confirm their intended use if relevant. It cannot render slides, perform OCR, interpret chart workbooks, read legacy PPT, or open encrypted/DRM sources. Obtain an owner-exported accessible source when required; do not claim that raw extraction preserves visual hierarchy.

## Author scene JSON

The AI reads the extracted material and authors the outline; the builder does not autonomously decide the narrative. Store the brief, source trace and editable JSON in the user's working folder.

On Windows, preserve UTF-8 when transferring Korean or other non-ASCII text through PowerShell. Do not pipe a non-ASCII Python program into Python under the default console encoding. Write a UTF-8 script file, use ASCII `\uXXXX` escapes, or explicitly set the pipe encoding first. After text edits, read the saved JSON and HTML back and compare the requested string exactly; a successful build alone does not detect replacement `?` characters.

```json
{
  "title": "Presentation title",
  "settings": {"width":1600,"height":900,"font":"system","motion":"key","playback":"both","end":"stop"},
  "scenes": [{
    "id":"overview",
    "eyebrow":"01 / Overview",
    "title":"One clear message",
    "lead":"Why this matters",
    "layout":"flow",
    "motion":"lines",
    "motion_caption":"Illustrative process",
    "items":[{"label":"Start","body":"Source-supported explanation"},{"label":"Finish","body":"Source-supported explanation"}],
    "message":"The audience's takeaway",
    "source":"Source slide 2",
    "duration":7
  }]
}
```

- `font`: `system` (system Korean sans-serif), `serif` (system serif), or `story` (bundled Story Sans review subset derived from Pretendard). The subset covers the current public example; other characters fall back to system fonts. Use a suitably licensed complete font for arbitrary documents needing consistent typography. Custom font packaging requires adapting the source and checking redistribution permission; the dropdown request alone does not install a font.
- `motion`: `none`, `key` (diagram motion), `rich` (also animate cards). Scene motion is `none`, `points`, `lines`, or `planes`. Other custom motion requires additional implementation.
- `playback`: `manual`, `both`, `auto`. All support visible previous/next controls. `end` is `stop` or explicitly requested `loop`.
- Each scene contains 1–4 concise items. Each item is one reveal step. Split dense material into scenes without omitting source qualifications. Title and message are required. Optional textual fields must be plain strings, not HTML.
- The player offers a small set of layouts, not a general-purpose PPT renderer. `cards` and `flow` use a list with an optional diagram; `compare` uses a two-column card grid. Design and implement additional layouts when the brief requires them.
- Treat 1600×900 as the supplied starter's design basis. Alternate ratios, long text and other fonts require visual checking and may require CSS changes.
- `duration` is seconds per reveal step, from 3 to 120. It must be long enough to read that step.

## Build and check

```text
python <skill-directory>/scripts/build_deck.py <work/deck.json> --output <output/presentation.html>
```

The builder validates data and embeds CSS, player JavaScript and JSON into one UTF-8 HTML file. It treats content as text rather than executable HTML and does not import source images or notes automatically. The delivered source and media still require appropriate review for the intended audience.

Check syntax and model validity first, then open the HTML through an authorized browser workflow. Inspect every step at the actual target size; check for clipping and errors. Browser verification is not provided by these scripts. Print CSS is only a convenience for the current scene; a fully verified multipage print/PDF export is not implemented. MP4 export is deferred.
