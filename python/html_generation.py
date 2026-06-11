def find_rhyme_suffix_span(word, phonemes, rhyme_unit):
    """
    Find the character span within `word` that corresponds to `rhyme_unit`.

    Uses a greedy phoneme-to-grapheme aligner: walks the word string
    left-to-right, consuming characters for each phoneme in sequence,
    then returns the start character index of the rhyme unit suffix.

    Parameters
    ----------
    word : str
        The surface word string (lowercase).
    phonemes : list of str
        Full ARPAbet phoneme sequence for the word.
    rhyme_unit : list of str
        The trailing sub-sequence of phonemes that forms the rhyme unit.

    Returns
    -------
    tuple of (int, int)
        (start_char, end_char) — slice indices such that
        word[start_char:end_char] is the rhyming suffix.
        Returns (0, len(word)) as a safe fallback if alignment fails.
    """

    if not phonemes or not rhyme_unit:
        return (0, len(word))

    # Number of prefix phonemes (those NOT in the rhyme unit)
    n_prefix = len(phonemes) - len(rhyme_unit)

    if n_prefix <= 0:
        return (0, len(word))

    # --- Greedy phoneme-to-grapheme aligner ---
    # Map each ARPAbet symbol to the set of grapheme strings it commonly
    # represents, ordered longest-first so greedy matching prefers
    # multi-character spellings.
    P2G = {
        # Vowels (stress digits stripped before lookup)
        "AA": ["a", "ah", "o"],
        "AE": ["a"],
        "AH": ["u", "a", "o", "uh", "e"],
        "AO": ["o", "au", "aw", "ough"],
        "AW": ["ow", "ou", "ough"],
        "AY": ["i", "y", "igh", "ie", "ai", "ay"],
        "EH": ["e", "ea", "a"],
        "ER": ["er", "ur", "ir", "ear", "or", "re"],
        "EY": ["a", "ay", "ai", "ea", "e"],
        "IH": ["i", "e", "y"],
        "IY": ["ee", "ea", "e", "ie", "i", "y"],
        "OW": ["o", "ow", "oa", "ough"],
        "OY": ["oy", "oi"],
        "UH": ["u", "oo", "o"],
        "UW": ["oo", "u", "ew", "ue", "ou"],
        # Consonants
        "B":  ["b", "bb"],
        "CH": ["ch", "tch", "t"],
        "D":  ["d", "dd", "ed"],
        "DH": ["th"],
        "F":  ["f", "ff", "ph"],
        "G":  ["g", "gg"],
        "HH": ["h"],
        "JH": ["j", "g", "dg"],
        "K":  ["k", "c", "ck", "ch", "q"],
        "L":  ["l", "ll"],
        "M":  ["m", "mm"],
        "N":  ["n", "nn", "kn"],
        "NG": ["ng", "n"],
        "P":  ["p", "pp"],
        "R":  ["r", "rr", "wr"],
        "S":  ["s", "ss", "c"],
        "SH": ["sh", "s", "ti", "ci"],
        "T":  ["t", "tt", "ed"],
        "TH": ["th"],
        "V":  ["v", "f"],
        "W":  ["w", "wh"],
        "Y":  ["y"],
        "Z":  ["z", "s", "zz"],
        "ZH": ["s", "z", "g"],
    }

    def strip_stress(p):
        return p.rstrip("012")

    word_lower = word.lower()
    pos = 0  # current character position in word_lower

    for i, phoneme in enumerate(phonemes):
        if i == n_prefix:
            # pos now points to the start of the rhyme unit
            return (pos, len(word_lower))

        key = strip_stress(phoneme)
        candidates = P2G.get(key, [])

        matched = False
        for grapheme in sorted(candidates, key=len, reverse=True):
            if word_lower[pos:].startswith(grapheme):
                pos += len(grapheme)
                matched = True
                break

        if not matched:
            # Consume one character and move on — silent letters, edge cases
            if pos < len(word_lower):
                pos += 1

    # Fallback: alignment ran out — return whole word
    return (0, len(word_lower))


