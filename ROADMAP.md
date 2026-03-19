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

---

## Upcoming

### [ ] Milestone 10 — Related-Cluster Colour Mapping

**Goal:** assign visually related colours to phonetically related clusters, so the
HTML output signals rhyme family relationships at a glance.

Subgoals:
- After clustering, compute inter-cluster similarity scores (average pairwise
  similarity between members of different clusters)
- Clusters scoring above an inter-cluster threshold get hues that are close together
  on the colour wheel; phonetically distant clusters get maximally different hues
- Implement a hue-based colour assignment function that takes a similarity graph of
  clusters and returns a colour per label
- Test on the sound/underground verse: `-oud` and `-ound` clusters should receive
  visually related colours

**Why this matters:** the current palette assigns colours arbitrarily. Related rhyme
families (e.g. `-oud` / `-ound`) are visually indistinguishable from unrelated ones.
Colour relatedness makes the rhyme structure legible at a glance without reading the
words.

**Depends on:** Milestone 9 — inter-cluster similarity scores are only meaningful once
the similarity function understands phoneme classes.

---

### [ ] Milestone 11 — Insertion-Tolerant Tail Scoring

**Goal:** upgrade `longest_common_tail_similarity()` to skip inserted consonants
when walking tails, so that clusters like `-oud` and `-ound` can be detected as
cross-cluster slant rhymes.

Subgoals:
- Design an insertion-skip mechanism: when the tail walk hits a mismatch, check
  whether skipping one phoneme on either side recovers a match
- Score the insertion penalty (skipped phoneme should reduce the total score)
- Verify that `proud`/`mound` scores above 0.7 with insertion tolerance enabled
- Verify that unrelated clusters are not over-merged
- Calibrate penalty weight so the feature is togglable without breaking M9 results

**Why this matters:** `-oud` / `-ound` are the canonical example of a real rhyme
relationship that the current tail walk misses because the inserted nasal `N` halts
the walk before `AW` can match `AW`. Noted as unresolved in M8 and M9.

**Depends on:** Milestone 9.

---

### [ ] Milestone 12 — MFA Limitation Evaluation

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

### [ ] Milestone 13 — Rhyme Complexity Scoring

**Goal:** produce a numeric score per verse reflecting rhyme density and sophistication.

Subgoals:
- Define scoring components:
  - Rhyme density: rhyming words / total words
  - Scheme complexity: number of distinct clusters, average cluster size
  - Multi-syllable bonus: weighted by length of shared rhyme unit
  - Internal rhyme bonus: mid-line rhymes count toward complexity
- Produce a per-verse score and a per-line breakdown
- Visualise as an annotated HTML page (extend `generate_rhyme_html()`)

---

### [ ] Milestone 14 — Structural Refactor for Modularity

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

### [ ] Milestone 15 — Phoneme-Stream Pipeline (separate repo)

**Goal:** implement the word-boundary-free phoneme-stream architecture as a parallel
system to the word-based pipeline.

Subgoals:
- Take raw phoneme sequence from TextGrid (phones tier only, no word boundaries)
- Sliding window over phoneme stream to find repeated patterns
- Map detected patterns back to word positions for visualisation
- Compare output against word-based pipeline on the same verse
- Document where phoneme-stream detects rhymes that word-based misses

**Why separate:** this is a fundamentally different architecture. It should be
developed and evaluated independently, then potentially merged or run alongside
the word-based system.

---

## Long-term vision (post-Milestone 15)

- Web app with song URL input → rhyme scheme visualisation output
- Custom audio-to-phoneme model (to replace MFA for non-standard pronunciations)
- Multi-language support (requires language-specific acoustic models)
- Music analysis layer (tonality, tempo, beat alignment) — separate from lyrics engine
- Rhyme scheme comparison across artists / albums (stylometric analysis)
