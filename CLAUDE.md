# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal collection of DevOps/security tool cheatsheets (`cheatsheet-files/*.md`) plus a one-line installer. There is no application code, no build system, no test suite, and no dependencies — contributions are almost always "add or edit a cheatsheet".

## Commands

```bash
mkdir -p ~/.cheats        # setup-cheatsheet.sh does NOT create it; cp fails if missing
./setup-cheatsheet.sh     # cp ./cheatsheet-files/*.md ~/.cheats/

./scripts/install-hooks.sh                      # one-time: core.hooksPath -> .githooks
python3 scripts/lint-cheatsheets.py             # lint every cheatsheet
python3 scripts/lint-cheatsheets.py <file.md>   # lint one file
python3 scripts/lint-cheatsheets.py --strict    # warnings become errors
python3 scripts/lint-cheatsheets.py --list-rules
```

`setup-cheatsheet.sh` is a plain overwrite copy — it does not sync deletions or renames out of `~/.cheats/`.

The `.githooks/pre-commit` hook lints staged `cheatsheet-files/*.md` and blocks the commit on errors (warnings pass). It lints the *staged blob*, not the worktree file, so partially staged edits are checked as they will actually land. Bypass with `git commit --no-verify`.

## Cheatsheet file format

Each file in `cheatsheet-files/` is consumed as a cheatsheet by the tool reading `~/.cheats/`, so the header structure matters more than prose quality. Follow the shape of an already-converted file (`helm.md`, `trivy.md`, `checkov.md`, `molecule.md`, `pip.md`, `qm.md`, `grype.md`, `playwright.md`, `crowdsec.md`):

```
# <Tool>

<One- or two-sentence description of what the tool does.>

#platform/multiple #target/<Domain> #cat/<Category>

% <tool>, <keyword>, <keyword>, <keyword>

## <Tool> - <Action in Title Case>

<One-line explanation.>

```
<command>
```
```

`scripts/lint-cheatsheets.py` enforces this; run `--list-rules` for the exact checks. Conventions observed across the converted files:

- The `%` line is the searchable keyword/tag line — always present, always after the `#platform/... #target/... #cat/...` line.
- Every entry heading is `## <Tool> - <Action>`; `###` is used only for sub-variants of a preceding `##` section (see `trivy.md` filtering/reporting sections).
- Code fences are unlabelled (```` ``` ````) in nearly every file; `trivy.md` mixes in ```` ```bash ````. Prefer unlabelled for consistency with the majority.
- Commands use `<placeholder>` angle-bracket style for user-supplied values.

## Known gaps

- `crowdsec-to-add.md` is unconverted raw notes, listed in `.cheatlintignore` so the hook does not block on it. Its content is a set of `cscli dashboard` commands that belongs in `crowdsec.md`; folding it in and deleting the file is the natural pickup work. Convert it, then delete its line from the ignore file.
- `trivy.md` uses ```` ```bash ```` fences where the rest of the collection uses unlabelled ones. This is a lint warning, not an error; left as-is pending a call on which style wins.
