import itertools

from panphon.distance import Distance

# ---------------------------------------------------------------------------
# panphon setup
# ---------------------------------------------------------------------------
# panphon is the single source of truth for how similar two speech sounds are.
# It is instantiated once at import time (it loads feature tables from disk).
_DIST = Distance()
_FM = _DIST.fm

# Cost panphon charges to insert or delete one whole sound = the sum of all
# feature weights (~7.25). Used as the normaliser and as the cap ceiling.
SEG_COST = sum(_FM.weights)


# ---------------------------------------------------------------------------
# Scoring configuration  (swap-ready for the M17 learned-weights milestone)
# ---------------------------------------------------------------------------
# Two interchangeable methods control how a missing/extra sound is penalised:
#   "D" — flat gentle penalty per inserted/deleted sound   (SIMILARITY_PENALTY)
#   "C" — weighted cost capped at SIMILARITY_CAP per inserted/deleted sound
# Substitutions always use panphon's weighted feature-difference cost.
SIMILARITY_METHOD = "D"
SIMILARITY_PENALTY = 0.75   # used when SIMILARITY_METHOD == "D"
SIMILARITY_CAP = 1.0        # used when SIMILARITY_METHOD == "C"


def normalize_phoneme(p):
    """Strip stress markers from an IPA phoneme symbol.

    MFA's english_mfa model prefixes stressed vowels with ˈ (primary) or
    ˌ (secondary). These are stripped so comparisons are stress-agnostic.
    """
    return p.lstrip("ˈˌ")


def _token_to_vector(token):
    """Return a single panphon feature vector for one rhyme-unit token.

    Most tokens are a single IPA segment. A few (diphthongs written as "aw",
    "aj", "oj") are two segments to panphon; for a *per-phoneme* comparison we
    average them into one vector so the token counts as one sound. Returns
    None if panphon does not recognise the token.
    """
    vl = _FM.word_to_vector_list(normalize_phoneme(token), numeric=True)
    if not vl:
        return None
    if len(vl) == 1:
        return vl[0]
    return [sum(col) / len(vl) for col in zip(*vl)]


def phoneme_similarity(p1, p2):
    """Return a panphon feature-based similarity in [0.0, 1.0] for two phonemes.

    1.0 means identical sounds; lower means more articulatory features differ.
    Computed as 1 minus panphon's weighted feature-difference cost, normalised
    by the cost of a whole sound (SEG_COST). Replaces the old hand-coded class
    table — any IPA symbol is scored without table maintenance.
    """
    p1, p2 = normalize_phoneme(p1), normalize_phoneme(p2)
    if p1 == p2:
        return 1.0
    v1, v2 = _token_to_vector(p1), _token_to_vector(p2)
    if v1 is None or v2 is None:
        return 0.0
    cost = _DIST.weighted_substitution_cost(v1, v2)
    return max(0.0, 1.0 - cost / SEG_COST)


def _insert_delete_cost(method, value):
    """Build the panphon insert/delete cost function for the chosen method."""
    if method == "D":
        penalty = SIMILARITY_PENALTY if value is None else value
        return lambda v: penalty
    if method == "C":
        cap = SIMILARITY_CAP if value is None else value
        return lambda v: min(SEG_COST, cap)
    raise ValueError(f"Unknown similarity method: {method!r} (use 'D' or 'C')")


def rhyme_unit_similarity(unitA, unitB, method=None, value=None):
    """Score how strongly two rhyme units rhyme, in [0.0, 1.0].

    Uses panphon's weighted feature edit distance: a substitution costs
    panphon's weighted feature difference between the two sounds, while an
    inserted/deleted sound costs a bounded penalty (method "D" = flat penalty,
    "C" = capped weighted cost). The total is normalised by the longer unit's
    sound count and subtracted from 1 (floored at 0).

    The rhyme unit's tokens are joined into one IPA string for panphon, which
    aligns and scores them; diphthongs written "aw"/"aj" are left as panphon's
    default two-segment split (a separate "diphthong as one" representation is
    deferred to the weight-learning milestone).

    Parameters
    ----------
    unitA, unitB : list of str
        IPA phoneme sequences (rhyme units) to compare.
    method : str or None
        "D" or "C"; defaults to the module-level SIMILARITY_METHOD.
    value : float or None
        Penalty (method "D") or cap (method "C"); defaults to the module
        config constant for the chosen method.
    """
    method = method or SIMILARITY_METHOD
    a = "".join(normalize_phoneme(p) for p in unitA)
    b = "".join(normalize_phoneme(p) for p in unitB)
    va = _FM.word_to_vector_list(a, numeric=True)
    vb = _FM.word_to_vector_list(b, numeric=True)
    if not va or not vb:
        return 0.0
    cost_fn = _insert_delete_cost(method, value)
    maxlen = max(len(va), len(vb))
    distance = _DIST.min_edit_distance(
        cost_fn, cost_fn, _DIST.weighted_substitution_cost, [[]], va, vb
    )
    return max(0.0, 1.0 - distance / maxlen)


def rhyme_similarity(rhymeA, rhymeB, mode="stressed"):
    """Score two rhyme units with the panphon feature edit distance.

    The `mode` argument is retained for backward compatibility with existing
    callers but no longer changes the scoring: the rhyme unit was already
    shaped by the chosen mode during extraction (see
    rhyme_extraction.extract_rhyme_unit). All modes now share one scorer.
    """
    return rhyme_unit_similarity(rhymeA, rhymeB)


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
