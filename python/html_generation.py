def generate_rhyme_html(
    rhyme_candidates,
    clusters,
    output_file="generated_html/rhyme_visualization.html",
    detection_mode="end_only"
):
    """
    Generate a colour-coded HTML file visualising rhyme clusters.

    Parameters
    ----------
    rhyme_candidates : list of dict
        Output of extract_rhyme_candidates().
    clusters : dict
        Mapping of word (str) → cluster label (str).
    output_file : str
        Path to write the HTML file to.
    detection_mode : str
        "end_only"  — one highlighted word per line (end word only).
        "full_line" — all candidate words highlighted inline.
    """

    colors = [
        "#ffcccc", "#cce5ff", "#ccffcc",
        "#ffe6cc", "#ffffcc", "#e6ccff",
        "#ffd6e7", "#ccfff5", "#e6f2ff"
    ]

    cluster_labels = sorted(set(clusters.values()))
    cluster_colors = {}

    for i, label in enumerate(cluster_labels):
        cluster_colors[label] = colors[i % len(colors)]

    css_rules = []
    for label, color in cluster_colors.items():
        css_rules.append(f".rhyme-{label} {{ background-color: {color}; padding:2px; }}")

    css_block = "\n".join(css_rules)

    # Group candidates by line_index, preserving line text
    lines_dict = {}

    for entry in rhyme_candidates:
        line_index = entry["line_index"]
        if line_index not in lines_dict:
            lines_dict[line_index] = {
                "line_text": entry["line_text"],
                "candidates": []
            }
        lines_dict[line_index]["candidates"].append(entry)

    html_lines = []

    for line_index in sorted(lines_dict.keys()):

        line_text = lines_dict[line_index]["line_text"]
        candidates = lines_dict[line_index]["candidates"]

        if detection_mode == "end_only":

            # Original behaviour — highlight the single end word
            entry = candidates[0]
            end_word = entry["end_word"]
            label = clusters.get(end_word)

            if label:
                highlighted_word = f'<span class="rhyme-{label}">{end_word}</span>'
                rendered = line_text.rsplit(end_word, 1)[0] + highlighted_word
            else:
                rendered = line_text

        elif detection_mode == "full_line":

            # Build a lookup: word_index → cluster label
            index_to_label = {}
            for entry in candidates:
                label = clusters.get(entry["end_word"])
                if label:
                    index_to_label[entry["word_index"]] = label

            # Walk words left to right, wrapping candidates in spans
            words = line_text.split()
            rendered_words = []

            for word_index, word in enumerate(words):
                if word_index in index_to_label:
                    label = index_to_label[word_index]
                    rendered_words.append(
                        f'<span class="rhyme-{label}">{word}</span>'
                    )
                else:
                    rendered_words.append(word)

            rendered = " ".join(rendered_words)

        html_lines.append(rendered)

    html_content = "<br>\n".join(html_lines)

    full_html = f"""
    <html>
    <head>
    <title>Verse DNA Rhyme Visualization</title>
    <style>
    body {{ font-family: Arial; font-size: 18px; }}
    {css_block}
    </style>
    </head>
    <body>
    {html_content}
    </body>
    </html>
    """

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_html)

    print("HTML file generated:", output_file)