# Verse DNA — Decision Log

This file records architectural and implementation decisions made during development,
including the reasoning behind each one. Intended to give any new chat (or future you)
enough context to continue without re-litigating settled questions.

---

## Project overview

Verse DNA is an audio-aligned phoneme extraction and rhyme structure analysis engine.
The near-term goal is end-rhyme detection and cluster visualization for English lyrics.
The long-term goal is a Genius-like web app where any song can be analysed for its
rhyme scheme, scored for rhyme complexity, and displayed with rhyming words highlighted
in matching colours.

Music analysis (tonality, tempo, etc.) is explicitly out of scope for now.
The system is English-only while MFA + ARPAbet is being used; other languages are a
future concern requiring different acoustic models.

---

## Architecture decision: two separate repos

**Decision:** maintain a word-based pipeline repo and a phoneme-stream repo as separate
projects, not as branches of the same repo.

**Reason:** these are genuinely different architectures, not just different modes.

- The word-based pipeline treats the *word* as the atomic unit. It derives phonemes per
  word from MFA alignment and compares rhyme units word-to-word. Word boundaries are
  a hard constraint.
- The phoneme-stream pipeline dissolves word boundaries entirely and works on the raw
  phoneme sequence. Rhyme patterns are found first, then mapped back to words. This can
  detect rhymes that span word boundaries, compressed syllables, and multi-word rhyme
  chains — all invisible to the word-based approach.

The word-based pipeline is the right baseline system and is easier to evaluate. The
phoneme-stream approach is the right long-term architecture for rap (especially artists
like Eminem whose Relapse accent systematically shifts vowel phonemes across words to
create schemes that span entire bars). Keep both.

---

## Why MFA phonemes, not a dictionary (CMU Pronouncing Dictionary)

**Decision:** all phonemes are derived from MFA forced alignment on the actual audio,
not looked up in a static dictionary.

**Reason:** this is the core insight of the project. Rappers bend pronunciation to make
words rhyme that would not rhyme in standard speech. Example: on Eminem's *Relapse*
album, the AY/EY vowel family is systematically shifted toward IY, so "again", "insane",
and "cocaine" all share the rhyme unit `IY1 N` in actual performance — but a dictionary
would assign them three different rhyme units (EH1 N, EY1 N, EY1 N). MFA on the audio
captures what was actually said. A dictionary lookup never would.

This means `word_to_phonemes` in the notebook is populated from the TextGrid produced
by MFA, not from any external lexicon.

---

## Pipeline: word-based repo (current working system)

```
audio + lyrics text
       ↓
MFA forced alignment  (mfa align ... english_us_arpa)
       ↓
TextGrid  (words tier + phones tier, with timecodes)
       ↓
word_to_phonemes dict  (built in Section 3 of notebook)
       ↓
extract_end_words()  →  rhyme candidates per line
       ↓
extract_rhyme_unit()  →  rhyme unit per word
       ↓
compute_similarity_pairs()  →  pairwise scores
       ↓
build_similarity_matrix()
       ↓
cluster_rhymes()  →  cluster labels (A, B, C…)
       ↓
generate_rhyme_html()  →  colour-coded HTML output
```

---

## RHYME_MODE options

Three modes are available via the `RHYME_MODE` config variable in Section 1 of the
notebook. Switching the variable automatically propagates the correct threshold.

### `"stressed"` (default, most reliable)

Rhyme unit = from primary stressed vowel to end of word.

Examples:
- `mound`   → `[AW1, N, D]`
- `flight`  → `[AY1, T]`
- `tonight` → `[AY1, T]`  (starts at the *last* primary stress)

Threshold: 0.7

### `"stressed_plus"`

Rhyme unit = from the start of the syllable *before* the primary stressed vowel to end
of word. Captures one extra syllable of context for richer multi-syllable matching.

