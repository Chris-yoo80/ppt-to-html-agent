# Video-like motion stories

Read when the brief asks for continuous process explanation rather than simple
entrance effects. `scripts/build_motion_demo.py` builds the bundled gallery from
a collection JSON. It includes three fixed, editable presets, not an arbitrary
natural-language video generator or an optimization engine.

```text
python <skill-directory>/scripts/build_motion_demo.py <stories.json> --output <output/demo.html>
```

The collection requires delivery, marketing and warehouse stories. Each has
`label`, `eyebrow`, `title`, `lead`, `note`, and four `phases`. Collection
`duration` is seconds per entire story. Delivery specifies a hub, twelve stops,
and before/after plans of three routes that each cover every stop exactly once.
Marketing supplies four positive, nonincreasing fictional counts. Warehouse is
a fixed isometric layout that can be adapted in the editable SVG scene code.

The runtime offers continuous playback, pause, four phase jumps and timeline
scrubbing. A single animation-frame clock drives deterministic scene state;
changing story cancels the prior clock. Playback pauses when the page becomes
hidden or the demo leaves view, stops at the end, and does not autoplay under
prefers-reduced-motion. Browser behavior still needs visual verification.

Keep the note distinguishing a conceptual scene from computed or observed
results. In particular, do not describe prescribed routes as an algorithm's
optimization output or the warehouse illustration as a physical simulation.
Use measured results only when actual inputs and verified calculations exist.

To adapt these presets to a new source, map each phase to the source's argument,
review the storyboard and figures, then change geometry or labels as required.
Do not silently drop source qualifications to fit the scene. Keep fonts and
legal notices in the generated output. MP4 export remains outside this version.

## Facts without motion and printed output

Each preset has a generated static summary below the player containing its title,
lead, all four phases, source qualifications and key figures. Delivery includes
stops/vehicles and the computed coordinate-distance comparison; marketing keeps
all four counts and reach-to-purchase rate; warehouse lists four illustrative
process steps without inventing throughput. Summaries do not depend on SVG opacity,
timeline position or animation frames.

Turn motion off stops frames while keeping manual phase/timeline controls. System
reduced motion takes precedence and cannot be overridden by the toggle. Enabling
it during playback preserves the time and pauses; removing it does not auto-resume.
Print / PDF previews all three complete summaries, not an arbitrary video frame.
The browser print dialog can save those summaries; returning preserves story/time
and stays paused. Verify saved-PDF layout separately. Do not describe DOM-double
tests as visual or operating-system preference verification.
