# Reference Design Mode

Use this mode when the user provides a website, GitHub repository, HTML file, screenshot, or named visual reference. A reference guides a new design; it is not permission to clone a page.

## Intake

Record these answers in the working brief:

1. Reference source: URL, repository, local HTML/image path, or preset.
2. Apply: overall mood, color, typography, layout, cards/charts, motion, navigation, or selected scenes.
3. Similarity: `inspiration` (recommended), `layout`, or `code`.
4. Permission: visual inspiration only, verified reusable license, user-owned, or Needs review.

If a URL cannot be opened in the host, ask for an HTML export or screenshot. Do not claim that the reference was inspected when it was not. Never request credentials for a private reference; use a user-provided accessible export.

## Bundled presets

The presets contain newly authored design rules, not third-party code or assets.

| Preset | Public references | Apply | Exclude |
|---|---|---|---|
| `slide-story` | Reveal.js and Slidev | large type, chapter rhythm, progressive reveal | logos, themes, example content |
| `dashboard` | Tabler | KPI hierarchy, filter rail, card spacing | icons, brand assets, demo data |
| `data-motion` | Apache ECharts | chart emphasis, staged data transitions | library bundle, copied option objects |
| `hybrid` | all of the above | presentation narrative + dashboard evidence + restrained motion | all third-party branding and sample data |

Run `scripts/reference_design.py --list` to inspect the exact catalog. The source links and license identifiers are evidence for the reference catalog only. They do not prove that arbitrary files copied from those projects are compatible with this Package.

## Analysis output

Create a design-reference manifest before authoring the representative scene. It must include:

- source and inspection status;
- chosen preset or custom reference;
- elements to apply and elements to exclude;
- similarity level and permission/license status;
- extracted design tokens: palette, typography scale, radii, spacing, chart treatment and motion behavior;
- runtime dependency policy (`none` for offline single-file output).

Use the bundled helper for a consistent manifest:

```text
python <skill-directory>/scripts/reference_design.py --preset hybrid --source "https://example.com/reference" --apply "layout,cards,charts,motion" --output work/design-reference.json
```

For visual inspiration, omit `--license` and keep the default `--reuse inspiration`. For copied code or assets, use `--reuse code`, provide `--license` and `--license-url`, preserve all required notices, and verify compatibility separately. The helper records declarations; it does not fetch a page or perform legal review.

## Authoring rules

1. Inspect the source only through host capabilities and record what was actually seen.
2. Extract abstract rules rather than copying DOM, CSS, branding, text, icons, images or example data.
3. Show the user a short application note and one representative scene before extending the style.
4. Rebuild patterns with project-owned HTML/CSS/SVG. Keep the output self-contained and offline.
5. Preserve source facts, accessibility, reduced-motion, print, contents and question-bookmark behavior.
6. Add a design-reference note to editable sources and the final report. Do not put implementation or license commentary into the audience-facing presentation unless requested.

Final reports state: **Reference / Inspected / Applied / Excluded / License or permission / Runtime dependency / Needs review**.
