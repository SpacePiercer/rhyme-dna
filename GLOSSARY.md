---
title: GLOSSARY
type: note
permalink: verse-dna/glossary
---

# GLOSSARY.md — Verse DNA

A plain-language dictionary of the domain-specific terms used in this project, plus a
dated backlog of the measurement/linguistic decisions that shaped the engine.

Maintained per **Rule 8** (explain terms) and **Rule 10** (keep this file current).
This file is the non-expert's reference: every linguistics, phonetics, or scoring term
that appears in code, notebook, or discussion should be defined here in everyday words.

**How this file is updated:** changes are batched onto a dedicated `glossary` branch
(class `g`, e.g. `g1-...`) and merged *after* the related milestone's technical work is
merged — never on the milestone branch or a mid-workflow `docs` branch (see Rule 10).
This initial version is the one-time bootstrap that rode with the rules introducing it.

---

## Part A — Dictionary of terms

> **✓ legend:** a leading `✓` marks a term the user has explicitly said he
> understands. Per Rule 8, ✓ terms are **not** re-explained inline (no bracketed
> definition); unmarked terms still get explained the first time they appear.

### Sounds and spelling

- ✓ **Vowel** — an open speech sound made with the mouth unobstructed, the kind a
  syllable is built around: the *a* in *cat*, the *ee* in *see*.
- ✓ **Consonant** — a speech sound made by blocking or restricting the airflow, e.g.
  *t*, *p*, *s*, *n*. Everything that isn't a vowel.
- **Phoneme** — the smallest unit of sound in speech that can change meaning.
  The `t` in *cat* is one phoneme; swap it for `p` and you get *cap*.
- **Grapheme** — a written letter (or group of letters) on the page, as opposed to the
  *sound* it makes. The word *phone* has 5 graphemes (letters) but only 3 phonemes
  (sounds): "f-oh-n".
- **IPA (International Phonetic Alphabet)** — a standard set of symbols where each symbol
  is exactly one sound, no matter the language or spelling. Example: the "sh" sound is
  written `ʃ`. We use IPA so the same sound always looks the same.
- **ARPAbet** — an older, English-only code that writes sounds using plain keyboard
  letters (e.g. the "igh" in *light* is `AY`). We used this before Milestone 10, then
  switched to IPA.
- **Diphthong** — a single vowel that *glides* from one sound to another inside one
  syllable. The vowel in *loud* starts at "ah" and slides to "oo" — written `aw` in our
  data. (Contrast a *pure* vowel like the "ee" in *see*, which stays put.)
- **Glide** — a sound that acts like a very short vowel sliding into another sound,
  such as `j` (the "y" in *yes*) or `w` (the "w" in *wet*).

### How sounds are described (phonetics)

- **Articulatory features** — descriptions of *how* the mouth makes a sound (where the
  tongue is, whether the vocal cords buzz, etc.). These are the building blocks panphon
  uses.
- **Phonological feature** — one yes/no-style property of a sound, e.g. "is it voiced?"
  panphon describes every sound with 24 such features.
- **Feature vector** — the full list of a sound's 24 feature values written as numbers
  (`+1` = yes, `0` = not applicable, `−1` = no). Think of it as the sound's "fingerprint".
- **Voicing / voiced / voiceless** — whether your vocal cords vibrate. `z` is voiced
  (throat buzzes), `s` is voiceless (no buzz). They are otherwise the same sound.
- **Manner of articulation** — *how* air is released: e.g. **stop/plosive** (air blocked
  then popped, like `t`, `p`), **fricative** (air hissed through a gap, like `s`, `f`),
  **nasal** (air through the nose, like `n`, `m`), **liquid/approximant** (smooth, like
  `l`, `r`).
- **Place of articulation** — *where* in the mouth the sound is made (lips, teeth, roof
  of mouth, etc.).
- **Syllable** — a single beat of a word built around a vowel. *Water* has two
  syllables: "wa-ter".
