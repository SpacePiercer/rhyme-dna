# Threshold for "stressed" and "entire_word" modes.
# With these modes rhyme units are compact (stressed vowel → end),
# so a high bar is appropriate.
SIMILARITY_THRESHOLD = 0.7

# Lower threshold for "stressed_plus" mode.
# stressed_plus units are longer (include the pre-stress syllable),
# so a perfect tail match on a two-syllable word scores ~0.5 against
# a one-syllable word. Lowering the threshold captures these correctly
# without over-merging unrelated clusters (cross-cluster scores stay at 0.0).
SIMILARITY_THRESHOLD_STRESSED_PLUS = 0.7


def get_threshold(rhyme_mode):
    """Return the appropriate clustering threshold for a given rhyme mode."""
    if rhyme_mode == "stressed_plus":
        return SIMILARITY_THRESHOLD_STRESSED_PLUS
    return SIMILARITY_THRESHOLD


def cluster_rhymes(similarity_matrix, threshold=SIMILARITY_THRESHOLD):

    words = list(similarity_matrix.keys())
    clusters = {}
    cluster_labels = {}
    current_cluster = "A"

    for word in words:

        if word in cluster_labels:
            continue

        clusters[current_cluster] = [word]
        cluster_labels[word] = current_cluster

        for other in words:

            if other == word:
                continue

            score = similarity_matrix[word][other]

            if score >= threshold and other not in cluster_labels:
                clusters[current_cluster].append(other)
                cluster_labels[other] = current_cluster

        current_cluster = chr(ord(current_cluster) + 1)

    return cluster_labels, clusters


def cluster_exact_rhymes(rhyme_candidates):

    clusters = {}
    cluster_labels = {}
    current_label = 0

    for entry in rhyme_candidates:

        rhyme_tuple = tuple(entry["rhyme_unit"])

        if rhyme_tuple not in clusters:

            label = chr(ord('A') + current_label)
            clusters[rhyme_tuple] = label
            current_label += 1

        cluster_labels[entry["end_word"]] = clusters[rhyme_tuple]

    return cluster_labels
