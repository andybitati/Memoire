"""Extrait le texte d'un PDF.

Usage:
    python scripts/extract_pdf.py docs/memoire/mon_memoire.pdf

Si aucun PDF n'est fourni, le script tente de prendre le premier PDF trouve
dans `docs/memoire`.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import PyPDF2


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PDF_DIR = ROOT / "docs" / "memoire"


def find_default_pdf() -> Path:
    """Retourne le premier PDF disponible dans docs/memoire."""

    pdfs = sorted(DEFAULT_PDF_DIR.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"Aucun PDF trouve dans {DEFAULT_PDF_DIR}")
    return pdfs[0]


def extract_text(pdf_path: Path) -> str:
    """Lit toutes les pages d'un PDF avec PyPDF2."""

    with pdf_path.open("rb") as file:
        reader = PyPDF2.PdfReader(file)
        pages = [(page.extract_text() or "") for page in reader.pages]
    return "\n".join(pages)


def main() -> int:
    parser = argparse.ArgumentParser(description="Extrait le texte d'un PDF.")
    parser.add_argument("pdf", nargs="?", type=Path, help="Chemin du PDF a lire")
    args = parser.parse_args()

    pdf_path = args.pdf or find_default_pdf()
    print(extract_text(pdf_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
