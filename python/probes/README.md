# python/probes

Exploratory **diagnostic scripts** — not unit tests.

These scripts run the real pipeline on the currently loaded verse and print
human-readable diagnostics (cluster membership, pairwise rhyme scores, method
comparisons) so we can *see* how a scoring or clustering change behaves before
committing to it. Unit tests (the `python/tests/` folder) assert fixed expected
values; probes are for open-ended inspection and tuning.

Run any probe from the **repo root** as a module, e.g.:

```
conda run -n mfa_env python -m python.probes.probe_clusters
```

| Script | What it shows |
|---|---|
| `probe_clusters.py` | The short-i scheme's cluster at different coda-discount values and clustering methods (incl. the experimental windowed/drift linkage kept for M17). |
