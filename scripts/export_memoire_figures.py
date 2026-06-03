from pathlib import Path

from html import escape
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg


def main() -> None:
    source_dir = Path("docs/memoire/figures")
    output_dir = Path("docs/memoire/figures_exports")
    page_dir = output_dir / "_html"
    output_dir.mkdir(parents=True, exist_ok=True)
    page_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for svg_path in sorted(source_dir.glob("*.svg")):
        base = svg_path.stem
        drawing = svg2rlg(str(svg_path))
        renderPDF.drawToFile(drawing, str(output_dir / f"{base}.pdf"))
        svg_uri = svg_path.resolve().as_uri()
        html = f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <title>{escape(base)}</title>
  <style>
    html, body {{
      margin: 0;
      width: 1600px;
      height: 1000px;
      background: #ffffff;
      display: grid;
      place-items: center;
    }}
    img {{
      max-width: 1520px;
      max-height: 940px;
    }}
  </style>
</head>
<body>
  <img src="{svg_uri}" alt="{escape(base)}" />
</body>
</html>
"""
        (page_dir / f"{base}.html").write_text(html, encoding="utf-8")
        count += 1

    print(f"Figures exportees: {count}")
    print(f"Dossier: {output_dir}")


if __name__ == "__main__":
    main()
