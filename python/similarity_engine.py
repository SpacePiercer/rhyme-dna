import itertools

def normalize_phoneme(p):
    """Strip stress markers from an IPA phoneme symbol.

    MFA's english_us_ipa model prefixes stressed vowels with ˈ (primary)
    or ˌ (secondary). These are stripped so comparisons are stress-agnostic.
    """
    return p.lstrip("ˈˌ")


# ---------------------------------------------------------------------------
# Phoneme class table and slant-rhyme similarity
# ---------------------------------------------------------------------------

# ARPAbet phonemes grouped into perceptually close classes.
# Phonemes within the same class receive partial credit; across classes = 0.
#
# Vowel classes are grouped by the primary acoustic dimension (height / backness).
# Consonant classes are grouped by manner of articulation.
# Voiced / unvoiced pairs sit in the same class so "t/d", "p/b", "k/g" rhyme partially.

PHONEME_CLASSES = {
    # --- Front vowels ---
    "IY": "vowel_front_high",   # b EE t
    "IH": "vowel_front_high",   # b I t
    "EY": "vowel_front_mid",    # b A ke
    "EH": "vowel_front_mid",    # b E d
    "AE": "vowel_front_low",    # b A t

    # --- Central / reduced vowels ---
    "AH": "vowel_central",      # b U t  /  schwa
    "ER": "vowel_central",      # b IR d

    # --- Back vowels ---
    "AO": "vowel_back_mid",     # b AW l
    "AA": "vowel_back_low",     # f A ther
    "OW": "vowel_back_mid",     # b OA t
    "UH": "vowel_back_high",    # b OO k
    "UW": "vowel_back_high",    # b OO t

    # --- Diphthongs ---
    "AW": "vowel_diphthong_aw", # c OW
    "AY": "vowel_diphthong_ay", # k ITE
    "OY": "vowel_diphthong_oy", # b OY

    # --- Stops (voiced/unvoiced pairs in same class) ---
    "P":  "stop_bilabial",
    "B":  "stop_bilabial",
    "T":  "stop_alveolar",
    "D":  "stop_alveolar",
    "K":  "stop_velar",
    "G":  "stop_velar",

    # --- Fricatives ---
    "F":  "fricative_labiodental",
    "V":  "fricative_labiodental",
    "TH": "fricative_dental",
    "DH": "fricative_dental",
    "S":  "fricative_alveolar",
    "Z":  "fricative_alveolar",
    "SH": "fricative_postalveolar",
    "ZH": "fricative_postalveolar",
    "HH": "fricative_glottal",

    # --- Affricates ---
    "CH": "affricate",
    "JH": "affricate",

    # --- Nasals ---
    "M":  "nasal",
    "N":  "nasal",
    "NG": "nasal",

    # --- Liquids ---
    "L":  "liquid",
    "R":  "liquid",

    # --- Glides ---
    "W":  "glide",
    "Y":  "glide",
}

# Within-superclass partial credit.
# Two vowel classes in the same broad group score 0.4 (they share height or backness).
# Exact same class scores 1.0 (handled in phoneme_similarity directly).
# Cross-superclass scores 0.0 (handled by absence from this table).

_SUPERCLASS = {
    "vowel_front_high":       "vowel_front",
    "vowel_front_mid":        "vowel_front",
    "vowel_front_low":        "vowel_front",
    "vowel_central":          "vowel_central",
    "vowel_back_high":        "vowel_back",
    "vowel_back_mid":         "vowel_back",
    "vowel_back_low":         "vowel_back",
    "vowel_diphthong_aw":     "vowel_diphthong",
    "vowel_diphthong_ay":     "vowel_diphthong",
    "vowel_diphthong_oy":     "vowel_diphthong",
    "stop_bilabial":          "stop",
    "stop_alveolar":          "stop",
    "stop_velar":             "stop",
    "fricative_labiodental":  "fricative",
    "fricative_dental":       "fricative",
    "fricative_alveolar":     "fricative",
    "fricative_postalveolar": "fricative",
    "fricative_glottal":      "fricative",
    "affricate":              "affricate",
    "nasal":                  "nasal",
    "liquid":                 "liquid",
    "glide":                  "glide",
}

# Partial-credit score awarded when two phonemes are in the *same class*
# (but not identical).  e.g. T vs D → 0.7 (same manner, voicing differs only)
SAME_CLASS_SCORE = 0.7

# Partial-credit score when phonemes share a *superclass* but not the same class.
# e.g. IY (front-high) vs EY (front-mid) → 0.4 (both front vowels)
SAME_SUPERCLASS_SCORE = 0.4


