"""scope_guard.py - Deterministic guard to ensure edits stayed inside target section.

Compares before/after markdown files and fails if text outside target section changed.
"""
from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path

from context_slicer import slice_file


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Arquivo inexistente: {path}") from exc


def _prefix_suffix(text: str, start: int, end: int) -> tuple[str, str]:
    lines = text.splitlines(keepends=True)
    return ("".join(lines[:start]), "".join(lines[end:]))


def _sample_diff(a: str, b: str, max_lines: int = 30) -> list[str]:
    diff = list(difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm=""))
    return diff[:max_lines]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate no collateral changes outside target section.")
    parser.add_argument("--before", required=True, help="Path to file before patch.")
    parser.add_argument("--after", required=True, help="Path to file after patch.")
    parser.add_argument("--section", required=True, help="Target section title/number.")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)

    before_path = Path(args.before)
    after_path = Path(args.after)

    before_text = _read(before_path)
    _ = _read(after_path)

    before_slice = slice_file(str(before_path), args.section)
    after_slice = slice_file(str(after_path), args.section)

    before_prefix, before_suffix = _prefix_suffix(before_text, before_slice.start, before_slice.end)
    after_text = _read(after_path)
    after_prefix, after_suffix = _prefix_suffix(after_text, after_slice.start, after_slice.end)

    prefix_changed = before_prefix != after_prefix
    suffix_changed = before_suffix != after_suffix
    only_target_changed = not (prefix_changed or suffix_changed)

    report = {
        "before": str(before_path),
        "after": str(after_path),
        "section": args.section,
        "only_target_section_changed": only_target_changed,
        "prefix_changed": prefix_changed,
        "suffix_changed": suffix_changed,
        "prefix_diff_sample": _sample_diff(before_prefix, after_prefix) if prefix_changed else [],
        "suffix_diff_sample": _sample_diff(before_suffix, after_suffix) if suffix_changed else [],
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.strict and not only_target_changed:
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, LookupError, ValueError) as exc:
        print(f"erro: {exc}")
        raise SystemExit(1)
