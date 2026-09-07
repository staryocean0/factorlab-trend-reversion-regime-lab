"""Public-seed publication boundary: no literature PDFs or bundled archives."""

from pathlib import Path

IGNORED = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache", "dist"}
FORBIDDEN = {".pdf", ".zip", ".7z", ".rar", ".tar", ".gz"}


def public_files(root):
    root = Path(root).resolve()
    result = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(p in IGNORED or p.endswith(".egg-info") for p in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError(f"symlink forbidden in seed: {relative}")
        if not path.is_file():
            continue
        if path.name == ".env" or path.suffix.lower() in FORBIDDEN:
            raise ValueError(f"nonpublic attachment forbidden: {relative}")
        with path.open("rb") as f:
            if f.read(5) == b"%PDF-":
                raise ValueError(f"disguised PDF forbidden: {relative}")
        if path.stat().st_size >= 100 * 1024 * 1024:
            raise ValueError(f"split large file before publishing: {relative}")
        result.append(path)
    return result
