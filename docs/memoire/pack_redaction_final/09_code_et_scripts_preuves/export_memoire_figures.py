import shutil
import subprocess
from pathlib import Path

from html import escape


def find_edge() -> Path | None:
    candidates = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\EdgeCore\msedge.exe"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def export_pdf(svg_path: Path, output_path: Path) -> bool:
    try:
        from reportlab.graphics import renderPDF
        from svglib.svglib import svg2rlg
    except ModuleNotFoundError:
        return False

    drawing = svg2rlg(str(svg_path))
    renderPDF.drawToFile(drawing, str(output_path))
    return True


def export_png(edge: Path, html_path: Path, output_path: Path, user_data_dir: Path) -> bool:
    user_data_dir.mkdir(parents=True, exist_ok=True)
    command = [
        str(edge),
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        "--no-first-run",
        "--disable-crash-reporter",
        "--disable-features=RendererCodeIntegrity",
        f"--user-data-dir={user_data_dir.resolve()}",
        "--window-size=1600,1000",
        f"--screenshot={output_path.resolve()}",
        html_path.resolve().as_uri(),
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
    except subprocess.SubprocessError as exc:
        print(f"PNG non exporte pour {html_path.stem}: {exc}")
        return False
    return output_path.exists() and output_path.stat().st_size > 0


def main() -> None:
    source_dir = Path("docs/memoire/figures")
    output_dir = Path("docs/memoire/figures_exports")
    page_dir = output_dir / "_html"
    user_data_dir = output_dir / "_edge_user_data"
    output_dir.mkdir(parents=True, exist_ok=True)
    page_dir.mkdir(parents=True, exist_ok=True)
    edge = find_edge()

    count = 0
    pdf_count = 0
    png_count = 0
    for svg_path in sorted(source_dir.glob("*.svg")):
        base = svg_path.stem
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
        html_path = page_dir / f"{base}.html"
        html_path.write_text(html, encoding="utf-8")
        if export_pdf(svg_path, output_dir / f"{base}.pdf"):
            pdf_count += 1
        if edge is not None:
            figure_user_data = user_data_dir / base
            if export_png(edge, html_path, output_dir / f"{base}.png", figure_user_data):
                png_count += 1
        count += 1

    if user_data_dir.exists():
        shutil.rmtree(user_data_dir, ignore_errors=True)

    print(f"Figures traitees: {count}")
    print(f"PDF exportes: {pdf_count}")
    print(f"PNG exportes: {png_count}")
    if edge is None:
        print("PNG non exportes: Microsoft Edge introuvable")
    if pdf_count < count:
        print("PDF non regeneres: dependances reportlab/svglib absentes")
    print(f"Dossier: {output_dir}")


if __name__ == "__main__":
    main()
