---
name: close-milestone
description: Run the Verse DNA milestone-completion sequence (Rules 5, 9, 10) — verify the milestone PR is merged and the pipeline green, write the DECISIONS.md section and flip ROADMAP to [x] on a docs branch, then batch glossary updates on a g-branch after that merges. Use when the user says a milestone is done/complete/finished, asks to close out or book-keep a milestone, or invokes /close-milestone.
---

# Close Milestone

Hard rule throughout: **none of this is ever committed to the milestone branch**
(Lesson L2 — milestone branches carry code + tests only).

## Preconditions (verify first; if unmet, stop and report what is pending)

1. The milestone PR is **MERGED** — check `gh pr view <number>` / `gh pr list`.
2. The pipeline gate is green on `main` — invoke `/run-pipeline` if in any doubt
   (Rules 6 + 7).

## Stage 1 — docs branch (Rules 5 + 9)

1. `git checkout main` + `git pull`, then a fresh **docs** branch numbered per the
   `/make-pr` procedure (scan branches AND past PRs for the next free `d` number).
2. Append the milestone section to `docs/DECISIONS.md`: what was built, each key
   decision **with why**, and before → after examples using real project data
   (a word, a rhyme, a score — Rule 9).
3. In `docs/ROADMAP.md`: flip the milestone to `[x]` and add its one-line entry to
   the Completed index (1–2 sentence summary; the full history lives only in
   DECISIONS — do not duplicate it back into ROADMAP).
4. Open the docs PR per `/make-pr`; give the URL; **stop for the user's merge**.

## Stage 2 — glossary branch (Rule 10; only after Stage 1 is merged)

1. New `g`-class branch off updated `main` (numbered per `/make-pr`).
2. `docs/GLOSSARY.md` Part A: add every domain term introduced during the
   milestone, in plain language (Rule 8 made permanent).
3. Part B: one backlog row per measurement/linguistic decision — date, branch,
   area, decision, effect on the output.
4. Open the glossary PR; give the URL; the user merges.

## Stage 3 — reminders

- The session still closes with `/wrap-up` (Rule 13) — this skill does not replace it.
- The next `[ ]` milestone in `docs/ROADMAP.md` starts with a `/grill-me` session
  before any code (Rule 12).
