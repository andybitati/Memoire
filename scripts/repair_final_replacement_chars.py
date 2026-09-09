from pathlib import Path

ROOT = Path("ARIEL_LOGMINER_MEMOIRE_FINAL")
for path in ROOT.rglob("*"):
    if path.is_file() and path.suffix.lower() in {".tex", ".bib", ".md", ".csv", ".json"}:
        text = path.read_text(encoding="utf-8")
        if "�" in text:
            path.write_text(text.replace("�", "–"), encoding="utf-8", newline="")
            print(path)
