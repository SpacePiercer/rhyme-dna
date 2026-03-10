def generate_rhyme_html(rhyme_candidates, clusters, output_file="generated_html/rhyme_visualization.html"):

    colors = [
        "#ffcccc", "#cce5ff", "#ccffcc",
        "#ffe6cc", "#ffffcc", "#e6ccff",
        "#ffd6e7", "#ccfff5", "#e6f2ff"
    ]

    # assign a color to each cluster label
    cluster_labels = sorted(set(clusters.values()))
    cluster_colors = {}

    for i, label in enumerate(cluster_labels):
        cluster_colors[label] = colors[i % len(colors)]

    # generate CSS classes
    css_rules = []
    for label, color in cluster_colors.items():
        css_rules.append(f".rhyme-{label} {{ background-color: {color}; padding:2px; }}")

    css_block = "\n".join(css_rules)

    html_lines = []

    for entry in rhyme_candidates:

        line = entry["line_text"]
        end_word = entry["end_word"]
        label = clusters[end_word]

        highlighted_word = f'<span class="rhyme-{label}">{end_word}</span>'

        highlighted_line = line.rsplit(end_word, 1)[0] + highlighted_word

        html_lines.append(highlighted_line)

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