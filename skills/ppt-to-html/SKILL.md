---
name: ppt-to-html
license: See LICENSE for internal-use terms and the presentation output exception.
description: Reconstruct PPT or PPTX material as an interactive HTML presentation with staged reveals and optional point-line-plane motion graphics. Use for presentation conversion and iterative editing, rather than pixel-perfect PPT reproduction or unrelated website creation.
---

# PPT to HTML presentation agent

Use the user's source material to build an HTML presentation with deliberate narrative and interaction. Preserve source meaning and distinguish sourced facts from illustrative data.

## Establish the brief

Read [references/intake.md](references/intake.md) before starting a new deck. Ask the required settings together in a short numbered form. Reuse settings already supplied; ask only for missing values. Let the user choose the recommended preset as one answer. Do not start rendering a new deck until these settings are answered or the user explicitly delegates their choice. Continue source inspection while awaiting answers.

Inspect the source with the tools available in the host. Extract text, tables, figures, slide order and relevant notes; use slide rendering when available to inspect spatial relationships. Report unavailable extraction or rendering capabilities. Do not claim extraction succeeded when only part of the source was read. For unreadable sources, identify the specific limitation and request an accessible export.

For accessible PPTX inputs and the bundled HTML starter, read [references/authoring.md](references/authoring.md). It documents the extraction and build commands, supported scene format, and actual tool limitations. The host AI performs interpretation and planning; the builder renders an authored outline.

## Plan and create

Map source slides to proposed HTML scenes. Identify the key message, evidence, reveal steps and suitable motion for each scene. Keep figures, units and assumptions traceable to the source. Mark sample data explicitly; do not invent results or introduce business assertions as facts.

For a new visual direction, present the scene outline and one representative scene before extending it to the whole deck. Reuse prior approval during later edits. Ask about material changes to scope, claims or narrative; decide routine implementation details independently.

Use HTML/CSS/SVG and local resources where they meet the brief. Preserve aspect ratio, make Korean wrapping readable, and make scene and substep navigation predictable. Separate editable content from playback logic where practical. Provide visible previous/next controls and usage instructions. Use an explicitly chosen end behavior rather than assuming the deck should loop.

When motion is requested, read [references/motion.md](references/motion.md). Treat motion amount and playback mode as separate settings. A single-file offline requirement includes fonts, images and other dependencies; avoid external runtime dependencies under that requirement.

For video-like delivery, marketing or warehouse process scenes, read [references/motion-stories.md](references/motion-stories.md). The bundled presets provide continuous playback and phase control with editable fictional data; they are not optimization solvers or simulations of a real operation.

For Excel-based charts, interactive slicers or supporting/backup analysis, read [references/supplemental-analysis.md](references/supplemental-analysis.md). Ask for the workbook location, sheets/ranges, and where the resulting analysis should appear (Additional resources, standalone HTML, or both), including its related scene and tab label. Reuse answers already given. Establish the analysis brief before building, start with left-side controls and right-side visual results when requested, and add advanced features after the base is agreed. Deliver the analysis as additional HTML accessible from the presentation; do not silently replace the presentation or attach the raw workbook.

## Verify and deliver

Ask about PDF output and backup resource files, placement and tab labels in the initial brief. The bundled Print / PDF button prints all scenes with every reveal visible, one scene per A4 landscape page. Supporting analysis prints its current filters and optional sections separately; resources are not automatically merged into the deck PDF. Preserve the presentation step and pause autoplay after printing. Verify print layout and page count separately from interactive playback.

Check source fidelity, every scene/substep, forward/backward transitions, direct scene navigation, timers on scene changes, replay and end behavior. Check text clipping, overflow, keyboard access and reduced-motion behavior at the agreed output size. For a requested print/PDF mode, inspect the rendered output separately from presentation screenshots.

Distinguish static checks from browser checks. If the host cannot render or operate the output, name the limitation and list the unverified behaviors; do not describe the presentation as visually verified. Do not bypass tool security restrictions to obtain rendering access.

Deliver the HTML, editable sources and brief operation notes supported by the actual implementation. Report what was tested and what remains unverified. Do not claim MP4 export, installed dependencies, offline support or host compatibility without checking them.

Keep the Package's LICENSE with copies of the skill and retain the builder's embedded legal notice and license text in presentation outputs. Personal, noncommercial and internal organizational use is permitted without a fee; external generation businesses and paid redistribution of the tool require separate permission. Completed presentations can be shared for the communication purposes in the output exception. A visible author watermark is a separate design choice, not a requirement of this license.

## Publishing examples

User-provided decks are working inputs, not automatically public examples. When preparing this project's public repository, exclude company documents, embedded images/videos, notes, hidden data, internal paths and derived business content. Use independently authored fictional examples. Do not publish or push as part of an ordinary conversion request.
