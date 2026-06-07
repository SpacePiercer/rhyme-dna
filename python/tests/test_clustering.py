"""Unit tests for cluster labelling.

Focus: cluster labels must always be ASCII letters so they are valid CSS class
names (`.rhyme-<label>`). The old chr()-incrementing scheme produced punctuation
labels ('[', '\\', ']', ...) after the 26th cluster, generating invalid CSS that
broke highlighting for the 27th+ rhyme group.
"""
import re

import pytest

from python.clustering import cluster_label, cluster_rhymes


# --- the label generator ----------------------------------------------------

@pytest.mark.parametrize("index, expected", [
    (0, "A"),
    (1, "B"),
    (25, "Z"),
    (26, "AA"),   # the first label past Z — was '[' under the old scheme
    (27, "AB"),
    (51, "AZ"),
    (52, "BA"),
])
def test_cluster_label_is_alphabetic(index, expected):
    assert cluster_label(index) == expected


# --- the 27th+ cluster must stay CSS-safe -----------------------------------

def test_more_than_26_clusters_all_alphabetic():
    """30 mutually non-rhyming words -> 30 singleton clusters. Every label must
    be letters only (no punctuation), so each is a valid CSS class name."""
    words = [f"w{i}" for i in range(30)]
    # Every pair scores 0 -> no merging -> one cluster per word.
    matrix = {a: {b: 0.0 for b in words if b != a} for a in words}

    cluster_labels, clusters = cluster_rhymes(matrix, threshold=0.7)

    assert len(clusters) == 30
    for label in clusters:
        assert re.fullmatch(r"[A-Z]+", label), f"label {label!r} is not CSS-safe"
    # The 27th cluster is 'AA', not '['
    assert "AA" in clusters
    assert "[" not in clusters


# --- average-linkage (Milestone 12) -----------------------------------------

def _matrix(words, scores):
    """Build a symmetric similarity matrix (diagonal 1.0) from a pair dict."""
    def s(x, y):
        if x == y:
            return 1.0
        return scores.get((x, y), scores.get((y, x), 0.0))
    return {x: {y: s(x, y) for y in words} for x in words}


def test_average_linkage_merges_when_close_to_all_members():
    """A, B, C are all mutually similar (~0.85) -> one cluster."""
    words = ["A", "B", "C"]
    matrix = _matrix(words, {("A", "B"): 0.85, ("A", "C"): 0.85, ("B", "C"): 0.85})

    cluster_labels, clusters = cluster_rhymes(matrix, threshold=0.7)

    assert len(clusters) == 1
    assert cluster_labels["A"] == cluster_labels["B"] == cluster_labels["C"]


def test_average_linkage_rejects_chaining_word():
    """C is close to B (0.95) but far from A (0.2). Single-linkage would chain C
    in via B; average-linkage rejects it because its MEAN to {A,B} is 0.575 <
    0.7. So {A,B} cluster and C stands alone."""
    words = ["A", "B", "C"]
    matrix = _matrix(words, {("A", "B"): 0.9, ("A", "C"): 0.2, ("B", "C"): 0.95})

    cluster_labels, clusters = cluster_rhymes(matrix, threshold=0.7)

    assert len(clusters) == 2
    assert cluster_labels["A"] == cluster_labels["B"]
    assert cluster_labels["C"] != cluster_labels["A"]
