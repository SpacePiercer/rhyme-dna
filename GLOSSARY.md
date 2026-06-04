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

### Sounds and spelling

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

- **Feature-overlap measure** — our score for how similar two sounds are: of panphon's
  24 features, what fraction do the two sounds agree on. `1.0` = identical, `0.0` =
  opposite on everything. Formula: `1 − (sum of |feature differences|) / (2 × 24)`.
- **Longest-common-tail similarity** — our rhyme score for two words: walk inward from
  the *end* of both, adding up how well each sound matches, and stop at the first clear
  mismatch.
- **Walk-stop threshold** — the cutoff used by the tail walk: keep matching sounds while
  their overlap is at or above this number; stop below it.
- **Clustering threshold** — the score two words must reach to be grouped into the same
  rhyme colour/cluster.

---

## Part B — Measurement & linguistic decision backlog

Newest first. Each entry: what was decided, and its effect on the output/score.
Branch names before the per-milestone branching workflow are marked *(early history)*.

| Date | Branch | Area | Decision | Effect |
|---|---|---|---|---|
| 2026-05-31 | `m11-panphon-similarity` | Diphthong handling | Approach **B (segment-expand)**: split tokens like `aj`/`aw` into their panphon segments and compare sound-by-sound, rather than averaging them into one vector | `aw` is compared as `a`+`w`; rhyme tails line up at the sound level instead of the token level |
| 2026-05-31 | `m11-panphon-similarity` | Similarity scorer | Replace the hand-coded phoneme-class table (0.7 / 0.4) with panphon **feature-overlap** | Sound similarity now comes from real phonetics; e.g. `t`/`d` score very high automatically, no manual table |
| 2026-05-31 | `m11-panphon-similarity` | Environment | Set `PYTHONUTF8=1` for `mfa_env` so panphon can read its IPA data file on Windows | Without it, importing panphon crashes; fix lets the notebook run end-to-end |
| 2026-05-24→27 | `m10-ipa-switch` | Phoneme alphabet | Switch MFA model from ARPAbet to **IPA** (`english_mfa`) | Sounds now written in IPA (`aw`, `aj`, `ɹ`…); old ARPAbet class table stopped working (deferred to M11) |
| 2026-03-18 | *(early history)* | Slant rhymes | Add phoneme-class scoring: same class = 0.7, same broad group = 0.4 | Near-rhymes (e.g. `t`/`d`) started getting partial credit instead of zero |
| 2026-03-11 | *(early history)* | Rhyme matching | Add longest-common-tail similarity + configurable `RHYME_MODE` | Multi-syllable words (e.g. *underground*) match on their shared ending rather than failing |
| 2026-03-09 | *(early history)* | Similarity scale | Upgrade similarity from yes/no to a continuous 0.0–1.0 score | Rhymes can now be ranked by strength, not just "rhyme or not" |

> **Pending in M11:** the walk-stop threshold and clustering threshold will be
> re-tuned once the feature-overlap numbers are measured (entry to be added with the
> chosen values and their effect on the `-oud` / `-ound` / `-ight` clusters).
