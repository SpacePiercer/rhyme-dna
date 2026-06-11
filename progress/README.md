---
title: README
type: note
permalink: rhyme-dna/progress/readme
---

# Progress Log

One file per session day, named `YYYY-MM-DD.md`.

Each entry records:
- **Session** — chat name and milestone being worked on
- **Decisions** — key decisions made or signed off (with brief rationale)
- **Commits** — commit hashes and their one-line messages created during the session
- **State** — where things stand at the end: what's done, what's pending, what's blocked

Claude writes to the current day's file during every session. At startup, Claude reads
all entries dated within the last 10 days for continuity.