# ---------------------------------------------------------------------------
# IPA-aware grapheme aligner (Milestone 13)
# ---------------------------------------------------------------------------
# find_rhyme_suffix_span above is ARPAbet-keyed; on english_mfa IPA input it
# silently falls back to one-char-per-phoneme. The syllable engine needs
# accurate *per-syllable* character spans (a multi-syllable word wears several
# colours), so this aligner maps each english_mfa IPA symbol to the grapheme(s)
# it commonly spells. Keys cover the 55-symbol inventory observed in the verse
# (stress-mark-free; english_mfa emits no stress digits). Each phoneme greedily
# consumes the longest matching grapheme run; the cumulative character positions
# become syllable boundaries. As with the ARPAbet aligner, the goal is good
# *boundaries*, not perfect spelling — unmatched sounds advance one character so
# alignment always makes progress and never crashes.
_IPA_TO_GRAPHEMES = {
    # --- vowels & diphthongs ---
    "a":  ["a", "o", "u", "e"],
    "aj": ["igh", "uy", "ie", "ai", "ay", "i", "y"],
    "aw": ["ough", "ow", "ou"],
    "e":  ["eigh", "ea", "ay", "ai", "ey", "ei", "a"],
    "eː": ["ai", "ay", "ei", "a"],
    "i":  ["ee", "ea", "ie", "i", "e", "y"],
    "o":  ["oa", "ow", "o"],
    "ow": ["oa", "ow", "o"],
    "oː": ["oa", "ough", "ow", "o"],
    "æ":  ["a"],
    "ɐ":  ["u", "o", "a"],
    "ɑ":  ["a", "o", "y"],
    "ɒ":  ["augh", "au", "ou", "a", "o"],
    "ə":  ["er", "ar", "ah", "re", "ou", "a", "e", "o", "u"],
    "əw": ["oe", "ough", "ou", "ow", "oa", "o"],
    "ɛ":  ["ea", "e", "a"],
    "ɛː": ["ere", "air", "are", "ai", "e"],
    "ɪ":  ["i", "e", "y", "a"],
    "ʉː": ["ew", "oo", "wo", "u", "o"],
    "ʊ":  ["oo", "ou", "u"],
    # --- consonants ---
    "b":  ["bb", "b"],
    "c":  ["ck", "c", "k"],
    "d":  ["dd", "d"],
    "dʒ": ["dg", "ge", "j", "g"],
    "d̪": ["th", "dd", "d"],
    "f":  ["ff", "ph", "f"],
    "fʲ": ["ff", "f"],
    "h":  ["h"],
    "j":  ["y"],
    "k":  ["ck", "ch", "k", "c", "q"],
    "l":  ["ll", "l"],
    "m":  ["mm", "m"],
    "mʲ": ["mm", "m"],
    "n":  ["kn", "nn", "n"],
    "p":  ["pp", "p"],
    "s":  ["ss", "s", "c"],
    "t":  ["tt", "t"],
    "tʃ": ["tch", "ch", "t"],
    "tʲ": ["tt", "t"],
    "t̪": ["th", "tt", "t"],
    "v":  ["v"],
    "z":  ["zz", "s", "z"],
    "ç":  ["h"],
    "ð":  ["th"],
    "ŋ":  ["ng", "n"],
    "ɖ":  ["dd", "d"],
    "ɟ":  ["g", "gu"],
    "ɫ":  ["ll", "l"],
    "ɹ":  ["wr", "rr", "r"],
    "ʃ":  ["sh", "ti", "ci", "ss", "s"],
    "ʈ":  ["tt", "t"],
    "ʋ":  ["wh", "w", "v"],
    "ʎ":  ["ll", "l"],
    "θ":  ["th"],
    # "spn" (MFA's spoken-noise token) is intentionally absent: it has no
    # grapheme, so it falls through to the one-char fallback.
}


