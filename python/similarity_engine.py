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

# Index of panphon's "syllabic" feature inside a numeric feature vector.
# A value of +1 marks a vowel; -1 marks a consonant. Used by the coda-discount
# logic to tell vowels and consonants apart.
_SYL_IDX = _FM.names.index("syl")


def _is_vowel_vector(vec):
    """True if a panphon numeric feature vector is a vowel ([+syllabic])."""
    return vec[_SYL_IDX] > 0


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

# Role weights (Milestone 12 coda discount, generalised by Milestone 13).
# A syllable has three roles: onset (leading consonants), nucleus (the vowel),
# and coda (trailing consonants). Each role scales its segments' edit cost:
#   onset   -> ONSET_WEIGHT   (default 0.0 — onsets ignored for now)
#   nucleus -> NUCLEUS_WEIGHT (1.0 — full weight; the vowel carries the rhyme)
#   coda    -> CODA_WEIGHT    (0.3 — graded contribution; the M12 coda discount)
# A weight of 1.0 counts a sound fully; 0.0 ignores it entirely. The coda weight
# is the old "coda discount": it makes the score driven mainly by shared vowels
# (assonance), the way fast rap rhyme is heard. With ONSET_WEIGHT = 0, *clip*
# and *grip* score 1.0 (the kl-/gr- onsets are dropped) while their shared -ɪp
# still matches. All three are swappable knobs for the M20 learned-weights
# milestone. (The flat word-tail scorer rhyme_unit_similarity has no onset/coda
# distinction, so it applies CODA_WEIGHT to every consonant.)
ONSET_WEIGHT = 0.0
NUCLEUS_WEIGHT = 1.0
CODA_WEIGHT = 0.3


def normalize_phoneme(p):
    """Strip stress markers from an IPA phoneme symbol.

    MFA's english_mfa model prefixes stressed vowels with ˈ (primary) or
    ˌ (secondary). These are stripped so comparisons are stress-agnostic.
    """
    return p.lstrip("ˈˌ")


# IPA vowel characters found in english_mfa output. Used to locate syllable
# nuclei (syllabification.py) and the rhyme anchor (rhyme_extraction.py). Lives
# here, beside normalize_phoneme, as a shared phonology primitive so both
# higher-level modules import it from one place (and avoid an import cycle).
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


def rhyme_unit_similarity(unitA, unitB, method=None, value=None, coda_discount=None):
    """Score how strongly two rhyme units rhyme, in [0.0, 1.0].

    Uses panphon's weighted feature edit distance: a substitution costs
    panphon's weighted feature difference between the two sounds, while an
    inserted/deleted sound costs a bounded penalty (method "D" = flat penalty,
    "C" = capped weighted cost). The total is normalised by the longer unit's
    sound count and subtracted from 1 (floored at 0).

    Coda discount (Milestone 12): every consonant cost is multiplied by
    `coda_discount` so the score is driven mainly by shared vowels. The discount
    applies to a consonant being inserted, deleted, or substituted for another
    consonant. A substitution that involves a vowel — including a mismatched
    vowel-vs-consonant alignment — keeps its full cost; that mismatch is so
    expensive the aligner routes around it with a cheap consonant insert/delete.

    The rhyme unit's tokens are joined into one IPA string for panphon, which
    aligns and scores them; diphthongs written "aw"/"aj" are left as panphon's
    default two-segment split (the glide half "w"/"j" counts as a consonant, so
    a mismatch on it is discounted — the separate "diphthong as one"
    representation is deferred to the weight-learning milestone).

    Parameters
    ----------
    unitA, unitB : list of str
        IPA phoneme sequences (rhyme units) to compare.
    method : str or None
        "D" or "C"; defaults to the module-level SIMILARITY_METHOD.
    value : float or None
        Penalty (method "D") or cap (method "C"); defaults to the module
        config constant for the chosen method.
    coda_discount : float or None
        Factor applied to consonant costs; defaults to module CODA_WEIGHT.
        1.0 reproduces the pre-M12 (consonants-count-fully) behaviour.
    """
    method = method or SIMILARITY_METHOD
    c = CODA_WEIGHT if coda_discount is None else coda_discount
    a = "".join(normalize_phoneme(p) for p in unitA)
    b = "".join(normalize_phoneme(p) for p in unitB)
    va = _FM.word_to_vector_list(a, numeric=True)
    vb = _FM.word_to_vector_list(b, numeric=True)
    if not va or not vb:
        return 0.0

    base_id_cost = _insert_delete_cost(method, value)

    def id_cost(vec):
        # Inserting/deleting a consonant is discounted by c; a vowel is full.
        cost = base_id_cost(vec)
        return cost if _is_vowel_vector(vec) else cost * c

    def sub_cost(v1, v2):
        # Consonant<->consonant substitutions are discounted by c; any
        # substitution touching a vowel (incl. vowel<->consonant) is full cost.
        cost = _DIST.weighted_substitution_cost(v1, v2)
        if _is_vowel_vector(v1) or _is_vowel_vector(v2):
            return cost
        return cost * c

    maxlen = max(len(va), len(vb))
    distance = _DIST.min_edit_distance(id_cost, id_cost, sub_cost, [[]], va, vb)
    return max(0.0, 1.0 - distance / maxlen)


