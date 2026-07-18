---
title: MANIFEST
type: config
permalink: rhyme-dna/manifest
tags:
- manifest
- navigation
- startup
---

# MANIFEST — Verse DNA

Entry point for the `rhyme-dna` knowledge base. Routing contract: what lives here, where to find it, when to use each note. Read this note first; it tells you everything else.

---

## Project scope

**Verse DNA** — audio-aligned phoneme extraction and rhyme structure analysis engine. Long-term goal: Genius-like web app where any song can be analysed for rhyme scheme, scored for complexity, and displayed with rhyming words highlighted in matching colours.

- English-only (MFA + ARPAbet in use)
- Music analysis (tonality, tempo) is out of scope until lyrics engine is mature
- All code logic lives in `python/` as importable modules; notebook (`rhyme-DNA.ipynb`) calls those modules

---

## Mandatory startup sequence

**Complete every step before answering any user request.**

0. `/caveman` skill already invoked by CLAUDE.md — confirm it is active
1. `read_note "rhyme-dna/decisions"` — build log: what was built and why, milestone by milestone
2. `read_note "rhyme-dna/roadmap"` — find the first milestone still marked `[ ]` (that is your target)
3. `read_note "rhyme-dna/glossary"` — domain-term dictionary (Part A) + dated decision backlog (Part B)
4. `read_note "rhyme-dna/lessons"` — mistakes already made and corrected; apply before touching any code
5. `search_notes "<milestone topic>"` — surface KB notes relevant to the upcoming milestone
6. Scan `progress/` folder — read all `.md` entries (skip `README.md`) dated within the last 10 days
7. Confirm ready: one short message — current project state + the next milestone you are about to begin

---

## Canonical notes

| Note | Identifier | Contains |
|---|---|---|
| [[DECISIONS]] | `rhyme-dna/decisions` | Milestone-by-milestone build log and architectural rationale |
| [[ROADMAP]] | `rhyme-dna/roadmap` | Milestone plan; `[x]` = done, `[ ]` = pending |
| [[GLOSSARY]] | `rhyme-dna/glossary` | Part A: term dictionary · Part B: dated decision backlog |
| [[LESSONS]] | `rhyme-dna/lessons` | Known mistakes and their corrections — read before every milestone |
| [[MFA Failures]] | `rhyme-dna/mfa_failures` | Alignment failure patterns and workarounds |
| Progress logs | `progress/YYYY-MM-DD.md` | Daily session summaries written by Rule 13 |

---

## Navigation rules

- **Active milestone** = first `[ ]` entry in `rhyme-dna/roadmap`
- **Start every milestone** with `/grill-me` before writing any code (Rule 12)
- **After milestone merges** run `/close-milestone` — writes DECISIONS section, flips ROADMAP, queues glossary branch (Rules 5, 9, 10)
- **Domain term unknown** → check [[GLOSSARY]] Part A; if missing, add it (Rule 10)
- **Past decision unclear** → search [[DECISIONS]] log
- **Alignment/phoneme issue** → check [[MFA Failures]] first
- **Session ending** → `/wrap-up` writes the Rule 13 progress entry

---

## Milestone workflow summary

```
grill-me → implement → test → pipeline run → commit → PR → (user merges) → close-milestone
```

Each step maps to a Constitution rule: grill-me = R12, tests = R6, pipeline = R7, decisions = R5, glossary branch = R10.

---

## Fallback (if MCP unavailable)

Read source files directly from the repo:

| Note | File |
|---|---|
| Decisions | `docs/DECISIONS.md` |
| Roadmap | `docs/ROADMAP.md` |
| Glossary | `docs/GLOSSARY.md` |
| Lessons | `docs/LESSONS.md` |
| MFA Failures | `docs/MFA_FAILURES.md` |

---

## Observations
- [fact] MANIFEST is the first note read every session — it drives the startup sequence #navigation
- [convention] Read Knowledge Map after MANIFEST when you need full KB topology, not just startup order #navigation
- [requirement] Complete all startup sequence steps before answering any user request #workflow
- [fact] Fallback when MCP unavailable: read `docs/` source files directly from repo #resilience

## Relations
- leads_to [[Knowledge Map]]
- relates_to [[Conventions]]
- relates_to [[Pipeline Architecture]]

## Canonical store rule

`docs/` source files are canonical truth for rules, decisions, and docs; `rhyme-dna/*` notes re-index from them on sync. Write-path: edit the `docs/` source file. Use `edit_note` only for notes that have no on-disk source file.
