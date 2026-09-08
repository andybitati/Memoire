#!/usr/bin/env python3
"""Compare frozen local datasets with separately acquired public copies.

The verifier is intentionally independent from experimental runners.  It never
modifies either input and writes only a CSV evidence table.  Each comparison is
declared in a JSON list so the exact objects compared remain auditable.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


FIELDS = [
    "dataset",
    "local_file",
    "public_file",
    "local_sha256",
    "public_sha256",
    "hash_equal",
    "local_size",
    "public_size",
    "local_rows",
    "public_rows",
    "columns_equal",
    "sample_content_equal",
    "comparison_method",
    "status",
    "notes",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def line_count(path: Path) -> int:
    count = 0
    last = b""
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            count += chunk.count(b"\n")
            last = chunk[-1:] or last
    return count + (1 if path.stat().st_size and last != b"\n" else 0)


def header(path: Path, kind: str, encoding: str) -> list[str] | None:
    if kind != "csv":
        return None
    with path.open("r", encoding=encoding, errors="strict", newline="") as handle:
        return next(csv.reader(handle))


def sample_digest(path: Path, physical_lines: int, encoding: str) -> str:
    """Hash the first, middle and last logical lines after newline removal."""
    wanted = {0, max(0, physical_lines // 2), max(0, physical_lines - 1)}
    digest = hashlib.sha256()
    with path.open("r", encoding=encoding, errors="strict", newline=None) as handle:
        for index, line in enumerate(handle):
            if index in wanted:
                digest.update(str(index).encode("ascii"))
                digest.update(b"\0")
                digest.update(line.rstrip("\r\n").encode("utf-8"))
                digest.update(b"\0")
    return digest.hexdigest()


def semantic_digest(path: Path, encoding: str) -> str:
    """Hash Unicode text after BOM and newline normalization to LF."""
    digest = hashlib.sha256()
    with path.open("r", encoding=encoding, errors="strict", newline=None) as handle:
        first = True
        for line in handle:
            value = line.rstrip("\r\n")
            if first:
                value = value.lstrip("\ufeff")
                first = False
            digest.update(value.encode("utf-8"))
            digest.update(b"\n")
    return digest.hexdigest()


def bool_text(value: bool | None) -> str:
    if value is None:
        return "NOT_APPLICABLE"
    return "true" if value else "false"


def compare(spec: dict[str, Any], root: Path) -> dict[str, Any]:
    local = (root / spec["local_file"]).resolve()
    public = (root / spec["public_file"]).resolve()
    kind = spec.get("format", "text")
    encoding = spec.get("encoding", "utf-8-sig")
    notes = spec.get("notes", "")

    if not local.is_file() or not public.is_file():
        missing = [str(path) for path in (local, public) if not path.is_file()]
        return {
            **{field: "" for field in FIELDS},
            "dataset": spec["dataset"],
            "local_file": str(local),
            "public_file": str(public),
            "comparison_method": "input existence check",
            "status": "PUBLIC_LOCAL_COPY_MATCH_NOT_PROVEN",
            "notes": f"Missing comparison input(s): {'; '.join(missing)}. {notes}".strip(),
        }

    local_hash = sha256(local)
    public_hash = sha256(public)
    exact = local_hash == public_hash
    local_lines = line_count(local)
    public_lines = line_count(public)
    local_rows = max(0, local_lines - 1) if kind == "csv" else local_lines
    public_rows = max(0, public_lines - 1) if kind == "csv" else public_lines
    columns_equal: bool | None = None
    semantic = False

    try:
        if kind == "csv":
            columns_equal = header(local, kind, encoding) == header(public, kind, encoding)
        if exact:
            samples_equal = True
        else:
            samples_equal = sample_digest(local, local_lines, encoding) == sample_digest(public, public_lines, encoding)
            semantic = semantic_digest(local, encoding) == semantic_digest(public, encoding)
    except (UnicodeError, csv.Error) as exc:
        samples_equal = False
        notes = f"{notes} Text comparison error: {exc}".strip()

    if exact:
        status = "PUBLIC_LOCAL_COPY_EXACT_MATCH"
        method = "SHA-256 over equivalent raw files; size, row count and sampled content"
    elif semantic:
        status = "PUBLIC_LOCAL_COPY_SEMANTIC_MATCH"
        method = "full Unicode text hash after UTF-8 BOM and CRLF/LF normalization"
    elif local_rows == public_rows and columns_equal is not False and samples_equal:
        status = "PUBLIC_LOCAL_COPY_STRONGLY_MATCHED"
        method = "size/row/header comparison plus first-middle-last content samples"
    else:
        status = "PUBLIC_LOCAL_COPY_MATCH_NOT_PROVEN"
        method = "SHA-256, size, row/header and first-middle-last content comparison"

    return {
        "dataset": spec["dataset"],
        "local_file": spec["local_file"],
        "public_file": spec["public_file"],
        "local_sha256": local_hash,
        "public_sha256": public_hash,
        "hash_equal": bool_text(exact),
        "local_size": local.stat().st_size,
        "public_size": public.stat().st_size,
        "local_rows": local_rows,
        "public_rows": public_rows,
        "columns_equal": bool_text(columns_equal),
        "sample_content_equal": bool_text(samples_equal),
        "comparison_method": method,
        "status": status,
        "notes": notes,
    }


def load_specs(path: Path) -> Iterable[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Specification must be a JSON list")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True, help="JSON list of comparisons")
    parser.add_argument("--output", type=Path, required=True, help="Evidence CSV to replace")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Base for relative input paths")
    args = parser.parse_args()

    rows = [compare(spec, args.root) for spec in load_specs(args.spec)]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} comparison(s) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
