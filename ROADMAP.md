---
title: ROADMAP
type: note
permalink: verse-dna/roadmap
---

# ROADMAP.md — Verse DNA

Forward-looking milestone plan. Each milestone gets its own chat named `Milestone N`.
When a milestone is complete, mark it `[x]` and add a section to `DECISIONS.md`.
The next chat always picks up the first `[ ]` milestone.

---

## Status key

- `[x]` Complete — documented in `DECISIONS.md`
- `[~]` In progress — current chat
- `[ ]` Not started

---

## Completed

### [x] Milestone 3 — Deterministic Rhyme Extraction Engine

- `extract_rhyme_unit()` with `stressed` mode
- `extract_end_words()` reading from lyrics `.txt` file
- End-of-line word detection from TextGrid
- Hard clustering with greedy threshold algorithm
- `generate_rhyme_html()` — colour-coded HTML output per rhyme cluster
- `debug_rhyme_analysis()` and `evaluate_rhyme_detection()` for testing

### [x] Milestone 4 — Controlled Testing Framework

- Test dataset: "sound/underground/mound/flight/tonight" verse
- `debug_rhyme_analysis()` debug mode
- Expected cluster annotation and accuracy evaluation
- Edge case coverage: multi-syllable words, secondary stress

### [x] Milestone 5 — Similarity Refinement Layer

- Similarity scoring upgraded from boolean to continuous 0.0–1.0 scale
- `compute_similarity_pairs()` and `build_similarity_matrix()`
- `longest_common_tail_similarity()` as the core scoring function
- Similarity matrix computed internally (heatmap visualisation deferred)

### [x] Milestone 6 — Multi-Syllable Expansion

- `RHYME_MODE` config variable: `"stressed"` / `"stressed_plus"` / `"entire_word"`
- `"stressed_plus"` implemented: walks back to preceding vowel for richer rhyme unit
- Mode-aware thresholds via `get_threshold(rhyme_mode)` in `clustering.py`
- `SIMILARITY_THRESHOLD_STRESSED_PLUS = 0.5` (mathematically justified)
- All three modes pass 4/4 accuracy on test verse

### [x] Intra-milestone fixes (between M6 and M7)

- `longest_common_tail_similarity` denominator fixed: `max_len` → `min_len`
- `rhyme_similarity()` routing fixed: `"stressed"` now uses tail similarity,
  retiring the broken vowel/coda/length weighted scorer
- `"stressed_plus"` extraction was a placeholder (copy of `"stressed"`) — now properly
  implemented
- `get_threshold()` wired into notebook Section 6

### [x] Milestone 7 — Internal Rhymes

- `DETECTION_MODE` config variable: `"end_only"` / `"full_line"`
- `extract_rhyme_candidates()` replacing `extract_end_words()` as the primary function
- `"full_line"` mode extracts every word in every line with no word-level filter
- Empty phoneme / empty rhyme unit guard (data quality, not linguistic filter)
- `is_line_end` and `word_index` fields added to candidate dicts
- `extract_end_words()` retained as a backwards-compatibility wrapper
- `generate_rhyme_html()` rewritten to group candidates by line and render each
  line once with all highlighted words inline — fixed staircase/repetition bug
- `DETECTION_MODE` passed through to `generate_rhyme_html()` from notebook Section 7
- Threshold tuning: `stressed_plus` threshold too permissive for full word pool;
  use `"stressed"` mode at `0.7` threshold for `"full_line"` mode
- Test verse: Eminem "Ja shit" quatrain — dense internal `-it` rhyme chain

### [x] Milestone 8 — Intelligent Rhyme Rendering

- `find_rhyme_suffix_span()` added to `html_generation.py` — greedy phoneme-to-grapheme
  aligner; returns `(start_char, end_char)` of the rhyming suffix within the word string
- `filter_clusters()` added to `html_generation.py` — render-time quality gate:
  passes clusters with rhyme unit depth >= 2 phonemes AND (>= 2 members across >= 2
  lines OR >= 3 members total); singletons suppressed automatically
