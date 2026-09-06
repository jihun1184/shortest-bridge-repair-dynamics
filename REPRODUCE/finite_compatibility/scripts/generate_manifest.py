"""Generate MANIFEST.json from the current distributable package files."""
from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "MANIFEST.json"
EXCLUDED_PARTS = {".git", "__pycache__", "outputs"}
EXCLUDED_FILES = {"MANIFEST.json"}


def digest(path: Path) -> str:
    """Return a streaming SHA-256 digest without loading large files at once."""
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def distributable_files():
    """Yield stable relative paths while excluding runtime/package metadata."""
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if not path.is_file():
            continue
        if path.name in EXCLUDED_FILES or any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        yield relative


def build_manifest() -> dict:
    files = {}
    for relative in sorted(distributable_files(), key=lambda p: p.as_posix()):
        path = ROOT / relative
        files[relative.as_posix()] = {
            "sha256": digest(path),
            "size_bytes": path.stat().st_size,
        }
    return {
        "package": "Bounded Compatibility Depth reproducibility package",
        "generated": date.today().isoformat(),
        "manifest_scope": "all distributed files except MANIFEST.json itself",
        "files": files,
        "claim_map": {
            "Table 1 / Proposition 2": "scripts/walk_counts.py",
            "Table 2 / Corollary 7": "scripts/depth_histogram.py",
            "Lemmas 3 and 4": "scripts/bridge_lemma.py",
            "Table 3, L=3 and L=5": "scripts/disjointness_L3_L5.py",
            "Table 3, L=4": "scripts/disjointness_L4.py",
            "Section 6.1 / Figure 4": "scripts/section6_1_split.py",
        },
    }


def main() -> None:
    try:
        manifest = build_manifest()
        with OUTPUT.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(manifest, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
    except OSError as exc:
        raise SystemExit(f"Could not write {OUTPUT}: {exc}") from exc
    print(f"Wrote {OUTPUT} with {len(manifest['files'])} file records")


if __name__ == "__main__":
    main()
