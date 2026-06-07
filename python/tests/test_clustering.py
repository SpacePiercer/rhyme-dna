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


# --- single-linkage chaining (Milestone 12) ---------------------------------

def test_single_linkage_chains_through_members():
    """B does not rhyme with the seed A (0.5) but does with C (0.9), and C
    rhymes with A (0.9). Single-linkage must pull all three into one cluster by
    linking B through C — the old seed-only test would have split B off."""
    words = ["A", "C", "B"]
    scores = {("A", "C"): 0.9, ("C", "B"): 0.9, ("A", "B"): 0.5}

    def s(x, y):
        if x == y:
            return 1.0
        return scores.get((x, y), scores.get((y, x), 0.0))

    matrix = {x: {y: s(x, y) for y in words} for x in words}

    cluster_labels, clusters = cluster_rhymes(matrix, threshold=0.7)

    assert len(clusters) == 1
    assert cluster_labels["A"] == cluster_labels["B"] == cluster_labels["C"]
