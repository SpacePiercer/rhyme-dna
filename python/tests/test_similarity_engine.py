"""Unit tests for the panphon-based similarity engine (Milestone 11).

Rhyme units are real IPA sequences as produced by english_mfa alignment on the
project verse:
    found/sound/mound  -> ["aw", "n", "d"]   (-ound)
    crowd/loud/proud   -> ["aw", "d"]        (-oud)
    light/night        -> ["aj", "t"]        (-ight)
    white/tonight      -> ["aj", "ʈ"]        (-ight with retroflex)
"""
import pytest

from python.similarity_engine import (
    rhyme_unit_similarity,
    rhyme_similarity,
    phoneme_similarity,
    SEG_COST,
    CODA_DISCOUNT,
)

OUND = ["aw", "n", "d"]
OUD = ["aw", "d"]
IGHT = ["aj", "t"]
IGHT_R = ["aj", "ʈ"]

# Short-i scheme units (real english_mfa alignment of the project verse):
IT = ["ɪ", "t"]      # "it"
TIP = ["t", "ɪ", "p"]  # "tip"  — same vowel, different coda
UP = ["ʌ", "p"]      # "up"  — wrong vowel, must stay out


# --- perfect rhymes ---------------------------------------------------------

def test_identical_units_score_one():
    assert rhyme_unit_similarity(OUND, OUND) == 1.0
    assert rhyme_unit_similarity(IGHT, IGHT) == 1.0


# --- insertion slant: the case that broke the naive metric ------------------

def test_insertion_slant_not_zero():
    """crowd/mound differ by one inserted 'n'; must read as a clear slant
    rhyme, not a non-rhyme (the bug that scored 0.000). Pinned to c=1.0 to
    assert the pre-M12 baseline."""
    score = rhyme_unit_similarity(OUD, OUND, coda_discount=1.0)   # D@0.75, no coda discount
    assert score == pytest.approx(0.8125, abs=1e-4)
    assert score > 0.7


# --- substitution slant: t vs retroflex ʈ -----------------------------------

def test_substitution_slant_high():
    score = rhyme_unit_similarity(IGHT, IGHT_R, coda_discount=1.0)
    assert score == pytest.approx(0.8333, abs=1e-3)
    assert score > 0.7


# --- non-rhyme should stay low and below any slant --------------------------

def test_non_rhyme_low():
    non = rhyme_unit_similarity(OUND, IGHT, coda_discount=1.0)
    assert non < 0.5
    # ordering: perfect > slant > non  (pinned to the c=1.0 baseline)
    assert (rhyme_unit_similarity(OUND, OUND, coda_discount=1.0)
            > rhyme_unit_similarity(OUD, OUND, coda_discount=1.0)
            > non)


# --- method C is stricter on insertions than D ------------------------------

def test_method_C_stricter_than_D_on_insertion():
    d = rhyme_unit_similarity(OUD, OUND, method="D", value=0.75, coda_discount=1.0)
    c = rhyme_unit_similarity(OUD, OUND, method="C", value=1.0, coda_discount=1.0)
    assert c == pytest.approx(0.75, abs=1e-4)
    assert c < d            # capped weighted cost penalises the missing sound more


def test_unknown_method_raises():
    with pytest.raises(ValueError):
        rhyme_unit_similarity(OUND, OUND, method="Z")


# --- empty units ------------------------------------------------------------

def test_empty_unit_scores_zero():
    assert rhyme_unit_similarity([], OUND) == 0.0
    assert rhyme_unit_similarity(OUND, []) == 0.0


# --- rhyme_similarity wrapper ignores mode, matches the core scorer ---------

def test_rhyme_similarity_wrapper_matches_core_and_ignores_mode():
    core = rhyme_unit_similarity(OUD, OUND)
    assert rhyme_similarity(OUD, OUND, mode="stressed") == core
    assert rhyme_similarity(OUD, OUND, mode="entire_word") == core


# --- phoneme_similarity (panphon feature-based) -----------------------------

def test_phoneme_similarity_identity_and_range():
    assert phoneme_similarity("t", "t") == 1.0
    # t vs retroflex ʈ differ in a single minor feature -> very close
    near = phoneme_similarity("t", "ʈ")
    assert 0.8 < near < 1.0
    # consonant vs vowel -> clearly dissimilar
    assert phoneme_similarity("t", "a") < near


def test_phoneme_similarity_stress_agnostic():
    # leading stress markers are stripped before comparison
    assert phoneme_similarity("ˈt", "t") == 1.0


def test_seg_cost_is_positive():
    assert SEG_COST > 0


# --- M12: coda-discount knob (assonance-first scoring) ----------------------

def test_default_coda_discount_is_assonance_setting():
    # The module ships with the swept value; default calls use it.
    assert CODA_DISCOUNT == 0.3
    assert rhyme_unit_similarity(IT, TIP) == rhyme_unit_similarity(IT, TIP, coda_discount=0.3)


def test_coda_discount_one_reproduces_m11_baseline():
    # c=1.0 must reproduce the pre-M12 score exactly.
    assert rhyme_unit_similarity(OUD, OUND, coda_discount=1.0) == pytest.approx(0.8125, abs=1e-4)


def test_coda_discount_raises_same_vowel_different_coda():
    # it vs tip share the ɪ vowel but differ in coda; discounting consonants
    # must raise the rhyme score relative to counting them fully.
    full = rhyme_unit_similarity(IT, TIP, coda_discount=1.0)
    disc = rhyme_unit_similarity(IT, TIP, coda_discount=0.3)
    assert disc > full


def test_coda_discount_keeps_wrong_vowel_out():
    # it vs up differ in the VOWEL; the discount must NOT pull them together.
    assert rhyme_unit_similarity(IT, UP, coda_discount=0.3) < 0.7


def test_vowel_cost_unchanged_by_discount():
    # Pure-vowel units have no consonants, so c cannot change the score at all.
    full = rhyme_unit_similarity(["ɪ"], ["ʌ"], coda_discount=1.0)
    zero = rhyme_unit_similarity(["ɪ"], ["ʌ"], coda_discount=0.0)
    assert full == zero
