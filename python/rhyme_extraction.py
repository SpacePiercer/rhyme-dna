def extract_rhyme_unit(phonemes, mode="stressed", debug=False):

    stressed_index = None

    # Find primary stress (1)
    for i in range(len(phonemes) - 1, -1, -1):
        if '1' in phonemes[i]:
            stressed_index = i
            break

    # If no primary stress, fallback to secondary/unstressed
    if stressed_index is None:
        for i in range(len(phonemes) - 1, -1, -1):
            if '2' in phonemes[i] or '0' in phonemes[i]:
                stressed_index = i
                break

    # If still none found
    if stressed_index is None:
        stressed_index = 0

    # --- Mode logic ---

    if mode == "stressed":
        rhyme_unit = phonemes[stressed_index:]

    elif mode == "stressed_plus":
        rhyme_unit = phonemes[stressed_index:]

    elif mode == "entire_word":
        rhyme_unit = phonemes[:]

    else:
        raise ValueError(f"Unknown rhyme mode: {mode}")

    if debug:
        print("MODE:", mode)
        print("PHONEMES:", phonemes)
        print("STRESS INDEX:", stressed_index)
        print("RHYME UNIT:", rhyme_unit)

    return rhyme_unit


def extract_end_words(lyrics_path, word_to_phonemes, rhyme_mode="stressed"):

    result = []

    with open(lyrics_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):

        line = line.strip()

        if not line:
            continue

        words = line.lower().split()
        end_word = words[-1]

        if end_word not in word_to_phonemes:
            print(f"WARNING: phonemes not found for '{end_word}'")
            continue

        phonemes = word_to_phonemes[end_word]
        rhyme_unit = extract_rhyme_unit(phonemes, mode=rhyme_mode)

        result.append({
            "line_index": i,
            "line_text": line,
            "end_word": end_word,
            "phonemes": phonemes,
            "rhyme_unit": rhyme_unit
        })

    return result