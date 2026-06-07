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

### [x] Milestone 11 — Replace Similarity Engine with panphon

**What was done:**
- Deleted the hand-coded `PHONEME_CLASSES` table, score constants, and the
  tail-walk scorers from `similarity_engine.py`
- New `rhyme_unit_similarity()` scores rhyme units with panphon's weighted
  feature edit distance (`min_edit_distance`): weighted substitution cost plus
  a bounded insert/delete penalty, normalised by sound count
- Two selectable methods via config constants — **D** (flat penalty, default
  0.75) and **C** (capped weighted cost); raw scores kept
- `phoneme_similarity()` reimplemented on panphon features; `rhyme_similarity()`
  is now mode-agnostic
- `filter_clusters()` gates on *deep* members so bare vowels ("I") stay in a
  cluster without blocking it
- Clustering threshold kept at 0.7 (**Option B**) → -ound / -oud merge into one
  "ow-ending" family; diphthong-as-one and bare-vowel handling deferred (M17 / M14)
- Tests: `python/tests/` (16 passing); notebook re-run end-to-end, both families render

**Decision detail:** see `DECISIONS.md` → "Milestone 11 — Replace Similarity Engine with panphon".

---

## Upcoming

### [ ] Milestone 12 — Assonance-First (Vowel-Weighted) Similarity

**Goal:** make the rhyme score driven primarily by shared **vowels** (assonance),
with consonants — especially the coda (the consonant[s] after the vowel) — counting
for less. This reflects how fast rap rhyme is actually heard: the vowel scheme carries
the rhyme; the final consonants vary freely.

Subgoals:
- Introduce a single **coda-discount knob** `c` into `rhyme_unit_similarity`: consonant
  substitutions and consonant insert/delete costs are multiplied by `c` (vowel costs
  unchanged). `c = 1.0` = today's behaviour; `c = 0.0` = pure assonance (codas ignored).
- Choose `c` by a **sweep validated against an ear-grouped target** (the verse's
  short-i scheme: *with / clip / hip / gripped / width / tip / slit / it / chips / fit /
  ultimate*). Pick the value that merges the target group while still excluding
  wrong-vowel words (e.g. *up*).
- **Chosen target (from the sweep): `c ≈ 0.3`.** Keeps the wrong-vowel *up* out with a
  safety margin (*it/up* = 0.58, *tip/up* = 0.63 — both below the 0.7 cut). A tighter
  setting (`c = 0.15`) merged the group too but left *up* at 0.67, uncomfortably close:
  panphon's default weights compress the vowel space (any two vowels score ~0.89–0.97;
  *ɐ* vs *ɪ* = 0.90, differing only in the *high* and *tense* features), so vowel
  contrasts are weak and *up* is easy to pull in.
