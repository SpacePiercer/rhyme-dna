---
title: DECISIONS
type: note
permalink: verse-dna/decisions
---

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
extract_rhyme_candidates()  →  rhyme candidates (end-only or full-line)
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

Threshold: 0.5 for `"end_only"` mode. Note: this threshold is too permissive when
used with `"full_line"` mode — the larger word pool produces shallow tail matches
(e.g. `N D` shared between `and` and `mound`) that clear the 0.5 bar incorrectly.
Use `"stressed"` mode at threshold 0.7 when running `"full_line"` detection.

### `"entire_word"`

Rhyme unit = full phoneme sequence of the word. Uses `phoneme_sequence_similarity`
(forward match) instead of tail similarity. Mainly useful for debugging and for
exact-rhyme detection on short words.

Threshold: 0.7

---

## DETECTION_MODE options

Two modes are available via the `DETECTION_MODE` config variable in Section 1 of the
notebook.

### `"end_only"` (original behaviour)

Only the last word of each line is treated as a rhyme candidate. This is the correct
mode for detecting end-rhyme schemes (AABB, ABAB, etc.).

### `"full_line"`

Every word in every line is treated as a rhyme candidate. No word-level filter is
applied — not even for grammatically insignificant words like "it", "and", "the".

**Reason for no filter:** function words and pronouns can be the backbone of an
intentional rhyme scheme. The canonical example is Eminem's "Ja shit" quatrain, where
"it" (an unstressed pronoun) is the rhyming unit across every line:
`squash it → stop it → crossed it → lost it → Nas shit`. Any word-level filter would
destroy this detection.

Noise from short or phonetically weak words is handled downstream at the
**visualisation layer** (Milestone 8), not here. Words with no matching cluster
partners naturally become singletons and are suppressed at render time.

The only guard applied at extraction time is a **data quality check**: words with an
empty phoneme list or an empty rhyme unit are skipped. This handles MFA alignment
failures, not linguistic filtering.

**Recommended mode pairing:** `"full_line"` + `"stressed"` + threshold `0.7`.
`"stressed_plus"` at threshold `0.5` over-merges when the candidate pool is large.

---

## similarity_engine.py — key decisions

### `rhyme_similarity()` routes through `longest_common_tail_similarity` for both `"stressed"` and `"stressed_plus"` modes

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

### `extract_rhyme_candidates()` replaces `extract_end_words()` as the primary function

**Decision:** `extract_end_words()` is retained as a backwards-compatibility wrapper
but all new code calls `extract_rhyme_candidates()` directly.

**New fields in candidate dicts:**
- `word_index` — position of the word within its line (0-based)
- `is_line_end` — boolean, True if this word is the last word of its line

These fields are used downstream by the visualisation layer (Milestone 8) to
distinguish end-rhymes from internal rhymes and to reason about positional alignment.

---

## html_generation.py — key decisions

### `generate_rhyme_html()` now accepts `detection_mode` parameter

**Problem:** the original function rendered one candidate per line — correct for
`"end_only"` but broken for `"full_line"`. With multiple candidates per line it
repeated the line once per candidate and truncated each line at the highlighted word,
producing a staircase effect.

**Fix:** candidates are first grouped by `line_index`. Each line is then rendered
exactly once. In `"full_line"` mode, words are walked left to right and each candidate
word is wrapped in its cluster colour span inline. In `"end_only"` mode, original
behaviour is preserved unchanged.

---

## evaluation.py — known limitation

`expected_clusters` in the notebook is fragile: it stores cluster *letters* (A, B, C…)
which shift whenever the word pool changes (e.g. switching between `"end_only"` and
`"full_line"` modes). Rather than updating the dict every time the mode changes, the
evaluation is left as-is for now. This will be replaced in Milestone 13 with a
**pairwise cluster identity** check: instead of comparing letters, the evaluator asks
"do these two words share a label?" — which is stable across any pool size or mode.

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

### Intra-milestone fixes (between M6 and M7)

1. **`longest_common_tail_similarity` denominator** — changed from `max_len` to
   `min_len`. Affected file: `similarity_engine.py`.

2. **`rhyme_similarity` routing** — `"stressed"` mode now uses
   `longest_common_tail_similarity` instead of the broken weighted vowel/coda/length
   scorer. Affected file: `similarity_engine.py`.