Examples:
- `mound`   → `[M, AW1, N, D]`       (no preceding vowel → include onset consonants)
- `flight`  → `[F, L, AY1, T]`       (no preceding vowel → include onset consonants)
- `tonight` → `[AH0, N, AY1, T]`     (preceding vowel AH0 found at index 1)
- `delight` → `[IH0, L, AY1, T]`     (preceding vowel IH0 found at index 1)

Threshold: 0.5  (lower because longer units make a perfect tail match score ~0.5
against a shorter unit; cross-cluster pairs still score 0.0 so there is no
over-merging risk at this threshold)

### `"entire_word"`

Rhyme unit = full phoneme sequence of the word. Uses `phoneme_sequence_similarity`
(forward match) instead of tail similarity. Mainly useful for debugging and for
exact-rhyme detection on short words.

Threshold: 0.7

---

## similarity_engine.py — key decisions

### `rhyme_similarity()` routes through `longest_common_tail_similarity` for both
`"stressed"` and `"stressed_plus"` modes

**Previous behaviour:** `"stressed"` mode used a weighted vowel/coda/length scorer.
`"stressed_plus"` called `longest_common_tail_similarity`.

**Problem:** the weighted scorer assumed `rhyme_unit[0]` is always the stressed vowel.
This breaks for multi-syllable words. For `underground`, the rhyme unit under
`"stressed"` mode is `[AH1, N, D, ER0, G, R, AW2, N, D]` — the first phoneme is `AH1`,
not `AW`. Comparing `AH` vs `AW` (for `mound`) gives vowel_score = 0.0, collapsing
the total score to ~0.1. Underground and mound failed to cluster.

**Fix:** both modes now route through `longest_common_tail_similarity`. The tail
comparison makes no assumption about where the rhyming vowel sits — it just finds the
longest matching ending, which is the correct definition of rhyme.

**Result:** `underground / mound` scores 1.0 (tail `AW N D` matches perfectly with
stress digits stripped). `flight / tonight` scores 1.0 under `"stressed"` (identical
units `AY1 T`) and 0.5 under `"stressed_plus"` (longer units share only 2 of 4
phonemes at the tail).

### `longest_common_tail_similarity()` uses `min_len` as denominator, not `max_len`

**Previous behaviour:** denominator was `max_len`.

**Problem:** `underground` (rhyme unit length 9) vs `mound` (length 3) — they share a
3-phoneme tail, but `3/9 = 0.33`, below the 0.7 threshold.

**Fix:** denominator is `min_len`. A short word that perfectly matches the tail of a
long word should score 1.0, not be penalised for the length difference. The rhyme is
real regardless of what precedes it in the longer word.

### `normalize_phoneme()` strips stress digits before all comparisons

ARPAbet vowels carry a stress digit (0 = unstressed, 1 = primary, 2 = secondary).
`AW1` and `AW2` are the same phoneme at different stress levels and should match.
`normalize_phoneme` strips these digits so all comparisons are stress-agnostic.

---

## clustering.py — key decisions

### Mode-aware thresholds via `get_threshold(rhyme_mode)`

**Decision:** clustering threshold is not a single constant. `get_threshold()` returns
the appropriate value for the active mode.

- `"stressed"` and `"entire_word"`: threshold = 0.7
- `"stressed_plus"`: threshold = 0.5

**Reason:** see `"stressed_plus"` section above. The threshold must match the scoring
range that the mode's similarity function actually produces.

**Usage in notebook:** `cluster_rhymes(similarity_matrix, threshold=get_threshold(RHYME_MODE))`
Switching `RHYME_MODE` in Section 1 automatically uses the correct threshold everywhere.

---

## rhyme_extraction.py — key decisions

### `"stressed_plus"` walks back to the previous vowel, not just onset consonants

**Implementation:** starting from `stressed_index - 1`, scan left until a phoneme
containing a digit (i.e. an ARPAbet vowel) is found. Use that index as the start of
the rhyme unit.