- `generate_rhyme_html()` updated: calls both helpers, adds `min_phonemes` and `debug`
  parameters, fully backwards-compatible
- Grapheme aligner chosen over TextGrid timecodes — timecodes don't map to character
  positions directly; aligner is simpler, self-contained, and equally accurate
- Test result: `-ound` (5 members), `-oud` (3 members), `-ight` (9 members) pass;
  all singletons and shallow clusters blocked

### [x] Milestone 9 — Slant & Phoneme-Class Similarity

**Goal:** detect near-rhymes (slant rhymes) by grouping phonemes into classes.

**What was done:**
- Defined phoneme class map (stops, fricatives, nasals, liquids, glides, vowel families)
- Upgraded `longest_common_tail_similarity()` to give partial credit for class matches:
  e.g. T and D (both alveolar stops) score 0.7; T and S (stop vs fricative) score 0.0
- Class weights defined as constants (`SAME_CLASS_SCORE = 0.7`, `SAME_SUPERCLASS_SCORE = 0.4`)
- Verified slant rhyme detection without over-merging unrelated clusters
- Tested on the sound/underground verse with known rhyme families

**Why this mattered:** rap frequently uses near-rhymes as intentional craft. Treating
them as non-rhymes produces false negatives. This is where the system starts to
reflect actual rhyme sophistication.

### [x] Milestone 10 — Switch MFA to IPA

**What was done:**
- MFA alignment switched from `english_us_arpa` to the `english_mfa` IPA model
- TextGrid `phones` tier now carries IPA symbols (`aw`, `aj`, `ɹ`, `ð`, …)
- `OUTPUT_TEXTGRID_PATH` renamed to `input.TextGrid` (MFA naming convention)
- `normalize_phoneme()` rewritten to strip IPA stress markers (`ˈ`, `ˌ`) instead
  of ARPAbet digits
- `extract_rhyme_unit()` rewritten — uses the rightmost IPA vowel as stress anchor
  (IPA has no per-vowel stress digits); `_IPA_VOWELS` set + `_is_ipa_vowel()` helper
  added to `rhyme_extraction.py`
- `.gitignore` extended (`.claude/`, `_debug_*`, `kb/`); notebook headless command
  in `CLAUDE.md` updated with `--kernel_name`
- Notebook re-executed end-to-end; HTML regenerated

**Known limitation (deferred to M11):** `PHONEME_CLASSES` is still ARPAbet-keyed
and not consulted on IPA input — slant scoring collapses to identity-only
(1.0 / 0.0). The `-ound` / `-oud` / `-ight` clusters survive because their tails
match exactly. M11 deletes the class table outright, so patching it would be
throwaway work.

---

## Upcoming

### [ ] Milestone 11 — Replace Similarity Engine with panphon

**Goal:** replace the hand-coded `PHONEME_CLASSES` table and score constants with
phonological feature vectors from the `panphon` library, so phoneme similarity is
grounded in articulatory features rather than manual decisions.

Subgoals:
- Install `panphon`; build an `ipa_to_features()` lookup returning a feature vector
  for any IPA symbol
- Remove `PHONEME_CLASSES`, `_SUPERCLASS`, `SAME_CLASS_SCORE`, `SAME_SUPERCLASS_SCORE`
  entirely from `similarity_engine.py`
- Implement `phoneme_similarity(p1, p2)` returning a feature-overlap ratio (0.0–1.0)
  computed from the two symbols' panphon vectors — no hand-coded tiers
- Update `longest_common_tail_similarity()` to call the new scorer
- Run spot-checks against the M9 score table to verify directional correctness

**Why this matters:** the current two-tier table (0.7 / 0.4) is a manual approximation
of phonological distance. Feature overlap ratio replaces magic constants with a
principled continuous measure that generalises to any IPA symbol without table
maintenance.

