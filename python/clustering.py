SIMILARITY_THRESHOLD = 0.7

def cluster_rhymes(similarity_matrix, threshold=SIMILARITY_THRESHOLD):

    words = list(similarity_matrix.keys())
    clusters = {}
    cluster_labels = {}

    visited = set()
    current_cluster = "A"

    for word in words:

        if word in visited:
            continue

        stack = [word]
        clusters[current_cluster] = []

        while stack:

            w = stack.pop()

            if w in visited:
                continue

            visited.add(w)
            clusters[current_cluster].append(w)
            cluster_labels[w] = current_cluster

            for other in words:
                if similarity_matrix[w][other] >= threshold and other not in visited:
                    stack.append(other)

        if clusters[current_cluster]:
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


