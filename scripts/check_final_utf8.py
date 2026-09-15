from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path("ARIEL_LOGMINER_MEMOIRE_FINAL")
EXTENSIONS = {".tex", ".bib", ".md", ".csv", ".json"}
PATTERNS = ["Ã©", "Ã¨", "Ã", "Ã§", "â€™", "â€œ", "â€", "ï¿½", "�"]

for path in ROOT.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
        continue
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        print(f"INVALID_UTF8\t{path}\t{exc}")
        continue
    hits = sorted({pattern for pattern in PATTERNS if pattern in text})
    if hits:
        print(f"MOJIBAKE\t{path}\t{hits}")

print("UTF8_SCAN_COMPLETE")