def align_phonemes_to_chars(word, phonemes):
    """Map a word's phonemes to character boundary positions (IPA-aware).

    Walks the word string left-to-right, letting each phoneme greedily consume
    the longest grapheme it commonly spells (see _IPA_TO_GRAPHEMES). Returns the
    cumulative character offset *before* each phoneme plus a final offset at the
    word end, so boundaries[k] is where phoneme k starts and boundaries[k+1]
    where it ends.

    Parameters
    ----------
    word : str
        The surface word string.
    phonemes : list of str
        The word's full IPA phoneme list (english_mfa tokens).

    Returns
    -------
    list of int
        len(phonemes) + 1 monotonic character offsets; first is 0, last is
        len(word). A safe, always-progressing fallback handles silent letters
        and unrecognised symbols.
    """
    word_lower = word.lower()
    n = len(phonemes)
    boundaries = [0] * (n + 1)

    pos = 0
    for i, phoneme in enumerate(phonemes):
        boundaries[i] = pos
        key = phoneme.lstrip("ˈˌ")
        candidates = _IPA_TO_GRAPHEMES.get(key, [])

        matched = False
        for grapheme in sorted(candidates, key=len, reverse=True):
            if word_lower[pos:].startswith(grapheme):
                pos += len(grapheme)
                matched = True
                break

        # Unknown symbol or no spelling matched here: consume one character so
        # alignment keeps moving (silent letters, MFA noise tokens, edge cases).
        if not matched and pos < len(word_lower):
            pos += 1

    boundaries[n] = len(word_lower)

    # Guard monotonicity: a late phoneme that ran past the word end must not
    # produce a boundary beyond len(word) (clamp), and boundaries never go back.
    for i in range(1, n + 1):
        if boundaries[i] < boundaries[i - 1]:
            boundaries[i] = boundaries[i - 1]
        if boundaries[i] > len(word_lower):
            boundaries[i] = len(word_lower)

    return boundaries


def find_syllable_spans(word, word_phonemes, syllable_ranges):
    """Return one (start_char, end_char) span per syllable within `word`.

    Parameters
    ----------
    word : str
        The surface word string.
    word_phonemes : list of str
        The word's full IPA phoneme list.
    syllable_ranges : list of (int, int)
        Each syllable's [phoneme_start, phoneme_end) range within word_phonemes
        (the phoneme_start / phoneme_end fields from extract_syllable_candidates).

    Returns
    -------
    list of (int, int)
        Character spans, one per syllable, tiling the word with no gaps. The
        last span always reaches len(word) so trailing silent letters (e.g. the
        final "e" in *give*) stay attached to the last syllable.
    """
    boundaries = align_phonemes_to_chars(word, word_phonemes)
    n = len(word_phonemes)
    spans = []
    for start_ph, end_ph in syllable_ranges:
        start_ph = max(0, min(start_ph, n))
        end_ph = max(start_ph, min(end_ph, n))
        spans.append((boundaries[start_ph], boundaries[end_ph]))
    return spans


