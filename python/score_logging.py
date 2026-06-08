"""Passive logging of every scored rhyme pair (Milestone 19a).

The pipeline scores every candidate word pair in Section 5. This module turns
those scores into a stable, versioned training-data file so a dataset for the
M20 learned-weights milestone accumulates on its own while other work continues.

Design (agreed in M19a):
- One JSON object per scored pair, appended to a `.jsonl` file.
- The scorer (`similarity_engine`) is never touched — this module only reads its
  output, keeping the scorer pure.
- Logging is **idempotent**: each record is keyed on
  `(verse_id, sorted word pair, scorer config, rhyme_mode)`. A pair whose key is
  already in the file is skipped. The score is deterministic given that key, so
  nothing is lost, and re-running an unchanged verse appends zero rows — which
  keeps the file a clean, committable asset with no diff churn.
- `label` / `label_source` are reserved (always None here) and filled later by
  Milestone 19b (human / screenshot rhyme judgments), so the schema is stable.
"""

import json
import os
from datetime import datetime, timezone

SCHEMA_VERSION = 1


def scorer_config():
    """Read the active scorer configuration from `similarity_engine`.

    Returns a dict with the method ("D"/"C"), its resolved numeric value
    (penalty for "D", cap for "C"), and the coda discount. Centralising this
    keeps the notebook cell free of logic (it just calls the logger).
    """
    from python import similarity_engine as se
    method = se.SIMILARITY_METHOD
    value = se.SIMILARITY_PENALTY if method == "D" else se.SIMILARITY_CAP
    return {"method": method, "value": value, "coda_discount": se.CODA_DISCOUNT}


def _utc_now_iso():
    """Current UTC time as an ISO-8601 string with a trailing Z (no microseconds)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rhyme_unit_map(rhyme_candidates):
    """Map each candidate word (lowercased) to its rhyme unit (first occurrence wins)."""
    mapping = {}
    for cand in rhyme_candidates:
        word = cand["end_word"].lower()
        if word not in mapping:
            mapping[word] = cand["rhyme_unit"]
    return mapping


def record_key(record):
    """Identity of a scored pair: verse, sorted word pair, scorer config, rhyme mode.

    The word pair is already stored alphabetically (see build_pair_records), so
    (a, b) and (b, a) collapse to one key. Used for idempotent de-duplication.
    """
    return (
        record["verse_id"],
        record["word_a"],
        record["word_b"],
        record["method"],
        record["value"],
        record["coda_discount"],
        record["rhyme_mode"],
    )


def build_pair_records(similarity_pairs, rhyme_candidates, *, verse_id,
                       rhyme_mode, detection_mode, config=None,
                       schema_version=SCHEMA_VERSION, now=None):
    """Turn scored pairs into schema records ready to append.

    Parameters
    ----------
    similarity_pairs : list of dict
        Output of `compute_similarity_pairs` — dicts with wordA/wordB/similarity.
    rhyme_candidates : list of dict
        The extraction output, used to look up each word's rhyme unit.
    verse_id : str
        Identifier of the aligned verse (e.g. "eminem-load-the-clip").
    rhyme_mode, detection_mode : str
        The active pipeline modes, recorded for reproducibility.
    config : dict or None
        Scorer config (method/value/coda_discount); defaults to scorer_config().
    now : str or None
        Timestamp to stamp on new records; defaults to the current UTC time.
        Passed explicitly by tests for determinism.
    """
    cfg = config if config is not None else scorer_config()
    ru = _rhyme_unit_map(rhyme_candidates)
    stamp = now if now is not None else _utc_now_iso()

    records = []
    for pair in similarity_pairs:
        wa, wb = pair["wordA"].lower(), pair["wordB"].lower()
        # Store the pair alphabetically so (a, b) and (b, a) are one record.
        if wb < wa:
            wa, wb = wb, wa
        records.append({
            "schema_version": schema_version,
            "verse_id": verse_id,
            "word_a": wa,
            "word_b": wb,
            "rhyme_unit_a": ru.get(wa),
            "rhyme_unit_b": ru.get(wb),
            "score": pair["similarity"],
            "method": cfg["method"],
            "value": cfg["value"],
            "coda_discount": cfg["coda_discount"],
            "rhyme_mode": rhyme_mode,
            "detection_mode": detection_mode,
            "first_logged_at": stamp,
            "label": None,
            "label_source": None,
        })
    return records


def _existing_keys(path):
    """Read all record keys already present in the .jsonl file (empty set if none)."""
    keys = set()
    if not os.path.exists(path):
        return keys
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            keys.add(record_key(json.loads(line)))
    return keys


def append_scored_pairs(records, path):
    """Append records to `path` (.jsonl), skipping any whose key already exists.

    Idempotent: writing the same batch twice adds its rows only once. Returns the
    number of records actually written. Creates the parent directory if needed.
    """
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    seen = _existing_keys(path)
    written = 0
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        for rec in records:
            key = record_key(rec)
            if key in seen:
                continue
            seen.add(key)
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            written += 1
    return written


def log_scored_pairs(similarity_pairs, rhyme_candidates, path, *, verse_id,
                     rhyme_mode, detection_mode, config=None, now=None):
    """Build records from scored pairs and append them idempotently.

    Convenience wrapper so the notebook cell is a single call. Returns the number
    of new records written.
    """
    records = build_pair_records(
        similarity_pairs, rhyme_candidates,
        verse_id=verse_id, rhyme_mode=rhyme_mode,
        detection_mode=detection_mode, config=config, now=now,
    )
    return append_scored_pairs(records, path)
