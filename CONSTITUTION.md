---
title: CONSTITUTION
type: note
permalink: rhyme-dna/constitution
---

# CONSTITUTION.md — Verse DNA

The fixed conversation rules of the project. These are the stable, rarely-edited
part of the standing instructions; the operational configuration (startup sequence,
environment commands, git workflow) lives in `CLAUDE.md`, which imports this file so
both load automatically every session.

Rule changes follow the same discipline as any documentation change: a dedicated
`docs` branch merged to `main` first (see the git workflow in `CLAUDE.md`).

---

## Rule 1 — MAIN / SIDE QUESTIONS branching

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

## Rule 2 — Pseudo-code after every code block

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

## Rule 3 — Chat naming

Name each chat according to the pattern: `Milestone N` where N is the milestone number
being worked on in that chat.

## Rule 4 — Notebook cell placement

For every new or corrected notebook cell, explicitly state which section of the
notebook it belongs to and where relative to existing cells it should be placed.
The notebook (`rhyme-DNA.ipynb`) is available in the project repo — look it up there.

## Rule 5 — Record decisions and progress at milestone completion

When a milestone is finished, append a new section to the decision-log note
(`rhyme-dna/decisions`, source file `DECISIONS.md`) describing what was built, what
decisions were made, and why. This becomes the context for the next chat. Update it via
basic-memory (`write_note` / `edit_note`) or by editing `DECISIONS.md` directly — it is
the source file behind the note, and basic-memory re-indexes it on sync.

Also mark the completed milestone as `[x]` in the roadmap note (`rhyme-dna/roadmap`,
source file `ROADMAP.md`).

## Rule 6 — Tests with every change

Every change must ship with the unit and/or integration tests that cover it. New
functions get unit tests; changes that span multiple pipeline stages get integration
tests. Do not consider a change complete until its tests exist and pass. Tests live
alongside the core code (e.g. `python/tests/`) and run with `pytest` in `mfa_env`.

**Why this exists:** the pipeline has many interacting stages (alignment, phoneme
extraction, rhyme detection). Tests are the only way to know a change did not silently
break an upstream or downstream stage.

## Rule 7 — Pipeline stays runnable with valid results

Every change must leave the pipeline runnable end-to-end and producing valid results.
Before considering any change complete, run the notebook (see "Running the notebook"
in `CLAUDE.md`) and confirm it executes without errors and the outputs are sensible.
Never leave the pipeline in a broken or half-migrated state between changes — if a
change is large, split it so each committed step is independently runnable.

## Rule 8 — Plain language and term explanations

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
- **Checkmark exemption:** terms marked with a leading `✓` in the glossary note
  (`rhyme-dna/glossary`, source file `GLOSSARY.md`) are ones
  I have explicitly told you I understand. Do **not** re-explain a ✓ term inline (no
  bracketed definition) — treat it as known. Unmarked terms still get the bracket
  treatment above. When I tell you I understand a term, add the `✓` to its glossary
  entry (on the appropriate `glossary`/`docs` branch) so the exemption is recorded.

**Why this exists:** I am driving the linguistic direction of this project without a
linguistics background. Clear, jargon-free explanations are how I verify the work is
correct and stay in control of the decisions.

## Rule 9 — Illustrate every decision with a concrete before/after example

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

## Rule 10 — Maintain the glossary and decision backlog

The project keeps a glossary note (`rhyme-dna/glossary`, source file `GLOSSARY.md`) with
two parts: (A) a plain-language dictionary of every domain-specific term, and (B) a dated
backlog of measurement/linguistic decisions.

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

## Rule 11 — No unilateral big decisions; list decisions for sign-off

Never make a big or architectural decision on your own. This includes (but is not
limited to): choosing a scoring formula or threshold, changing how sounds/rhymes are
compared, picking an algorithm or data source, altering pipeline structure, or anything
that changes the meaning of the output. Surface the choice, explain the options in plain
language with examples, and wait for my approval before implementing.

**End every message with a "Decisions" list** — a short, numbered list of the decisions
you have reached or are proposing. **Format every entry exactly the same way:**

```
N. (status) description of the decision
```

where `(status)` is a bracketed tag at the very start of the entry indicating where the
decision stands — use `(agreed)` for one already signed off and `(needs your sign-off)`
for one awaiting my approval (or another short bracketed phrase if a different status
fits better). The bracket always comes first, the description follows. If a message
genuinely involved no decisions, write "Decisions: none this message."

**Why this exists:** I steer the direction of this project. Seeing every pending decision
in one place, in plain terms, is how I stay in control and catch wrong turns early.

## Rule 12 — Grill-me before starting a milestone

Before writing any code or making any changes on a new milestone, invoke the `/grill-me`
skill to stress-test the milestone plan with me. Work through the plan together — surface
assumptions, edge cases, and scope questions — until we both agree it is solid. Only then
begin implementation.

**Why this exists:** catching wrong assumptions before implementation is far cheaper than
discovering them mid-build. One grilling session at the start prevents multiple correction
cycles later.

## Rule 13 — Write a session summary to the progress log on close

When I signal the end of a session — by saying "finished", "done", "closing", "wrapping up",
or any equivalent — write a summary to the current day's file in `progress/` before stopping.
If no entry exists for today, create one. The summary must cover:

- **Session** — chat name and branch
- **Decisions** — every decision made or signed off this session (copy from the Decisions
  lists at the bottom of messages)
- **Commits** — all commit hashes and their one-line messages created this session
- **State** — what is complete, what is in progress, and any blockers or deferred items

Do not ask for confirmation — write the file and then confirm it was written.

**Why this exists:** the progress log is only useful if it is actually written. Tying it
to the session-close signal ensures it never gets skipped.

---

## What not to do

- Do not hallucinate progress — if something is not in the decision log (`rhyme-dna/decisions`), it has not been built
- Do not change the direction of the project without explicitly flagging it
- Do not answer everything in one message — keep responses focused; let me ask follow-ups
- Do not skip the pseudo-code requirement
- Do not use a dictionary (CMU Pronouncing Dictionary or similar) for phoneme lookup —
  all phonemes must come from MFA alignment on the actual audio
