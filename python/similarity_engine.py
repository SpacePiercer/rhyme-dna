import itertools

def rhyme_similarity(rhymeA, rhymeB):

    # ----- VOWEL MATCH -----
    vowelA = rhymeA[0]
    vowelB = rhymeB[0]

    vowel_score = 1.0 if vowelA == vowelB else 0.0


    # ----- CODA OVERLAP -----
    codaA = rhymeA[1:]
    codaB = rhymeB[1:]

    if len(codaA) == 0 and len(codaB) == 0:
        coda_score = 1.0
    else:
        overlap = len(set(codaA) & set(codaB))
        max_len = max(len(codaA), len(codaB))

        if max_len == 0:
            coda_score = 0
        else:
            coda_score = overlap / max_len


    # ----- LENGTH SIMILARITY -----
    lenA = len(rhymeA)
    lenB = len(rhymeB)

    length_score = 1 - abs(lenA - lenB) / max(lenA, lenB)


    # ----- WEIGHTED FINAL SCORE -----
    similarity = (
        0.6 * vowel_score +
        0.3 * coda_score +
        0.1 * length_score
    )

    return similarity


def compute_similarity_pairs(end_word_objects):

    similarity_results = []

    for a, b in itertools.combinations(end_word_objects, 2):

        wordA = a["end_word"]
        wordB = b["end_word"]

        rhymeA = a["rhyme_unit"]
        rhymeB = b["rhyme_unit"]

        score = rhyme_similarity(rhymeA, rhymeB)

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