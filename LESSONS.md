# LESSONS.md — Verse DNA

An in-repo log of mistakes made and corrections received, so the same ones are not
repeated in a fresh session. Read this at the start of every chat (see the startup
sequence in `CLAUDE.md`). Newest first.

---

## L2 — Documentation changes never go on a milestone branch

**Mistake (Milestone 12):** I committed `LESSONS.md` (and the `DECISIONS.md` /
`ROADMAP.md` updates) directly onto the `m12` milestone branch. Per `CLAUDE.md`'s
mid-milestone rule, *any* planning/documentation change goes on a dedicated `docs`
branch (class `d`) merged to `main` first — never bundled into milestone code. Georgii
caught it; this is the same discipline that produced `d13`/`d14`.

**Lesson:**
- Milestone branches contain **code + tests only**.
- All doc/planning files (`DECISIONS.md`, `ROADMAP.md`, `LESSONS.md`, `CLAUDE.md`, …)
  ride a `docs` branch — including milestone-completion updates, unless explicitly told
  otherwise.
- `GLOSSARY.md` is stricter still: its own `glossary` branch, merged *after* the
  milestone (Rule 10).

---

## L1 — Judge engine output by the module's spec, not by guessed artist intent

**Mistake (Milestone 12):** I labelled several words that the assonance scorer put in
the short-*i* cluster — *explosive, give, is, still, think* — as "incidental noise."
They are not noise: they genuinely share the scheme's short-*i* vowel, which is exactly
what the vowel-weighted scorer is built to detect. I had quietly imported a *human
intent judgment* ("the rapper probably didn't mean these as the scheme") and treated
the engine's correct detections as if they were errors.

**Also wrong:** I said stress weighting (M13) would "drop" *explosive*. Its shared vowel
is in the unstressed "-ive", so stress would only **down-weight** it (rank it as a weaker
member), not exclude it.

**Lesson:**
- Evaluate output by "is this correct by the module's spec?" *before* "does this match my
  intuition of what the artist intended?"
- Never call a correct detection "noise" or "incidental." If it is weaker or part of a
  bigger structure, say exactly that and name the milestone that will refine it (M13
  stress, M14 syllables, M17 cross-word streams).
- Distinguish **down-weighting** (strength/ranking) from **exclusion** (membership).
