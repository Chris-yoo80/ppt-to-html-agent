# Install and try the skill

Status: early preview. A fictional five-slide input/build/revision workflow was tested in Claude Code and Codex CLI. The marketing supporting HTML and parent presentation were also exercised in Edge; see the [browser record](browser-verification-2026-10-23.md) for scope and limits. These tools do not connect to an AI API. Actual agent execution uses your existing AI environment and its applicable subscription or usage charges.

Self-contained user manuals: [English HTML](guide.en.html) / [한국어 HTML](guide.ko.html). They are also included as additional HTML inside the marketing presentation example.

Use is governed by the project-specific [Community License 1.0](../LICENSE). Personal, noncommercial and internal company use is free. Selling the tool or operating an external generation/conversion business requires separate written permission. Completed presentations may be shared for the purposes in the presentation output exception, with retained notices. This package is source-available, not MIT or OSI-approved open source.

Run the commands below from the repository root. Use Python 3.10 or newer for the helper scripts. Node.js is only needed for the JavaScript syntax checks in development.

## Codex — project scope

PowerShell:

```powershell
New-Item -ItemType Directory -Force .agents/skills | Out-Null
Copy-Item -Recurse skills/ppt-to-html .agents/skills/
```

macOS / Linux:

```sh
mkdir -p .agents/skills
cp -R skills/ppt-to-html .agents/skills/
```

Open Codex in this repository and request `$ppt-to-html`. For another working repository, copy the complete skill folder to that repository's `.agents/skills/` instead. Keep its scripts, assets and references together.

## Claude Code — project scope

PowerShell:

```powershell
New-Item -ItemType Directory -Force .claude/skills | Out-Null
Copy-Item -Recurse skills/ppt-to-html .claude/skills/
```

macOS / Linux:

```sh
mkdir -p .claude/skills
cp -R skills/ppt-to-html .claude/skills/
```

Open Claude Code in the repository and request `/ppt-to-html`. For another working repository, use that repository's `.claude/skills/` directory. This package does not install or authenticate Claude Code or Codex.

## ZIP alternative

Download `docs/downloads/ppt-to-html.zip`. It contains a `ppt-to-html/` folder. Unpack that whole folder into `.agents/skills/` for Codex or `.claude/skills/` for Claude Code. Keep the scripts, assets and references together. This is a portable folder package, not a claim that every ChatGPT or Claude interface accepts the same ZIP import.

## First request

```text
Use the ppt-to-html skill to turn my attached PPT into an HTML presentation.
Ask me the required settings first: purpose, audience, time, dimensions,
fonts, motion frequency, playback mode and point-line-plane graphics.
Then propose an outline and representative scene before building the rest.
Preserve the source's figures and meaning. No MP4 export is needed.
```

The website's local brief form can create a Korean version with your settings. It does not upload a PPT or contact an AI service.

## Try the tools without AI

```text
python skills/ppt-to-html/scripts/build_deck.py examples/library/deck.json --output output/library.html
```

Open the resulting HTML in an allowed browser. The file contains the player and styles and has no external fonts or script dependencies. Use the visible arrows or keyboard arrows, Home, End and A (when autoplay is enabled). The final step stops by default. Browser or embedding policies may restrict fullscreen.

For an accessible PPTX:

```text
python skills/ppt-to-html/scripts/extract_pptx.py private-inputs/input.pptx --output work/source.json
```

This command extracts text, tables, notes and a media inventory. It does not create the story outline. Ask the agent to interpret the extracted content, consult source slides where available, and author scene JSON before running the builder.

## Privacy and publishing

Keep private inputs, extracted notes and generated client presentations out of the public repository. `private-inputs/`, `work/` and `output/` are ignored convenience folders; `.gitignore` is not a content audit. Review explicit file lists before committing. Do not initialize a repository in a parent folder containing business materials.

Other ChatGPT or Claude surfaces may support different installation and execution mechanisms. No compatibility claim is made for untested environments.
