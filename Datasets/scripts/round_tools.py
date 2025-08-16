#!/usr/bin/env python3
"""
Round tools: convert between pretty (JSON array, indented) and clean (JSONL),
plus map pretty index to clean line for manual deletion.

Usage (Windows PowerShell):
  # Convert staging JSONL to pretty JSON
  python nyaya/Datasets/scripts/round_tools.py to-pretty `
    --input nyaya/nyaya_corpus_staging.jsonl `
    --output nyaya/Datasets/rounds/staging_round_0001/nyaya_corpus_staging_round_0001_pretty.json

  # Convert pretty JSON to clean JSONL
  python nyaya/Datasets/scripts/round_tools.py to-clean `
    --input nyaya/Datasets/rounds/staging_round_0001/nyaya_corpus_staging_round_0001_pretty.json `
    --output nyaya/Datasets/rounds/staging_round_0001/nyaya_corpus_staging_round_0001_clean.jsonl

  # Map pretty index (0-based or 1-based) to clean line number
  python nyaya/Datasets/scripts/round_tools.py map-index `
    --pretty nyaya/Datasets/rounds/staging_round_0001/nyaya_corpus_staging_round_0001_pretty.json `
    --clean nyaya/Datasets/rounds/staging_round_0001/nyaya_corpus_staging_round_0001_clean.jsonl `
    --index 12
"""
import argparse
import json
from pathlib import Path

def to_pretty(input_path: Path, output_path: Path) -> None:
    objs = []
    with input_path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            objs.append(json.loads(line))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(objs, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Wrote pretty JSON array: {output_path}")

def to_clean(input_path: Path, output_path: Path) -> None:
    data = json.loads(Path(input_path).read_text(encoding='utf-8'))
    if not isinstance(data, list):
        raise ValueError("Pretty file must be a JSON array of objects")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('w', encoding='utf-8') as f:
        for obj in data:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    print(f"Wrote clean JSONL: {output_path}")

def map_index(pretty_path: Path, clean_path: Path, index: int) -> None:
    # Normalize index (accept 1-based)
    idx = index - 1 if index >= 1 else index
    data = json.loads(pretty_path.read_text(encoding='utf-8'))
    if not isinstance(data, list):
        raise ValueError("Pretty file must be a JSON array")
    if not (0 <= idx < len(data)):
        raise IndexError(f"Index {index} out of range (0..{len(data)-1} or 1..{len(data)})")

    # In clean JSONL, objects are in the same order; line numbers are 1-based
    clean_line = idx + 1
    print(json.dumps({
        "pretty_index_input": index,
        "normalized_index": idx,
        "mapped_clean_line": clean_line
    }, indent=2))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd', required=True)

    sp1 = sub.add_parser('to-pretty')
    sp1.add_argument('--input', required=True)
    sp1.add_argument('--output', required=True)

    sp2 = sub.add_parser('to-clean')
    sp2.add_argument('--input', required=True)
    sp2.add_argument('--output', required=True)

    sp3 = sub.add_parser('map-index')
    sp3.add_argument('--pretty', required=True)
    sp3.add_argument('--clean', required=True)
    sp3.add_argument('--index', required=True, type=int)

    args = p.parse_args()
    if args.cmd == 'to-pretty':
        to_pretty(Path(args.input), Path(args.output))
    elif args.cmd == 'to-clean':
        to_clean(Path(args.input), Path(args.output))
    elif args.cmd == 'map-index':
        map_index(Path(args.pretty), Path(args.clean), args.index)

if __name__ == '__main__':
    main()
