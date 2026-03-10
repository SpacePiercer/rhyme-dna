SIMILARITY_THRESHOLD = 0.7

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