3. **`"stressed_plus"` extraction implemented** — previously a copy-paste placeholder.
   Affected file: `rhyme_extraction.py`.

4. **`get_threshold()` helper added** — `clustering.py` now exports this function.
   Affected files: `clustering.py`, `rhyme-DNA.ipynb`.

### Milestone 7 — Internal Rhymes

**What was built:**

- `DETECTION_MODE` config variable added to Section 1 of the notebook
- `extract_rhyme_candidates()` added to `rhyme_extraction.py` as the new primary
  extraction function; `extract_end_words()` kept as backwards-compatible wrapper
- No word-level filter in `"full_line"` mode — all words extracted as candidates
- Data quality guards only: skip empty phoneme list, skip empty rhyme unit
- `word_index` and `is_line_end` fields added to all candidate dicts
- `generate_rhyme_html()` rewritten: groups by `line_index`, renders each line once,
  walks words left-to-right wrapping candidates in colour spans
- `DETECTION_MODE` threaded through from notebook Section 1 to Section 7

**Key decisions:**

- No function word filter — Eminem "Ja shit" example proves short unstressed words
  can be the primary rhyming unit. Filter noise at render time (Milestone 8) instead.
- `"stressed_plus"` threshold (0.5) too permissive for `"full_line"` mode — shallow
  tail matches (e.g. `N D` in `and` vs `mound`) over-merge at that threshold.
  Recommended pairing: `"full_line"` + `"stressed"` + threshold `0.7`.
- `expected_clusters` evaluation left as-is; will be replaced with pairwise identity
  check in Milestone 14.

**Test verses:**
```
I found the sound of the underground
The crowd was loud and proud around the mound
A light at night ignites the kite in flight
The sight of white delight shines bright tonight
```
```
That Ja shit I tried to squash it it was too late to stop it
Theres a certain line you just dont cross and he crossed it
I heard him say Hailies name on a song and I just lost it
It was crazy the shit went way beyond some Jay Z and Nas shit
```

### Milestone 8 — Intelligent Rhyme Rendering

**What was built:**

- `find_rhyme_suffix_span()` added to `html_generation.py` — a greedy
  phoneme-to-grapheme aligner that maps the rhyme unit back to a character span
  within the word string. Returns `(start_char, end_char)` so only the rhyming
  suffix is wrapped in the colour span, not the whole word.
- `filter_clusters()` added to `html_generation.py` — a quality gate applied at
  render time. A cluster passes if its minimum rhyme unit length is >= `min_phonemes`
  (default 2) AND either >= 2 members span >= 2 different lines, OR >= 3 members
  total. Singletons are suppressed automatically.
- `generate_rhyme_html()` updated to call both new helpers. Accepts two new
  parameters: `min_phonemes` (default 2) and `debug` (default False). Existing
  call signatures are fully backwards-compatible.

**Key decisions:**

- **Grapheme aligner over TextGrid timecodes** — the phone tier gives start/end
  times per phoneme, but timecodes do not map to character positions directly. A
  grapheme aligner working on the surface word string is simpler, equally accurate,
  and self-contained. Timecodes remain useful for a future audio waveform
  highlighting feature but are not the right tool here.
- **Filter at render time, not extraction time** — consistent with the Milestone 7
  decision not to filter function words at extraction time. All candidates flow
  through the pipeline; the render layer decides what is worth showing. This keeps
  the pipeline data complete for scoring and evaluation (Milestone 13).
- **Safe fallback on alignment failure** — `find_rhyme_suffix_span()` returns
  `(0, len(word))` (whole-word highlight) on any alignment failure. Never crashes,
  never silently drops a highlight.
- **`-oud` / `-ound` correctly split into separate clusters** — `crowd/loud/proud`
  share `AW1 D`; `found/sound/underground/mound` share `AW1 N D`. These are
  genuinely distinct rhyme units. The visual separation is correct. Related-cluster
  colour mapping (Milestone 10) will signal their phonetic kinship visually.

**Test result (sound/underground verse, `"stressed"` mode, `"full_line"` detection,
threshold 0.7):**

