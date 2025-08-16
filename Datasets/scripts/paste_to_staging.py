#!/usr/bin/env python3
"""
Paste-to-staging utility for Nyāya syllogisms.

Purpose
- Accept a JSON array or JSONL from stdin or a file and append valid entries to:
  - nyaya/nyaya_corpus_staging.jsonl (global staging)
  - nyaya/Datasets/rounds/<round_id>/nyaya_corpus_<round_id>_pretty.json (readable)
  - nyaya/Datasets/rounds/<round_id>/nyaya_corpus_<round_id>_clean.jsonl (processing)

Windows PowerShell examples
- Paste JSON array from clipboard into staging_round_0001:
  Get-Clipboard | python nyaya/Datasets/scripts/paste_to_staging.py --round staging_round_0001

- From a file:
  python nyaya/Datasets/scripts/paste_to_staging.py --input path\to\batch.json --round staging_round_0001

Input format
- Either a JSON array: [ {record}, {record}, ... ]
- Or JSONL: one JSON object per line

Validation
- Required fields: domain, pratijna, hetu, udaharana, upanaya, nigamana, grounding_authority
- Normalizes whitespace; assigns an id if missing.

"""
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
import uuid

REQUIRED = ['domain','pratijna','hetu','udaharana','upanaya','nigamana','grounding_authority']

NYAYA_ROOT = Path('nyaya')
GLOBAL_STAGING = NYAYA_ROOT / 'nyaya_corpus_staging.jsonl'
ROUNDS_DIR = NYAYA_ROOT / 'Datasets' / 'rounds'


def normalize_text(s: Any) -> str:
    if s is None:
        return ''
    return ' '.join(str(s).strip().split())

def validate(rec: Dict[str, Any]) -> Dict[str, Any]:
    r = {k: normalize_text(rec.get(k)) for k in REQUIRED}
    r['id'] = rec.get('id') or str(uuid.uuid4())
    # keep optional metadata if present
    for k in ('complexity_indicators','cultural_tradition','cross_references','notes','source'):
        if k in rec:
            r[k] = rec[k]
    missing = [k for k in REQUIRED if not r[k]]
    if missing:
        raise ValueError(f"Missing fields: {missing}")
    return r


def read_input_text(path: str | None) -> str:
    if path:
        return Path(path).read_text(encoding='utf-8')
    return sys.stdin.read()


def parse_payload(txt: str) -> List[Dict[str, Any]]:
    txt_strip = txt.lstrip()
    # JSON array
    if txt_strip.startswith('['):
        data = json.loads(txt)
        if not isinstance(data, list):
            raise ValueError('Top-level JSON must be an array')
        return [x for x in data if isinstance(x, dict)]
    # JSONL fallback
    items: List[Dict[str, Any]] = []
    for line in txt.splitlines():
        s = line.strip()
        if not s:
            continue
        items.append(json.loads(s))
    return items


def append_global_staging(valids: List[Dict[str, Any]]):
    GLOBAL_STAGING.parent.mkdir(parents=True, exist_ok=True)
    with GLOBAL_STAGING.open('a', encoding='utf-8') as f:
        for r in valids:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')


def load_pretty(pretty_path: Path) -> List[Dict[str, Any]]:
    if not pretty_path.exists():
        return []
    arr = json.loads(pretty_path.read_text(encoding='utf-8'))
    return arr if isinstance(arr, list) else []


def write_pretty(pretty_path: Path, arr: List[Dict[str, Any]]):
    pretty_path.parent.mkdir(parents=True, exist_ok=True)
    pretty_path.write_text(json.dumps(arr, ensure_ascii=False, indent=2), encoding='utf-8')


def append_clean(clean_path: Path, valids: List[Dict[str, Any]]):
    clean_path.parent.mkdir(parents=True, exist_ok=True)
    with clean_path.open('a', encoding='utf-8') as f:
        for r in valids:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', help='Path to JSON/JSONL. If omitted, reads stdin.')
    ap.add_argument('--round', default='staging_round_0001', help='Round folder name under Datasets/rounds')
    ap.add_argument('--dry-run', action='store_true', help='Validate only, no writes')
    args = ap.parse_args()

    txt = read_input_text(args.input)
    raw_items = parse_payload(txt)
    valids: List[Dict[str, Any]] = []
    errors: List[str] = []
    for i, rec in enumerate(raw_items):
        try:
            valids.append(validate(rec))
        except Exception as e:
            errors.append(f"Item {i}: {e}")

    round_dir = ROUNDS_DIR / args.round
    pretty_path = round_dir / f"nyaya_corpus_{args.round}_pretty.json"
    clean_path = round_dir / f"nyaya_corpus_{args.round}_clean.jsonl"

    if not args.dry_run:
        # Global staging
        append_global_staging(valids)
        # Round pretty (append to array)
        arr = load_pretty(pretty_path)
        arr.extend(valids)
        write_pretty(pretty_path, arr)
        # Round clean (append lines)
        append_clean(clean_path, valids)

    summary = {
        'round': args.round,
        'input_items': len(raw_items),
        'validated': len(valids),
        'errors': errors,
        'global_staging': str(GLOBAL_STAGING),
        'round_pretty': str(pretty_path),
        'round_clean': str(clean_path),
        'dry_run': args.dry_run,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
