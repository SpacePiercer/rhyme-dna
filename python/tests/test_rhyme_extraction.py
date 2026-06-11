"""Unit tests for rhyme candidate extraction.

Focus: lyric tokens must be normalised the same way MFA normalises words during
alignment, so punctuation-attached words (e.g. line-final "wait,") still match
the phoneme dictionary instead of being silently dropped.
"""
import pytest

from python.rhyme_extraction import (
    _normalize_token,
    extract_rhyme_candidates,
    extract_syllable_candidates,
)


# --- token normalisation ----------------------------------------------------

@pytest.mark.parametrize("raw, expected", [
    ("with,", "with"),      # trailing comma
    ("for?", "for"),        # trailing question mark
    ("up,", "up"),          # trailing comma
    ("(yeah)", "yeah"),     # wrapping parentheses
    ("'cause", "cause"),    # leading apostrophe (MFA drops it)
    ("Hello", "hello"),     # lowercasing
    ("wait,", "wait"),      # the line-final rhyme word that was being dropped
])
def test_strips_surrounding_punctuation(raw, expected):
    assert _normalize_token(raw) == expected


def test_preserves_word_internal_apostrophe():
    """Internal apostrophes are part of the word and must survive."""
    assert _normalize_token("i'm") == "i'm"
    assert _normalize_token("don't") == "don't"


def test_punctuation_only_token_becomes_empty():
    assert _normalize_token("--") == ""
    assert _normalize_token("...") == ""


# --- end-to-end through extract_rhyme_candidates ----------------------------

def test_line_final_punctuated_word_is_found(tmp_path):
    """A line ending in 'wait,' must resolve to the clean 'wait' and produce a
    candidate, not a 'phonemes not found' skip."""
    lyrics = tmp_path / "lyrics.txt"
    lyrics.write_text("hold up, wait,\n", encoding="utf-8")

    word_to_phonemes = {"wait": ["w", "aj", "t"], "up": ["a", "p"], "hold": ["h", "o", "l", "d"]}

    candidates = extract_rhyme_candidates(
        str(lyrics), word_to_phonemes, rhyme_mode="stressed", detection_mode="end_only"
    )

    assert len(candidates) == 1
    assert candidates[0]["end_word"] == "wait"
    assert candidates[0]["is_line_end"] is True


def test_internal_apostrophe_word_resolves(tmp_path):
    lyrics = tmp_path / "lyrics.txt"
    lyrics.write_text("i'm here\n", encoding="utf-8")

    word_to_phonemes = {"i'm": ["aj", "m"], "here": ["h", "i", "ɹ"]}

    candidates = extract_rhyme_candidates(
        str(lyrics), word_to_phonemes, rhyme_mode="stressed", detection_mode="full_line"
    )

    found_words = {c["end_word"] for c in candidates}
    assert "i'm" in found_words


# --- syllable units (Milestone 13) ------------------------------------------

# Real english_mfa alignments (from the roadmap).
_SYL_PHON = {
    "explosive": ["ɛ", "k", "s", "p", "l", "o", "s", "i", "v"],  # ex·plo·sive
    "clip": ["k", "l", "ɪ", "p"],                                  # one syllable
}


def test_syllable_candidates_emit_one_unit_per_syllable(tmp_path):
    lyrics = tmp_path / "lyrics.txt"
    lyrics.write_text("explosive clip\n", encoding="utf-8")

    units = extract_syllable_candidates(
        str(lyrics), _SYL_PHON, detection_mode="full_line"
    )

    # explosive (3 syllables) + clip (1) = 4 units
    assert len(units) == 4
    by_word = {}
    for u in units:
        by_word.setdefault(u["source_word"], []).append(u)
    assert len(by_word["explosive"]) == 3
    assert len(by_word["clip"]) == 1

    nuclei = [u["nucleus"] for u in by_word["explosive"]]
    assert nuclei == ["ɛ", "o", "i"]


def test_syllable_unit_ids_are_unique(tmp_path):
    lyrics = tmp_path / "lyrics.txt"
    lyrics.write_text("explosive clip\nclip explosive\n", encoding="utf-8")

    units = extract_syllable_candidates(str(lyrics), _SYL_PHON)
    ids = [u["unit_id"] for u in units]
    assert len(ids) == len(set(ids))


def test_syllable_phoneme_ranges_tile_the_word(tmp_path):
    lyrics = tmp_path / "lyrics.txt"
    lyrics.write_text("explosive\n", encoding="utf-8")

    units = extract_syllable_candidates(str(lyrics), _SYL_PHON)

    # The syllables' [start, end) ranges must tile the word's phonemes exactly,
    # in order, with no gaps or overlaps — this is what lets the render layer
    # map each syllable back to a character span.
    units = sorted(units, key=lambda u: u["syllable_index"])
    offset = 0
    rebuilt = []
    for u in units:
        assert u["phoneme_start"] == offset
        assert u["word_phonemes"][u["phoneme_start"]:u["phoneme_end"]] == u["phonemes"]
        offset = u["phoneme_end"]
        rebuilt.extend(u["phonemes"])
    assert rebuilt == _SYL_PHON["explosive"]


def test_syllable_end_only_uses_last_word(tmp_path):
    lyrics = tmp_path / "lyrics.txt"
    lyrics.write_text("clip explosive\n", encoding="utf-8")

    units = extract_syllable_candidates(
        str(lyrics), _SYL_PHON, detection_mode="end_only"
    )

    # Only the line-final word 'explosive' contributes (3 syllables).
    assert {u["source_word"] for u in units} == {"explosive"}
    assert len(units) == 3
    assert all(u["is_line_end"] for u in units)
