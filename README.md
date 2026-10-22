# PPT to HTML Presentation Agent

**Motion you can pause. A story you can explain.**

A source-available agent skill for turning slide content into interactive HTML presentations. Play a process continuously, pause at the point that matters, or explain it one phase at a time. Designed for Claude Code and Codex; end-to-end host verification is pending.

[한국어](README.ko.md) · [Install](docs/install.md) · [Verification](docs/verification.md) · [Release status](docs/release-plan.md)

![Conceptual preview of delivery routes, a marketing funnel and an isometric warehouse](docs/assets/motion-preview.svg)

## See the motion

| Story | What unfolds | Controls |
|---|---|---|
| Delivery network | Orders → regions → prescribed routes → moving vehicles | Play, pause, four phase jumps, scrub |
| Marketing journey | Reach → engagement → conversion → return flow | Play, pause, four phase jumps, scrub |
| Warehouse operations | Receiving → storage → picking → shipping | Play, pause, four phase jumps, scrub |

Each story lasts 24 seconds and stops at the end. The illustration above is a static preview; open `docs/index.html` in an allowed browser for the interactive gallery. [Try the English demo](https://chris-yoo80.github.io/ppt-to-html-agent/index.en.html) · [한국어](https://chris-yoo80.github.io/ppt-to-html-agent/).

The scenes and data are fictional and hand-authored. The delivery percentage compares prescribed paths on an invented coordinate plane; it is not an optimizer performance result. The gallery demonstrates controllable HTML motion, not a completed automatic PPT-to-HTML run.

Build the self-contained motion gallery with Python 3.10+:

```sh
python skills/ppt-to-html/scripts/build_motion_demo.py examples/motion-stories/stories.json --output output/motion-stories.html
```

Open `output/motion-stories.html`; no runtime server, framework, AI key or network connection is needed for this prebuilt fictional gallery. Running the agent on your own PPT uses your existing AI environment and its applicable charges.

## What you get

- A skill package: instructions, references, Python helpers and a self-contained HTML player.
- A brief before building: audience, duration, dimensions, fonts, motion frequency and playback.
- PPTX extraction: text, tables, speaker notes and media inventory, in presentation order.
- A portable starter: the agent writes scene JSON; the builder renders an offline HTML file.
- Simple motion graphics: point entrances, connecting lines and plane reveals, with reduced-motion handling.
- A motion gallery: fictional delivery routes, a marketing funnel and an isometric warehouse, with continuous playback, four phase jumps and timeline scrubbing. These are hand-authored presets, not automatic PPT conversion or an optimization solver.
- A smaller library example remains as a starter for the scene-JSON builder.
- A static introduction page: demo and local prompt generator. No upload form, AI connection, tracking or runtime CDN dependencies.

The Package is source-available under the project-specific [Community License 1.0](LICENSE), with free personal, noncommercial and internal organizational use. Reselling the tool, including it in a paid tool, or operating an external generation/conversion business requires separate written permission. Completed presentation outputs can be shared and delivered for reporting, proposals, training and customer presentations under the output exception. Retain legal notices. This is not MIT or an OSI-approved open source license. [한국어 사용 조건](docs/license.ko.md)

These are project-specific terms, not independently reviewed standard-license advice. AI subscriptions and API usage follow your provider's terms.

The website and fictional demo use Story Sans, renamed character subsets derived from Pretendard 1.3.9. These font files retain their separate [SIL Open Font License](skills/ppt-to-html/assets/fonts/OFL.txt) and are not relicensed under the Community License. They cover the current demo; other characters fall back to the system font. The `story` preset embeds the font files and notices in the generated HTML.

## How the agent works

```text
PPTX → extract source → ask the brief → propose scenes
     → review a representative scene → author HTML → verify → refine
```

The host AI interprets the source and designs the narrative. The scripts do not call an AI model or automatically invent a scene plan. Preserve source figures and meaning, mark illustrative material, and ask only for missing preferences.

## Try the builder

Python 3.10+; standard library only:

```sh
python skills/ppt-to-html/scripts/build_deck.py examples/library/deck.json --output output/library.html
```

Open `output/library.html` in an authorized browser. It embeds its content, CSS and JavaScript. Use the visible controls or arrow keys to progress; the last step stops.

Extract an accessible PPTX:

```sh
python skills/ppt-to-html/scripts/extract_pptx.py private-inputs/input.pptx --output work/source.json
```

This extracts source information, including potentially private notes. It does not build the narrative. [Install the skill](docs/install.md) and ask the agent to turn the extracted material into a reviewed scene plan. Keep business input and output outside public commits.

## Start a presentation

```text
Use the ppt-to-html skill to turn my PPT into an HTML presentation.
Ask about the audience, time, screen size, fonts, motion frequency,
playback and point-line-plane graphics before building.
Show me the outline and one representative scene first.
```

The [intake reference](skills/ppt-to-html/references/intake.md) defines the starting questions. The generated HTML uses finite SVG/CSS animation rather than an exported video. A [portable skill ZIP](docs/downloads/ppt-to-html.zip) contains the license, skill instructions, references, scripts and assets; see the installation guide for where to unpack it.

## Website and demo

`docs/index.html` is a buildless GitHub Pages introduction page. `docs/demo.html` is generated from `examples/motion-stories/stories.json`; `docs/library-demo.html` retains the smaller starter. The website builds a request prompt locally; visitors run the actual agent in their own AI environment.

After the public repository is created, enable GitHub Pages from `main` → `/docs`. Hosting setup and publication are not complete. The tentative public repository name is `ppt-to-html-agent`.

## Current limits

- No pixel-perfect PPT rendering, image OCR, chart workbook interpretation, legacy `.ppt`, or encrypted/DRM document reader.
- The starter supports 1–4 short items per scene, cards/flow/compare layouts and three diagram styles. Richer layouts and custom fonts require additional implementation.
- Extraction has synthetic fixture tests. The library example demonstrates JSON-to-HTML generation, not a complete PPT-to-HTML conversion.
- Static and syntax checks do not prove visual quality. Browser layout, interaction, accessibility and alternative ratios still require verification.
- Claude Code and Codex end-to-end compatibility is pending. Other ChatGPT/Claude surfaces are not claimed as supported.
- MP4 export, a hosted AI conversion app and verified multipage PDF output are deferred.

## Development checks

```sh
python -m unittest discover -s tests -v
node --check skills/ppt-to-html/assets/player.js
node --check docs/site.js
python skills/ppt-to-html/scripts/build_deck.py examples/library/deck.json --output docs/library-demo.html
python skills/ppt-to-html/scripts/build_motion_demo.py examples/motion-stories/stories.json --output docs/demo.html
node --test tests/motion.test.cjs
```

The CI workflow also checks the motion runtime's JavaScript syntax, geometry tests and generated artifacts.

## Contributing

Useful contributions include fictional PPTX fixtures, reproducible layout failures, better scene templates and host-specific installation feedback. Include target dimensions, reproduction steps and expected behavior. Do not submit client decks, internal figures, speaker notes, credentials or proprietary media.
