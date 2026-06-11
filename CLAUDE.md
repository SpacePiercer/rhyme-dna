---
title: CLAUDE
type: note
permalink: rhyme-dna/claude
---

# CLAUDE.md — Verse DNA

This file is the operational configuration for every chat in this project (auto-loaded
each session): startup sequence, environment commands, code style, and git workflow.
The fixed conversation rules (Rules 1–13 and "What not to do") live in
`CONSTITUTION.md`, imported below so both files load automatically.

@CONSTITUTION.md

The project's decisions, roadmap, glossary, and lessons live in the **basic-memory**
knowledge base (project `rhyme-dna`) — load them at the start of every chat per the
startup sequence below. The current milestone to work on is always the first one still
marked `[ ]` in the roadmap note (`rhyme-dna/roadmap`).

---

## Startup sequence for every new chat

The project's knowledge lives in the **basic-memory** knowledge base (project
`rhyme-dna`), which indexes the governance notes in this repo. Retrieve from it rather
than reading raw files:

0. Invoke the `/caveman` skill immediately — every session runs in compressed communication mode
1. Read this file (`CLAUDE.md`) and `CONSTITUTION.md` — the standing rules (auto-loaded each session)
2. `read_note "rhyme-dna/decisions"` — the decision log: what has been built and why
3. `read_note "rhyme-dna/roadmap"` — identify the next incomplete milestone (the first
   one still marked `[ ]`)
4. `read_note "rhyme-dna/glossary"` — domain-term dictionary and the decision backlog
5. `read_note "rhyme-dna/lessons"` — mistakes already made and corrected
6. `search_notes "<milestone topic>"` — find KB notes relevant to the upcoming milestone
7. Scan `progress/` folder — read all `.md` entries (excluding `README.md`) whose filename
   date falls within the last 10 days of today's date; these give recent session context
8. Confirm you are ready with a brief recap: current state of the project, and the
   milestone you are about to begin

If the basic-memory MCP tools are unavailable in a session, fall back to reading the same
content from the source files in the repo (`DECISIONS.md`, `ROADMAP.md`, `GLOSSARY.md`,
`LESSONS.md`) — they are the markdown behind these notes.

---

## Project identity

**Verse DNA** is an audio-aligned phoneme extraction and rhyme structure analysis engine
for performance-aware lyrical analysis. The long-term goal is a Genius-like web app
where any song can be analysed for its rhyme scheme, scored for complexity, and
displayed with rhyming words highlighted in matching colours.

The system is English-only while MFA + ARPAbet is in use. Music analysis (tonality,
tempo, etc.) is explicitly out of scope until the lyrics engine is mature.

All architectural decisions and their reasoning live in the decision-log note
(`rhyme-dna/decisions`, source file `DECISIONS.md`). The forward-looking milestone plan
lives in the roadmap note (`rhyme-dna/roadmap`, source file `ROADMAP.md`).

---

## Running the notebook

Whenever it is time to execute the notebook, run it headlessly using:

```
conda run -n mfa_env jupyter nbconvert --to notebook --execute rhyme-DNA.ipynb --output rhyme-DNA.ipynb --ExecutePreprocessor.timeout=120
```

This runs all cells in order using the `mfa_env` kernel, writes output back into
the notebook file, and allows Claude to read the results directly.

---

## Code style preferences

- Python only for the core pipeline
- All logic lives in `python/` as importable modules; the notebook imports from there
- No logic inside notebook cells — cells call functions, functions live in `.py` files
- Every function should have a docstring
- Debug output controlled by a `debug=False` parameter, not by commenting/uncommenting

---

## Git workflow

### Branches and PR titles

Use the format `class(number)-short-description` for branches and
`class(number): Short description` for PR titles. This follows the
[Conventional Commits](https://www.conventionalcommits.org/) convention.

| Class | Use for | Numbered by |
|---|---|---|
| `milestone` | implementing a milestone from ROADMAP.md | milestone number |
| `docs` | changes to planning or documentation files only (no code) | sequential from 1 |
| `glossary` | updates to `GLOSSARY.md` (terms + decision backlog); merged *after* the related milestone (see Rule 10 in `CONSTITUTION.md`) | sequential from 1 |
| `fix` | bug fix | sequential from 1 |
| `refactor` | restructuring existing code without changing behaviour | sequential from 1 |
| `chore` | maintenance — config, tooling, dependencies | sequential from 1 |

**Examples:**
```
Branch:   m10-ipa-switch
PR title: milestone(10): IPA Switch

Branch:   d1-roadmap-restructure
PR title: docs(1): Roadmap Restructure and Workflow

Branch:   f1-oud-ound-clustering
PR title: fix(1): Correct -oud / -ound cluster separation

Branch:   g1-m11-panphon-terms
PR title: glossary(1): M11 panphon terms and decision backlog
```

Create the branch at the start of the work session, before writing any code or
making any changes. Merge to `main` only when the work is complete and tested.

### Mid-milestone rule and documentation updates

When the rules (`CLAUDE.md`, `CONSTITUTION.md`) or other planning/documentation files
need updating in the middle of an ongoing milestone, **do not commit the update onto
the milestone branch**. Instead:

1. Create a separate `docs(N)` branch off `main` for the rule/doc change.
2. Commit the change there and merge it into `main` **first**.
3. Rebase the in-progress milestone branch onto the updated `main` so it picks up the
   new rules.
4. Resume milestone work on the rebased branch.

**Why this exists:** rule and documentation changes are independent of milestone code
and should land cleanly on `main` without being entangled in unfinished milestone work.
Rebasing the milestone branch afterwards keeps it building on the latest rules.

### Commits

Commit **frequently** — after every self-contained change (a new function, a bug fix,
a passing test). A commit should be reviewable in under two minutes. If the diff is
large enough that you need to scroll to understand it, it should have been two commits.

Remind the user to commit if a chat session has produced significant code changes
and no commit has been made yet.

### GitHub CLI

Always use the `gh` CLI for all GitHub interactions — creating PRs, viewing PRs,
checking CI status, listing issues, etc. Never use the GitHub web UI
instructions or raw `git push` + manual PR creation. The repo is
`SpacePiercer/rhyme-dna`.

**Never merge a PR.** I (the user) always merge PRs manually. Do not run
`gh pr merge`, any other merge command, or otherwise merge a branch into `main`.
Your job ends at creating/updating the PR and reporting it is ready; then stop and
let me do the merge. After I confirm a PR is merged, you may continue (e.g. pull
`main`, rebase, start the next branch).

**Always give me the PR link.** Whenever you create or update a PR, include its full
URL in your message so I can open it quickly.

### Pull requests

One PR per milestone. Keep milestones short enough that the PR diff is readable in
a single sitting. If a milestone grows large during planning, propose splitting it
into two before implementation begins.

**PR title format:**
```
Milestone N: Short description matching the milestone heading
```

**PR description template:**
```
## Motivations
Why this change was needed — the problem or gap it addresses.

## Changes
What was built or modified. Bullet list of files/functions changed.

## Testing
How the change was verified — test verses used, accuracy results, spot-checks.

## Considerations
Trade-offs made, known limitations, deferred items, and anything a reviewer
should keep in mind when reading the diff.
```

When asked to create a PR, populate this template using the milestone description
from the roadmap note (`rhyme-dna/roadmap`) and the decisions recorded in the
decision-log note (`rhyme-dna/decisions`) for that milestone.