**Depends on:** Milestone 10.

---

### [ ] Milestone 12 — Phoneme-Class Letter Colouring (DNA View)

**Goal:** add a new output mode — the default — where every letter in the lyrics is
coloured by the phoneme class of the sound it represents, using panphon's built-in
feature categories. The result is a full phonological texture of the piece; rhyme
patterns become visible as repeated colour patterns rather than being explicitly
detected.

Subgoals:
- Extend the grapheme-phoneme aligner (`find_rhyme_suffix_span()` covers only the
  rhyme suffix; extend it to cover the full word) so every letter can be mapped to
  its corresponding phoneme
- Map each IPA phoneme to its panphon built-in feature category (classes are
  linguistically defined and stable across songs — not derived from clustering)
- Assign a distinct colour to each category
- Generate HTML where every letter `<span>` carries the colour of its phoneme's
  category; letters with no corresponding phoneme (silent letters, e.g. the `e`
  in *phone*) receive no colour (transparent/unstyled)
- Digraphs (`sh`, `th`, etc.) — both letters share the colour of the single phoneme
  they represent
- Add an `OUTPUT_MODE` config variable: `"dna"` (this view, default) and `"rhyme"`
  (existing cluster view)

**Why this matters:** this is the "Verse DNA" concept made literal — a phonological
fingerprint of the lyrics at the individual-sound level. It requires no threshold
decisions and no rhyme-unit extraction; phonological relationships emerge visually.

**Depends on:** Milestone 11 (panphon in place, IPA symbols available).

---

### [ ] Milestone 13 — Similarity-Driven Colour Intensity

**Goal:** make the HTML output encode not just *which* cluster a word belongs to, but
*how strongly* it belongs there — using `rgba` alpha to visualise similarity score.

Subgoals:
- After clustering, compute each word's average pairwise similarity to other members
  of its cluster (its "membership strength")
- Pass membership strength into `generate_rhyme_html()` and use it as the alpha
  channel: `rgba(r, g, b, strength)` — perfect rhymes render at full opacity, slant
  rhymes at partial opacity
- Assign hues so that phonetically related clusters (e.g. `-oud` / `-ound`) receive
  visually close colours on the colour wheel; unrelated clusters get maximally
  different hues
- Compute inter-cluster similarity (average pairwise score across cluster members)
  to drive the hue proximity assignment
- Test on the sound/underground verse: `-oud` and `-ound` clusters should be visually
  related; a word that barely cleared the threshold should visibly fade

**Why this matters:** a hard colour boundary (in / out) hides the continuous nature of
rhyme. Alpha-encoded strength lets the reader perceive rhyme confidence at a glance —
which is closer to how a listener actually hears near-rhymes.

**Note on threshold:** the clustering threshold still controls cluster membership.
Threshold calibration from data (Otsu's method over the verse's own pairwise score
distribution) is a known improvement but is deferred — it will be addressed once the
full panphon scorer is stable.

**Depends on:** Milestone 11.

---

### [ ] Milestone 14 — Global Phoneme-Stream Rhyme Detection

**Goal:** replace the word-ending tail-walk with a boundary-free, stream-based
pattern detector that finds repeated or similar phoneme subsequences anywhere in
the piece — across word and line boundaries — and maps them back to character
positions for visualisation.

**Why the tail-walk is being retired:** `longest_common_tail_similarity()` is
anchored at word endings and compares fixed-length tails position by position.
This makes it brittle to insertions (the `-oud` / `-ound` problem), unable to
detect multi-word rhyme schemes (e.g. *"document shredder"* / *"you meant shredder"*),
and increasingly hard to patch without accumulating special cases. Each fix
(insertion skipping, penalty weights, skip limits) adds a new magic constant and
a new failure mode.

Subgoals:
- Treat the entire lyric piece as one continuous IPA phoneme sequence, ignoring
  word and line boundaries during pattern search
