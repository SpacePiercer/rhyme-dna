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
    filter_syllable_clusters,
    generate_syllable_html,
)
from python.syllabification import syllabify
from python.rhyme_extraction import extract_syllable_candidates


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


# --- per-syllable cluster filter + rendering (Milestone 13) ---

def _syl(unit_id, line, depth):
    return {
        "unit_id": unit_id,
        "line_index": line,
        "phonemes": ["x"] * depth,
    }


def test_filter_passes_cross_line_pair():
    units = [_syl("0:0:0", 0, 3), _syl("1:0:0", 1, 3)]
    labels = {"0:0:0": "A", "1:0:0": "A"}
    assert filter_syllable_clusters(labels, units) == {"A"}


def test_filter_blocks_singleton_and_same_line_pair():
    # singleton
    assert filter_syllable_clusters({"0:0:0": "A"}, [_syl("0:0:0", 0, 3)]) == set()
    # two deep but one line -> no spread, fewer than 3 -> blocked
    units = [_syl("0:0:0", 0, 3), _syl("0:1:0", 0, 3)]
    labels = {"0:0:0": "A", "0:1:0": "A"}
    assert filter_syllable_clusters(labels, units) == set()


def test_bare_vowel_syllable_does_not_count_as_deep():
    # one deep + one shallow (depth 1) on different lines -> only 1 deep -> blocked
    units = [_syl("0:0:0", 0, 3), _syl("1:0:0", 1, 1)]
    labels = {"0:0:0": "A", "1:0:0": "A"}
    assert filter_syllable_clusters(labels, units) == set()


def test_multisyllable_word_wears_two_colours(tmp_path):
    # explosive -> ex·plo·sive ; put "plo" in cluster P (with load) and "sive" in
    # cluster S (with tip), each spanning two lines so both clusters pass. The
    # rendered "explosive" must therefore carry BOTH colour classes.
    phon = {
        "explosive": ["ɛ", "k", "s", "p", "l", "o", "s", "i", "v"],
        "load": ["l", "əw", "d"],
        "tip": ["ʈ", "ɪ", "p"],
    }
    lyrics = tmp_path / "lyrics.txt"
    lyrics.write_text("explosive\nload\ntip\n", encoding="utf-8")
    units = extract_syllable_candidates(str(lyrics), phon, detection_mode="full_line")

    labels = {}
    for u in units:
        if u["source_word"] == "load":
            labels[u["unit_id"]] = "P"
        elif u["source_word"] == "tip":
            labels[u["unit_id"]] = "S"
        elif u["source_word"] == "explosive" and u["syllable_index"] == 1:
            labels[u["unit_id"]] = "P"      # "plo"
        elif u["source_word"] == "explosive" and u["syllable_index"] == 2:
            labels[u["unit_id"]] = "S"      # "sive"

    out = tmp_path / "syl.html"
    html = generate_syllable_html(units, labels, output_file=str(out))

    explosive_line = html.split("<body>")[1].split("<br>")[0]
    assert 'class="syl-P"' in explosive_line
    assert 'class="syl-S"' in explosive_line
    # the unlabelled onset "ex" stays outside any coloured span
    assert explosive_line.strip().startswith("ex")


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
