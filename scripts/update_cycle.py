"""update_cycle.py - Deterministic update loop for README section edits.

This script enforces a local-first update cycle:
1) slice current section (source of truth)
2) apply deterministic patch from prepared markdown
3) slice updated section and compare hashes
4) append a feedback event to a local JSONL history file

No LLM call is performed here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from context_slicer import slice_file
from patch_applier import apply_patch


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Arquivo inexistente: {path}") from exc


def _append_jsonl(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic section update with local feedback history."
    )
    parser.add_argument("--file", required=True, help="Markdown target (ex.: README.md).")
    parser.add_argument("--section", required=True, help="Section title/number (H2/H3+).")
    parser.add_argument("--new-content", required=True, help="Path to new section markdown.")
    parser.add_argument(
        "--history",
        default="scripts/.update-history.jsonl",
        help="JSONL history path for feedback loop.",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Disable .bak creation from patch_applier.",
    )
    args = parser.parse_args(argv)

    target_path = Path(args.file)
    new_content_path = Path(args.new_content)
    history_path = Path(args.history)

    before = slice_file(str(target_path), args.section)
    before_hash = _sha256(before.text)
    before_chars = len(before.text)

    new_content = _load_text(new_content_path)
    apply_patch(str(target_path), args.section, new_content, backup=not args.no_backup)

    after = slice_file(str(target_path), args.section)
    after_hash = _sha256(after.text)
    after_chars = len(after.text)

    event = {
        "ts": _now_iso(),
        "file": str(target_path),
        "section": args.section,
        "before": {
            "start_line": before.start + 1,
            "end_line_exclusive": before.end + 1,
            "chars": before_chars,
            "sha256": before_hash,
        },
        "after": {
            "start_line": after.start + 1,
            "end_line_exclusive": after.end + 1,
            "chars": after_chars,
            "sha256": after_hash,
        },
        "changed": before_hash != after_hash,
        "char_delta": after_chars - before_chars,
    }
    _append_jsonl(history_path, event)

    print(json.dumps(event, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (LookupError, FileNotFoundError, ValueError) as exc:
        print(f"erro: {exc}")
        raise SystemExit(1)
