"""Integration tests for the syllable engine pipeline (Milestone 13).

Covers the chain extract_syllable_candidates -> compute_syllable_pairs ->
build_syllable_matrix -> cluster_rhymes, on real english_mfa phonemes from the
project verse. The headline behaviour M13 exists to deliver is a *cross-word*
syllable win: clip and gripped come from different words yet cluster together on
their shared -ip.
"""
from python.rhyme_extraction import extract_syllable_candidates
from python.similarity_engine import (
    compute_syllable_pairs,
    build_syllable_matrix,
    syllable_similarity,
)
from python.clustering import cluster_rhymes

# Real english_mfa alignments from the verse (see notebook Section 3).
PHON = {
    "clip": ["c", "ʎ", "i", "p"],
    "gripped": ["ɟ", "ɹ", "i", "p", "t"],
    "load": ["l", "əw", "d"],
    "both": ["b", "əw", "θ"],
    "dark": ["d", "a", "k"],
}


def _units(tmp_path, text):
    lyrics = tmp_path / "lyrics.txt"
    lyrics.write_text(text, encoding="utf-8")
    return extract_syllable_candidates(str(lyrics), PHON, detection_mode="full_line")


def test_matrix_is_symmetric_with_unit_diagonal(tmp_path):
    units = _units(tmp_path, "clip gripped\n")
    pairs = compute_syllable_pairs(units)
    matrix = build_syllable_matrix(units, pairs)

    ids = [u["unit_id"] for u in units]
    assert set(matrix.keys()) == set(ids)
    for i in ids:
        assert matrix[i][i] == 1.0
        for j in ids:
            assert matrix[i][j] == matrix[j][i]


def test_clip_gripped_cluster_across_words(tmp_path):
    # clip (c ʎ i p) and gripped (ɟ ɹ i p t) share -ip; onsets are ignored, so
    # they must land in the same cluster even though they are different words.
    units = _units(tmp_path, "clip gripped\n")
    pairs = compute_syllable_pairs(units)
    matrix = build_syllable_matrix(units, pairs)
    labels, _ = cluster_rhymes(matrix, threshold=0.7)

    clip_id = next(u["unit_id"] for u in units if u["source_word"] == "clip")
    grip_id = next(u["unit_id"] for u in units if u["source_word"] == "gripped")
    assert labels[clip_id] == labels[grip_id]


def test_unrelated_syllable_separates(tmp_path):
    # 'dark' (d a k) shares neither nucleus nor coda with the -ip syllables and
    # must NOT join their cluster.
    units = _units(tmp_path, "clip gripped dark\n")
    pairs = compute_syllable_pairs(units)
    matrix = build_syllable_matrix(units, pairs)
    labels, _ = cluster_rhymes(matrix, threshold=0.7)

    clip_id = next(u["unit_id"] for u in units if u["source_word"] == "clip")
    dark_id = next(u["unit_id"] for u in units if u["source_word"] == "dark")
    assert labels[clip_id] != labels[dark_id]


def test_scorer_kwargs_pass_through(tmp_path):
    # compute_syllable_pairs must forward scorer kwargs: with onset_weight=1 the
    # clip/gripped pair scores lower than with the default (onsets ignored).
    units = _units(tmp_path, "clip gripped\n")
    default_pairs = compute_syllable_pairs(units)
    onset_pairs = compute_syllable_pairs(units, onset_weight=1.0)

    assert default_pairs[0]["similarity"] > onset_pairs[0]["similarity"]
