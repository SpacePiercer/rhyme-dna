---
title: ROADMAP
type: note
permalink: rhyme-dna/roadmap
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
- `[-]` Deferred / dropped — kept for reference; not on the active path (numbers stay
  stable so existing cross-references don't break)

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
  "ow-ending" family; diphthong-as-one and bare-vowel handling deferred (M17 / M13)
- Tests: `python/tests/` (16 passing); notebook re-run end-to-end, both families render

**Decision detail:** see `DECISIONS.md` → "Milestone 11 — Replace Similarity Engine with panphon".

### [x] Milestone 12 — Assonance-First (Vowel-Weighted) Similarity

**What was done:**
- Added the **coda-discount setting** `c` (default 0.3) to `rhyme_unit_similarity`:
  consonant costs (insert/delete a consonant, or substitute one consonant for another)
  are multiplied by `c`; vowel costs and vowel↔consonant substitutions stay full cost.
  `c = 1.0` reproduces pre-M12 behaviour; kept a swappable parameter for M20.
- `cluster_rhymes` switched to **average-linkage** (a word joins only if its mean
  similarity to all current members clears the threshold).
- New `python/probes/` diagnostics folder (`probe_clusters.py`, incl. an experimental
  windowed/drift linkage kept for M17).
- Tests: coda-discount + average-linkage merge/chaining-rejection (42 passing);
  notebook re-run end-to-end.

**Result (short-i verse, `c = 0.3`):** the scheme merges into one 17-word family
(11/11 of *with/clip/hip/gripped/width/tip/slit/it/chips/fit/ultimate*), plus 6 more
words that genuinely share the short-i vowel (*explosive, give, in, is, still, think*) —
correct matches, not noise. Refining them is later work: M14 (stress) down-weights ones
whose vowel is unstressed; M13/M17 surface the multi-word compound schemes some belong
to. Single-linkage was tried first but chained the whole verse into one 79-word blob, so
average-linkage was adopted.

**Decision detail:** see `DECISIONS.md` → "Milestone 12 — Assonance-First (Vowel-Weighted) Similarity".

---

## Upcoming

> **Reorder + scope override (2026-06-08, grill session; renumbered 2026-06-09).** The
> syllable engine and the stress milestone were swapped in order, and the syllable engine
> was re-scoped. **M13 (now the boundary-free syllable engine)** is the **next** milestone;
> **M14 (stress)** becomes a **per-syllable weight layered on top of M13** and follows it.
> This supersedes the 2026-06-07 "word-boundary-respecting" scoping of the syllable engine
> and consciously **revives the boundary-free rewrite that was deferred to M17** — decision
> made with full knowledge of the cost (the word-based engine and the word-level rhyme unit
> are retired). The milestones were then **renumbered so the numbers follow work order**
> (M13 = syllables, M14 = stress); earlier dated notes below that say "M14 = syllables /
> M13 = stress" are pre-renumber snapshots and are kept as history.

### [ ] Milestone 13 — Syllable Engine (boundary-free, syllable-as-unit)

**Goal:** make the **syllable** the atomic unit the pipeline clusters and colours,
replacing the word-level single-tail rhyme unit. Syllables cluster **freely across word
and line boundaries**, so a long word participates in a scheme through *any* of its
syllables and cross-word compound rhymes start to surface.

**What this retires:** `extract_rhyme_unit` (word tail), the word-level `rhyme_unit`,
and the word-as-scored-unit assumption running through `compute_similarity_pairs` /
`build_similarity_matrix` / clustering / HTML / evaluation. (The tail-walk
`longest_common_tail_similarity` was already retired in M11.) `extract_rhyme_candidates`
is reworked to emit syllable units, each keeping a back-pointer to its source word +
character span (needed for colouring).

Subgoals / agreed design (grill 2026-06-08):
- **Syllabifier** — a maximal-onset splitter built on **panphon's IPA-native sonority**
  (no new dependency; syllabipy was tested and rejected — it returns `[]` on IPA input).
  Each vowel is a nucleus; a consonant cluster between two vowels gives its
  rising-sonority tail to the *next* syllable's onset, the rest become the coda.
  Diphthongs (`aj`, `aw`) stay one nucleus via the existing vowel detector (panphon's
  sonority mis-scores the diphthong token). The sonority threshold becomes an
  M20-tunable knob.
- **Comparison unit = the full syllable**, scored through the existing panphon weighted
  feature-edit-distance scorer, now made **role-aware** with a small family of knobs
  (all swap-ready for M20):
  - onset weight `o = 0` (new — onsets ignored for now; tunable later)
  - nucleus / vowel = full weight
  - coda discount `c = 0.3` (M12, unchanged)
  - Effect: *clip* / *grip* = 1.0 (onsets dropped) while the coda still contributes a
    graded amount.
- **Free cross-word clustering** — syllable units cluster regardless of which word or
  line they came from.
- **Clustering rule** — average-linkage (chaining risk is *higher* with short syllable
  units, so it is even more justified than in M12), threshold carried at **0.7** but
  **re-swept** on the verse and reported.
- **Rendering** — per-syllable independent colours: a multi-syllable word can wear
  several colours, one per syllable's cluster (the literal "Verse DNA" texture). Extend
  the grapheme aligner from suffix-only to per-syllable character spans (also groundwork
  for M15).

**What is left for M17 (still deferred / optional):** stitching matched syllables into
*contiguous multi-syllable run* objects — recognising *load-the-clip* ↔ *both-are-gripped*
as **one** rhyme rather than three coincidental syllable matches. The cross-word
syllable *matches* themselves are now M13's job; M17's orphaned items (the `ignites`
false-negative and the windowed/drift linkage) move under that reduced M17.

**Before/after (real data, current verse):**
```
"explosive"  (english_mfa: ɛ k s p l o s i v)
- Now (tail-only):  one unit "-ɪv"  → sits weakly in the short-i family, one colour
- After M13:        ex · plo · sive
                    plo  → "o" family (load / both …)   [colour 1]
                    sive → short-i family (clip / tip)  [colour 2; stress later fades it]
```

**Validation (definition of done — targeted behavioural checks):** splitter unit tests
(`ultimate → ul·ti·mate`, `explosive → ex·plo·sive`); asserted cross-word wins
(`clip ~ gripped`, `load·oʊ ~ both·oʊ`); the short-i monosyllable family preserved;
`o = 0` verified; notebook runs clean end-to-end (Rule 7) on the *load the clip* verse.
Build in independently-runnable slices: (1) splitter + tests, (2) syllable extraction
replacing `extract_rhyme_unit`, (3) role-aware scorer with `o`, (4) clustering +
per-syllable HTML. A formal accuracy metric is deferred.

**Depends on:** Milestone 12 (assonance scorer), Milestone 11 (panphon). Feeds the
reduced Milestone 17 (run stitching).

---

### [ ] Milestone 14 — Stress as a Per-Syllable Prominence Weight (after M13)

> **Premise correction (2026-06-08).** The original "stop discarding MFA's stress marks"
> subgoal is **void**: `english_mfa` emits **no stress marks at all** — confirmed in both
> the aligned TextGrid phones tier *and* the dictionary itself (`explosive → ɛ k s p l o
> s i v`, `guitar → ɡ ɐ tʰ ɑ`, `ultimate → ɐ ɫ t ə mʲ ɪ t`). `normalize_phoneme`
> stripping `ˈ`/`ˌ` is a no-op on real data. Stress must therefore be **estimated
> acoustically** and is applied as a weight on M13's syllable units — so it runs **after**
> M13.

**Goal:** weight each syllable by how *prominent* (stressed) it was, so the prominent
syllable carries the rhyme and unstressed syllables are down-weighted — bringing the
score closer to what the ear hears as the backbone of a line.

Subgoals (revised):
- Estimate per-syllable prominence from acoustic cues. **Duration** (vowel length, read
  from the TextGrid) is the only **beat-robust** cue and works on the current mixed
  input. **Loudness** and **pitch** are corrupted by the instrumental — confirmed: the
  silent gaps between words measured as loud as the vowels (a −10.4 dB gap vs
  *explosive*'s −12 to −15 dB vowels) — so they require a **clean vocal**, gated behind a
  future acapella / source-separation input step.
- Apply prominence as a per-syllable weight in the M13 scorer: up-weight the prominent
  syllable, down-weight the unstressed (e.g. demote *explosive*'s "-ive" match to the
  short-i family — see the M13 before/after). Swap-ready for the M20 learned weights.
- **Open question to revisit, not assume:** M16 (colour intensity) and M20 (learned
  weights) may *partially substitute* for an explicit stress signal. Re-judge whether
  acoustic stress is worth its noise once M13/M16 exist.

**Why this matters:** the stressed syllable is the anchor of a rhyme; weighting it makes
the engine agree with the ear on which syllable "carries" the rhyme — without it, M13's
richer syllable comparison surfaces more incidental unstressed-syllable matches.

**Depends on:** Milestone 13.

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

### [-] Milestone 17 — Global Phoneme-Stream Rhyme Detection (DEFERRED / OPTIONAL)

> **Status (2026-06-08): reduced, still deferred / optional.** *Supersedes the
> 2026-06-07 status below.* The M13 override (boundary-free syllable engine) absorbed
> M17's cross-word *matching* capability — syllable units now cluster freely across word
> boundaries in M13, so compound rhymes like *load the clip* / *both are gripped* surface
> there as parallel syllable matches. What remains uniquely M17's is **run stitching**:
> recognising those parallel matches as **one contiguous multi-syllable rhyme object**
> rather than several coincidental syllable matches. The word-based engine and the
> word-level rhyme unit **are** being retired (in M13), so the earlier "keep the
> word-based engine" framing no longer holds. The two orphaned items — the `ignites`
> false-negative and the windowed/drift linkage — now live under this reduced M17.
>
> **Original status (2026-06-07), kept for history:** *M14 delivers whole-word rhyme
> within word boundaries; M17's only irreplaceable capability is cross-word compound
> rhymes; the word-based engine is kept and the tail-walk is not retired.* — This was
> overridden on 2026-06-08; see above.
>
> The rest of this section is kept verbatim as a design reference for if/when M17 is revived.

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

**Concrete multi-word targets (found in M12, current verse):** two compound schemes
(multi-word, multi-syllable rhymes the word-based engine cannot represent — it only
catches the last word of each phrase). Vowels are the **objective IPA** from the actual
`english_mfa` alignment; the parenthesised shorthand is the by-ear label.

- **Scheme A** (by ear "o i i") — back/rounded → reduced → close-front anchor, ≈ `/oʊ ə i/`:
  - ex[plosive with] `ɛ o i ɪ` · [load the clip] `əw a i` · [pistols on hip] `ɪ ə a i` ·
    [both are gripped] `əw a i` · sup[posed to fit] `ə oː ə i`
- **Scheme B** (by ear "ay uh o er") — front-mid → reduced → back-rounded → reduced,
  ≈ `/eɪ ə oʊ ə/`:
  - [days are over] `e a əw ə` · [save at Kroger] `e a ɒ ə` · [Trader Joe for] `(trader
    unaligned) əw a` · [change in sofas] `(change unaligned) ɪ …`
  - *change in sofas* is "less similar but still similar" — drift along the scheme.
- The unaligned words (*change*, *trader*, partially *sofas*) are catalogued in
  `MFA_FAILURES.md`: they have no usable phonemes, so the detector cannot see them at all.

**Depends on:** Milestone 11 (panphon similarity as the core comparison function).

---

### [-] Milestone 18 — MFA Limitation Evaluation (DROPPED — now a living catalogue)

> **Status (2026-06-07): dropped as a milestone.** This was evaluation-only, and we are
> already running real adlib verses and spotting MFA failures as they happen. Rather than
> a one-off milestone, MFA failures are now collected in a **living catalogue**:
> `MFA_FAILURES.md`. It grows whenever a failure is hit, and — for free — it is fed by the
> M19 screenshot-label workflow: any verse where a human rhyme-breakdown video disagrees
> with our pipeline output is exactly an MFA/scorer failure to log there.
>
> Holds the current verse's unaligned/mis-aligned words; rows are dropped and replaced as
> the pipeline's verse changes.

---

### [ ] Milestone 19 — Rhyme-Judgment Dataset & Score Logging

**Goal:** start building the labelled data the weight-learning milestone (M20) will need,
and make the pipeline log every pair it scores — so a training set accumulates passively
while other work continues. Split into two parts so logging starts immediately and
labelling happens incrementally, not in one batch at the end.

#### 19a — Passive logging (start NOW, ahead of the milestone)

- Add lightweight logging: every scored pair (`word A`, `word B`, rhyme units, raw
  score, method, config) appended to a versioned dataset file (`.jsonl`)
- Define the dataset schema once, stable and versioned, so future training reads it
  directly
- This runs from now on as the pipeline executes — no labels yet, just the raw scored
  pairs accumulating.

#### 19b — Incremental human labelling (ongoing, not one batch)

- **Do not label all pairs at the end.** Most pairs are obvious non-rhymes
  (`the / mound = 0.0`) and need no human label. Label only the **interesting slice**:
  borderline scores near the threshold, and cases where the engine disagrees with the
  ear. Label **per-milestone-cycle**, not in one final pass.
- M20's loss is *ranking/contrastive* (perfect > slant > non), so we mostly need
  *orderings* and a handful of anchored examples — not a number on every pair.
- **Screenshot ingestion (expert labels, for free):** rhyme-breakdown videos (e.g.
  colour-coded Eminem verses) hand us expert **cluster memberships** on real rap audio.
  Workflow: the user sends a screenshot → it is read out and recorded as labelled cluster
  memberships for a verse we have **already aligned** → any disagreement with our pipeline
  output drops into `MFA_FAILURES.md` (this is the old M18 evaluation, generated
  automatically).
  - Record the **source video** per label (slant grouping is subjective; provenance lets
    us weight/dedupe).
  - A screenshot is only usable for a verse we have run through MFA (the labels need
    feature vectors to attach to).
  - These memberships are the same "do two words share a label?" signal as the
    pulled-forward pairwise-identity evaluation (see "Dissolved milestones" below).

**Why this matters:** there is no target to learn from today. Collecting judgments is
the real unlock and the slowest part — starting logging now means data is ready when the
fitting milestone (M20) arrives.

**Depends on:** Milestone 11 (panphon scorer producing scores to log). 19a starts now.

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

### [-] Milestone 22 — Structural Refactor for Modularity (DROPPED — dissolved)

> **Status (2026-06-07): dropped as a milestone.** The code is already split by concern
> (`similarity_engine.py`, `clustering.py`, `rhyme_extraction.py`, `html_generation.py`,
> `evaluation.py`), and the existing CLAUDE.md rule — *"all logic lives in `python/` as
> importable modules; the notebook only calls them"* — already provides the modularity
> guarantee a refactor milestone would have added. Blast-radius protection comes from the
> tests (Rule 6), not from folder names. So no big-bang refactor and **no new modularity
> rule.** Its three pieces are split out:
>
> - **Pairwise cluster-identity evaluation → pulled forward** (near-term task). Replace the
>   fragile cluster-letter comparison with "do two words share a label?". This has been a
>   known testing pain since M7, it makes M13/M14 easier to validate, and it is the *same*
>   membership signal as the M19b screenshot labels — so it earns its keep immediately.
> - **Folder grouping + CLI entry point → small pre-M23 task.** Group the existing modules
>   into `alignment/ · rhyme_engine/ · scoring/ · visualisation/`, add a thin
>   `python -m versedna analyse …` entry point, and per-module READMEs — done just before
>   M23 when the structure has stopped moving (premature folder structure is churn).
> - **"No logic in notebook cells" → already a rule**, kept as-is.

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
