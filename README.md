---
title: README
type: note
permalink: rhyme-dna/readme
---

# Rhyme DNA

Audio-aligned phoneme extraction and rhyme-structure analysis for rap and song
lyrics. It reads the sounds a performer actually made rather than dictionary
spellings, then finds, scores and colour-codes the rhyme families in a verse.

## The idea

Performers bend pronunciation to make words rhyme that would not rhyme on paper.
A vowel can be shifted so that *again* and *insane* land on the same ending sound:

```
                 again      insane
Dictionary:      ...EH-N    ...EY-N     → different vowels, no rhyme
Performance:     ...iː-n    ...iː-n     → same vowel as sung, perfect rhyme
```

A dictionary lookup can never see this, but forced alignment on the recording can.
So the pipeline runs the Montreal Forced Aligner (MFA) on the audio and works from
the IPA phonemes it actually heard.

For the test verse

```
I found the sound of the underground
The crowd was loud and proud around the mound
A light at night ignites the kite in flight
The sight of white delight shines bright tonight
```

the engine detects the *-ound*, *-oud* and *-ight* families and highlights only
the rhyming part of each word (under**ground**, m**ound**) in an HTML rendering.

## Pipeline

```
audio + lyrics text
       ↓
MFA forced alignment  (english_mfa IPA model)
       ↓
TextGrid  (words tier + phones tier, with timecodes)
       ↓
syllabification (maximal onset)  →  rhyme candidates
       ↓
panphon feature-based similarity  (assonance-first, vowel-weighted)
       ↓
average-linkage clustering  →  rhyme families
       ↓
colour-coded HTML output
```

## Current state

Working research pipeline, driven from a notebook and covered by unit tests.

- **Done:** deterministic rhyme extraction; a controlled test verse; multi-syllable
  and internal rhymes; suffix-only highlighting; switch from ARPAbet to IPA alignment;
  similarity engine replaced with panphon weighted feature distance; assonance-first
  (vowel-weighted) scoring; syllable engine that treats the syllable as the rhyme unit;
  passive logging of every scored pair to build a judgment dataset.
- **Next:** use stress as a per-syllable prominence weight, add a phoneme-class
  letter colouring ("DNA view"), and scale colour intensity by similarity.
- **Limits:** English only; MFA struggles with slang, ad-libs and heavily bent
  pronunciations; no UI beyond generated HTML; you supply your own audio and lyrics
  (none are included, for copyright reasons).

## Ideal state

- A Genius-style web app: paste a song (or upload audio + lyrics) and get its rhyme
  scheme visualised, with rhyming syllables highlighted in matching colours.
- A rhyme **complexity score** per verse, so artists, albums and eras can be compared.
- Similarity weights **learned from human rhyme judgments** instead of hand-tuned.
- A custom audio-to-phoneme model to replace MFA for non-standard pronunciation.
- Multi-language support, plus an optional music layer (beat, tempo) aligned with the lyrics.

## Quick start

Requires a conda environment with Python, MFA, panphon and Jupyter (named `mfa_env` below).

```
# 1. put your audio (input.wav) + lyrics (input.txt) in data/input/current_input/
# 2. align them (produces a TextGrid)
conda run -n mfa_env mfa align <corpus_dir> english_mfa english_mfa <output_dir>

# 3. run the full pipeline headlessly
conda run -n mfa_env jupyter nbconvert --to notebook --execute rhyme-DNA.ipynb --output rhyme-DNA.ipynb

# run the tests
conda run -n mfa_env python -m pytest python/tests -q
```

## Repository layout

| Path | Contents |
|---|---|
| `python/` | pipeline modules (`syllabification`, `similarity_engine`, `rhyme_extraction`, `clustering`, `html_generation`, `score_logging`, …) |
| `python/tests/` | unit tests |
| `python/probes/` | diagnostic scripts that print cluster membership and pairwise scores |
| `scripts/readout/` | inspection scripts for pipeline artifacts (TextGrid, scored pairs) |
| `rhyme-DNA.ipynb` | the notebook that drives the pipeline (no logic in cells) |

## Tech

Python · Montreal Forced Aligner · panphon · Jupyter · pytest