- **Coda** — the consonant(s) at the end of a syllable, after the vowel. In *mound*, the
  coda is "nd".
- **Stress** — which syllable in a word is said with more force. In *gui-TAR* the second
  syllable is stressed. IPA marks it with `ˈ` (primary) or `ˌ` (secondary) before the
  syllable.
- **Natural class** — a group of sounds that share features and behave alike, e.g. the
  nasals `m`/`n`/`ŋ` (all made by sending air through the nose) or the broad group of all
  vowels. Defined by how humans make sounds, so it is the same for every song — the basis
  for colouring sounds by family in later milestones.

### Rhyme concepts

- **Rhyme unit** — the chunk of a word we actually compare for rhyming, usually from the
  stressed vowel to the end. For *mound* it's the "ow-n-d" part.
- **Perfect rhyme** — endings that match exactly in sound: *light* / *night*.
- **Slant rhyme (near-rhyme)** — endings that *almost* match: *late* / *made* (only the
  final sound differs). Rappers use these deliberately.
- **End rhyme** — rhyme at the end of lines (the classic kind).
- **Internal rhyme** — rhyming words *inside* a line, not just at the end.

### Tools and data

- **MFA (Montreal Forced Aligner)** — software that listens to a recording plus its
  lyrics and works out the exact time each word and sound is spoken. ("Forced alignment"
  = lining up known text to audio.)
- **TextGrid** — the file MFA produces, listing each word/sound with its start and end
  time.
- **panphon** — a Python library that turns any IPA sound symbol into its 24-feature
  fingerprint, so we can measure how similar two sounds are using real phonetics.

### Scoring terms (this project's own measures)

- **Phoneme similarity** — how alike two single sounds are, on a `0.0`–`1.0` scale. Built
  from panphon: `1 − (panphon's weighted difference between the two sounds) ÷ (cost of a
  whole sound)`. `1.0` = identical; near-identical sounds like `t` and retroflex `ʈ` score
  about 0.93. Replaced the old hand-coded 0.7 / 0.4 class table in Milestone 11.
- **Edit distance** — the cheapest set of changes to turn one sequence of sounds into
  another, using three moves: **substitution** (swap one sound for another),
  **insertion** (add a sound), **deletion** (remove a sound). Each move has a cost; the
  cheapest total is the distance.
- **Weighted feature edit distance** — the core rhyme score since Milestone 11. It runs
  an edit distance over two rhyme units where a *substitution* costs panphon's weighted
  feature difference between the two sounds, and an *insertion/deletion* costs a fixed
  penalty. The total cost ÷ the number of sounds, subtracted from 1, gives the `0.0`–`1.0`
  rhyme score.
- **Feature weight** — panphon's importance value for each feature: major identity
  features (vowel-vs-consonant) weigh most, fine details least. They sum to about 7.25,
  which is also the cost panphon charges to insert or delete one whole sound.
- **Penalty method D / cap method C** — two interchangeable ways to charge for a missing
  or extra sound. **D** (default) charges a small flat penalty (0.75); **C** caps the
  weighted cost (at 1.0). Chosen by a sweep on the verse — D@0.75 gave the cleanest
  separation of perfect vs slant vs non-rhyme. Raw scores are kept (no rescaling).
- **Clustering threshold** — the score two words must reach to be grouped into the same
  rhyme colour/cluster. Kept at `0.7` in Milestone 11, which groups the `-oud` and `-ound`
  families together (they score ~0.81 — genuinely close in sound).
- **Deep member** — a cluster member whose rhyme unit has at least two sounds. Since
  Milestone 11 the render filter counts only deep members, so a bare vowel like "I" can
  sit inside a rhyme group without causing the whole group to be hidden.
- **Longest-common-tail similarity** *(retired in Milestone 11)* — the previous rhyme
  score: walk inward from the *end* of both words, adding up how well each sound matched,
  stopping at the first clear mismatch. Replaced by the weighted feature edit distance.
