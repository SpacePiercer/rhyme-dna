# CLAUDE.md — Verse DNA

This file contains standing instructions for every chat in this project.
Read this file and `DECISIONS.md` at the start of every new chat before doing anything else.
The current milestone to work on is always the first one marked `[ ]` in `ROADMAP.md`.

---

## Startup sequence for every new chat

1. Read this file (`CLAUDE.md`)
2. Read `DECISIONS.md` — understand what has been built and why
3. Read `ROADMAP.md` — identify the next incomplete milestone
4. Read `GLOSSARY.md` — domain-term dictionary and the decision backlog
5. Search the basic-memory KB (`verse-dna` project) for notes relevant to the
   upcoming milestone — use `mcp__basic-memory__search` with the milestone topic
6. Confirm you are ready with a brief recap: current state of the project, and the
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

This applies to **every** piece of code you run or produce — not only code written to
files or notebook cells, but also ad-hoc/inline scripts executed in the terminal
(e.g. `python -c "..."` probes, one-off exploration scripts). Whenever you run such a
script, include its pseudo-code in the same message.

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

### Rule 6 — Tests with every change

Every change must ship with the unit and/or integration tests that cover it. New
functions get unit tests; changes that span multiple pipeline stages get integration
tests. Do not consider a change complete until its tests exist and pass. Tests live
alongside the core code (e.g. `python/tests/`) and run with `pytest` in `mfa_env`.

**Why this exists:** the pipeline has many interacting stages (alignment, phoneme
extraction, rhyme detection). Tests are the only way to know a change did not silently
break an upstream or downstream stage.

### Rule 7 — Pipeline stays runnable with valid results

Every change must leave the pipeline runnable end-to-end and producing valid results.
Before considering any change complete, run the notebook (see "Running the notebook")
and confirm it executes without errors and the outputs are sensible. Never leave the
pipeline in a broken or half-migrated state between changes — if a change is large,
split it so each committed step is independently runnable.

### Rule 8 — Plain language and term explanations

I am not a linguist and not a domain expert. Write for a general audience:

- Use simple, everyday language by default; prefer the plain word over the technical one.
- The **first time** any domain-specific term appears in a response (linguistics,
  phonetics, audio processing, advanced ML/maths, etc.), explain it in one short
  accessible phrase — ideally with a concrete everyday example.
  e.g. "*phoneme* (the smallest unit of sound in speech — the `t` in *cat*)".
- If a concept only makes sense through an analogy, give the analogy before the
  precise definition.
- Never assume I know jargon, abbreviations, or symbols (IPA characters, feature
  names, etc.) — spell them out the first time they come up.

**Why this exists:** I am driving the linguistic direction of this project without a
linguistics background. Clear, jargon-free explanations are how I verify the work is
correct and stay in control of the decisions.

### Rule 9 — Illustrate every decision with a concrete before/after example

For **every** design decision or correction you make, show a simple worked example of
how it changes the output or an intermediate result. Use real data from the project
(a word, a rhyme, a score) wherever possible.

Format the example as a small before → after comparison, e.g.:

```
Decision: average diphthong segments instead of comparing them separately
- Word "loud" vs "mound"
- Before: similarity = 0.50
- After:  similarity = 0.62  (the shared "ow" sound now contributes partial credit)
```

If a decision changes nothing visible yet (e.g. internal refactor), say so explicitly
and explain what result it *would* affect later.

**Why this exists:** seeing the effect on a real word or score is how I judge whether a
decision is correct, without needing to read the implementation.

### Rule 10 — Maintain the glossary and decision backlog

The project keeps a `GLOSSARY.md` with two parts: (A) a plain-language dictionary of
every domain-specific term, and (B) a dated backlog of measurement/linguistic decisions.

- **When you use a domain term** that is not yet in Part A, add it there with a plain
  explanation (this is how Rule 8 is recorded permanently).
- **When you make a measurement or linguistic decision** (a new score, a threshold, a
  rule for handling sounds), add a row to Part B with the date, the current branch, the
  area, the decision, and its effect on the output.

**How glossary updates are committed (branching):**

- Glossary/backlog updates are **never** committed on the milestone branch, and **never**
  on a mid-workflow `docs` branch.
- Instead, collect them and commit them on a dedicated **glossary** branch (class `g`,
  e.g. `g1-m11-panphon-terms`, PR title `glossary(1): ...`), created and merged **only
  after** the related milestone's technical changes have been implemented and merged.
- This keeps milestone PRs purely technical and records the terms/decisions once the
  work they describe is actually on `main`.
- *One-time exception:* the initial creation of `GLOSSARY.md` itself rides with the
  `docs` change that introduces this rule.

**Why this exists:** it gives me a single, jargon-free reference and an auditable record
of every decision that shaped how rhymes are scored — added once the work is merged, not
mixed into the technical milestone PR.

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
| `glossary` | updates to `GLOSSARY.md` (terms + decision backlog); merged *after* the related milestone (see Rule 10) | sequential from 1 |
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

When the rules (`CLAUDE.md`) or other planning/documentation files need updating in
the middle of an ongoing milestone, **do not commit the update onto the milestone
branch**. Instead:

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
