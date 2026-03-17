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

---

## Upcoming

### [ ] Milestone 7 — Internal Rhymes

**Goal:** detect rhymes on all words within a line, not just end-of-line words.

Subgoals:
- Add `DETECTION_MODE` toggle: `"end_only"` (current) vs `"full_line"`
- In `"full_line"` mode, extract rhyme candidates from every content word in every line
- Filter out function words (articles, prepositions, conjunctions) — these produce
  noise and are rarely part of intentional rhyme schemes
- Update `generate_rhyme_html()` to highlight mid-line words, not just line endings
- Test on the existing verse; add a second test verse with clear internal rhymes

**Why this matters:** end-rhyme detection misses the majority of rap rhyme craft.
Internal rhymes are where Eminem's Relapse schemes actually live.

---

### [ ] Milestone 8 — Slant & Phoneme-Class Similarity

**Goal:** detect near-rhymes (slant rhymes) by grouping phonemes into classes.

Subgoals:
- Define phoneme class map (stops, fricatives, nasals, liquids, glides, vowel families)
- Upgrade `rhyme_similarity()` to give partial credit for class matches:
  e.g. T and D (both stops) score higher than T and S (stop vs fricative)
- Make class weights configurable
- Evaluate: does this correctly identify slant rhymes without over-merging
  unrelated clusters?
- Test on a verse with known slant rhymes

**Why this matters:** rap frequently uses near-rhymes as intentional craft. Treating
them as non-rhymes produces false negatives. This is where the system starts to
reflect actual rhyme sophistication.

---

### [ ] Milestone 9 — MFA Limitation Evaluation

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

### [ ] Milestone 10 — Rhyme Complexity Scoring

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

### [ ] Milestone 11 — Structural Refactor for Modularity

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

---

### [ ] Milestone 12 — Phoneme-Stream Pipeline (separate repo)

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

## Long-term vision (post-Milestone 12)

- Web app with song URL input → rhyme scheme visualisation output
- Custom audio-to-phoneme model (to replace MFA for non-standard pronunciations)
- Multi-language support (requires language-specific acoustic models)
- Music analysis layer (tonality, tempo, beat alignment) — separate from lyrics engine
- Rhyme scheme comparison across artists / albums (stylometric analysis)
