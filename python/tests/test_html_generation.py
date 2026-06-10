"""Tests for the render-time cluster quality filter (filter_clusters).

Milestone 11 change: the gate counts *deep* members (rhyme unit depth >=
min_phonemes) instead of blocking on the shallowest member. This keeps a bare
vowel like "I" (depth 1) in the cluster for rendering without suppressing an
otherwise-strong cluster.
"""
from python.html_generation import (
    filter_clusters,
    align_phonemes_to_chars,
    find_syllable_spans,
)
from python.syllabification import syllabify


def _cand(word, ru, line):
    return {"end_word": word, "rhyme_unit": ru, "line_index": line}


def _ranges(syllables):
    """Build [phoneme_start, phoneme_end) ranges from syllabify() output."""
    ranges, off = [], 0
    for s in syllables:
        ranges.append((off, off + len(s["phonemes"])))
        off += len(s["phonemes"])
    return ranges


# --- IPA-aware grapheme aligner (Milestone 13) ---

def test_align_boundaries_are_monotonic_and_cover_word():
    word, phon = "explosive", ["ɛ", "k", "s", "p", "l", "o", "s", "i", "v"]
    bounds = align_phonemes_to_chars(word, phon)
    assert len(bounds) == len(phon) + 1
    assert bounds[0] == 0
    assert bounds[-1] == len(word)
    assert all(bounds[i] <= bounds[i + 1] for i in range(len(bounds) - 1))


def test_single_syllable_spans_whole_word():
    word, phon = "clip", ["c", "ʎ", "i", "p"]
    spans = find_syllable_spans(word, phon, _ranges(syllabify(phon)))
    assert spans == [(0, len(word))]


def test_silent_final_e_attaches_to_last_syllable():
    # give = ɟ i v (3 sounds, 4 letters): the trailing silent "e" must be kept.
    word, phon = "give", ["ɟ", "i", "v"]
    spans = find_syllable_spans(word, phon, _ranges(syllabify(phon)))
    assert spans[-1][1] == len(word)
    assert word[spans[0][0]:spans[0][1]] == "give"


def test_multisyllable_spans_tile_word_without_gaps():
    # ultimate -> ul·ti·mate ; spans must be contiguous and cover the whole word.
    word, phon = "ultimate", ["ɐ", "ɫ", "t", "ə", "mʲ", "ɪ", "t"]
    syls = syllabify(phon)
    spans = find_syllable_spans(word, phon, _ranges(syls))
    assert len(spans) == len(syls)
    assert spans[0][0] == 0
    assert spans[-1][1] == len(word)
    for a, b in zip(spans, spans[1:]):
        assert a[1] == b[0]            # no gaps, no overlaps
    pieces = [word[a:b] for a, b in spans]
    assert "".join(pieces) == word
    assert pieces == ["ul", "ti", "mate"]


def test_two_syllable_split_is_sensible():
    word, phon = "poker", ["p", "oː", "k", "ə"]
    spans = find_syllable_spans(word, phon, _ranges(syllabify(phon)))
    assert [word[a:b] for a, b in spans] == ["po", "ker"]


def test_shallow_member_does_not_block_deep_cluster():
    # -ight family (deep, 3 members over 3 lines) + the bare vowel "I" (depth 1)
    cands = [
        _cand("light", ["aj", "t"], 0),
        _cand("night", ["aj", "t"], 1),
        _cand("flight", ["aj", "t"], 2),
        _cand("i", ["aj"], 0),            # shallow — must not block
    ]
    clusters = {"light": "A", "night": "A", "flight": "A", "i": "A"}
    assert "A" in filter_clusters(clusters, cands)


def test_all_shallow_cluster_blocked():
    cands = [_cand("the", ["a"], 0), _cand("a", ["a"], 1)]
    clusters = {"the": "A", "a": "A"}
    assert filter_clusters(clusters, cands) == set()


def test_singleton_deep_blocked():
    cands = [_cand("found", ["aw", "n", "d"], 0)]
    clusters = {"found": "A"}
    assert filter_clusters(clusters, cands) == set()


def test_two_deep_members_same_line_blocked():
    # 2 deep members but only one line -> no spread, fewer than 3 -> blocked
    cands = [_cand("found", ["aw", "n", "d"], 0), _cand("sound", ["aw", "n", "d"], 0)]
    clusters = {"found": "A", "sound": "A"}
    assert filter_clusters(clusters, cands) == set()


def test_two_deep_members_two_lines_pass():
    cands = [_cand("found", ["aw", "n", "d"], 0), _cand("mound", ["aw", "n", "d"], 1)]
    clusters = {"found": "A", "mound": "A"}
    assert filter_clusters(clusters, cands) == {"A"}