- **Walk-stop threshold** *(retired in Milestone 11)* — the cutoff that told the old tail
  walk when to stop. Gone with the tail walk.
- **Feature-overlap measure** *(superseded in Milestone 11)* — the originally-planned
  simple version: the fraction of panphon's 24 features two sounds agree on,
  `1 − sum|diff| ÷ (2 × 24)`. The shipped scorer uses panphon's *weighted* feature
  difference instead (see *Phoneme similarity* and *Weighted feature edit distance*).

---

## Part B — Measurement & linguistic decision backlog

Newest first. Each entry: what was decided, and its effect on the output/score.
Branch names before the per-milestone branching workflow are marked *(early history)*.

| Date | Branch | Area | Decision | Effect |
|---|---|---|---|---|
| 2026-06-04 | `m11-panphon-similarity` | Rhyme scorer | Score rhyme units with panphon **weighted feature edit distance** (substitution = weighted feature difference; insert/delete = bounded penalty); method **D@0.75** default, **C@1.0** selectable; raw scores kept | Insertion slant rhymes score correctly: `crowd`/`mound` 0.000 → **0.812**; perfect = 1.0, non-rhymes ≤ 0.44 |
| 2026-06-04 | `m11-panphon-similarity` | Clustering threshold | Keep threshold at **0.7** (Option B) instead of raising it | `-oud` and `-ound` merge into one "ow-ending" family (they score ~0.81); finer grouping deferred to M12/M13 |
| 2026-06-04 | `m11-panphon-similarity` | Render filter | `filter_clusters` counts **deep members** (≥2 sounds), not the shallowest member | A bare vowel ("I") can join a group without hiding it; the `-ight` family renders with "I" included |
| 2026-06-04 | `m11-panphon-similarity` | Tail walk | **Retire** `longest_common_tail_similarity` and its walk-stop threshold | Whole rhyme units compared by edit distance; scoring no longer halts at the first mismatch |
| 2026-05-31 | `m11-panphon-similarity` | Diphthong handling | Approach **B (segment-expand)**: split tokens like `aj`/`aw` into their panphon segments and compare sound-by-sound, rather than averaging them into one vector | `aw` is compared as `a`+`w`; rhyme tails line up at the sound level instead of the token level |
| 2026-05-31 | `m11-panphon-similarity` | Similarity scorer | Replace the hand-coded phoneme-class table (0.7 / 0.4) with panphon **feature-overlap** | Sound similarity now comes from real phonetics; e.g. `t`/`d` score very high automatically, no manual table |
| 2026-05-31 | `m11-panphon-similarity` | Environment | Set `PYTHONUTF8=1` for `mfa_env` so panphon can read its IPA data file on Windows | Without it, importing panphon crashes; fix lets the notebook run end-to-end |
| 2026-05-24→27 | `m10-ipa-switch` | Phoneme alphabet | Switch MFA model from ARPAbet to **IPA** (`english_mfa`) | Sounds now written in IPA (`aw`, `aj`, `ɹ`…); old ARPAbet class table stopped working (deferred to M11) |
| 2026-03-18 | *(early history)* | Slant rhymes | Add phoneme-class scoring: same class = 0.7, same broad group = 0.4 | Near-rhymes (e.g. `t`/`d`) started getting partial credit instead of zero |
| 2026-03-11 | *(early history)* | Rhyme matching | Add longest-common-tail similarity + configurable `RHYME_MODE` | Multi-syllable words (e.g. *underground*) match on their shared ending rather than failing |
| 2026-03-09 | *(early history)* | Similarity scale | Upgrade similarity from yes/no to a continuous 0.0–1.0 score | Rhymes can now be ranked by strength, not just "rhyme or not" |

> **Resolved in M11:** the walk-stop threshold was retired with the tail walk; the
> clustering threshold was kept at `0.7` (Option B), which merges the `-oud` and `-ound`
> families and lets the `-ight` family render with "I" included. See the 2026-06-04 rows.
