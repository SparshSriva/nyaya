#!/usr/bin/env python3
"""
Parse ramayana_translation_data.txt into structured JSONL and YAML formats.

This script processes the structured text file containing Ramayana verses with:
- Akshara phonetic breakdowns
- Sanskrit verses 
- Word-by-word glosses
- English translations

Outputs:
- data/processed/bk1_sarga1_verses.jsonl (verse-level data)
- data/processed/bk1_sarga1_units.yaml (unit-level discourse structure)
"""

import json
import re
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional

def parse_verse_id(verse_line: str) -> str:
    """Extract verse ID from lines like 'Verse 1.1.1' or 'Verse 2'."""
    if "Verse 1.1.1" in verse_line:
        return "1.1.1"
    elif match := re.search(r'Verse (\d+)', verse_line):
        verse_num = match.group(1)
        return f"1.1.{verse_num}"
    return ""

def extract_akshara(lines: List[str], start_idx: int) -> List[str]:
    """Extract akshara phonetic breakdown from hyphenated lines."""
    akshara = []
    i = start_idx
    while i < len(lines):
        line = lines[i].strip()
        # Look for lines with Devanagari and hyphens
        if re.search(r'[ऀ-ॿ].*-', line):
            # Split on hyphens and spaces, filter out empty
            syllables = [s.strip() for s in re.split(r'[-\s]+', line) if s.strip()]
            akshara.extend(syllables)
        elif line.startswith(('त', 'न', 'क', 'च', 'आ', 'ए')):
            # Sanskrit verse line without hyphens
            break
        i += 1
    return akshara

def extract_sanskrit_verse(lines: List[str], start_idx: int) -> str:
    """Extract the main Sanskrit verse (usually after ॐ or direct)."""
    verse_lines = []
    i = start_idx
    while i < len(lines):
        line = lines[i].strip()
        if line == "ॐ":
            i += 1
            continue
        if re.search(r'[ऀ-ॿ]', line) and not re.search(r'-', line):
            verse_lines.append(line)
        elif line and not re.search(r'[ऀ-ॿ]', line):
            # Reached transliteration or other content
            break
        i += 1
    return ' '.join(verse_lines)

def extract_word_glosses(lines: List[str], start_idx: int) -> List[Dict[str, str]]:
    """Extract word-by-word glosses with Sanskrit, morphology, Hindi, English."""
    glosses = []
    i = start_idx
    current_word = None
    
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
            
        # Check for English translation (quoted line)
        if line.startswith('"') and line.endswith('"'):
            break
            
        # Check for word entry (Sanskrit word with transliteration)
        if re.search(r'[ऀ-ॿ].*\(.*\)', line):
            if current_word:
                glosses.append(current_word)
            
            # Parse: संस्कृत (transliteration)
            match = re.match(r'([ऀ-ॿ\s]+)\s*\(([^)]+)\)', line)
            if match:
                current_word = {
                    'sn': match.group(1).strip(),
                    'morph': '',
                    'hi': '',
                    'en': ''
                }
        
        # Check for morphological breakdown (indented line)
        elif line.startswith('\t') and current_word:
            parts = line.strip().split('\t')
            if len(parts) >= 3:
                current_word['morph'] = parts[0] if parts[0] else ''
                current_word['hi'] = parts[1] if len(parts) > 1 else ''
                current_word['en'] = parts[2] if len(parts) > 2 else ''
            elif len(parts) == 1:
                # Sometimes morphology is on separate line
                if not current_word['morph']:
                    current_word['morph'] = parts[0]
        
        i += 1
    
    if current_word:
        glosses.append(current_word)
    
    return glosses

def extract_english_translation(lines: List[str], start_idx: int) -> str:
    """Extract the English translation (quoted line at end of verse block)."""
    for i in range(start_idx, len(lines)):
        line = lines[i].strip()
        if line.startswith('"') and line.endswith('"'):
            return line[1:-1]  # Remove quotes
    return ""

