"""Print the text outputs of an executed Jupyter notebook, cell by cell.

A small dev convenience for reviewing pipeline results after a notebook run,
without scrolling the raw .ipynb JSON or writing a throwaway script each time.

Usage (from repo root, inside mfa_env):
    conda run -n mfa_env python python/scripts/show_outputs.py
    conda run -n mfa_env python python/scripts/show_outputs.py rhyme-DNA.ipynb --max 3000
"""
import argparse
import json
import sys

# IPA phonemes (ʈ, ð, ɹ, …) are non-ASCII; force the console to UTF-8 so printing
# them doesn't crash under Windows' default cp1252 codepage.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


def show_outputs(notebook_path, max_chars):
    """Print each code cell's text output, truncated to max_chars."""
    with open(notebook_path, encoding="utf-8") as fh:
        nb = json.load(fh)

    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] != "code":
            continue
        for out in cell.get("outputs", []):
            text = ""
            if out.get("output_type") == "stream":
                text = "".join(out.get("text", []))
            elif "data" in out and "text/plain" in out["data"]:
                text = "".join(out["data"]["text/plain"])
            if text.strip():
                print(f"--- cell {i} ---")
                print(text[:max_chars])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebook", nargs="?", default="rhyme-DNA.ipynb",
                        help="path to the .ipynb file (default: rhyme-DNA.ipynb)")
    parser.add_argument("--max", type=int, default=1800,
                        help="max characters printed per output (default: 1800)")
    args = parser.parse_args()
    show_outputs(args.notebook, args.max)


if __name__ == "__main__":
    main()
