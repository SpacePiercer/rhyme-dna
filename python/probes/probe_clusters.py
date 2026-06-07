"""Diagnostic probe: inspect rhyme clustering of the loaded verse.

Not a unit test — an exploratory script for eyeballing how the assonance score
(coda-discount `c`) and the clustering method shape the short-i scheme of the
current input verse. Useful when tuning `c` (M12), stress weighting (M13), or
the position-aware detector (M17 — see `windowed_linkage`).

Run from the repo root as a module:
    conda run -n mfa_env python -m python.probes.probe_clusters
(reads the live TextGrid + lyrics under input/ and output/).
"""
from praatio import textgrid

import python.similarity_engine as se
from python.rhyme_extraction import extract_rhyme_candidates
from python.similarity_engine import compute_similarity_pairs, build_similarity_matrix
from python.clustering import cluster_rhymes, get_threshold

TG = "output/current_output/input.TextGrid"
LYRICS = "input/current_input/input.txt"
RHYME_MODE = "stressed"
DETECTION_MODE = "full_line"

# The ear-grouped short-i scheme this verse is built around (the M12 target).
TARGET = {"with", "clip", "hip", "gripped", "width", "tip", "slit",
          "it", "chips", "fit", "ultimate"}


def build_word_to_phonemes():
    """Map each word to its phonemes from the TextGrid, like the notebook does:
    first occurrence of a word; phones whose midpoint falls inside the word."""
    tg = textgrid.openTextgrid(TG, includeEmptyIntervals=False)
    word_tier = tg.getTier("words")
    phone_tier = tg.getTier("phones")
    w2p = {}
    for w in word_tier.entries:
        if w.label in w2p:
            continue
        w2p[w.label] = [p.label for p in phone_tier.entries
                        if w.start <= (p.start + p.end) / 2 <= w.end]
    return w2p


def get_candidates():
    return extract_rhyme_candidates(LYRICS, build_word_to_phonemes(),
                                    rhyme_mode=RHYME_MODE,
                                    detection_mode=DETECTION_MODE)


def _matrix(candidates, c):
    se.CODA_DISCOUNT = c
    pairs = compute_similarity_pairs(candidates, rhyme_mode=RHYME_MODE)
    return build_similarity_matrix(candidates, pairs)


def _report(name, best):
    in_t = sorted(set(w for w in best if w in TARGET))
    extra = sorted(set(w for w in best if w not in TARGET))
    missing = sorted(TARGET - set(best))
    print(f"\n--- {name} ---")
    print(f"  best short-i cluster size: {len(best)}")
    print(f"    target in it ({len(in_t)}/{len(TARGET)}): {in_t}")
    print(f"    extra (incidental): {extra}")
    print(f"    missing targets: {missing}")


def live_clustering(candidates, c):
    """Cluster with the project's current cluster_rhymes (average-linkage)."""
    matrix = _matrix(candidates, c)
    _, clusters = cluster_rhymes(matrix, threshold=get_threshold(RHYME_MODE))
    best = max(clusters.values(), key=lambda m: len(set(m) & TARGET))
    _report(f"LIVE cluster_rhymes (c={c})", best)


def windowed_linkage(candidates, c, n):
    """EXPERIMENTAL (deferred to M17): sequential drift clustering — a word joins
    the cluster whose LAST n members it is most similar to (mean >= threshold).
    Models a scheme drifting along the verse instead of staying near its whole
    self. On this verse it fragments the scheme; kept for M17 exploration."""
    matrix = _matrix(candidates, c)
    thr = get_threshold(RHYME_MODE)
    clusters = []
    for w in matrix:  # first-appearance (verse) order
        best_cl, best_mean = None, -1.0
        for cl in clusters:
            window = cl[-n:]
            mean = sum(matrix[m][w] for m in window) / len(window)
            if mean >= thr and mean > best_mean:
                best_mean, best_cl = mean, cl
        (best_cl.append(w) if best_cl is not None else clusters.append([w]))
    best = max(clusters, key=lambda m: len(set(m) & TARGET))
    _report(f"WINDOWED-LINKAGE (c={c}, n={n})", best)


def sample_pairs(candidates, c, pairs):
    """Print raw pairwise rhyme scores for a few illustrative word pairs."""
    units = {cand["end_word"]: cand["rhyme_unit"] for cand in candidates}
    print(f"\n--- sample pairwise scores (c={c}) ---")
    for a, b in pairs:
        if a in units and b in units:
            s = se.rhyme_unit_similarity(units[a], units[b], coda_discount=c)
            print(f"  {a:8} {str(units[a]):14} vs {b:8} {str(units[b]):14} = {s:.3f}")


if __name__ == "__main__":
    cands = get_candidates()
    live_clustering(cands, 1.0)   # before M12: consonants count fully
    live_clustering(cands, 0.3)   # M12: assonance-first
    for n in (1, 2, 3):
        windowed_linkage(cands, 0.3, n)
    sample_pairs(cands, 0.3, [("it", "tip"), ("clip", "hip"), ("it", "up"),
                              ("it", "the"), ("it", "and")])
