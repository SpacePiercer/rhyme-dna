def debug_rhyme_analysis(rhyme_candidates, predicted_clusters):

    print("\n===== RHYME DEBUG REPORT =====\n")

    for r in rhyme_candidates:

        word = r["end_word"]
        phonemes = r["phonemes"]
        rhyme_unit = r["rhyme_unit"]
        expected = r.get("expected_cluster", None)
        predicted = predicted_clusters.get(word, None)

        print(f"WORD: {word}")
        print(f"PHONEMES: {phonemes}")
        print(f"RHYME UNIT: {rhyme_unit}")
        print(f"EXPECTED CLUSTER: {expected}")
        print(f"PREDICTED CLUSTER: {predicted}")

        if expected == predicted:
            print("STATUS: ✓ CORRECT")
        else:
            print("STATUS: ✗ MISMATCH")

        print("-" * 40)