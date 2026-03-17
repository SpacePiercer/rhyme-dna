import itertools

def normalize_phoneme(p):

    # remove stress digits from ARPAbet vowels
    return p.rstrip("012")


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


def longest_common_tail_similarity(seqA, seqB):
    """
    Score how well two rhyme units match from the end (tail) inward.

    Uses min_len as denominator — a short word rhyming perfectly with the
    tail of a long word should score 1.0, not be penalised for the length
    difference. Example: 'mound' [AW1 N D] vs 'underground' [... AW2 N D]
    share a 3-phoneme tail; min_len=3, score = 3/3 = 1.0.

    Stress digits are stripped before comparison so AW1 == AW2.
    """

    i = len(seqA) - 1
    j = len(seqB) - 1

    matches = 0

    while i >= 0 and j >= 0:

        if normalize_phoneme(seqA[i]) == normalize_phoneme(seqB[j]):
            matches += 1
            i -= 1
            j -= 1
        else:
            break

    min_len = min(len(seqA), len(seqB))

    if min_len == 0:
        return 0.0

    return matches / min_len