def parse_ramayana_file(filepath: str) -> List[Dict[str, Any]]:
    """Parse the complete ramayana file into structured verse data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    verses = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for verse markers
        if line.startswith('Verse'):
            verse_id = parse_verse_id(line)
            if not verse_id:
                i += 1
                continue
            
            # Extract components
            i += 1
            akshara_start = i
            akshara = extract_akshara(lines, akshara_start)
            
            # Find Sanskrit verse
            while i < len(lines) and not re.search(r'[ऀ-ॿ]', lines[i]):
                i += 1
            sa_verse = extract_sanskrit_verse(lines, i)
            
            # Skip to word glosses
            while i < len(lines) and not (lines[i].strip() and re.search(r'[ऀ-ॿ].*\(', lines[i])):
                i += 1
            word_glosses = extract_word_glosses(lines, i)
            
            # Find English translation
            while i < len(lines) and not (lines[i].strip().startswith('"') and lines[i].strip().endswith('"')):
                i += 1
            en_translation = extract_english_translation(lines, i)
            
            verse_data = {
                'id': verse_id,
                'book': 1,
                'sarga': 1,
                'akshara': akshara,
                'sa_verse': sa_verse,
                'word_gloss': word_glosses,
                'en': en_translation,
                'role': None,
                'entities': []
            }
            verses.append(verse_data)
        
        i += 1
    
    return verses

def create_unit_yaml(verses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create unit-level YAML structure for verses 1.1.1-1.1.5."""
    unit_verses = [v for v in verses if v['id'] in ['1.1.1', '1.1.2', '1.1.3', '1.1.4', '1.1.5']]
    
    unit_data = {
        'unit_id': 1,
        'book': 1,
        'sarga': 1,
        'verses': [v['id'] for v in unit_verses],
        'participants': [
            {'id': 'Valmiki', 'type': 'PERSON'},
            {'id': 'Narada', 'type': 'PERSON'}
        ],
        'events': [
            {
                'id': 'e1',
                'type': 'ASKS',
                'args': {'agent': 'Valmiki', 'addressee': 'Narada'},
                'spans': ['1.1.1']
            },
            {
                'id': 'e2', 
                'type': 'QUALITIES_QUERY',
                'args': {'seeker': 'Valmiki', 'target': 'UnknownIdealPerson'},
                'spans': ['1.1.2', '1.1.3', '1.1.4', '1.1.5']
            }
        ],
        'relations': [
            {'head': 'e1', 'dep': 'e2', 'label': 'MOTIVATES'}
        ]
    }
    
    return unit_data

def main():
    """Main function to parse and output structured data."""
    # Setup paths
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    data_dir = root_dir / 'data'
    input_file = data_dir / 'ramayana_translation_data.txt'
    
    # Create output directory
    output_dir = data_dir / 'processed'
    output_dir.mkdir(exist_ok=True)
    
    # Parse verses
    print(f"Parsing {input_file}...")
    verses = parse_ramayana_file(str(input_file))
    print(f"Parsed {len(verses)} verses")
    
    # Output JSONL
    jsonl_file = output_dir / 'bk1_sarga1_verses.jsonl'
    with open(jsonl_file, 'w', encoding='utf-8') as f:
        for verse in verses:
            json.dump(verse, f, ensure_ascii=False)
            f.write('\n')
    print(f"Wrote verse data to {jsonl_file}")
    
    # Output unit YAML
    unit_data = create_unit_yaml(verses)
    yaml_file = output_dir / 'bk1_sarga1_units.yaml'
    with open(yaml_file, 'w', encoding='utf-8') as f:
        yaml.dump(unit_data, f, default_flow_style=False, allow_unicode=True)
    print(f"Wrote unit data to {yaml_file}")
    
    # Print summary
    print(f"\nSummary:")
    print(f"- {len(verses)} verses processed")
    print(f"- Unit 1 spans verses: {unit_data['verses']}")
    print(f"- Participants: {[p['id'] for p in unit_data['participants']]}")
    print(f"- Events: {[e['type'] for e in unit_data['events']]}")

if __name__ == '__main__':
    main()