- Passing clusters: `B` (-ound, 5 members), `E` (-oud, 3 members), `H` (-ight, 9 members)
- Blocked clusters: all singletons and shallow matches (`i`, `the`, `a`, `of`,
  `was`, `and`, `at`, `in`, `ignites`, `shines`)
- Suffix highlighting confirmed: e.g. `under`**`ground`**, `a`**`round`**,
  `m`**`ound`** — prefix unstyled, rhyming suffix coloured

### Milestone 9 — Slant Rhyme Detection

**What was built:**

- `PHONEME_CLASSES` table added to `similarity_engine.py` — maps every ARPAbet
  symbol (stress digits stripped) to a fine-grained articulatory class (e.g.
  `"stop_alveolar"`, `"vowel_front_high"`). Voiced/unvoiced pairs (T/D, S/Z,
  P/B, F/V) share the same class so they score partially against each other.
- `_SUPERCLASS` table added — maps each fine class to a broader group (e.g.
  `"vowel_front_high"` and `"vowel_front_mid"` both map to `"vowel_front"`),
  enabling a second tier of partial credit for related-but-not-identical phonemes.
- Two score constants defined:
  - `SAME_CLASS_SCORE = 0.7` (same articulatory class, e.g. T/D)
  - `SAME_SUPERCLASS_SCORE = 0.4` (same broad family, e.g. IY/EY)
- `phoneme_similarity(p1, p2)` added to `similarity_engine.py` — returns 1.0
  (identical), 0.7 (same class), 0.4 (same superclass), or 0.0 (unrelated).
- `longest_common_tail_similarity()` upgraded — replaces exact-match comparison
  with `phoneme_similarity()`. Walk continues as long as score >= 0.4; accumulates
  fractional scores; divides by min_len as before.

**Spot-check results (manually supplied rhyme units):**

| Pair | Score | Type |
|---|---|---|
| light / night | 1.000 | Perfect |
| found / mound | 1.000 | Perfect |
| late / made | 0.850 | Slant (T/D) |
| face / days | 0.850 | Slant (S/Z) |
| beat / bit | 0.850 | Slant (IY/IH) |
| fate / feet | 0.700 | Slant (EY/IY) |
| light / found | 0.350 | Unrelated (below threshold) |
| the / mound | 0.000 | Unrelated |

**Regression result (sound/underground verse, `"stressed"` mode, `"full_line"`
detection, threshold 0.7, min_phonemes=2):**

- `B`: found, sound, underground, around, mound (-ound) ✓
- `D`: of, was (weak AH slant — acceptable) ✓
- `E`: crowd, loud, proud (-oud) ✓
- `G`: light, night, kite, flight, sight, white, delight, bright, tonight (-ight) ✓

All three core clusters from M8 preserved. Cluster labels shifted by one letter
due to `of`/`was` joining cluster D — cosmetic only.

**Key decisions:**

- **Partial credit on consonants accepted** — voiced/unvoiced pairs (T/D, S/Z)
  get 0.7. An attempt to restrict partial credit to vowels only was rejected
  because it broke classic slant rhymes like `late`/`made` (T vs D at coda).
- **`of`/`was` slant cluster accepted** — the scorer correctly detects their
  shared `AH` vowel. These are weak but real slant rhymes; filtering them out
  would require a quality gate change that risks blocking legitimate weak clusters
  elsewhere. Left as-is.
- **Walk stop condition: score < 0.4** — a score below `SAME_SUPERCLASS_SCORE`
  means the phonemes are from entirely different families. Walking further would
  only accumulate zeros, so stopping is correct.
- **`debug=False` parameter added to `longest_common_tail_similarity()`** —
  prints per-position pair scores when enabled. Follows project convention.

### Milestone 10 — Switch MFA to IPA

**What was built:**

- MFA alignment switched from the `english_us_arpa` acoustic model to the
  `english_mfa` model. The TextGrid `phones` tier now carries IPA symbols
  (`aw`, `aj`, `ɹ`, `ð`, `a`, `t`, `d`, …) instead of ARPAbet (`AW1`, `AY1`,
  `R`, `DH`, …).
- `OUTPUT_TEXTGRID_PATH` changed to `input.TextGrid` to match MFA's naming
  convention (MFA names the output after the input wav stem).
