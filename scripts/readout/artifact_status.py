"""Pipeline artifact status — timestamps, sizes, and freshness check.

Shows the modification time and size of every file the pipeline touches, in
stage order (audio convert → alignment → notebook → scored pairs → HTML).
Run this at the start of a session to see which stages need re-running and
whether the TextGrid is stale relative to the audio / lyrics.

Usage (from repo root):
    python scripts/readout/artifact_status.py
    python scripts/readout/artifact_status.py --root path/to/repo

No mfa_env dependencies — runs with the base Python interpreter.
"""
import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

# Pipeline artifacts in stage order.
# Each entry: (label, path-relative-to-repo-root, stage-number)
_ARTIFACTS = [
    # Stage 1 — audio convert
    ("audio (input)",  "data/input/current_input/input.m4a",  1),
    ("wav",            "data/input/current_input/input.wav",   1),
    # Stage 2 — MFA alignment
    ("lyrics (txt)",   "data/input/current_input/input.txt",   2),
    ("TextGrid",       "data/output/current_output/input.TextGrid", 2),
    ("align CSV",      "data/output/current_output/alignment_analysis.csv", 2),
    # Stage 3 — notebook
    ("notebook",       "rhyme-DNA.ipynb",                      3),
    # Stage 5 — scored pairs logging
    ("scored pairs",   "data/scored_pairs.jsonl",              5),
    # Stage 7 — HTML (word-based)
    ("rhyme HTML",     "data/generated_html/rhyme_visualization.html", 7),
    # Stage 8 — HTML (syllable-based)
    ("syllable HTML",  "data/generated_html/syllable_visualization.html", 8),
]

# Freshness rule: TextGrid must be NEWER than both wav and lyrics.
_FRESHNESS_CHECKS = [
    ("TextGrid", "wav",          "TextGrid older than wav — alignment is STALE"),
    ("TextGrid", "lyrics (txt)", "TextGrid older than lyrics — alignment is STALE"),
]


def _fmt_mtime(path: Path) -> str:
    """Return a human-readable local modification time string."""
    ts = path.stat().st_mtime
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def _fmt_size(path: Path) -> str:
    """Return a compact human-readable file size."""
    n = path.stat().st_size
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=str(Path(__file__).resolve().parents[2]),
        help="repo root directory (default: the repo containing this script)",
    )
    args = parser.parse_args()
    root = Path(args.root).resolve()

    # Collect mtime for freshness checks (label -> mtime float or None)
    mtimes: dict[str, float | None] = {}

    col_w = max(len(label) for label, _, _ in _ARTIFACTS)
    print(f"\n{'ARTIFACT':<{col_w}}  {'MTIME':<19}  {'SIZE':>8}  STATUS")
    print("-" * (col_w + 45))

    for label, rel, _stage in _ARTIFACTS:
        path = root / rel
        if not path.exists():
            print(f"{label:<{col_w}}  {'—':<19}  {'—':>8}  NOT FOUND")
            mtimes[label] = None
        else:
            mtime = path.stat().st_mtime
            mtimes[label] = mtime
            print(f"{label:<{col_w}}  {_fmt_mtime(path):<19}  {_fmt_size(path):>8}")

    # Freshness checks
    print()
    warnings = []
    for newer_label, older_label, msg in _FRESHNESS_CHECKS:
        t_newer = mtimes.get(newer_label)
        t_older = mtimes.get(older_label)
        if t_newer is not None and t_older is not None:
            if t_newer < t_older:
                warnings.append(f"  WARNING: {msg}")

    if warnings:
        print("FRESHNESS:")
        for w in warnings:
            print(w)
    else:
        present = [
            label for label, rel, _ in _ARTIFACTS
            if (root / rel).exists()
            and label in ("TextGrid", "wav", "lyrics (txt)")
        ]
        if len(present) == 3:
            print("FRESHNESS: TextGrid is up to date (newer than wav and lyrics)")
        else:
            print("FRESHNESS: (some artifacts missing — cannot check)")
    print()


if __name__ == "__main__":
    main()