- Design a pattern-matching approach that can find similar phoneme subsequences
  at any position in the stream (candidate approaches: sliding window with
  panphon similarity, local sequence alignment — exact method TBD at milestone start)
- Map detected pattern instances back to grapheme positions for HTML highlighting
- Verify detection of end rhymes, internal rhymes, and multi-word rhyme schemes
  on the test verses from M7–M9
- Retire `longest_common_tail_similarity()`, `extract_rhyme_unit()`, and
  `extract_rhyme_candidates()` once the new detector covers their use cases

**Depends on:** Milestone 11 (panphon similarity as the core comparison function).

---

### [ ] Milestone 15 — MFA Limitation Evaluation

**Goal:** stress-test the pipeline on real rap audio and identify where MFA fails.

Subgoals:
- Align a real rap verse (suggest: Eminem — 3 a.m., or a verse from Relapse)
- Compare MFA-derived phonemes against expected pronunciations
- Identify failure categories: fast delivery, non-standard pronunciation, ad-libs,
  overlapping sounds
- Document failure rate and its effect on rhyme detection accuracy
- Decision point: is MFA sufficient, or is a hybrid acoustic approach needed?

**Note:** do not attempt to fix MFA failures yet — this milestone is evaluation only.

---

### [ ] Milestone 16 — Rhyme Complexity Scoring

**Goal:** produce a numeric score per verse reflecting rhyme density and sophistication.
Operates on `OUTPUT_MODE = "rhyme"` cluster output only.

Subgoals:
- Define scoring components:
  - Rhyme density: rhyming words / total words
  - Scheme complexity: number of distinct clusters, average cluster size
  - Multi-syllable bonus: weighted by length of shared rhyme unit
  - Internal rhyme bonus: mid-line rhymes count toward complexity
- Produce a per-verse score and a per-line breakdown
- Visualise as an annotated HTML page (extend `generate_rhyme_html()`)

**Depends on:** Milestone 13 (rhyme cluster output with rgba intensity).

---

### [ ] Milestone 17 — Structural Refactor for Modularity

**Goal:** separate the pipeline into clean modules ready for API wrapping.

Subgoals:
- Define module boundaries:
  - `alignment/` — MFA interface, TextGrid parsing, `word_to_phonemes` builder
  - `rhyme_engine/` — extraction, similarity, clustering
  - `scoring/` — complexity scoring
  - `visualisation/` — HTML generation
- Add a thin CLI entry point (`python -m versedna analyse input.txt output.TextGrid`)
- Write module-level docstrings and a `README.md` for each module
- Notebook becomes a demo/testing surface only — no pipeline logic inside cells
- **Upgrade evaluation to pairwise cluster identity** — instead of comparing cluster
  letters directly, check whether two words share a label. Eliminates fragility caused
  by cluster letter shifts when the word pool changes (e.g. switching between
  `"end_only"` and `"full_line"` modes).

---

### [ ] Milestone 18 — Web App MVP

**Goal:** wrap the pipeline in a minimal web interface — song input, rhyme scheme
visualisation output — as the first step toward the Genius-like long-term vision.

Subgoals:
- Define the input surface: lyrics text upload + pre-aligned TextGrid upload
  (full audio-to-alignment pipeline integration is a later step)
- Serve the DNA view and the rhyme cluster view as toggleable HTML output
- No user accounts, no database — static analysis, results shown in browser
- Identify the engineering gaps between the current notebook pipeline and a
  deployable service

**Note:** scope and approach to be decided at milestone start once the core pipeline
(M10–M17) is stable.

---

## Long-term vision (post-Milestone 18)

- Web app with song URL input → rhyme scheme visualisation output
- Custom audio-to-phoneme model (to replace MFA for non-standard pronunciations)
- Multi-language support (requires language-specific acoustic models)
- Music analysis layer (tonality, tempo, beat alignment) — separate from lyrics engine
- Rhyme scheme comparison across artists / albums (stylometric analysis)
