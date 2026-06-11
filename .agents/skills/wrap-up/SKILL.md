---
name: wrap-up
description: Write the Rule 13 session-close summary to the progress log — session, decisions, commits, state — then report it written without asking for confirmation. Use when the user says "finished", "done for today", "closing", "wrapping up", "end of session", or invokes /wrap-up.
---

# Wrap Up (Rule 13 session close)

Write today's session summary to `progress/YYYY-MM-DD.md`. Per Rule 13: do **not**
ask for confirmation — write the file, then confirm it was written.

## Steps

1. **Gather**
   - **Session**: chat name + current branch (`git branch --show-current`).
   - **Decisions**: every decision made or signed off this session — copy from the
     Decisions lists at the bottom of messages, including AskUserQuestion sign-offs.
   - **Commits**: `git log --oneline --since=midnight`, cross-checked against the
     commits actually made in this session (drop other sessions' commits from the
     same day).
   - **State**: what is complete, in progress, blocked, or deferred. Check
     `gh pr list` for PRs awaiting the user's merge and `git status --short` for
     uncommitted changes.

2. **Write `progress/YYYY-MM-DD.md`** (today's date)
   - If absent, create it matching the existing entries' format: basic-memory
     frontmatter (`title: 'YYYY-MM-DD'`, `type: note`,
     `permalink: rhyme-dna/progress/YYYY-MM-DD`), then `# YYYY-MM-DD` and the four
     sections **Session / Decisions / Commits / State**.
   - If today's file exists (multi-session day), append a clearly separated second
     entry (`---` + repeated Session/Decisions/Commits/State block) — never
     overwrite the earlier session's record.

3. **Branch discipline (Lesson L2)**: the progress file is documentation. If a
   milestone branch is checked out, still write the file, but commit it on a
   docs-class branch — never onto milestone code. On an already-open docs/chore
   branch it may ride along.

4. **Report**: confirm the file was written, then flag anything live — PRs awaiting
   merge, uncommitted changes, and the next `[ ]` milestone in `docs/ROADMAP.md`.