**Fallback:** if no preceding vowel exists (monosyllabic words, or words where the
primary stress is at index 0), include all phonemes from position 0 — this captures
onset consonants like `[F, L]` in `flight`, which is still richer than `[AY1, T]` and
contributes to graded similarity scores.

**Why not just "include one more consonant":** consonant clusters before a vowel vary
in length (0 consonants for `around`, 2 for `flight`, 3 for potential clusters).
Walking back to the previous *vowel* is linguistically principled — it captures the
full preceding syllable nucleus regardless of how many consonants precede it.

---

## Milestone progress summary

### Milestones 3–4 (completed before this log)
- `extract_rhyme_unit()` with `stressed` mode
- `extract_end_words()` reading from lyrics `.txt` file
- `compute_similarity_pairs()` and `build_similarity_matrix()`
- `cluster_rhymes()` with greedy threshold clustering
- `generate_rhyme_html()` producing colour-coded output
- `debug_rhyme_analysis()` and `evaluate_rhyme_detection()` for testing
- Test dataset: "sound/underground/mound/flight/tonight" verse, 100% accuracy in
  `stressed_plus` mode

### Milestone 5 (completed before this log)
- Similarity scoring upgraded from boolean to 0.0–1.0 continuous scale
- Similarity matrix computed internally (not yet visualised as heatmap)

### Milestone 6 (completed before this log)
- `RHYME_MODE` config variable: `"stressed"` / `"stressed_plus"` / `"entire_word"`
- `extract_rhyme_unit()` extended with mode logic
- `SIMILARITY_THRESHOLD_STRESSED_PLUS` constant introduced

### Intra-milestone fixes (introduced during this conversation)

These fixes were made after Milestone 6 was nominally complete, correcting bugs
discovered during testing.

1. **`longest_common_tail_similarity` denominator** — changed from `max_len` to
   `min_len`. Affected file: `similarity_engine.py`.

2. **`rhyme_similarity` routing** — `"stressed"` mode now uses
   `longest_common_tail_similarity` instead of the broken weighted vowel/coda/length
   scorer. The weighted scorer assumed index 0 of the rhyme unit is always the stressed
   vowel, which fails for multi-syllable words. Affected file: `similarity_engine.py`.

3. **`"stressed_plus"` extraction implemented** — previously both `"stressed"` and
   `"stressed_plus"` ran identical code (a copy-paste placeholder). `"stressed_plus"`
   now correctly walks back to the preceding vowel. Affected file: `rhyme_extraction.py`.

4. **`get_threshold()` helper added** — `clustering.py` now exports this function and
   the notebook Section 6 uses it instead of the hardcoded `SIMILARITY_THRESHOLD`
   constant, ensuring the correct threshold is applied automatically for any mode.
   Affected files: `clustering.py`, `rhyme-DNA.ipynb`.

---

## Test results after all intra-milestone fixes

Input verse:
```
I found the sound of the underground
The crowd was loud and proud around the mound
A light at night ignites the kite in flight
The sight of white delight shines bright tonight
```

Expected clusters: A = {underground, mound}, B = {flight, tonight}

| Mode           | Accuracy |
|----------------|----------|
| stressed       | 4/4 ✓    |
| stressed_plus  | 4/4 ✓    |

---

## Open questions / next steps

- Internal rhymes (Milestone 7): expand from end-of-line words to all words per line.
  Toggle: `mode = end_only | full_line`. This is where the Relapse-style schemes become
  detectable in the word-based pipeline.
- Phoneme-stream repo: separate development track. Word boundaries dissolved; rhyme
  patterns found in the raw phoneme sequence first, then mapped back to text.
- Rhyme grading / complexity scoring: not yet started. Long-term goal is a numeric
  score per verse reflecting density, length, and sophistication of rhyme schemes.
- Language support: English only for now (MFA + ARPAbet). Other languages require
  different acoustic models. Future plan to train a custom audio-to-phoneme model.