def filter_clusters(clusters, rhyme_candidates, min_phonemes=2):
    """
    Filter clusters to only those worth rendering.

    A cluster passes based on its "deep" members — those whose rhyme unit has
    >= min_phonemes sounds. Shallow members (e.g. the bare vowel "I", a single
    sound) stay in the cluster for rendering but neither count toward nor block
    the gate. A cluster passes if either:
          (a) it has >= 2 deep members appearing in >= 2 different lines, OR
          (b) it has >= 3 deep members total

    Clusters with fewer than 2 deep members never pass (this also blocks
    singletons and all-shallow clusters).

    Parameters
    ----------
    clusters : dict
        Mapping of word (str) -> cluster label (str), from cluster_rhymes().
    rhyme_candidates : list of dict
        Output of extract_rhyme_candidates(). Each dict has 'end_word',
        'rhyme_unit', and 'line_index'.
    min_phonemes : int
        Minimum rhyme unit length required for a cluster to render. Default 2.

    Returns
    -------
    set of str
        The cluster labels that pass the quality filter.
    """

    # Build per-label metadata. A member is "deep" if its rhyme unit has at
    # least min_phonemes sounds. Only deep members count toward the quality
    # gate; shallow members (e.g. the bare vowel "I") still belong to the
    # cluster for rendering but do not block an otherwise-strong cluster.
    label_to_members = {}        # label -> list of words (all members)
    label_to_deep_words = {}     # label -> set of deep member words
    label_to_deep_lines = {}     # label -> set of line indices with a deep member

    for entry in rhyme_candidates:
        word = entry["end_word"]
        label = clusters.get(word)
        if label is None:
            continue

        ru_len = len(entry["rhyme_unit"])

        if label not in label_to_members:
            label_to_members[label] = []
            label_to_deep_words[label] = set()
            label_to_deep_lines[label] = set()

        if word not in label_to_members[label]:
            label_to_members[label].append(word)

        if ru_len >= min_phonemes:
            label_to_deep_words[label].add(word)
            label_to_deep_lines[label].add(entry["line_index"])

    passing = set()

    for label in label_to_members:
        deep_count = len(label_to_deep_words[label])
        deep_line_count = len(label_to_deep_lines[label])

        spread_ok = (deep_count >= 2 and deep_line_count >= 2)
        density_ok = (deep_count >= 3)

        if spread_ok or density_ok:
            passing.add(label)

    return passing


