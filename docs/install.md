# Install and try the skill

[한국어](install.ko.md) · English

Status: early preview. A fictional five-slide input/build/revision workflow was tested in Claude Code and Codex CLI. The marketing supporting HTML and parent presentation were also exercised in Edge; see the [browser record](browser-verification-2026-10-23.md) for scope and limits. These tools do not connect to an AI API. Actual agent execution uses your existing AI environment and its applicable subscription or usage charges.

Self-contained user manuals: [English HTML](https://chris-yoo80.github.io/ppt-to-html-agent/guide.en.html) / [한국어 HTML](https://chris-yoo80.github.io/ppt-to-html-agent/guide.ko.html). They are also included as additional HTML inside the marketing presentation example.

Use is governed by the project-specific [Community License 1.0](../LICENSE). Personal, noncommercial and internal company use is free. Selling the tool or operating an external generation/conversion business requires separate written permission. Completed presentations may be shared for the purposes in the presentation output exception, with retained notices. This package is source-available, not MIT or OSI-approved open source.

## Before you start

- **Claude Code or Codex** must already be installed and signed in. This package does not install or authenticate either tool. Regular ChatGPT and Claude web chats cannot run this local skill.
- **Python 3.10 or newer** runs the bundled helpers. Check it in a terminal:

  | System | Check | Use in commands |
  |---|---|---|
  | Windows | `python --version` (or `py --version`) | `python` or `py` |
  | macOS / Linux | `python3 --version` | `python3` |

  If the command is not found, install Python from [python.org](https://www.python.org/downloads/). Examples in this repository write `python`; macOS/Linux users type `python3` instead.
- Node.js is only needed for development checks.

## 1. Get the skill

Download the [skill ZIP](https://chris-yoo80.github.io/ppt-to-html-agent/downloads/ppt-to-html.zip), or clone this repository. Either way you need the complete `ppt-to-html` folder: its `SKILL.md`, `scripts/`, `assets/` and `references/` must stay together.

## Easiest: ask the agent to install it

Unpack the ZIP anywhere (for example, your Downloads folder), open **your project folder** in Claude Code or Codex, and send:

```text
Install the ppt-to-html folder from my Downloads folder as a Claude Code skill for this project.
The result must be .claude/skills/ppt-to-html/SKILL.md, not one folder deeper.
Then check the path and tell me how to invoke the skill.
```

For Codex, write "Codex skill" and `.agents/skills/ppt-to-html/SKILL.md`. For every project, ask for `~/.claude/skills` or `~/.agents/skills` instead. The agent may ask permission to create folders and copy files. When it finishes, continue with [4. Check that it worked](#4-check-that-it-worked).

Simply asking the agent to read `SKILL.md` from an arbitrary folder can also work, but you must repeat it in every new conversation, `/ppt-to-html` and `$ppt-to-html` are unavailable, and the agent may skip the reference files. Installing is more reliable.

Prefer to copy the files yourself? Continue with steps 2–4.

## 2. Choose where to install it

| Host | One project only (inside your project folder) | Every project (your user folder) | Invoke |
|---|---|---|---|
| Claude Code | `.claude/skills/ppt-to-html/` | `~/.claude/skills/ppt-to-html/` | `/ppt-to-html` |
| Codex | `.agents/skills/ppt-to-html/` | `~/.agents/skills/ppt-to-html/` | `$ppt-to-html` |

`~` is your user folder: `C:\Users\<name>` on Windows, `/Users/<name>` on macOS, `/home/<name>` on Linux. "Your project folder" is the folder that holds your PPT/Excel work, not this repository.

**The correct result is always `.../skills/ppt-to-html/SKILL.md`.** `SKILL.md` must not be one folder deeper.

## 3a. Install from the ZIP (no terminal)

1. Open the destination from the table above. `.claude` and `.agents` start with a dot, so they are hidden by default:
   - **Windows:** File Explorer → View → Show → Hidden items. Create the folder if it does not exist.
   - **macOS:** press `Cmd+Shift+.` in Finder to show hidden folders. Finder may refuse names that start with a dot; use the terminal command in 3b if it does.
2. Extract the ZIP. It contains one `ppt-to-html/` folder.
   - **Windows warning:** "Extract All" suggests a new folder named after the ZIP, which produces `skills\ppt-to-html\ppt-to-html\SKILL.md`. Extract to the `skills` folder itself, or move the inner `ppt-to-html` folder up one level afterwards.
3. Confirm that `SKILL.md` sits directly inside `skills/ppt-to-html/`.

## 3b. Install with a terminal

Run these from **your project folder** (project scope). Replace `<download>` with the folder that contains the unpacked `ppt-to-html` folder, or with `<clone>/skills` if you cloned this repository.

Claude Code, PowerShell:

```powershell
New-Item -ItemType Directory -Force .claude/skills | Out-Null
Copy-Item -Recurse <download>/ppt-to-html .claude/skills/
```

Claude Code, macOS / Linux:

```sh
mkdir -p .claude/skills
cp -R <download>/ppt-to-html .claude/skills/
```

Codex: use the same commands with `.agents/skills` instead of `.claude/skills`.

For every project, replace `.claude/skills` with `~/.claude/skills` (Claude Code) or `~/.agents/skills` (Codex). In PowerShell, write `$HOME/.claude/skills` or `$HOME/.agents/skills`.

## 4. Check that it worked

1. Open your project folder in Claude Code or Codex. If the tool was already running, restart it.
2. Claude Code: type `/` and look for `ppt-to-html`. Codex: type `$` (or run `/skills`) and look for `ppt-to-html`.
3. Not listed? Check that the path ends in `skills/ppt-to-html/SKILL.md` (see the Windows warning above) and that you opened the folder where you installed it.

## Update or remove

To update, delete the existing `ppt-to-html` skill folder and install the new one. Copying over the old folder keeps files that a newer version removed. To remove, delete the `ppt-to-html` folder from `skills/`.

## First request

Put an accessible `.pptx` or `.xlsx` in your project folder, then send:

```text
Use the ppt-to-html skill to turn my attached PPT into an HTML presentation.
Ask me the required settings first: purpose, audience, time, dimensions,
fonts, motion frequency, playback mode and point-line-plane graphics.
Then propose an outline and representative scene before building the rest.
Preserve the source's figures and meaning. No MP4 export is needed.
```

Legacy `.ppt` and password-protected files are unsupported. The website's local brief form can create a version of this prompt with your settings. It does not upload a PPT or contact an AI service.

## Try the tools without AI

Run from a clone of this repository (macOS/Linux: `python3`):

```sh
python skills/ppt-to-html/scripts/build_deck.py examples/library/deck.json --output output/library.html
```

Open the resulting HTML in an allowed browser. The file contains the player and styles and has no external fonts or script dependencies. Use the visible arrows or keyboard arrows, Home, End and A (when autoplay is enabled). The final step stops by default. Browser or embedding policies may restrict fullscreen.

For an accessible PPTX:

```sh
python skills/ppt-to-html/scripts/extract_pptx.py private-inputs/input.pptx --output work/source.json
```

This command extracts text, tables, notes and a media inventory. It does not create the story outline. Ask the agent to interpret the extracted content, consult source slides where available, and author scene JSON before running the builder.

## Privacy and publishing

Keep private inputs, extracted notes and generated client presentations out of the public repository. `private-inputs/`, `work/` and `output/` are ignored convenience folders; `.gitignore` is not a content audit. Review explicit file lists before committing. Do not initialize a repository in a parent folder containing business materials.

Other ChatGPT or Claude surfaces may support different installation and execution mechanisms. No compatibility claim is made for untested environments.