- **Clustering caveat to resolve during implementation:** at `c = 0.3`, *clip*/*hip*
  score 0.83+ against the core group (*clip/it* = 0.83, *clip/tip* = 0.88) yet only 0.67
  against the seed word *with*, so today's greedy *single-link-from-seed* clustering
  files them in a sibling cluster. This is a clustering-seed artifact, not a scoring
  failure — fix with proper single-linkage (compare to any member; small change) or
  defer to M17's seedless detector.
- Keep `c` a swappable parameter (not hard-coded into the formula) so Milestone 20
  (learned weights) can replace it without code changes.

**Why this matters:** today the engine splits this one audible scheme into three
clusters by coda (`-ip` / `-it` / `-id̪`). Vowel-weighting merges them into the single
"short-i" family the listener hears.

**Known boundary (hand off to M13/M17):** vowel-weighting is *vowel-greedy* — it also
pulls in other words that happen to share the same last vowel (*is, still, give, think,
explosive*). Distinguishing the *intentional* scheme from *incidental* shared vowels
needs the stress layer (M13) and/or the position-aware stream detector (M17); it is out
of scope here.

**Depends on:** Milestone 11 (panphon scorer in place).

---

### [ ] Milestone 13 — Stress-Aware Scoring

**Goal:** use **stress** (which syllable is said with more force) so the *stressed*
vowel weighs more than unstressed ones — bringing the score closer to which rhymes a
listener actually perceives as the backbone of a line.

Subgoals:
- Stop discarding MFA's stress marks: `normalize_phoneme` currently strips `ˈ` (primary)
  and `ˌ` (secondary) on line 36 of `similarity_engine.py`. Carry that information
  through extraction instead of throwing it away.
- Give the stressed vowel extra weight in `rhyme_unit_similarity` (layered on top of the
  M12 vowel-weighting).
- **Scope limit:** this is *word-internal lexical* stress only (where a word is normally
  stressed, e.g. ÚL-ti-mate). The *performed/metrical* accent across the bar (the 1-vs-2
  groove accents) is NOT available from MFA's labels and is deferred — a possible future
  proxy is vowel duration from the TextGrid, revisited only if needed.

**Why this matters:** the stressed vowel is the anchor of a rhyme. Weighting it makes
the engine agree with the ear on which syllable "carries" the rhyme.

**Depends on:** Milestone 12.

---

### [ ] Milestone 14 — Syllable Decomposition

**Goal:** cut multi-syllable words into **syllables** and compare them
syllable-by-syllable, instead of taking only the single tail from the last stressed
vowel to the end of the word. This lets a long word participate in a scheme through
*each* of its syllables (e.g. *ultimate* → ul-ti-mate matching across *utmost · with ·
it*).

Subgoals:
- Add a **syllabifier** — a standard algorithm that chops a phoneme stream into
  syllables by the rise-and-fall of sonority (how open/loud each sound is).
- Produce a per-syllable representation; compare words (or word-spans) syllable-by-
  syllable rather than as one tail blob.
- Keep the M12/M13 vowel- and stress-weighting working on the new per-syllable units.

**Why this matters:** the current "last-vowel-to-end" rhyme unit can only see one
syllable. Syllable decomposition is the prerequisite for multi-syllable and multi-word
schemes (which the M17 stream detector then finds across word boundaries).

**Depends on:** Milestone 13. Feeds Milestone 17 (stream detection).

---

### [ ] Milestone 15 — Phoneme-Class Letter Colouring (DNA View)

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

### [ ] Milestone 16 — Similarity-Driven Colour Intensity

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

### [ ] Milestone 17 — Global Phoneme-Stream Rhyme Detection

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

**Known false-negative to address here (found in M11):** `ignites`
(`['aj','t','s']`) is a true `-ight` rhyme — it scores 0.812 against `light` — but
is dropped from the cluster. The current clustering is greedy *single-link from a
seed word*: each cluster compares candidates only to its first (seed) word, and the
`-ight` cluster is seeded by the bare vowel "I" (`['aj']`), against which `ignites`
scores only 0.625 (below the 0.7 threshold). A boundary-free stream detector with no
per-cluster seed should catch it. (By contrast, `shines` — `['aj','n','z']`, the
`-ines` ending — scores 0.438 against `light`; it is a genuine slant the scorer
rates lower, a separate question, not a clustering bug.)

**Depends on:** Milestone 11 (panphon similarity as the core comparison function).

---

### [ ] Milestone 18 — MFA Limitation Evaluation

**Goal:** stress-test the pipeline on real rap audio and identify where MFA fails.

Subgoals:
- Align a real rap verse (suggest: Eminem — 3 a.m., or a verse from Relapse)
- Compare MFA-derived phonemes against expected pronunciations
- Identify failure categories: fast delivery, non-standard pronunciation, ad-libs,
  overlapping sounds
- Document failure rate and its effect on rhyme detection accuracy
- Decision point: is MFA sufficient, or is a hybrid acoustic approach needed?

**Concrete failure example (found in M11):** MFA aligns `kite` as
`['c', 'iː', 'ʈ', 'ə']` (a palatal `c`, long `iː`, retroflex `ʈ`, and a stray
trailing schwa) instead of /k aɪ t/. Its rhyme unit becomes the junk `['ə']`, so it
never clusters with the `-ight` family — a clear mis-alignment to catalogue here.

**Note:** do not attempt to fix MFA failures yet — this milestone is evaluation only.

---

### [ ] Milestone 19 — Rhyme-Judgment Dataset & Score Logging

**Goal:** start building the labelled data the weight-learning milestone will need, and
make the pipeline log every pair it scores — so a training set accumulates passively
while other work continues.

Subgoals:
- Add lightweight logging: every scored pair (`word A`, `word B`, rhyme units, raw
  score, method) appended to a versioned dataset file (`.jsonl` / `.csv`)
- Build a tiny rating surface (notebook cell or CLI) to attach a human label to a pair —
  either a 0–1 rating or, preferably, a *ranking* ("A rhymes more than B")
- Define the dataset schema once, stable and versioned, so future training reads it
  directly
- Seed it with the current verse's pairs, hand-labelled by ear

**Why this matters:** there is no target to learn from today. Collecting judgments is
the real unlock and the slowest part — starting early means data is ready when the
fitting milestone arrives. (Passive score-logging can begin informally as soon as the
M11 scorer exists, even before this milestone is formally reached.)

**Depends on:** Milestone 11 (panphon scorer producing scores to log).

---

### [ ] Milestone 20 — Learn panphon Feature Weights from Judgments

**Goal:** replace the hand-chosen feature weights (and insert/delete cost) with values
*fitted* to human rhyme judgments, so the scorer matches how rhymes actually sound
rather than how they were guessed.

Subgoals:
- Keep the scorer pure and parameterised: weights + costs passed in, never hard-coded
  (already the M11 design)
- Loss = **ranking / contrastive** (keep perfect > slant > non with a margin) — easier
  to label than absolute numbers; optionally support regression against 0–1 ratings
- Fit **gradient-free first** (Bayesian optimisation / evolutionary search) — only ~22
  weights, which sidesteps the non-differentiable edit-distance `min()`; a differentiable
  "soft" edit distance is a later option if needed
- Store learned weights in a swappable config file, so the trained metric drops in by
  replacing one file
- Evaluate fitted weights against a held-out set of judgments; compare separation /
  ordering to the hand-tuned D@0.75 baseline
- Candidate first use of learned weights: revisit the deferred "diphthong as one segment"
  question (let the data decide how much a diphthong's halves count)

**Why this matters:** it turns "a penalty was picked by hand" into "the data picked the
weights." It is the natural endpoint of making panphon the source of truth — the
*weights* become learned, not assumed.

**Depends on:** Milestone 19 (labelled data) and Milestone 11 (panphon scorer).

---

### [ ] Milestone 21 — Rhyme Complexity Scoring

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

**Depends on:** Milestone 16 (rhyme cluster output with rgba intensity).

---

### [ ] Milestone 22 — Structural Refactor for Modularity

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

### [ ] Milestone 23 — Web App MVP

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
(M10–M19) is stable.

---

## Long-term vision (post-Milestone 23)

- Web app with song URL input → rhyme scheme visualisation output
- Custom audio-to-phoneme model (to replace MFA for non-standard pronunciations)
- Multi-language support (requires language-specific acoustic models)
- Music analysis layer (tonality, tempo, beat alignment) — separate from lyrics engine
- Rhyme scheme comparison across artists / albums (stylometric analysis)
