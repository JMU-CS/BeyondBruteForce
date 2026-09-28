#!/usr/bin/env python3
"""Verify course-owned files against the local SHA-256 manifest.

The local manifest is for catching accidental edits. Gradescope should use its
own canonical copy of the expected hashes rather than trusting this submitted
manifest.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
from pathlib import Path

IGNORED_PARTS = {"__pycache__", ".DS_Store"}
IGNORED_PATTERNS = ("*.pyc", "*.pyo")


def _ignored(path: Path) -> bool:
    if any(part in IGNORED_PARTS for part in path.parts):
        return True
    return any(fnmatch.fnmatch(path.name, pat) for pat in IGNORED_PATTERNS)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as infile:
        for chunk in iter(lambda: infile.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(repo_root: Path) -> dict:
    path = repo_root / "tools" / "course_file_manifest.json"
    return json.loads(path.read_text(encoding="utf-8"))


def verify_course_files(repo_root: Path) -> dict[str, list[str]]:
    manifest = load_manifest(repo_root)
    expected = manifest["files"]
    missing: list[str] = []
    modified: list[str] = []
    unexpected: list[str] = []

    for rel, expected_hash in expected.items():
        path = repo_root / rel
        if not path.is_file():
            missing.append(rel)
            continue
        if sha256_file(path) != expected_hash:
            modified.append(rel)

    expected_paths = set(expected)
    for root_rel in manifest.get("strict_roots", []):
        root = repo_root / root_rel
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(repo_root)
            if _ignored(rel):
                continue
            rel_s = rel.as_posix()
            if rel_s not in expected_paths:
                unexpected.append(rel_s)

    return {
        "missing": sorted(missing),
        "modified": sorted(modified),
        "unexpected": sorted(unexpected),
    }


def is_clean(result: dict[str, list[str]]) -> bool:
    return not any(result.values())
