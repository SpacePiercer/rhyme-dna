"""Unit tests for the boundary-free syllable splitter (Milestone 13).

The headline cases (`ultimate`, `explosive`) use the real english_mfa IPA
alignments recorded in the roadmap, so these assert the splitter against actual
pipeline data, not invented phonemes. The remaining cases cover the structural
guarantees: one syllable per vowel, diphthongs stay a single nucleus, word-edge
clusters go entirely to onset/coda, and the maximal-onset sonority split.
"""
import pytest

from python.syllabification import syllabify, _onset_split


def _shape(phonemes):
    """Return syllables as (onset, nucleus, coda) tuples for compact asserts."""
    return [
        (tuple(s["onset"]), s["nucleus"], tuple(s["coda"]))
        for s in syllabify(phonemes)
    ]


# --- headline cases: REAL english_mfa alignments (from the roadmap) ----------

def test_ultimate_real():
    phonemes = ["ɐ", "ɫ", "t", "ə", "mʲ", "ɪ", "t"]
    assert _shape(phonemes) == [
        ((), "ɐ", ("ɫ",)),          # ul  : no onset, coda ɫ
        (("t",), "ə", ()),          # ti  : onset t
        (("mʲ",), "ɪ", ("t",)),     # mate: onset mʲ, coda t
    ]


def test_explosive_real():
    # explosive -> ɛ k s p l o s i v  =>  ex · plo · sive
    phonemes = ["ɛ", "k", "s", "p", "l", "o", "s", "i", "v"]
    assert _shape(phonemes) == [
        ((), "ɛ", ("k", "s")),       # ex  : coda ks
        (("p", "l"), "o", ()),       # plo : onset pl
        (("s",), "i", ("v",)),       # sive: onset s, coda v
    ]


# --- structural guarantees ---------------------------------------------------

def test_one_syllable_per_vowel():
    # ultimate has 3 vowels -> 3 syllables; explosive likewise.
    assert len(syllabify(["ɐ", "ɫ", "t", "ə", "mʲ", "ɪ", "t"])) == 3
    assert len(syllabify(["ɛ", "k", "s", "p", "l", "o", "s", "i", "v"])) == 3


def test_monosyllable_clip():
    # clip -> k l ɪ p : single syllable, both onset consonants kept, coda p
    assert _shape(["k", "l", "ɪ", "p"]) == [(("k", "l"), "ɪ", ("p",))]


def test_diphthong_stays_one_nucleus():
    # The diphthong token 'aw' is ONE nucleus (panphon mis-scores it; the vowel
    # detector keeps it whole). load-like [l aw d] -> one syllable.
    syls = syllabify(["l", "aw", "d"])
    assert len(syls) == 1
    assert syls[0]["nucleus"] == "aw"
    assert syls[0]["onset"] == ["l"]
    assert syls[0]["coda"] == ["d"]


def test_word_initial_cluster_all_onset():
    # street -> s t ɹ i t : the leading cluster is entirely onset (word-initial),
    # regardless of internal sonority shape.
    assert _shape(["s", "t", "ɹ", "i", "t"]) == [(("s", "t", "ɹ"), "i", ("t",))]


def test_word_final_cluster_all_coda():
    # text-like coda [k s t] after the last vowel stays entirely in the coda.
    assert _shape(["t", "ɛ", "k", "s", "t"]) == [(("t",), "ɛ", ("k", "s", "t"))]


def test_adjacent_vowels_are_separate_syllables():
    # Two vowels in a row -> two nuclei; the second syllable has an empty onset.
    syls = syllabify(["b", "i", "ə"])
    assert len(syls) == 2
    assert syls[0]["nucleus"] == "i" and syls[0]["onset"] == ["b"]
    assert syls[1]["nucleus"] == "ə" and syls[1]["onset"] == []


def test_no_vowel_is_single_nucleusless_syllable():
    syls = syllabify(["s"])
    assert len(syls) == 1
    assert syls[0]["nucleus"] is None
    assert syls[0]["coda"] == ["s"]


def test_phonemes_field_reconstructs_each_syllable():
    for phonemes in (["ɐ", "ɫ", "t", "ə", "mʲ", "ɪ", "t"],
                     ["ɛ", "k", "s", "p", "l", "o", "s", "i", "v"]):
        rebuilt = []
        for s in syllabify(phonemes):
            assert s["phonemes"] == s["onset"] + [s["nucleus"]] + s["coda"]
            rebuilt.extend(s["phonemes"])
        assert rebuilt == phonemes  # whole word is preserved, in order


# --- the maximal-onset sonority split, in isolation --------------------------

def test_onset_split_rising_suffix():
    # k s p l : son 1,3,1,6 -> maximal rising suffix is [p, l]; coda [k, s].
    assert _onset_split(["k", "s", "p", "l"]) == (["k", "s"], ["p", "l"])


def test_onset_split_single_consonant_is_onset():
    assert _onset_split(["t"]) == ([], ["t"])


def test_onset_split_falling_keeps_only_last_in_onset():
    # ɫ t : son 6,1 -> falling, so only t is onset, ɫ is coda.
    assert _onset_split(["ɫ", "t"]) == (["ɫ"], ["t"])