- `normalize_phoneme()` rewritten — strips IPA stress markers (`ˈ` primary,
  `ˌ` secondary) instead of ARPAbet stress digits (`0`, `1`, `2`).
- `extract_rhyme_unit()` rewritten — IPA carries no per-vowel stress digits,
  so the function now walks the phoneme list right-to-left and uses the
  rightmost IPA vowel as the stress anchor.
- `_IPA_VOWELS` set added to `rhyme_extraction.py` — a hand-curated set of
  the IPA vowel symbols that actually appear in `english_mfa` output (ASCII
  base vowels plus `ɑ`, `ɒ`, `ɐ`, `æ`, `ɛ`, `ɜ`, `ɪ`, `ɔ`, `ʊ`, `ʌ`, `ə`).
  `_is_ipa_vowel()` checks membership.
- Notebook re-executed end-to-end with the IPA alignment; HTML output
  regenerated.
- `.gitignore` extended to exclude `.claude/`, `_debug_*` files, and `kb/`
  (basic-memory notes).
- `CLAUDE.md` notebook command updated with explicit `--kernel_name` flag.

**Key decisions:**

- **`english_mfa` chosen over `english_us_ipa`** — `english_mfa` is the
  current MFA-distributed English IPA model; `english_us_ipa` (the name
  used in earlier ROADMAP wording) refers to the same family of models
  under an older naming. Both emit IPA. The currently downloadable model
  is `english_mfa`, so that is what the pipeline uses.
- **Rightmost IPA vowel as stress anchor** — IPA represents stress as a
  prefix mark on the syllable (`ˈ`), not as a per-vowel digit suffix.
  Reliably attaching `ˈ` to the correct phoneme inside a multi-phoneme
  syllable is not straightforward at this layer. The rightmost vowel is
  a robust proxy for the rhyme anchor: end-rhymes hinge on the final
  stressed syllable, and that syllable's vowel is almost always the
  rightmost vowel in the word.
- **Hand-curated `_IPA_VOWELS` set** — restricted to symbols observed in
  `english_mfa` output rather than the entire IPA vowel chart. Keeps the
  vowel test deterministic and avoids false positives from rare or
  unrelated IPA codepoints.

**Known limitation deferred to Milestone 11:**

- `PHONEME_CLASSES`, `_SUPERCLASS`, `SAME_CLASS_SCORE`, `SAME_SUPERCLASS_SCORE`
  in `similarity_engine.py` are still **ARPAbet-keyed** (`"AW"`, `"T"`,
  `"D"`, …). With IPA inputs the class lookups all return `None`, so
  `phoneme_similarity()` collapses to identity-only: exact match → 1.0,
  everything else → 0.0. The M9 slant-rhyme partial credit (T/D = 0.7,
  IY/EY = 0.4) is effectively disabled.
- Identity-based clustering still works on the test verse (`-ound`,
  `-oud`, `-ight` still cluster correctly because their tails match
  exactly), so the regression is graceful rather than catastrophic.
- The class table is **not** being migrated to IPA keys because
  Milestone 11 deletes it outright in favour of panphon
  feature-overlap ratios. Patching it now would be throwaway work.

---

## Open questions / next steps

- Milestone 10: switch MFA to IPA — prerequisite for panphon integration.
- Milestone 11: replace hand-coded similarity table with panphon feature vectors.
- Milestone 12: phoneme-class letter colouring (DNA view) — default output mode.
- Milestone 13: rgba alpha-encoded colour intensity for rhyme cluster view.
- Milestone 14: global phoneme-stream rhyme detection — replaces tail-walk entirely.
- Milestone 16: complexity scoring tied to OUTPUT_MODE = "rhyme" cluster output.
- Milestone 17: replace letter-based evaluation with pairwise cluster identity check.
- Phoneme-stream repo: separate development track.
- Language support: English only for now.

---

## Architectural decision: move to IPA + panphon (agreed before Milestone 10)

### What changes and why

Three parts of the pipeline were hand-coded decisions that are being replaced by
phonologically grounded alternatives:

| Current (manual) | Proposed (grounded) |
|---|---|
| ARPAbet phonemes via `english_us_arpa` | IPA phonemes via `english_us_ipa` |
| Hand-coded `PHONEME_CLASSES` table | panphon articulatory feature vectors |
| Magic constants `0.7`, `0.4` | Feature overlap ratio — computed, not guessed |

### Why IPA instead of ARPAbet

panphon, the standard Python library for phonological feature vectors, operates on
IPA symbols. ARPAbet is not supported. The switch is a prerequisite, not a goal in
itself.

### Why panphon instead of the class table

The hand-coded two-tier table (`SAME_CLASS_SCORE = 0.7`, `SAME_SUPERCLASS_SCORE = 0.4`)
is a manual approximation of articulatory similarity. It requires maintenance when new
phoneme types are encountered and the tier boundaries are arbitrary.

panphon represents each phoneme as a fixed-length binary feature vector (voicing,
place of articulation, manner, etc.). Similarity between two phonemes is computed as
the ratio of shared features — a continuous 0.0–1.0 value derived from phonological
fact, not from a lookup table.

### How the new similarity chain works

```
IPA symbol
    ↓
panphon feature vector  (e.g. /d/ → [+voice, +alveolar, +stop, ...])
    ↓
phoneme_similarity(p1, p2)  →  feature overlap ratio  (0.0–1.0)
    ↓
longest_common_tail_similarity()  →  sequence score  (0.0–1.0)
    ↓
cluster_rhymes()  →  cluster labels
```

The tail-walking loop in `longest_common_tail_similarity()` is unchanged — it still
walks from the right end of both sequences and stops on a low-scoring pair. Only
what it calls changes: `phoneme_similarity()` now returns a panphon-derived ratio
instead of a class-table lookup.

### Threshold

The clustering threshold (currently `0.7`) still controls cluster membership. The
correct long-term approach is to derive the threshold empirically from the verse's
own pairwise score distribution (find the natural valley between rhyme-pair scores
and non-rhyme-pair scores — analogous to Otsu's method in image thresholding).
This is deferred until the panphon scorer is stable; the threshold is kept as a
manually set constant for now.

### DNA view — Milestone 12 design decisions

- **Phoneme classes:** panphon's built-in feature categories are used directly as
  the colour classes. Classes are linguistically defined and stable across songs —
  no clustering step, no per-verse variation.
- **Silent letters:** letters with no corresponding phoneme (e.g. the `e` in *phone*)
  receive no colour (transparent/unstyled). They are visually neutral.
- **Digraphs:** both letters of a multi-letter grapheme (e.g. `sh`, `th`) share the
  colour of the single phoneme they represent.
- **Output mode switch:** `OUTPUT_MODE = "dna"` (default) / `"rhyme"` (cluster view).

### Rhyme cluster view — Milestone 13 design decisions

Rather than treating cluster membership as binary (in / out), each word's highlight
will use `rgba(r, g, b, alpha)` where alpha encodes the word's average pairwise
similarity to other members of its cluster. Perfect rhymes render at full opacity;
slant rhymes at partial opacity. This reflects the continuous nature of rhyme without
requiring a second threshold.

Hue assignment will also be similarity-driven: phonetically related clusters (e.g.
`-oud` / `-ound`) receive hues that are close together on the colour wheel.

### Tail-walk retirement — Milestone 14

`longest_common_tail_similarity()`, `extract_rhyme_unit()`, and
`extract_rhyme_candidates()` are to be retired in Milestone 14 in favour of a
boundary-free, stream-based pattern detector.

**Why:** the tail-walk is anchored at word endings and compares fixed-length phoneme
sequences position by position. It cannot handle insertions (the `-oud` / `-ound`
problem), cannot detect multi-word rhyme schemes (e.g. *"document shredder"* /
*"you meant shredder"*), and each attempted fix adds a new magic constant and a new
failure mode. The approach is too rigid to expand upon without accumulating patches.

**What replaces it:** a phoneme-stream detector that treats the full lyric piece as
one continuous IPA sequence, finds similar subsequences at any position, and maps
them back to grapheme positions. The exact algorithm (sliding window, local sequence
alignment, or similar) is to be decided at the start of Milestone 14.

The phoneme-stream pipeline that was originally planned as a separate repo (old M18)
is subsumed by this approach — it is now the core detection method, not a parallel
experiment.
