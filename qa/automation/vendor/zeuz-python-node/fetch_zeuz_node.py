#!/usr/bin/env python
"""Fetch or copy the open-source ZeuZ Node runtime for local test adapters."""

from __future__ import annotations

import argparse
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path


DEFAULT_URL = "https://github.com/AutomationSolutionz/Zeuz_Python_Node/archive/refs/heads/dev.zip"
DEFAULT_DEST = Path(__file__).resolve().parent / "runtime"


def _copy_tree(src: Path, dest: Path, force: bool) -> None:
    if dest.exists():
        if not force:
            raise SystemExit(f"Destination already exists: {dest}. Use --force to replace it.")
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dest)


def _download_zip(url: str, zip_path: Path) -> None:
    with urllib.request.urlopen(url, timeout=120) as response:
        zip_path.write_bytes(response.read())


def _install_from_zip(url: str, dest: Path, force: bool) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        zip_path = tmp_path / "zeuz_node.zip"
        _download_zip(url, zip_path)
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(extract_dir)
        roots = [p for p in extract_dir.iterdir() if p.is_dir()]
        if len(roots) != 1:
            raise SystemExit("Could not identify extracted ZeuZ Node root folder.")
        _copy_tree(roots[0], dest, force)


def main() -> None:
    parser = argparse.ArgumentParser(description="Install ZeuZ Node runtime for ZKME local adapters.")
    parser.add_argument("--source", help="Local Zeuz_Python_Node checkout to copy instead of downloading.")
    parser.add_argument("--url", default=DEFAULT_URL, help="ZeuZ Node zip URL to download.")
    parser.add_argument("--dest", default=str(DEFAULT_DEST), help="Destination runtime directory.")
    parser.add_argument("--force", action="store_true", help="Replace destination if it already exists.")
    args = parser.parse_args()

    dest = Path(args.dest).resolve()
    if args.source:
        source = Path(args.source).resolve()
        if not source.exists():
            raise SystemExit(f"Source does not exist: {source}")
        _copy_tree(source, dest, args.force)
    else:
        _install_from_zip(args.url, dest, args.force)

    print(f"Installed ZeuZ Node runtime at {dest}")


if __name__ == "__main__":
    main()
