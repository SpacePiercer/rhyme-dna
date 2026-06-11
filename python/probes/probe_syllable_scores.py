"""Measurement probe for the Milestone 13 normalisation decision.

This is the measurement behind the 2026-06-09 sign-off. The syllable scorer's
edit-distance denominator can be either the raw segment count (`maxlen`) or the
*effective (weighted) length* — each segment counted by its role weight
(onset 0, nucleus 1.0, coda 0.3). The question was which to ship.

The probe defines BOTH denominators locally (so it stays reproducible no matter
what the engine currently uses) and:
  1. dumps the pairwise score distribution under each, and
  2. clusters under each and compares memberships (the two cross-word wins, and
     the breadth of the big short-i cluster).

Outcome (recorded): effective length gives a far cleaner rhyme/non-rhyme split
and tighter clusters; re-swept to threshold 0.65 it keeps both cross-word wins
(clip~gripped, load~both) while dropping the e/eː over-merge maxlen@0.70 had.
Effective length @ 0.65 was adopted into syllable_similarity.

Run:
  $env:PYTHONUTF8=1
  conda run --no-capture-output -n mfa_env python python/probes/probe_syllable_scores.py
"""
import sys
sys.path.append(".")

import itertools

from praatio import textgrid

from python.rhyme_extraction import extract_syllable_candidates
from python.similarity_engine import (
    build_syllable_matrix,
    _syllable_segments,
    _insert_delete_cost,
    _DIST,
    SIMILARITY_METHOD,
    ONSET_WEIGHT,
    NUCLEUS_WEIGHT,
    CODA_WEIGHT,
)
from python.clustering import cluster_rhymes

INPUT_TXT_PATH = "input/current_input/input.txt"
OUTPUT_TEXTGRID_PATH = "output/current_output/input.TextGrid"


def build_word_to_phonemes():
    """Rebuild word_to_phonemes from the TextGrid (mirrors notebook Section 3)."""
    tg = textgrid.openTextgrid(OUTPUT_TEXTGRID_PATH, includeEmptyIntervals=False)
    words, phones = tg.getTier("words"), tg.getTier("phones")
    w2p = {}
    for w in words.entries:
        seq = [p.label for p in phones.entries if p.start >= w.start and p.end <= w.end]
        w2p.setdefault(w.label.lower(), seq)
    return w2p


def _role_weight(role):
    if role == "nucleus":
        return NUCLEUS_WEIGHT
    if role == "onset":
        return ONSET_WEIGHT
    return CODA_WEIGHT


def _eff_len(segments):
    """Weighted length of a syllable: sum of each segment's role weight."""
    total = sum(_role_weight(role) for _, role in segments)
    return total if total > 0 else len(segments)   # zero-guard


def syllable_similarity_efflen(sylA, sylB):
    """Same role-aware scorer, but normalised by effective (weighted) length."""
    segA, segB = _syllable_segments(sylA), _syllable_segments(sylB)
    if not segA or not segB:
        return 0.0
    base_id_cost = _insert_delete_cost(SIMILARITY_METHOD, None)

    def id_cost(elem):
        vec, role = elem
        return base_id_cost(vec) * _role_weight(role)

    def sub_cost(e1, e2):
        v1, r1 = e1
        v2, r2 = e2
        return _DIST.weighted_substitution_cost(v1, v2) * max(_role_weight(r1), _role_weight(r2))

    distance = _DIST.min_edit_distance(id_cost, id_cost, sub_cost, [[]], segA, segB)
    denom = max(_eff_len(segA), _eff_len(segB))
    return max(0.0, 1.0 - distance / denom)


def matrix_from(units, scorer):
    pairs = []
    for a, b in itertools.combinations(units, 2):
        pairs.append({"idA": a["unit_id"], "idB": b["unit_id"], "similarity": scorer(a, b)})
    return build_syllable_matrix(units, pairs), pairs


def distribution(pairs):
    vals = sorted(p["similarity"] for p in pairs)
    n = len(vals)
    buckets = {f"{lo/10:.1f}-{lo/10+0.1:.1f}": 0 for lo in range(10)}
    for v in vals:
        lo = min(int(v * 10), 9)
        buckets[f"{lo/10:.1f}-{lo/10+0.1:.1f}"] += 1
    return sum(vals) / n, vals[n // 2], buckets


def cluster_of(units, labels, unit_id):
    """Return the 'word·syll' labels sharing unit_id's cluster."""
    target = labels[unit_id]
    return sorted(
        f'{u["source_word"]}·{u["syllable_index"]}'
        for u in units
        if labels[u["unit_id"]] == target
    )


def uid(units, word, syll=0):
    return next(u["unit_id"] for u in units if u["source_word"] == word and u["syllable_index"] == syll)


def report(name, units, scorer):
    print(f"\n################  {name}  ################")
    matrix, pairs = matrix_from(units, scorer)
    mean, median, buckets = distribution(pairs)
    print(f"pairs={len(pairs)}  mean={mean:.3f}  median={median:.3f}")
    print("score histogram:")
    top = max(buckets.values())
    for k, v in buckets.items():
        print(f"  {k}: {v:5d} {'#' * (v * 60 // top)}")

    labels, clusters = cluster_rhymes(matrix, threshold=0.7)
    clip_cluster = cluster_of(units, labels, uid(units, "clip"))
    load_cluster = cluster_of(units, labels, uid(units, "load"))
    print(f"\nclusters at 0.7: {len(clusters)}")
    print("clip~gripped together:", "gripped·0" in clip_cluster)
    print("load~both together:  ", "both·0" in load_cluster)
    print(f"clip's cluster ({len(clip_cluster)}): {clip_cluster}")
    print(f"load's cluster ({len(load_cluster)}): {load_cluster}")
    return labels


def sweep(name, units, scorer, thresholds):
    print(f"\n################  THRESHOLD SWEEP — {name}  ################")
    matrix, _ = matrix_from(units, scorer)
    print(f"{'thr':>5} {'#clust':>7} {'clip~grip':>10} {'load~both':>10} {'clipN':>6} {'loadN':>6}")
    for thr in thresholds:
        labels, clusters = cluster_rhymes(matrix, threshold=thr)
        clipc = cluster_of(units, labels, uid(units, "clip"))
        loadc = cluster_of(units, labels, uid(units, "load"))
        print(f"{thr:>5.2f} {len(clusters):>7} "
              f"{str('gripped·0' in clipc):>10} {str('both·0' in loadc):>10} "
              f"{len(clipc):>6} {len(loadc):>6}")


def main():
    w2p = build_word_to_phonemes()
    units = extract_syllable_candidates(INPUT_TXT_PATH, w2p, detection_mode="full_line")
    print(f"{len(units)} syllable units")
    report("MAXLEN (shipped)", units, syllable_similarity)
    report("EFFECTIVE LENGTH (candidate)", units, syllable_similarity_efflen)
    thresholds = [0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85]
    sweep("MAXLEN", units, syllable_similarity, thresholds)
    sweep("EFFECTIVE LENGTH", units, syllable_similarity_efflen, thresholds)


if __name__ == "__main__":
    main()
