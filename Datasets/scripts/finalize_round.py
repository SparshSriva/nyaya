#!/usr/bin/env python3
"""
Finalize a staging round:
- Writes an approved snapshot under Datasets/approved/
- Optionally merges unique records into nyaya/nyaya_corpus_clean.jsonl
- Respects validation_result.json unless --force is set

Examples (PowerShell):
py -3 nyaya\Datasets\scripts\finalize_round.py --round staging_round_0001 --merge
py -3 nyaya\Datasets\scripts\finalize_round.py --round staging_round_0001 --output approved_custom.jsonl --force
"""
from __future__ import annotations
import argparse, json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Set

NYAYA_ROOT = Path('nyaya')
ROUNDS_DIR = NYAYA_ROOT / 'Datasets' / 'rounds'
APPROVED_DIR = NYAYA_ROOT / 'Datasets' / 'approved'
CLEAN_FILE = NYAYA_ROOT / 'nyaya_corpus_clean.jsonl'


def read_jsonl(p: Path) -> List[Dict[str, Any]]:
    if not p.exists():
        return []
    items: List[Dict[str, Any]] = []
    for line in p.read_text(encoding='utf-8').splitlines():
        s = line.strip()
        if not s:
            continue
        items.append(json.loads(s))
    return items


def append_jsonl(p: Path, items: List[Dict[str, Any]]):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('a', encoding='utf-8') as f:
        for r in items:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--round', required=True)
    ap.add_argument('--merge', action='store_true', help='Append unique records into nyaya_corpus_clean.jsonl')
    ap.add_argument('--force', action='store_true', help='Proceed even if validation_result.json indicates failure')
    ap.add_argument('--output', help='Approved snapshot filename (defaults to approved_YYYYMMDD_<round>.jsonl)')
    args = ap.parse_args()

    round_dir = ROUNDS_DIR / args.round
    clean_path = round_dir / f"nyaya_corpus_{args.round}_clean.jsonl"
    val_path = round_dir / 'validation_result.json'

    # Check validation
    if val_path.exists() and not args.force:
        try:
            val = json.loads(val_path.read_text(encoding='utf-8'))
            if not val.get('passes', False):
                raise SystemExit('Validation did not pass. Use --force to override.')
        except Exception as e:
            raise SystemExit(f'Could not parse validation result: {e}')

    items = read_jsonl(clean_path)
    if not items:
        raise SystemExit(f'No items found in {clean_path}')

    today = datetime.utcnow().strftime('%Y%m%d')
    out_name = args.output or f"approved_{today}_{args.round}.jsonl"
    approved_path = APPROVED_DIR / out_name

    # Write approved snapshot
    approved_path.parent.mkdir(parents=True, exist_ok=True)
    approved_path.write_text('', encoding='utf-8')  # truncate/create
    append_jsonl(approved_path, items)

    merged = 0
    skipped = 0
    if args.merge:
        existing_ids: Set[str] = set()
        if CLEAN_FILE.exists():
            for r in read_jsonl(CLEAN_FILE):
                rid = str(r.get('id',''))
                if rid:
                    existing_ids.add(rid)
        new_items = []
        for r in items:
            rid = str(r.get('id',''))
            if rid and rid in existing_ids:
                skipped += 1
                continue
            new_items.append(r)
        append_jsonl(CLEAN_FILE, new_items)
        merged = len(new_items)

    summary = {
        'round': args.round,
        'approved_snapshot': str(approved_path),
        'snapshot_count': len(items),
        'merged_into_clean': merged,
        'skipped_existing': skipped,
        'clean_file': str(CLEAN_FILE)
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
