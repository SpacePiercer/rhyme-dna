---
title: README
type: note
permalink: rhyme-dna/readme
---

# Verse DNA

Audio-aligned phoneme extraction and rhyme structure analysis engine for
performance-aware lyrical analysis. The long-term goal is a Genius-like web app where
any song can be analysed for its rhyme scheme, scored for complexity, and displayed
with rhyming words highlighted in matching colours.

## The core insight

Phonemes come from **the actual audio**, never from a pronunciation dictionary.
Performers bend pronunciation to make words rhyme that would not rhyme on paper —
a vowel can be shifted so that *again* and *insane* land on the same ending sound:

```
                 again      insane
Dictionary:      ...EH-N    ...EY-N     → different vowels, no rhyme
Performance:     ...iː-n    ...iː-n     → same vowel as sung, perfect rhyme
```

A dictionary lookup can never see this; forced alignment on the recording can.
That is why the pipeline runs MFA (Montreal Forced Aligner) on the audio and reads
the phonemes it heard, in IPA.

## What the output looks like

For the test verse

```
I found the sound of the underground
The crowd was loud and proud around the mound
A light at night ignites the kite in flight
The sight of white delight shines bright tonight
```

the engine detects and colour-codes the rhyme families — the *-ound* words
(found / sound / underground / around / mound), the *-oud* words
(crowd / loud / proud), and the *-ight* words (light / night / kite / flight / …) —
highlighting only the rhyming suffix of each word (e.g. under**ground**, m**ound**)
in an HTML rendering.

## Pipeline

```
audio + lyrics text
       ↓
MFA forced alignment  (english_mfa IPA model)
       ↓
TextGrid  (words tier + phones tier, with timecodes)
       ↓
phoneme extraction  →  rhyme candidates
       ↓
panphon feature-based similarity scoring  (assonance-first, vowel-weighted)
       ↓
average-linkage clustering  →  rhyme families
       ↓
colour-coded HTML output
```

All logic lives in `python/` as importable modules; `rhyme-DNA.ipynb` only calls them.

## Quick start

Requires the `mfa_env` conda environment (Python, MFA, panphon, jupyter).

```
# align audio + lyrics (produces input/input.TextGrid)
conda run -n mfa_env mfa align <corpus_dir> english_mfa english_mfa <output_dir>

# run the full pipeline headlessly
conda run -n mfa_env jupyter nbconvert --to notebook --execute rhyme-DNA.ipynb --output rhyme-DNA.ipynb --ExecutePreprocessor.timeout=120

# run the tests
conda run -n mfa_env python -m pytest python/tests -q
```

## Repository layout

| Path | Contents |
|---|---|
| `python/` | core pipeline modules (`similarity_engine`, `clustering`, `rhyme_extraction`, `html_generation`, …) + `tests/` + `probes/` |
| `rhyme-DNA.ipynb` | the notebook driving the pipeline (no logic in cells) |
| `docs/` | governance docs (see index below), plus `archive/` (legacy planning texts) and `research/` (local reading, untracked) |
| `progress/` | rolling per-day session log |
| `data/` | everything per-song: `input/` (lyrics + wav), `output/` (TextGrids), `m4a/`, `full_songs/`, `scored_pairs.jsonl`, and regenerable `generated_html/` (gitignored) |

## Documentation index

- `CLAUDE.md` — operational config for working sessions (startup, environment, git workflow)
- `CONSTITUTION.md` — the fixed conversation rules (Rules 1–13)
- `docs/DECISIONS.md` — the decision log: everything built so far and why (the past)
- `docs/ROADMAP.md` — the milestone plan (the future); first `[ ]` entry is next up
- `docs/GLOSSARY.md` — plain-language dictionary of every domain term + decision backlog
- `docs/LESSONS.md` — mistakes made and corrected
- `docs/MFA_FAILURES.md` — living catalogue of known alignment failures
