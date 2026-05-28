from python.similarity_engine import normalize_phoneme

# IPA vowel characters found in english_mfa output.
# Used to locate the stressed vowel in extract_rhyme_unit().
_IPA_VOWELS = {
    'a', 'e', 'i', 'o', 'u',   # ASCII base vowels (covers diphthongs aj, aw, oj)
    'ɑ', 'ɒ', 'ɐ',              # open back / near-open central
    'æ',                        # near-open front
    'ɛ', 'ɜ',                   # open-mid front / central
    'ɪ',                        # near-close near-front
    'ɔ',                        # open-mid back
    'ʊ',                        # near-close near-back
    'ʌ',                        # open-mid back unrounded
    'ə',                        # schwa
}


def _is_ipa_vowel(phoneme):
    """Return True if any character in this IPA phoneme is a vowel."""
    return any(c in _IPA_VOWELS for c in normalize_phoneme(phoneme))


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

        words = line.lower().split()

        if detection_mode == "end_only":
            candidates = [(len(words) - 1, words[-1])]

        elif detection_mode == "full_line":
            candidates = list(enumerate(words))

        else:
            raise ValueError(f"Unknown detection_mode: {detection_mode}")

        for word_index, word in candidates:

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