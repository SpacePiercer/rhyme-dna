import string

from python.similarity_engine import _is_ipa_vowel, normalize_phoneme
from python.syllabification import syllabify

# Punctuation stripped from the ENDS of a lyric token before looking it up in
# the phoneme dictionary. MFA normalises words the same way during alignment
# (e.g. "with," -> "with", "'cause" -> "cause"), so the lyric side must match.
# Word-internal apostrophes are preserved because strip() only removes from the
# ends, so "i'm" stays "i'm" while "'cause" becomes "cause".
_EDGE_PUNCTUATION = string.punctuation


def _normalize_token(word):
    """Lowercase a lyric token and strip surrounding punctuation.

    Returns the cleaned token, or "" if the token was punctuation-only.
    Mirrors MFA's word normalisation so lyric words match the TextGrid keys.
    """
    return word.lower().strip(_EDGE_PUNCTUATION)


def extract_rhyme_unit(phonemes, mode="stressed", debug=False):
    """
    Extract the rhyme unit from a phoneme sequence.

    Parameters
    ----------
    phonemes : list of str
        IPA phoneme sequence for a word (from english_mfa MFA alignment).
    mode : str
        One of "stressed", "stressed_plus", or "entire_word".
    debug : bool
        If True, print intermediate values.

    Returns
    -------
    list of str
        The rhyme unit phoneme sequence.
    """

    # Find the rightmost vowel phoneme — IPA carries no stress-digit markers,
    # so the rightmost vowel is used as the start of the rhyme unit.
    stressed_index = None

    for i in range(len(phonemes) - 1, -1, -1):
        if _is_ipa_vowel(phonemes[i]):
            stressed_index = i
            break

    if stressed_index is None:
        stressed_index = 0

    if mode == "stressed":
        rhyme_unit = phonemes[stressed_index:]

    elif mode == "stressed_plus":
        pre_index = stressed_index - 1
        start_index = 0

        while pre_index >= 0:
            if _is_ipa_vowel(phonemes[pre_index]):
                start_index = pre_index
                break
            pre_index -= 1

        rhyme_unit = phonemes[start_index:]

    elif mode == "entire_word":
        rhyme_unit = phonemes[:]

    else:
        raise ValueError(f"Unknown rhyme mode: {mode}")

    if debug:
        print("MODE:", mode)
        print("PHONEMES:", phonemes)
        print("STRESS INDEX:", stressed_index)
        print("RHYME UNIT:", rhyme_unit)

    return rhyme_unit


