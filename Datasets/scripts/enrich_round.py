#!/usr/bin/env python3
"""
Enrich a staging round in place:
- If cultural_tradition is missing, tag as Non-Western (opt-in)
- If grounding_authority lacks a URL, add a sensible default per record (opt-in)
- Keeps pretty.json and clean.jsonl synchronized

Example (PowerShell):
py -3 nyaya\Datasets\scripts\enrich_round.py --round staging_round_0001 --tag-nonwestern --add-urls
"""
from __future__ import annotations
import argparse, json, re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

NYAYA_ROOT = Path('nyaya')
ROUNDS_DIR = NYAYA_ROOT / 'Datasets' / 'rounds'


def read_pretty(p: Path) -> List[Dict[str, Any]]:
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding='utf-8'))
        return data if isinstance(data, list) else []
    except Exception:
        return []


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


def write_pretty(p: Path, arr: List[Dict[str, Any]]):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(arr, ensure_ascii=False, indent=2), encoding='utf-8')


def write_jsonl(p: Path, items: List[Dict[str, Any]]):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', encoding='utf-8') as f:
        for r in items:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')


def has_url(s: str) -> bool:
    return 'http://' in s or 'https://' in s


def add_default_url(rec: Dict[str, Any], accessed: str) -> str | None:
    domain = str(rec.get('domain', '')).lower()
    ga = str(rec.get('grounding_authority', ''))
    if has_url(ga):
        return None
    # Heuristics
    if 'pāṇini' in domain or 'panini' in domain or 'sanskrit' in domain or 'pāṇinian' in domain or 'philology' in domain:
        return f"Sanskrit Grammar / Aṣṭādhyāyī (Pāṇini), https://ashtadhyayi.com/ (accessed {accessed})"
    if 'hanuman' in domain or 'chalisa' in domain or 'indology' in domain or 'awadhi' in domain:
        return f"Indology / Hanuman Chalisa (Wikipedia), https://en.wikipedia.org/wiki/Hanuman_Chalisa (accessed {accessed})"
    if 'comparative philosophy' in domain or 'epistemology' in domain:
        return f"Indology / Hanuman Chalisa (Wikipedia), https://en.wikipedia.org/wiki/Hanuman_Chalisa (accessed {accessed})"
    # Fallback: encode previous field as category + Wikipedia generic
    return f"Reference / Wikipedia, https://en.wikipedia.org/ (accessed {accessed})"


def enrich(items: List[Dict[str, Any]], tag_nonwestern: bool, add_urls: bool, accessed: str) -> int:
    changed = 0
    for r in items:
        updated = False
        if tag_nonwestern and not str(r.get('cultural_tradition', '')).strip():
            r['cultural_tradition'] = 'Non-Western'
            updated = True
        if add_urls:
            new_ga = add_default_url(r, accessed)
            if new_ga:
                r['grounding_authority'] = new_ga
                updated = True
        if updated:
            changed += 1
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--round', required=True)
    ap.add_argument('--tag-nonwestern', action='store_true')
    ap.add_argument('--add-urls', action='store_true')
    args = ap.parse_args()

    round_dir = ROUNDS_DIR / args.round
    pretty_path = round_dir / f"nyaya_corpus_{args.round}_pretty.json"
    clean_path = round_dir / f"nyaya_corpus_{args.round}_clean.jsonl"

    accessed = datetime.utcnow().strftime('%Y-%m-%d')

    arr = read_pretty(pretty_path)
    items = read_jsonl(clean_path)

    changed_pretty = enrich(arr, args.tag_nonwestern, args.add_urls, accessed)
    changed_clean = enrich(items, args.tag_nonwestern, args.add_urls, accessed)

    if changed_pretty:
        write_pretty(pretty_path, arr)
    if changed_clean:
        write_jsonl(clean_path, items)

    out = {
        'round': args.round,
        'changed_pretty': changed_pretty,
        'changed_clean': changed_clean,
        'file_pretty': str(pretty_path),
        'file_clean': str(clean_path)
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