def _syllable_segments(syllable):
    """Yield (vector, role) pairs for each panphon segment of a syllable unit.

    A syllable unit is a dict with 'onset' (list), 'nucleus' (str or None) and
    'coda' (list). Each token is expanded into panphon feature vectors — a
    diphthong nucleus such as "aw" becomes two segments, both tagged 'nucleus'.
    Unrecognised tokens are skipped. Tagging every segment with its role lets the
    edit-distance cost functions weight onsets, the nucleus, and the coda
    differently (the heart of Milestone 13's role-aware scoring).
    """
    segments = []
    parts = [(syllable["onset"], "onset")]
    if syllable["nucleus"] is not None:
        parts.append(([syllable["nucleus"]], "nucleus"))
    parts.append((syllable["coda"], "coda"))

    for tokens, role in parts:
        for tok in tokens:
            for v in _FM.word_to_vector_list(normalize_phoneme(tok), numeric=True):
                segments.append((v, role))
    return segments


def syllable_similarity(
    sylA, sylB, method=None, value=None,
    onset_weight=None, nucleus_weight=None, coda_weight=None,
):
    """Score how strongly two SYLLABLES rhyme, in [0.0, 1.0] (Milestone 13).

    Like rhyme_unit_similarity, this uses panphon's weighted feature edit
    distance, but it is **role-aware**: each segment's cost is scaled by the
    weight of its role in the syllable — onset (ONSET_WEIGHT, default 0),
    nucleus (NUCLEUS_WEIGHT, 1.0), coda (CODA_WEIGHT, 0.3). For a substitution
    that aligns two segments, the larger of the two role weights is used (so a
    vowel always pulls full weight, and two onsets together pull none). The
    total is normalised by the longer syllable's segment count and subtracted
    from 1.

    Parameters
    ----------
    sylA, sylB : dict
        Syllable units (with 'onset', 'nucleus', 'coda'), e.g. from
        syllabification.syllabify or rhyme_extraction.extract_syllable_candidates.
    method : str or None
        "D" or "C"; defaults to the module-level SIMILARITY_METHOD.
    value : float or None
        Penalty (method "D") or cap (method "C"); defaults to the module config.
    onset_weight : float or None
        Onset role weight; defaults to module ONSET_WEIGHT. 0 ignores onsets.
    nucleus_weight : float or None
        Nucleus role weight; defaults to module NUCLEUS_WEIGHT.
    coda_weight : float or None
        Coda role weight; defaults to module CODA_WEIGHT.
    """
    method = method or SIMILARITY_METHOD
    o = ONSET_WEIGHT if onset_weight is None else onset_weight
    nuc = NUCLEUS_WEIGHT if nucleus_weight is None else nucleus_weight
    c = CODA_WEIGHT if coda_weight is None else coda_weight

    segA = _syllable_segments(sylA)
    segB = _syllable_segments(sylB)
    if not segA or not segB:
        return 0.0

    base_id_cost = _insert_delete_cost(method, value)

    def role_weight(role):
        if role == "nucleus":
            return nuc
        if role == "onset":
            return o
        return c  # coda

    def id_cost(elem):
        # Insert/delete one segment: scale the flat penalty by its role weight.
        vec, role = elem
        return base_id_cost(vec) * role_weight(role)

    def sub_cost(e1, e2):
        # Align two segments: scale panphon's feature cost by the larger role
        # weight, so a nucleus pulls full weight and two onsets pull none.
        v1, r1 = e1
        v2, r2 = e2
        cost = _DIST.weighted_substitution_cost(v1, v2)
        return cost * max(role_weight(r1), role_weight(r2))

    maxlen = max(len(segA), len(segB))
    distance = _DIST.min_edit_distance(id_cost, id_cost, sub_cost, [[]], segA, segB)
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


# ---------------------------------------------------------------------------
# Syllable-unit scoring (Milestone 13)
# ---------------------------------------------------------------------------
# The syllable engine clusters syllable units (from
# rhyme_extraction.extract_syllable_candidates), not words. These two helpers
# mirror compute_similarity_pairs / build_similarity_matrix but key everything
# on each syllable's unique unit_id (a word contributes several syllables, and
# the same syllable shape recurs across words, so the word string is no longer a
# usable key). The resulting matrix feeds clustering.cluster_rhymes unchanged.

def compute_syllable_pairs(syllable_units, **scorer_kwargs):
    """Score every pair of syllable units with syllable_similarity.

    Parameters
    ----------
    syllable_units : list of dict
        Syllable units (each with 'unit_id', 'onset', 'nucleus', 'coda').
    **scorer_kwargs
        Passed through to syllable_similarity (e.g. onset_weight, coda_weight).

    Returns
    -------
    list of dict
        Each with keys 'idA', 'idB', 'similarity'.
    """
    results = []
    for a, b in itertools.combinations(syllable_units, 2):
        score = syllable_similarity(a, b, **scorer_kwargs)
        results.append({
            "idA": a["unit_id"],
            "idB": b["unit_id"],
            "similarity": score,
        })
    return results


def build_syllable_matrix(syllable_units, syllable_pairs):
    """Build a similarity matrix keyed by syllable unit_id.

    Diagonal is 1.0 (a unit is identical to itself); off-diagonal entries come
    from syllable_pairs; any unscored pair defaults to 0.0.
    """
    ids = [u["unit_id"] for u in syllable_units]
    matrix = {i: {j: 0.0 for j in ids} for i in ids}
    for i in ids:
        matrix[i][i] = 1.0
    for pair in syllable_pairs:
        a, b, score = pair["idA"], pair["idB"], pair["similarity"]
        matrix[a][b] = score
        matrix[b][a] = score
    return matrix
