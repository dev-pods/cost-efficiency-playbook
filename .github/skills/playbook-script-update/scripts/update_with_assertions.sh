#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  cat <<'USAGE'
Usage:
  update_with_assertions.sh --file <markdown> --section <title> --new-content <path> [--history <jsonl>]
USAGE
}

file=""
section=""
new_content=""
history=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --file)
      file="$2"
      shift 2
      ;;
    --section)
      section="$2"
      shift 2
      ;;
    --new-content)
      new_content="$2"
      shift 2
      ;;
    --history)
      history="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "erro: argumento desconhecido: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ -z "$file" || -z "$section" || -z "$new_content" ]]; then
  echo "erro: --file, --section e --new-content sao obrigatorios" >&2
  usage
  exit 2
fi

if [[ ! -f "$file" ]]; then
  echo "erro: arquivo alvo inexistente: $file" >&2
  exit 1
fi

if [[ ! -f "$new_content" ]]; then
  echo "erro: arquivo de novo conteudo inexistente: $new_content" >&2
  exit 1
fi

tmp_root="${TMPDIR:-/tmp}/playbook-script-update"
mkdir -p "$tmp_root"
tmp_dir="$(mktemp -d "$tmp_root/update-run.XXXXXX")"
before_file="$tmp_dir/before-update.md"
event_file="$tmp_dir/update-event.json"
scope_file="$tmp_dir/scope-report.json"
history_file="$tmp_dir/update-history.jsonl"

if [[ -n "$history" ]]; then
  history_file="$history"
fi

cp "$file" "$before_file"

cleanup() {
  rm -rf "$tmp_dir"
}
trap cleanup EXIT INT TERM HUP ERR

python3 scripts/update_cycle.py \
  --file "$file" \
  --section "$section" \
  --new-content "$new_content" \
  --no-backup \
  --history "$history_file" \
  > "$event_file"

python3 scripts/scope_guard.py \
  --before "$before_file" \
  --after "$file" \
  --section "$section" \
  --strict \
  > "$scope_file"

python3 scripts/validate_readme_structure.py --file "$file" --strict >/dev/null

python3 - "$event_file" "$scope_file" <<'PY'
import json
import sys

event_path, scope_path = sys.argv[1], sys.argv[2]
with open(event_path, "r", encoding="utf-8") as fh:
    event = json.load(fh)
with open(scope_path, "r", encoding="utf-8") as fh:
    scope = json.load(fh)

if not event.get("changed", False):
    raise SystemExit("erro: assertion falhou: changed=false")
if not scope.get("only_target_section_changed", False):
    raise SystemExit("erro: assertion falhou: scope_guard detectou alteracao fora da secao")

summary = {
    "section": event.get("section"),
    "changed": event.get("changed"),
    "char_delta": event.get("char_delta"),
    "scope_guard_ok": scope.get("only_target_section_changed"),
    "structure_validation_ok": True,
}
print(json.dumps(summary, ensure_ascii=False, indent=2))
PY

echo "OK: update com assertions aplicado para secao '$section'."
