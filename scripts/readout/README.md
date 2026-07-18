---
title: README
type: note
permalink: rhyme-dna/scripts/readout/readme-1
---

# scripts/readout

Permanent pipeline inspection scripts. Run these instead of writing throwaway
`_debug_*.py` or `_probe_*.py` scripts to read pipeline outputs.

The existing notebook readout script lives at `python/scripts/show_outputs.py`
(see Stage 5 in `.claude/skills/run-pipeline/SKILL.md`).

---

| Script | What it shows | How to run |
|---|---|---|
| `artifact_status.py` | Timestamps and sizes of every pipeline artifact in stage order; flags a stale TextGrid (older than wav or lyrics). Run at session start to see what needs re-running. | `python scripts/readout/artifact_status.py` |
| `textgrid_summary.py` | Total audio duration, word/phone counts, empty-interval (silence) counts, and the full word → IPA-phonemes mapping. Useful for spotting alignment gaps before running the notebook. | `conda run -n mfa_env python scripts/readout/textgrid_summary.py` |
| `scored_pairs_summary.py` | Verse IDs in the dataset, total pair count, score-distribution histogram, and top-scoring pairs with their rhyme units. Sanity-checks the Milestone 19a pair-logging output. | `python scripts/readout/scored_pairs_summary.py` |

All scripts print `"no <artifact> found at <path>"` and exit 0 when the
expected output file is absent.

Optional args: each script accepts a positional path override and `--help` for
full usage.