"""Unit tests for passive pair logging (Milestone 19a).

Focus: the logger must (1) build stable schema records with the word pair stored
alphabetically and each word's rhyme unit attached, and (2) append idempotently —
writing the same batch twice must add its rows only once, so re-running an
unchanged verse produces no new lines.
"""
import json

from python.score_logging import (
    SCHEMA_VERSION,
    build_pair_records,
    record_key,
    append_scored_pairs,
    log_scored_pairs,
)

CONFIG = {"method": "D", "value": 0.75, "coda_discount": 0.3}

# wordA/wordB deliberately NOT alphabetical, to exercise the swap.
PAIRS = [
    {"wordA": "mound", "wordB": "crowd", "similarity": 0.812},
    {"wordA": "the", "wordB": "mound", "similarity": 0.438},
]

CANDIDATES = [
    {"end_word": "crowd", "rhyme_unit": ["aw", "d"]},
    {"end_word": "mound", "rhyme_unit": ["aw", "n", "d"]},
    {"end_word": "the", "rhyme_unit": ["a"]},
]


def _build():
    return build_pair_records(
        PAIRS, CANDIDATES,
        verse_id="eminem-load-the-clip",
        rhyme_mode="stressed", detection_mode="full_line",
        config=CONFIG, now="2026-06-07T20:00:00Z",
    )


# --- record building --------------------------------------------------------

def test_pair_stored_alphabetically_with_rhyme_units():
    rec = _build()[0]
    # "mound"/"crowd" -> sorted to crowd, mound
    assert rec["word_a"] == "crowd"
    assert rec["word_b"] == "mound"
    assert rec["rhyme_unit_a"] == ["aw", "d"]
    assert rec["rhyme_unit_b"] == ["aw", "n", "d"]


def test_score_and_config_captured():
    rec = _build()[0]
    assert rec["score"] == 0.812
    assert rec["method"] == "D"
    assert rec["value"] == 0.75
    assert rec["coda_discount"] == 0.3
    assert rec["rhyme_mode"] == "stressed"
    assert rec["detection_mode"] == "full_line"
    assert rec["verse_id"] == "eminem-load-the-clip"


def test_schema_version_and_reserved_label_slots():
    rec = _build()[0]
    assert rec["schema_version"] == SCHEMA_VERSION
    assert rec["label"] is None
    assert rec["label_source"] is None
    assert rec["first_logged_at"] == "2026-06-07T20:00:00Z"


def test_record_key_is_order_independent():
    # Same pair given in the opposite input order yields the same key.
    forward = build_pair_records(
        [{"wordA": "crowd", "wordB": "mound", "similarity": 0.812}], CANDIDATES,
        verse_id="v", rhyme_mode="stressed", detection_mode="full_line",
        config=CONFIG, now="t",
    )[0]
    backward = build_pair_records(
        [{"wordA": "mound", "wordB": "crowd", "similarity": 0.812}], CANDIDATES,
        verse_id="v", rhyme_mode="stressed", detection_mode="full_line",
        config=CONFIG, now="t",
    )[0]
    assert record_key(forward) == record_key(backward)


# --- idempotent appending ---------------------------------------------------

def test_append_is_idempotent(tmp_path):
    path = str(tmp_path / "data" / "scored_pairs.jsonl")
    records = _build()

    first = append_scored_pairs(records, path)
    second = append_scored_pairs(records, path)  # same batch again

    assert first == len(records)   # all written the first time
    assert second == 0             # nothing written the second time

    with open(path, encoding="utf-8") as f:
        lines = [l for l in f if l.strip()]
    assert len(lines) == len(records)


def test_append_creates_parent_dir_and_valid_jsonl(tmp_path):
    path = str(tmp_path / "nested" / "dir" / "pairs.jsonl")
    written = log_scored_pairs(
        PAIRS, CANDIDATES, path,
        verse_id="v", rhyme_mode="stressed", detection_mode="full_line",
        config=CONFIG, now="t",
    )
    assert written == len(PAIRS)
    with open(path, encoding="utf-8") as f:
        rows = [json.loads(l) for l in f if l.strip()]
    assert {r["word_a"] for r in rows} == {"crowd", "mound"}


def test_new_config_appends_again(tmp_path):
    """A changed scorer config is a new key, so its pairs append alongside the old."""
    path = str(tmp_path / "pairs.jsonl")
    append_scored_pairs(_build(), path)

    changed = build_pair_records(
        PAIRS, CANDIDATES,
        verse_id="eminem-load-the-clip",
        rhyme_mode="stressed", detection_mode="full_line",
        config={"method": "D", "value": 0.75, "coda_discount": 0.5},  # c changed
        now="2026-06-07T20:00:00Z",
    )
    written = append_scored_pairs(changed, path)
    assert written == len(PAIRS)
