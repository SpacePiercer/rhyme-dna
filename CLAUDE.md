---
title: CLAUDE
type: note
permalink: rhyme-dna/claude
---

# CLAUDE.md — Verse DNA

Bootstrap script. Loaded by the Claude Code harness before every session.
Sole job: invoke caveman mode and load the knowledge-base MANIFEST.
All project knowledge, navigation, and context live in basic-memory — not here.

@CONSTITUTION.md

---

## Startup — MANDATORY

**Do not answer any user request before completing both steps.**

1. Invoke the `/caveman` skill — every session runs in compressed-communication mode
2. Call `read_note "rhyme-dna/manifest"` — then follow every step in its startup sequence

If basic-memory MCP tools are unavailable, fall back to reading `docs/DECISIONS.md`,
`docs/ROADMAP.md`, `docs/GLOSSARY.md`, `docs/LESSONS.md` directly, then proceed.

---

## Operational constants

These live here because the harness needs them, not because they are knowledge.

### Running the notebook

```
conda run -n mfa_env jupyter nbconvert --to notebook --execute rhyme-DNA.ipynb --output rhyme-DNA.ipynb --ExecutePreprocessor.timeout=120
```

### Code style

- Python only for the core pipeline
- All logic in `python/` as importable modules; notebook imports from there
- No logic inside notebook cells — cells call functions, functions live in `.py` files
- Every function gets a docstring
- Debug output via `debug=False` parameter, not commenting/uncommenting

### Git workflow

#### Branches and PR titles

Format: `class(number)-short-description` for branches, `class(number): Short description` for PR titles.

| Class | Use for | Numbered by |
|---|---|---|
| `milestone` | implementing a milestone from `docs/ROADMAP.md` | milestone number |
| `docs` | planning/documentation changes only (no code) | sequential from 1 |
| `glossary` | updates to `docs/GLOSSARY.md`; merged *after* the related milestone (Rule 10) | sequential from 1 |
| `fix` | bug fix | sequential from 1 |
| `refactor` | restructuring without behaviour change | sequential from 1 |
| `chore` | maintenance — config, tooling, dependencies | sequential from 1 |

Examples:
```
Branch:   m10-ipa-switch          PR title: milestone(10): IPA Switch
Branch:   d1-roadmap-restructure  PR title: docs(1): Roadmap Restructure and Workflow
Branch:   f1-oud-ound-clustering  PR title: fix(1): Correct -oud / -ound cluster separation
Branch:   g1-m11-panphon-terms    PR title: glossary(1): M11 panphon terms and decision backlog
```

Create the branch before writing any code. Merge to `main` only when work is complete and tested.

#### Mid-milestone doc updates

Rule/doc changes during a milestone → separate `docs(N)` branch off `main` → merge first → rebase milestone branch onto updated `main` → resume.

#### Commits

Commit after every self-contained change. A commit should be reviewable in under two minutes. Remind the user to commit if significant code was written with no commit yet.

#### GitHub CLI

Always use `gh` CLI for all GitHub interactions. Repo: `SpacePiercer/rhyme-dna`.

**Never merge a PR** — user always merges manually. Do not run `gh pr merge` or any merge command. Create/update PR → report it ready → stop.

**Always include the PR URL** in your message when creating or updating a PR.

#### Pull request template

One PR per milestone. PR title: `Milestone N: Short description matching roadmap heading`.

```
## Motivations
Why this change was needed.

## Changes
What was built or modified. Bullet list of files/functions changed.

## Testing
How the change was verified — test verses, accuracy results, spot-checks.

## Considerations
Trade-offs, known limitations, deferred items.
```

Populate from `rhyme-dna/roadmap` and `rhyme-dna/decisions` when creating a PR.
