"""TextGrid alignment summary — word/phone counts, duration, empty intervals.

Parses the MFA-produced TextGrid at data/output/current_output/input.TextGrid
and prints a compact summary: total audio duration, word and phone counts,
empty-interval (silence) counts, and the full word-to-IPA-phonemes mapping
so you can spot missing or garbled alignments without opening Praat or the
notebook.

Usage (from repo root, needs praatio from mfa_env):
    conda run -n mfa_env python scripts/readout/textgrid_summary.py
    conda run -n mfa_env python scripts/readout/textgrid_summary.py path/to/input.TextGrid

Prints "no TextGrid found at <path>" and exits 0 if the file is absent.
"""
import argparse
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

DEFAULT_TG = str(Path(__file__).resolve().parents[2]
                 / "data/output/current_output/input.TextGrid")


def summarise(tg_path: str) -> None:
    """Load and print a summary of the TextGrid at tg_path."""
    from praatio import textgrid  # mfa_env dependency

    path = Path(tg_path)
    if not path.exists():
        print(f"no TextGrid found at {path.resolve()}")
        return

    tg = textgrid.openTextgrid(str(path), includeEmptyIntervals=True)

    word_tier = tg.getTier("words")
    phone_tier = tg.getTier("phones")

    duration = tg.maxTimestamp - tg.minTimestamp

    # Split intervals into labelled and empty
    word_entries = word_tier.entries
    phone_entries = phone_tier.entries

    word_labelled = [e for e in word_entries if e.label.strip()]
    word_empty    = [e for e in word_entries if not e.label.strip()]
    phone_labelled = [e for e in phone_entries if e.label.strip()]
    phone_empty    = [e for e in phone_entries if not e.label.strip()]

    print(f"\nTextGrid: {path.resolve()}")
    print(f"Duration : {duration:.3f}s")
    print()
    print(f"Words tier  : {len(word_labelled):4d} labelled  |  {len(word_empty):3d} empty (silences)")
    print(f"Phones tier : {len(phone_labelled):4d} labelled  |  {len(phone_empty):3d} empty")
    print()

    # Build word → phonemes mapping (first occurrence of each word wins).
    # Mirrors the notebook Section 3 logic so the output matches what the
    # pipeline actually uses — useful for spotting 'WARNING: phonemes not found'
    # errors before running the notebook.
    w2p: dict[str, list[str]] = {}
    for w in word_tier.entries:
        if not w.label.strip():
            continue
        key = w.label.lower()
        if key in w2p:
            continue
        phones_in_word = [
            p.label for p in phone_tier.entries
            if p.label.strip()
            and w.start <= (p.start + p.end) / 2 <= w.end
        ]
        w2p[key] = phones_in_word

    print(f"Unique words aligned: {len(w2p)}")
    print()
    print(f"{'WORD':<20}  {'PHONEMES'}")
    print("-" * 60)
    for word, phones in sorted(w2p.items()):
        phones_str = " ".join(phones) if phones else "(no phones)"
        print(f"{word:<20}  {phones_str}")
    print()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "textgrid",
        nargs="?",
        default=DEFAULT_TG,
        help=f"path to the .TextGrid file (default: {DEFAULT_TG})",
    )
    args = parser.parse_args()
    summarise(args.textgrid)


if __name__ == "__main__":
    main()
