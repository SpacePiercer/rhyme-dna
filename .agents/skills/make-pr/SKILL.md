---
name: make-pr
description: Create a correctly numbered branch and pull request per the Verse DNA git workflow — computes the next free class number from branches AND past PRs (prevents the d16/d17/g1 double-numbering that has already happened), fills the PR template, returns the URL, and never merges. Use when the user asks to create or open a PR, start a work branch, or invokes /make-pr [class] [description].
---

# Make PR

## Steps

1. **Class** — infer from the work: `milestone / docs / glossary / fix / refactor /
   chore` (table in CLAUDE.md). Ask the user only if genuinely ambiguous.

2. **Number** — this is the collision fix; branch names alone miss merged/deleted
   work and caused `d16`, `d17`, and `g1` to each be used twice:
   - `milestone` → the milestone number from `docs/ROADMAP.md`.
   - every other class → scan **both** `git branch -a` and
     `gh pr list --state all --limit 100 --json headRefName,title` for the class
     prefix (`d`, `g`, `f`, `r`, `c` followed by digits); next number = max + 1.

3. **L2 guard** — if the change set touches planning/documentation files
   (`CLAUDE.md`, `CONSTITUTION.md`, `docs/*`, `progress/*`) while a milestone
   branch is checked out: stop and move those changes to a docs branch first
   (Lesson L2: milestone branches carry code + tests only).

4. **Branch** — if the work is not on its own branch yet:
   `git checkout -b <abbrev><N>-<short-description>` off `main`
   (e.g. `c8-workflow-skills`, `d18-...`, `m14-...`). Push with `-u origin`.

5. **PR** — `gh pr create`, title `class(N): Short description`, body per the
   CLAUDE.md template (Motivations / Changes / Testing / Considerations). For
   milestone PRs populate from the `docs/ROADMAP.md` entry and the
   `docs/DECISIONS.md` sections; otherwise from the actual diff.
   - **Base on `main`.** If stacking on an unmerged branch is truly unavoidable,
     say so in the PR body and warn the user explicitly: GitHub merges a PR into
     its **base** branch — a stacked PR must be retargeted to `main` (or its base
     branch deleted, which auto-retargets) **before** merging, or the work lands in
     the wrong branch. This exact failure happened with PR #38.

6. **Finish** — output the full PR URL. **Never merge**: no `gh pr merge` or any
   equivalent, ever. The user merges; work ends at the URL.
