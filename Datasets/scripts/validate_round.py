#!/usr/bin/env python3
"""
Validate a staging round and emit a JSON summary.

Example (PowerShell):
py -3 nyaya\Datasets\scripts\validate_round.py --round staging_round_0001
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Dict, Any, List

NYAYA_ROOT = Path('nyaya')
ROUNDS_DIR = NYAYA_ROOT / 'Datasets' / 'rounds'
APPROVED_DIR = NYAYA_ROOT / 'Datasets' / 'approved'
REQUIRED = ['domain','pratijna','hetu','udaharana','upanaya','nigamana','grounding_authority']


def read_jsonl(p: Path) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    if not p.exists():
        return items
    for line in p.read_text(encoding='utf-8').splitlines():
        s = line.strip()
        if not s:
            continue
        items.append(json.loads(s))
    return items


def is_non_western(trad: str) -> bool:
    t = (trad or '').strip().lower()
    if not t:
        return False
    return 'non' in t or t in {'indian','chinese','islamic','buddhist','jain','hindu','confucian','taoist'}


def has_specific_source(ga: str) -> bool:
    s = (ga or '').strip().lower()
    return ('http://' in s or 'https://' in s) and (' / ' in s or ':' in s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--round', default='staging_round_0001')
    ap.add_argument('--nonwestern-thresh', type=float, default=0.25)
    ap.add_argument('--specificity-thresh', type=float, default=0.90)
    ap.add_argument('--output', help='Path to write validation_result.json; defaults to round dir')
    args = ap.parse_args()

    round_dir = ROUNDS_DIR / args.round
    clean_path = round_dir / f"nyaya_corpus_{args.round}_clean.jsonl"
    items = read_jsonl(clean_path)

    total = len(items)
    missing_list = []
    non_w_count = 0
    spec_count = 0
    char_sum = 0

    for i, r in enumerate(items):
        # schema
        miss = [k for k in REQUIRED if not str(r.get(k, '')).strip()]
        if miss:
            missing_list.append({'index': i, 'missing': miss})
        # diversity
        if is_non_western(str(r.get('cultural_tradition',''))):
            non_w_count += 1
        # specificity
        if has_specific_source(str(r.get('grounding_authority',''))):
            spec_count += 1
        # complexity proxy
        for k in ('pratijna','hetu','udaharana','upanaya','nigamana'):
            char_sum += len(str(r.get(k,'')).strip())

    schema_ok = len(missing_list) == 0
    non_w_share = (non_w_count / total) if total else 0.0
    spec_share = (spec_count / total) if total else 0.0
    avg_chars = (char_sum / total) if total else 0.0

    result = {
        'round': args.round,
        'file': str(clean_path),
        'total': total,
        'schema_ok': schema_ok,
        'missing_details': missing_list[:50],
        'non_western_share': round(non_w_share, 3),
        'specificity_share': round(spec_share, 3),
        'avg_chars_across_steps': round(avg_chars, 1),
        'thresholds': {
            'non_western_share': args.nonwestern_thresh,
            'specificity_share': args.specificity_thresh
        },
        'passes': (schema_ok and non_w_share >= args.nonwestern_thresh and spec_share >= args.specificity_thresh)
    }

    out_path = Path(args.output) if args.output else (round_dir / 'validation_result.json')
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
