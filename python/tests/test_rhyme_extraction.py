"""Unit tests for rhyme candidate extraction.

Focus: lyric tokens must be normalised the same way MFA normalises words during
alignment, so punctuation-attached words (e.g. line-final "wait,") still match
the phoneme dictionary instead of being silently dropped.
"""
import pytest

from python.rhyme_extraction import _normalize_token, extract_rhyme_candidates


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
