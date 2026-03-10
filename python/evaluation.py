def evaluate_rhyme_detection(rhyme_candidates, predicted_clusters):

    total = 0
    correct = 0
    mismatches = []

    for r in rhyme_candidates:

        word = r["end_word"]
        expected = r.get("expected_cluster")
        predicted = predicted_clusters.get(word)

        if expected is None:
            continue

        total += 1

        if expected == predicted:
            correct += 1
        else:
            mismatches.append({
                "word": word,
                "expected": expected,
                "predicted": predicted
            })

    accuracy = correct / total if total > 0 else 0

    print("\n===== RHYME EVALUATION =====\n")
    print(f"TOTAL WORDS: {total}")
    print(f"CORRECT: {correct}")
    print(f"ACCURACY: {accuracy:.2f}")

    if mismatches:
        print("\nMISMATCHES:")
        for m in mismatches:
            print(m)

    return accuracy, mismatches