def phoneme_similarity(p1: str, p2: str) -> float:
    """
    Return a similarity score in [0.0, 1.0] between two ARPAbet phonemes.

    Scoring tiers:
      1.0  — identical (after stress-digit stripping)
      0.7  — same articulatory class  (e.g. T / D, S / Z, IY / IH)
      0.4  — same broad superclass    (e.g. IY / EY — both front vowels)
      0.0  — unrelated
    """
    p1 = normalize_phoneme(p1)
    p2 = normalize_phoneme(p2)

    if p1 == p2:
        return 1.0

    class1 = PHONEME_CLASSES.get(p1)
    class2 = PHONEME_CLASSES.get(p2)

    # Unknown phoneme — can't score
    if class1 is None or class2 is None:
        return 0.0

    if class1 == class2:
        return SAME_CLASS_SCORE

    super1 = _SUPERCLASS.get(class1)
    super2 = _SUPERCLASS.get(class2)

    if super1 is not None and super1 == super2:
        return SAME_SUPERCLASS_SCORE

    return 0.0


def phoneme_sequence_similarity(seqA, seqB):
    
    min_len = min(len(seqA), len(seqB))
    
    if min_len == 0:
        return 0.0

    matches = 0

    for a, b in zip(seqA, seqB):
        if normalize_phoneme(a) == normalize_phoneme(b):
            matches += 1

    return matches / min_len


def rhyme_similarity(rhymeA, rhymeB, mode="stressed"):

    # Both "stressed" and "stressed_plus" use tail similarity.
    #
    # The old vowel/coda/length weighted scorer assumed the first phoneme
    # of the rhyme unit is always the stressed vowel — but for multi-syllable
    # words like "underground" [AH1 N D ER0 G R AW2 N D] this is wrong:
    # the rhyming vowel is buried at the tail (AW2), not at index 0 (AH1).
    # Tail similarity correctly finds the shared ending regardless of length.
    if mode in ("stressed", "stressed_plus"):
        return longest_common_tail_similarity(rhymeA, rhymeB)

    if mode == "entire_word":
        return phoneme_sequence_similarity(rhymeA, rhymeB)

    raise ValueError(f"Unknown rhyme mode: {mode}")


def compute_similarity_pairs(end_word_objects, rhyme_mode="stressed"):

    similarity_results = []

    for a, b in itertools.combinations(end_word_objects, 2):

        wordA = a["end_word"]
        wordB = b["end_word"]

        rhymeA = a["rhyme_unit"]
        rhymeB = b["rhyme_unit"]

        score = rhyme_similarity(rhymeA, rhymeB, mode=rhyme_mode)

        similarity_results.append({
            "wordA": wordA,
            "wordB": wordB,
            "similarity": score
        })

    return similarity_results


def build_similarity_matrix(rhyme_candidates, similarity_pairs):

    # collect all words
    words = [obj["end_word"] for obj in rhyme_candidates]

    # initialize matrix
    matrix = {w: {v: 0.0 for v in words} for w in words}

    # diagonal = identical words
    for w in words:
        matrix[w][w] = 1.0

    # fill matrix using computed pairs
    for pair in similarity_pairs:

        wA = pair["wordA"]
        wB = pair["wordB"]
        score = pair["similarity"]

        matrix[wA][wB] = score
        matrix[wB][wA] = score

    return matrix


def longest_common_tail_similarity(seqA, seqB, debug=False):
    """
    Score how well two rhyme units match from the end (tail) inward.

    Uses phoneme_similarity() for each position so that near-identical
    phonemes (e.g. T/D, AW/AO) contribute partial credit rather than
    scoring zero on a mismatch and halting the walk.

    Walk behaviour:
      - Continue inward as long as phoneme_similarity >= 0.4
        (same class or same superclass).
      - Stop on the first position that scores below 0.4.
      - Accumulate the fractional scores; divide by min_len.

    Uses min_len as denominator so a short tail that perfectly matches
    the end of a longer sequence still scores 1.0.
    """
    i = len(seqA) - 1
    j = len(seqB) - 1

    score_sum = 0.0
    steps = 0

    while i >= 0 and j >= 0:
        sim = phoneme_similarity(seqA[i], seqB[j])

        if debug:
            print(f"  [{steps}] {seqA[i]} vs {seqB[j]} → {sim:.2f}")

        if sim < SAME_SUPERCLASS_SCORE:   # below 0.4 → stop walking
            break

        score_sum += sim
        steps += 1
        i -= 1
        j -= 1

    min_len = min(len(seqA), len(seqB))

    if min_len == 0:
        return 0.0

    return score_sum / min_len