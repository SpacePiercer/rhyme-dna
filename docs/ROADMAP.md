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

One line per milestone. The full history — what was built, the key decisions and why,
before/after examples — lives in `DECISIONS.md` (milestone sections of the same name);
this list is only the index.

- [x] **M3 — Deterministic Rhyme Extraction Engine** — first end-to-end chain:
  stressed-mode rhyme units, end-of-line word detection, greedy threshold clustering,
  colour-coded HTML output.

- [x] **M4 — Controlled Testing Framework** — sound/underground test verse,
  expected-cluster annotation and accuracy evaluation, debug mode.
- [x] **M5 — Similarity Refinement Layer** — similarity upgraded from boolean to a
  continuous 0.0–1.0 scale; similarity matrix built internally.
- [x] **M6 — Multi-Syllable Expansion** — `RHYME_MODE` config
  (`stressed` / `stressed_plus` / `entire_word`) with mode-aware thresholds.
- [x] **Intra-milestone fixes (M6→M7)** — `min_len` denominator, `stressed` routed
  through tail similarity, real `stressed_plus` extraction, `get_threshold()` wiring.

- [x] **M7 — Internal Rhymes** — `DETECTION_MODE` (`end_only` / `full_line`),
  `extract_rhyme_candidates()` with no word-level filter, line-grouped HTML rendering.

- [x] **M8 — Intelligent Rhyme Rendering** — suffix-only highlighting
  (`find_rhyme_suffix_span()`) and the render-time cluster quality gate
  (`filter_clusters()`).
- [x] **M9 — Slant & Phoneme-Class Similarity** — hand-coded phoneme class table giving
  near-rhymes partial credit (superseded by panphon in M11).

- [x] **M10 — Switch MFA to IPA** — alignment moved to the `english_mfa` IPA model;
  phoneme normalisation and rhyme-unit extraction rewritten for IPA.
- [x] **M11 — Replace Similarity Engine with panphon** — weighted feature edit distance
  scorer (method D@0.75), hand-coded class table deleted, deep-member render gate,
  threshold kept at 0.7 (Option B).
- [x] **M12 — Assonance-First (Vowel-Weighted) Similarity** — coda-discount `c = 0.3`
  (vowels drive the score), average-linkage clustering (single-linkage chained),
  `python/probes/` diagnostics folder.
- [x] **M13 — Syllable Engine (boundary-free, syllable-as-unit)** — maximal-onset
  syllabifier on panphon sonority, role-aware syllable scorer (onset 0 / nucleus 1.0 /
  coda 0.3) with effective-length normalisation, free cross-word clustering at
  threshold 0.65, IPA-aware per-syllable colour spans as the new primary view.

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
> The phoneme-stream pipeline once planned as a separate repo (old M18 numbering) is
> likewise subsumed here: it is this milestone's detection method, not a parallel project.
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