def generate_rhyme_html(
    rhyme_candidates,
    clusters,
    output_file="generated_html/rhyme_visualization.html",
    detection_mode="end_only",
    min_phonemes=2,
    debug=False
):
    """
    Generate a colour-coded HTML file visualising rhyme clusters.

    Only clusters that pass the quality filter are rendered. Within each
    rendered word, only the rhyming suffix is highlighted (not the whole word).

    Parameters
    ----------
    rhyme_candidates : list of dict
        Output of extract_rhyme_candidates().
    clusters : dict
        Mapping of word (str) -> cluster label (str).
    output_file : str
        Path to write the HTML file to.
    detection_mode : str
        "end_only"  — one candidate per line (end word only).
        "full_line" — all candidate words highlighted inline.
    min_phonemes : int
        Minimum shared rhyme unit depth for a cluster to be rendered.
        Default 2.
    debug : bool
        If True, print which clusters passed and failed the filter.
    """

    # --- Step 1: filter clusters ---
    passing_labels = filter_clusters(
        clusters, rhyme_candidates, min_phonemes=min_phonemes
    )

    if debug:
        all_labels = set(clusters.values())
        blocked = all_labels - passing_labels
        print(f"[HTML] Passing clusters: {sorted(passing_labels)}")
        print(f"[HTML] Blocked clusters: {sorted(blocked)}")

    # --- Step 2: build per-candidate lookup for phonemes and rhyme unit ---
    # word -> (phonemes, rhyme_unit) — last entry wins if word appears twice
    word_to_units = {}
    for entry in rhyme_candidates:
        word_to_units[entry["end_word"]] = (
            entry["phonemes"],
            entry["rhyme_unit"]
        )

    # --- Step 3: colours ---
    colors = [
        "#ffcccc", "#cce5ff", "#ccffcc",
        "#ffe6cc", "#ffffcc", "#e6ccff",
        "#ffd6e7", "#ccfff5", "#e6f2ff"
    ]
    cluster_labels_sorted = sorted(passing_labels)
    cluster_colors = {
        label: colors[i % len(colors)]
        for i, label in enumerate(cluster_labels_sorted)
    }

    css_rules = [
        f".rhyme-{label} {{ background-color: {color}; border-radius: 3px; padding: 1px 2px; }}"
        for label, color in cluster_colors.items()
    ]
    css_block = "\n".join(css_rules)

    # --- Step 4: group candidates by line ---
    lines_dict = {}
    for entry in rhyme_candidates:
        line_index = entry["line_index"]
        if line_index not in lines_dict:
            lines_dict[line_index] = {
                "line_text": entry["line_text"],
                "candidates": []
            }
        lines_dict[line_index]["candidates"].append(entry)

    # --- Step 5: render each line ---
    html_lines = []

    for line_index in sorted(lines_dict.keys()):
        line_text = lines_dict[line_index]["line_text"]
        candidates = lines_dict[line_index]["candidates"]

        if detection_mode == "end_only":
            entry = candidates[0]
            word = entry["end_word"]
            label = clusters.get(word)

            if label and label in passing_labels:
                phonemes, rhyme_unit = word_to_units[word]
                start, end = find_rhyme_suffix_span(word, phonemes, rhyme_unit)
                prefix = word[:start]
                suffix = word[start:end]
                span = f'{prefix}<span class="rhyme-{label}">{suffix}</span>'
                rendered = line_text.rsplit(word, 1)[0] + span
            else:
                rendered = line_text

        elif detection_mode == "full_line":
            # Build word_index -> (label, entry) for candidates that pass
            index_to_entry = {}
            for entry in candidates:
                label = clusters.get(entry["end_word"])
                if label and label in passing_labels:
                    index_to_entry[entry["word_index"]] = (label, entry)

            words = line_text.split()
            rendered_words = []

            for word_index, word in enumerate(words):
                if word_index in index_to_entry:
                    label, entry = index_to_entry[word_index]
                    phonemes, rhyme_unit = word_to_units[entry["end_word"]]
                    start, end = find_rhyme_suffix_span(word, phonemes, rhyme_unit)
                    prefix = word[:start]
                    suffix = word[start:end]
                    rendered_words.append(
                        f'{prefix}<span class="rhyme-{label}">{suffix}</span>'
                    )
                else:
                    rendered_words.append(word)

            rendered = " ".join(rendered_words)

        html_lines.append(rendered)

    # --- Step 6: assemble and write HTML ---
    html_content = "<br>\n".join(html_lines)

    full_html = f"""<html>
<head>
<title>Verse DNA Rhyme Visualization</title>
<style>
body {{ font-family: Arial; font-size: 18px; line-height: 1.8; }}
{css_block}
</style>
</head>
<body>
{html_content}
</body>
</html>"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_html)

    print("HTML file generated:", output_file)


# ---------------------------------------------------------------------------
# Per-syllable rendering (Milestone 13)
# ---------------------------------------------------------------------------

def filter_syllable_clusters(labels, syllable_units, min_phonemes=2):
    """Pick the syllable clusters worth colouring (render-time quality gate).

    Mirrors filter_clusters but counts *syllable* units instead of words. A
    syllable is a "deep" member if it has at least min_phonemes sounds, so a
    bare-vowel syllable (e.g. "I" = aj) stays in its cluster for rendering but
    neither props up nor blocks the gate. A cluster passes if it has either
    >= 2 deep members across >= 2 lines, or >= 3 deep members total.

    Parameters
    ----------
    labels : dict
        unit_id (str) -> cluster label (str), from cluster_rhymes on the
        syllable matrix.
    syllable_units : list of dict
        Output of extract_syllable_candidates().
    min_phonemes : int
        Minimum syllable depth to count as a deep member. Default 2.

    Returns
    -------
    set of str
        The cluster labels that pass.
    """
    label_to_deep_units = {}
    label_to_deep_lines = {}

    for u in syllable_units:
        label = labels.get(u["unit_id"])
        if label is None:
            continue
        label_to_deep_units.setdefault(label, set())
        label_to_deep_lines.setdefault(label, set())
        if len(u["phonemes"]) >= min_phonemes:
            label_to_deep_units[label].add(u["unit_id"])
            label_to_deep_lines[label].add(u["line_index"])

    passing = set()
    for label in label_to_deep_units:
        deep = len(label_to_deep_units[label])
        lines = len(label_to_deep_lines[label])
        if (deep >= 2 and lines >= 2) or deep >= 3:
            passing.add(label)
    return passing


def generate_syllable_html(
    syllable_units,
    labels,
    output_file="generated_html/syllable_visualization.html",
    min_phonemes=2,
    debug=False,
):
    """Render the lyrics with each SYLLABLE coloured by its cluster (M13).

    Unlike generate_rhyme_html (one colour per word), a multi-syllable word can
    wear several colours — one per syllable's cluster — which is the literal
    "Verse DNA" texture. Only clusters that pass filter_syllable_clusters are
    coloured; every other syllable renders as plain text. The per-syllable
    character spans come from the IPA-aware aligner (find_syllable_spans).

    Parameters
    ----------
    syllable_units : list of dict
        Output of extract_syllable_candidates().
    labels : dict
        unit_id (str) -> cluster label (str).
    output_file : str
        Path to write the HTML file to.
    min_phonemes : int
        Minimum syllable depth for a cluster to colour. Default 2.
    debug : bool
        If True, print which clusters passed and failed the filter.

    Returns
    -------
    str
        The full HTML document written to output_file (also returned so callers
        and tests can inspect it without reading the file back).
    """
    passing_labels = filter_syllable_clusters(labels, syllable_units, min_phonemes)

    if debug:
        all_labels = set(labels.values())
        blocked = all_labels - passing_labels
        print(f"[SYL HTML] Passing clusters: {sorted(passing_labels)}")
        print(f"[SYL HTML] Blocked clusters: {sorted(blocked)}")

    # --- colours ---
    colors = [
        "#ffcccc", "#cce5ff", "#ccffcc",
        "#ffe6cc", "#ffffcc", "#e6ccff",
        "#ffd6e7", "#ccfff5", "#e6f2ff",
    ]
    sorted_labels = sorted(passing_labels)
    cluster_colors = {
        label: colors[i % len(colors)]
        for i, label in enumerate(sorted_labels)
    }
    css_rules = [
        f".syl-{label} {{ background-color: {color}; border-radius: 3px; padding: 1px 2px; }}"
        for label, color in cluster_colors.items()
    ]
    css_block = "\n".join(css_rules)

    # --- group syllable units by line, then by word position within the line ---
    lines_dict = {}
    for u in syllable_units:
        line_index = u["line_index"]
        slot = lines_dict.setdefault(
            line_index, {"line_text": u["line_text"], "words": {}}
        )
        slot["words"].setdefault(u["word_index"], []).append(u)

    # --- render each line ---
    html_lines = []
    for line_index in sorted(lines_dict.keys()):
        slot = lines_dict[line_index]
        words = slot["line_text"].split()
        rendered_words = []

        for word_index, word in enumerate(words):
            units = slot["words"].get(word_index)
            if not units:
                rendered_words.append(word)
                continue

            units = sorted(units, key=lambda u: u["syllable_index"])
            word_phonemes = units[0]["word_phonemes"]
            ranges = [(u["phoneme_start"], u["phoneme_end"]) for u in units]
            spans = find_syllable_spans(word, word_phonemes, ranges)

            pieces = []
            for u, (start, end) in zip(units, spans):
                piece = word[start:end]
                label = labels.get(u["unit_id"])
                if label in passing_labels:
                    pieces.append(f'<span class="syl-{label}">{piece}</span>')
                else:
                    pieces.append(piece)
            rendered_words.append("".join(pieces))

        html_lines.append(" ".join(rendered_words))

    html_content = "<br>\n".join(html_lines)

    full_html = f"""<html>
<head>
<title>Verse DNA Syllable Visualization</title>
<style>
body {{ font-family: Arial; font-size: 18px; line-height: 1.8; }}
{css_block}
</style>
</head>
<body>
{html_content}
</body>
</html>"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_html)

    print("Syllable HTML file generated:", output_file)
    return full_html
