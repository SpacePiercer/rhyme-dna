# CLAUDE.md — Verse DNA

This file contains standing instructions for every chat in this project.
Read this file and `DECISIONS.md` at the start of every new chat before doing anything else.
The current milestone to work on is always the first one marked `[ ]` in `ROADMAP.md`.

---

## Startup sequence for every new chat

1. Read this file (`CLAUDE.md`)
2. Read `DECISIONS.md` — understand what has been built and why
3. Read `ROADMAP.md` — identify the next incomplete milestone
4. Confirm you are ready with a brief recap: current state of the project, and the
   milestone you are about to begin

---

## Project identity

**Verse DNA** is an audio-aligned phoneme extraction and rhyme structure analysis engine
for performance-aware lyrical analysis. The long-term goal is a Genius-like web app
where any song can be analysed for its rhyme scheme, scored for complexity, and
displayed with rhyming words highlighted in matching colours.

The system is English-only while MFA + ARPAbet is in use. Music analysis (tonality,
tempo, etc.) is explicitly out of scope until the lyrics engine is mature.

All architectural decisions and their reasoning live in `DECISIONS.md`.
The forward-looking milestone plan lives in `ROADMAP.md`.

---

## Conversation rules

### Rule 1 — MAIN / SIDE QUESTIONS branching

Every chat starts on the **MAIN** branch. Label the top of each response in bold:
**MAIN** or **SIDE QUESTIONS**.

- If my message contains a question, a `?`, or a clarification request → switch to
  **SIDE QUESTIONS** and answer the question there. Continue as if the main thread
  was not interrupted.
- When I write `DONE` → switch back to **MAIN** and resume from where you left off,
  incorporating any new instructions that emerged from the side discussion.
- If a side discussion produces new instructions or workflow changes, remember them
  and apply them when returning to MAIN.

**Why this exists:** milestones often involve step-by-step sequences. Mid-sequence
questions can break the flow. This branching system lets me ask without disrupting
the algorithm.

### Rule 2 — Pseudo-code after every code block

After every code chunk you produce, add a plain-English pseudo-code summary written
for a second-year university student. Do NOT include it as a part of the produced 
code, instead, make it in a separate section below the code window in your message. 
Divide the two resulted sections by a pharase: "Here's the PSEUDOCODE version of the 
code chunk above". Its purpose is twofold: it lets me verify you are doing the right 
thing, and it helps me understand the code without reading every line.

Format:
```
# PSEUDO-CODE
# 1. Do this
# 2. Then do that
# 3. Return the result
```

### Rule 3 — Chat naming

Name each chat according to the pattern: `Milestone N` where N is the milestone number
being worked on in that chat.

### Rule 4 — Notebook cell placement

For every new or corrected notebook cell, explicitly state which section of the
notebook it belongs to and where relative to existing cells it should be placed.
The notebook (`rhyme-DNA.ipynb`) is available in the project repo — look it up there.

### Rule 5 — Update DECISIONS.md at milestone completion

When a milestone is finished, produce an updated `DECISIONS.md` that appends a new
section describing what was built, what decisions were made, and why. This section
becomes the context for the next chat.

Also mark the completed milestone as `[x]` in `ROADMAP.md`.

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
```

Create the branch at the start of the work session, before writing any code or
making any changes. Merge to `main` only when the work is complete and tested.

### Commits

Commit **frequently** — after every self-contained change (a new function, a bug fix,
a passing test). A commit should be reviewable in under two minutes. If the diff is
large enough that you need to scroll to understand it, it should have been two commits.

Remind the user to commit if a chat session has produced significant code changes
and no commit has been made yet.

### GitHub CLI

Always use the `gh` CLI for all GitHub interactions — creating PRs, viewing PRs,
checking CI status, merging, listing issues, etc. Never use the GitHub web UI
instructions or raw `git push` + manual PR creation. The repo is
`SpacePiercer/verse-dna`.

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
from `ROADMAP.md` and the decisions recorded in `DECISIONS.md` for that milestone.

---

## What not to do

- Do not hallucinate progress — if something is not in `DECISIONS.md`, it has not been built
- Do not change the direction of the project without explicitly flagging it
- Do not answer everything in one message — keep responses focused; let me ask follow-ups
- Do not skip the pseudo-code requirement
- Do not use a dictionary (CMU Pronouncing Dictionary or similar) for phoneme lookup —
  all phonemes must come from MFA alignment on the actual audio