def extract_rhyme_candidates(
    lyrics_path,
    word_to_phonemes,
    rhyme_mode="stressed",
    detection_mode="end_only"
):
    """
    Extract rhyme candidates from a lyrics file.

    Parameters
    ----------
    lyrics_path : str
        Path to the plain-text lyrics file.
    word_to_phonemes : dict
        Mapping of word (str) → phoneme list (list of str), built from MFA TextGrid.
    rhyme_mode : str
        One of "stressed", "stressed_plus", "entire_word".
    detection_mode : str
        "end_only"  — only the last word of each line.
        "full_line" — every word in every line.

    Returns
    -------
    list of dict
        Each dict has keys: line_index, line_text, word_index, end_word,
        phonemes, rhyme_unit, is_line_end.
    """

    result = []

    with open(lyrics_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line_index, line in enumerate(lines):

        line = line.strip()

        if not line:
            continue

        # Strip surrounding punctuation so tokens match MFA's clean word keys.
        words = [_normalize_token(w) for w in line.split()]

        if detection_mode == "end_only":
            candidates = [(len(words) - 1, words[-1])]

        elif detection_mode == "full_line":
            candidates = list(enumerate(words))

        else:
            raise ValueError(f"Unknown detection_mode: {detection_mode}")

        for word_index, word in candidates:

            if not word:
                continue

            if word not in word_to_phonemes:
                print(f"WARNING: phonemes not found for '{word}' (line {line_index})")
                continue

            phonemes = word_to_phonemes[word]

            if len(phonemes) == 0:
                continue

            rhyme_unit = extract_rhyme_unit(phonemes, mode=rhyme_mode)

            if len(rhyme_unit) == 0:
                continue

            is_line_end = (word_index == len(words) - 1)

            result.append({
                "line_index": line_index,
                "line_text": line,
                "word_index": word_index,
                "end_word": word,
                "phonemes": phonemes,
                "rhyme_unit": rhyme_unit,
                "is_line_end": is_line_end
            })

    return result


def extract_syllable_candidates(
    lyrics_path,
    word_to_phonemes,
    detection_mode="full_line"
):
    """Extract one candidate unit per SYLLABLE (Milestone 13).

    This is the syllable-engine replacement for extract_rhyme_candidates: the
    atomic unit the pipeline scores and clusters is no longer the word and its
    single tail rhyme unit, but each syllable of each word — so a long word
    participates in a scheme through any of its syllables and syllables cluster
    freely across word and line boundaries.

    Each syllable unit carries a back-pointer to its source word (the word
    string, its full phoneme list, and the syllable's phoneme range within that
    word) so the render layer can colour the exact character span later.

    Parameters
    ----------
    lyrics_path : str
        Path to the plain-text lyrics file.
    word_to_phonemes : dict
        Mapping of word (str) → phoneme list (list of str), from the MFA TextGrid.
    detection_mode : str
        "full_line" — every word in every line (default; M13 is boundary-free).
        "end_only"  — only the last word of each line.

    Returns
    -------
    list of dict
        One dict per syllable, with keys:
          unit_id        — unique id "<line>:<word_index>:<syllable_index>"
          line_index, line_text, word_index
          source_word    — the word this syllable came from
          is_line_end    — True if the source word is last in its line
          syllable_index — 0-based position of this syllable within the word
          n_syllables    — number of syllables the source word has
          onset, nucleus, coda — the syllable's parts (lists / str / None)
          phonemes       — the syllable's phoneme list (the comparison unit)
          word_phonemes  — the source word's full phoneme list
          phoneme_start, phoneme_end — the syllable's [start, end) phoneme range
                            within word_phonemes (for the char-span aligner)
    """
    result = []

    with open(lyrics_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line_index, line in enumerate(lines):

        line = line.strip()

        if not line:
            continue

        words = [_normalize_token(w) for w in line.split()]

        if detection_mode == "end_only":
            candidates = [(len(words) - 1, words[-1])]
        elif detection_mode == "full_line":
            candidates = list(enumerate(words))
        else:
            raise ValueError(f"Unknown detection_mode: {detection_mode}")

        for word_index, word in candidates:

            if not word:
                continue

            if word not in word_to_phonemes:
                print(f"WARNING: phonemes not found for '{word}' (line {line_index})")
                continue

            phonemes = word_to_phonemes[word]

            if len(phonemes) == 0:
                continue

            syllables = syllabify(phonemes)
            is_line_end = (word_index == len(words) - 1)

            phoneme_offset = 0
            for syllable_index, syl in enumerate(syllables):
                syl_len = len(syl["phonemes"])

                result.append({
                    "unit_id": f"{line_index}:{word_index}:{syllable_index}",
                    "line_index": line_index,
                    "line_text": line,
                    "word_index": word_index,
                    "source_word": word,
                    "is_line_end": is_line_end,
                    "syllable_index": syllable_index,
                    "n_syllables": len(syllables),
                    "onset": syl["onset"],
                    "nucleus": syl["nucleus"],
                    "coda": syl["coda"],
                    "phonemes": syl["phonemes"],
                    "word_phonemes": phonemes,
                    "phoneme_start": phoneme_offset,
                    "phoneme_end": phoneme_offset + syl_len,
                })

                phoneme_offset += syl_len

    return result


def extract_end_words(lyrics_path, word_to_phonemes, rhyme_mode="stressed"):
    """
    Legacy wrapper. Calls extract_rhyme_candidates with detection_mode='end_only'.
    Existing notebook cells that call extract_end_words() continue to work unchanged.
    """
    return extract_rhyme_candidates(
        lyrics_path,
        word_to_phonemes,
        rhyme_mode=rhyme_mode,
        detection_mode="end_only"
    )