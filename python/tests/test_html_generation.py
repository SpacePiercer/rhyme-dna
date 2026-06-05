"""Tests for the render-time cluster quality filter (filter_clusters).

Milestone 11 change: the gate counts *deep* members (rhyme unit depth >=
min_phonemes) instead of blocking on the shallowest member. This keeps a bare
vowel like "I" (depth 1) in the cluster for rendering without suppressing an
otherwise-strong cluster.
"""
from python.html_generation import filter_clusters


def _cand(word, ru, line):
    return {"end_word": word, "rhyme_unit": ru, "line_index": line}


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
