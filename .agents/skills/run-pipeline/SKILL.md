---
name: run-pipeline
description: Run the full Verse DNA verification gate — execute rhyme-DNA.ipynb
  end-to-end in mfa_env and run the pytest suite — then report pass/fail. Use when
  the user asks to run the pipeline, run or re-run the notebook, re-run rhyme
  analysis, verify the pipeline after a change (Rule 7), or run a pre-commit/pre-PR
  check.
---

# Run Pipeline

The "change complete" gate for Verse DNA. Verifies a change two ways:
Rule 7 (notebook runs end-to-end with sensible results) and Rule 6 (tests pass).
Run this before considering any change done or opening a PR.

## Quick start

From the repo root (`C:\Users\Georgii\GitHub\verse-dna`):

```
conda run -n mfa_env jupyter nbconvert --to notebook --execute rhyme-DNA.ipynb --output rhyme-DNA.ipynb --ExecutePreprocessor.timeout=120
conda run -n mfa_env pytest python/tests/
```

## Workflow

1. **Run the notebook** (command 1). On failure, open `rhyme-DNA.ipynb`, find the
   cell that raised, and report which cell and stage (alignment / phoneme
   extraction / rhyme detection) broke, with the traceback. Stop.
2. **Run the tests** (command 2, Rule 6). Treat BOTH real test failures AND
   "no tests collected" (pytest exit code 5 — the suite is missing/empty) as a
   FAILURE of the gate. The project requires tests to exist for every change, so
   an empty `python/tests/` is not a pass — report it and stop.
3. **Report the gate result.** Only call the change complete if BOTH the notebook
   executed cleanly with sensible outputs AND pytest collected and passed at least
   one test. Summarise the key notebook results (alignment counts, detected
   rhymes, similarity scores) so the user can sanity-check them.

## Notes

- Always use `mfa_env`; never call `mfa.exe` directly.
- `--output rhyme-DNA.ipynb` overwrites the notebook in place with the executed
  version, so results are readable straight from the file afterward.
- Raise `--ExecutePreprocessor.timeout` only if a legitimately long cell times out.
- There is no `python/tests/` suite yet; until one exists, this gate will fail at
  step 2 by design (Rule 6). Backs Rule 6 (tests with every change) and Rule 7
  (pipeline stays runnable).
