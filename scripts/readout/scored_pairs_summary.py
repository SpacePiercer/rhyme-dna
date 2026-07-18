"""Scored-pairs dataset summary — verse IDs, counts, score distribution, top pairs.

Reads data/scored_pairs.jsonl (the Milestone 19a passive-logging dataset) and
prints a compact overview: which verse IDs are present, total pair count, score
distribution histogram, and the highest-scoring pairs so you can sanity-check
that the pipeline wrote sensible rhymes.

Usage (from repo root — stdlib only, no mfa_env needed):
    python scripts/readout/scored_pairs_summary.py
    python scripts/readout/scored_pairs_summary.py path/to/scored_pairs.jsonl
    python scripts/readout/scored_pairs_summary.py --verse eminem-load-the-clip --top 20

Prints "no scored pairs found at <path>" and exits 0 if the file is absent.
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

DEFAULT_PATH = str(Path(__file__).resolve().parents[2]
                   / "data/scored_pairs.jsonl")


def load_records(path: Path) -> list[dict]:
    """Read all JSONL records from path. Returns empty list if file absent."""
    if not path.exists():
        return []
    records = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def histogram(scores: list[float], n_buckets: int = 10) -> str:
    """Return a compact ASCII histogram of scores in [0, 1]."""
    bucket_size = 1.0 / n_buckets
    counts = [0] * n_buckets
    for s in scores:
        idx = min(int(s / bucket_size), n_buckets - 1)
        counts[idx] += 1
    max_count = max(counts) if counts else 1
    bar_width = 30
    lines = []
    for i, count in enumerate(counts):
        lo = i * bucket_size
        hi = lo + bucket_size
        bar = "#" * round(count * bar_width / max_count)
        lines.append(f"  {lo:.1f}-{hi:.1f}: {count:5d}  {bar}")
    return "\n".join(lines)


def summarise(path: Path, verse_filter: str | None, top_n: int) -> None:
    """Load and print a summary of the scored pairs at path."""
    records = load_records(path)

    if not records:
        print(f"no scored pairs found at {path.resolve()}")
        return

    # Filter by verse if requested
    if verse_filter:
        records = [r for r in records if r.get("verse_id") == verse_filter]
        if not records:
            print(f"no records for verse_id='{verse_filter}' in {path.resolve()}")
            return

    scores = [r["score"] for r in records]
    verse_counts = Counter(r.get("verse_id", "?") for r in records)

    print(f"\nDataset: {path.resolve()}")
    print(f"Total records : {len(records)}")
    print()

    print("Verse IDs:")
    for verse_id, count in sorted(verse_counts.items()):
        print(f"  {verse_id:<40}  {count:>6} pairs")
    print()

    print(f"Scores — min={min(scores):.3f}  max={max(scores):.3f}  "
          f"mean={sum(scores)/len(scores):.3f}")
    print("Distribution:")
    print(histogram(scores))
    print()

    # Top-scoring pairs
    top = sorted(records, key=lambda r: r["score"], reverse=True)[:top_n]
    col = max(len(r["word_a"]) for r in top)
    print(f"Top {top_n} pairs by score:")
    print(f"  {'WORD A':<{col}}  {'WORD B':<{col}}  {'SCORE':>6}  RHYME UNITS")
    print("  " + "-" * (col * 2 + 30))
    for r in top:
        ru_a = " ".join(r.get("rhyme_unit_a") or [])
        ru_b = " ".join(r.get("rhyme_unit_b") or [])
        print(f"  {r['word_a']:<{col}}  {r['word_b']:<{col}}  {r['score']:>6.3f}  "
              f"[{ru_a}] vs [{ru_b}]")
    print()

    # Labelled pairs (for evaluation readiness)
    labelled = [r for r in records if r.get("label") is not None]
    print(f"Labelled pairs (for M19b): {len(labelled)} / {len(records)}")
    print()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        nargs="?",
        default=DEFAULT_PATH,
        help=f"path to the .jsonl file (default: {DEFAULT_PATH})",
    )
    parser.add_argument(
        "--verse",
        metavar="VERSE_ID",
        default=None,
        help="filter to a single verse_id (default: show all)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=15,
        help="number of top-scoring pairs to display (default: 15)",
    )
    args = parser.parse_args()
    summarise(Path(args.path), args.verse, args.top)


if __name__ == "__main__":
    main()
