"""Boundary-free syllable splitter (Milestone 13).

Splits an IPA phoneme sequence (from english_mfa MFA alignment) into syllables
using the **Maximal Onset Principle** driven by **panphon's IPA-native sonority**.

The idea in plain terms: every vowel is the centre ("nucleus") of one syllable.
When a run of consonants sits between two vowels, we hand as many of them as
possible to the *following* syllable's start ("onset"), as long as they keep
*rising* in sonority toward that vowel; whatever is left clings to the previous
vowel as its ending ("coda"). Sonority is how "open/loud" a sound is — vowels are
most sonorous, then glides, liquids, nasals, fricatives, and stops at the bottom.

Two deliberate choices, both confirmed on real alignment data:
- **Nuclei are found with `_is_ipa_vowel`, not panphon sonority.** panphon scores
  the diphthong tokens (`aw`, `aj`, `oj`, `əw`) as sonority 1 (it reads only the
  glide half), which would hide them as nuclei. The vowel detector reads them as
  vowels via their leading `a`/`o`/`ə`, keeping each diphthong as ONE nucleus.
- **panphon sonority ranks only the consonants** inside an inter-vowel cluster,
  which is exactly what the maximal-onset split needs.

The sonority comparison is kept behind one knob (`ONSET_SONORITY_STRICT`) so the
M20 learned-weights milestone can tune how greedily onsets absorb consonants.
"""

from panphon.sonority import Sonority

from python.rhyme_extraction import _is_ipa_vowel
from python.similarity_engine import normalize_phoneme

# panphon's sonority scorer, instantiated once at import (loads feature tables).
_SON = Sonority()

# Maximal-onset knob (M20-tunable). When True, a consonant joins the onset only
# if it is *strictly* less sonorous than the consonant to its right (standard
# sonority sequencing). When False, equal sonority is also allowed to chain.
ONSET_SONORITY_STRICT = True


def _sonority(token):
    """Return panphon's sonority value for one consonant token (0 if unknown)."""
    try:
        return _SON.sonority(normalize_phoneme(token))
    except Exception:
        return 0


def _onset_split(run):
    """Split an inter-vowel consonant run into (coda_prev, onset_next).

    The onset is the maximal *rising-sonority* suffix of the run (the longest
    ending stretch whose sonority climbs toward the following vowel). The rest
    becomes the coda of the preceding syllable. The rightmost consonant always
    joins the onset — it sits directly before the vowel.
    """
    if not run:
        return [], []

    split = len(run) - 1  # rightmost consonant always starts the onset
    while split > 0:
        left, right = _sonority(run[split - 1]), _sonority(run[split])
        rising = left < right if ONSET_SONORITY_STRICT else left <= right
        if not rising:
            break
        split -= 1

    return run[:split], run[split:]


def syllabify(phonemes, debug=False):
    """Split an IPA phoneme list into syllables (maximal-onset, sonority-based).

    Parameters
    ----------
    phonemes : list of str
        IPA phoneme sequence for a word (from english_mfa MFA alignment).
    debug : bool
        If True, print the nuclei and the resulting syllables.

    Returns
    -------
    list of dict
        One dict per syllable, each with keys:
          onset    : list of str   (leading consonants, may be empty)
          nucleus  : str or None   (the vowel token; None only if the word has
                                    no vowel at all)
          coda     : list of str   (trailing consonants, may be empty)
          phonemes : list of str   (onset + [nucleus] + coda, in order)
    """
    phonemes = list(phonemes)
    nuclei = [i for i, p in enumerate(phonemes) if _is_ipa_vowel(p)]

    # Degenerate word with no vowel at all (rare; MFA edge cases): keep every
    # phoneme as one nucleus-less syllable rather than dropping it.
    if not nuclei:
        syllables = [{
            "onset": [],
            "nucleus": None,
            "coda": list(phonemes),
            "phonemes": list(phonemes),
        }]
        if debug:
            print("NO NUCLEUS:", phonemes)
        return syllables

    n = len(nuclei)

    # For each gap between consecutive nuclei, decide where the consonant run
    # splits: the left part is the previous syllable's coda, the right part is
    # the next syllable's onset.
    codas_before = {}   # syllable k -> its coda (from the gap after nucleus k)
    onsets_after = {}    # syllable k+1 -> its onset (from the gap before it)
    for k in range(n - 1):
        a, b = nuclei[k], nuclei[k + 1]
        run = phonemes[a + 1:b]
        coda_prev, onset_next = _onset_split(run)
        codas_before[k] = coda_prev
        onsets_after[k] = onset_next

    syllables = []
    for k, idx in enumerate(nuclei):
        if k == 0:
            onset = phonemes[:idx]            # leading consonants -> first onset
        else:
            onset = onsets_after[k - 1]

        if k == n - 1:
            coda = phonemes[idx + 1:]          # trailing consonants -> last coda
        else:
            coda = codas_before[k]

        nucleus = phonemes[idx]
        syllables.append({
            "onset": onset,
            "nucleus": nucleus,
            "coda": coda,
            "phonemes": onset + [nucleus] + coda,
        })

    if debug:
        print("PHONEMES:", phonemes)
        print("NUCLEI:", [phonemes[i] for i in nuclei])
        for s in syllables:
            print("  ", s["onset"], s["nucleus"], s["coda"])

    return syllables
