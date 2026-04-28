#!/usr/bin/env python3
"""
Sanskrit prosody feature extraction for Ramayana verses.

Extracts syllable patterns and laghu/guru (light/heavy) prosodic features
for metrical analysis of Sanskrit verses.

Features extracted:
- Syllable count per line
- Laghu/guru pattern approximation
- Basic meter pattern recognition
"""

import re
from typing import List, Tuple, Dict, Any
from pathlib import Path

# Sanskrit vowel patterns for prosodic analysis
DEVANAGARI_VOWELS = set('अआइईउऊऋएऐओऔ')
DEVANAGARI_LONG_VOWELS = set('आईऊएऐओऔ')
DEVANAGARI_SHORT_VOWELS = set('अइउऋ')

def extract_syllables(text: str) -> List[str]:
    """
    Extract syllable-like units from Sanskrit text.
    Basic approximation: consonant+vowel combinations.
    """
    # Remove punctuation and spaces
    clean_text = re.sub(r'[।॥\s]', '', text)
    
    syllables = []
    i = 0
    
    while i < len(clean_text):
        char = clean_text[i]
        syllable = char
        
        # If we start with a consonant, collect until next consonant
        if is_consonant(char):
            i += 1
            while i < len(clean_text) and not is_consonant(clean_text[i]):
                syllable += clean_text[i]
                i += 1
        else:
            # Vowel by itself
            i += 1
            
        if syllable:
            syllables.append(syllable)
    
    return syllables

def is_consonant(char: str) -> bool:
    """Check if character is a Devanagari consonant."""
    return '\u0915' <= char <= '\u0939'  # क to ह range

def is_vowel(char: str) -> bool:
    """Check if character is a Devanagari vowel."""
    return char in DEVANAGARI_VOWELS

def get_vowel_weight(syllable: str) -> str:
    """
    Determine if syllable is laghu (L) or guru (G) based on vowel length.
    Simple rule: long vowels = guru, short vowels = laghu.
    """
    for char in syllable:
        if char in DEVANAGARI_LONG_VOWELS:
            return 'G'  # Guru (heavy)
        elif char in DEVANAGARI_SHORT_VOWELS:
            return 'L'  # Laghu (light)
    
    # Default to laghu for unclear cases
    return 'L'

def analyze_meter_pattern(laghu_guru_pattern: str) -> Dict[str, Any]:
    """
    Analyze the laghu/guru pattern to identify possible meters.
    Returns basic pattern analysis.
    """
    pattern_len = len(laghu_guru_pattern)
    
    # Count laghu and guru
    laghu_count = laghu_guru_pattern.count('L')
    guru_count = laghu_guru_pattern.count('G')
    
    # Basic pattern recognition (simplified)
    meter_hints = []
    
    if pattern_len == 8:
        meter_hints.append("Anushtubh variant")
    elif pattern_len in [11, 12]:
        meter_hints.append("Trishtubh variant")
    elif pattern_len == 16:
        meter_hints.append("Jagati variant")
    
    return {
        'syllable_count': pattern_len,
        'laghu_count': laghu_count,
        'guru_count': guru_count,
        'pattern': laghu_guru_pattern,
        'meter_hints': meter_hints
    }

def extract_chandas_features(verse_text: str) -> Dict[str, Any]:
    """
    Extract complete prosodic features from a Sanskrit verse.
    
    Args:
        verse_text: Sanskrit verse in Devanagari
        
    Returns:
        Dictionary with syllable analysis and meter patterns
    """
    # Split into lines (pada)
    lines = [line.strip() for line in verse_text.split('\n') if line.strip()]
    
    features = {
        'verse_text': verse_text,
        'pada_count': len(lines),
        'pada_analysis': []
    }
    
    total_syllables = 0
    full_pattern = []
    
    for i, line in enumerate(lines):
        syllables = extract_syllables(line)
        laghu_guru = ''.join(get_vowel_weight(syl) for syl in syllables)
        
        pada_features = {
            'pada_number': i + 1,
            'text': line,
            'syllables': syllables,
            'syllable_count': len(syllables),
            'laghu_guru_pattern': laghu_guru,
            'meter_analysis': analyze_meter_pattern(laghu_guru)
        }
        
        features['pada_analysis'].append(pada_features)
        total_syllables += len(syllables)
        full_pattern.append(laghu_guru)
    
    # Overall verse analysis
    features['total_syllables'] = total_syllables
    features['full_pattern'] = '|'.join(full_pattern)
    features['verse_meter_analysis'] = analyze_meter_pattern(''.join(full_pattern))
    
    return features

def process_verse_file(jsonl_file: str) -> List[Dict[str, Any]]:
    """
    Process a JSONL file of verses and add chandas features.
    
    Args:
        jsonl_file: Path to verse JSONL file
        
    Returns:
        List of verses with added chandas features
    """
    import json
    
    verses_with_features = []
    
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            verse_data = json.loads(line)
            
            # Extract chandas features from Sanskrit verse
            if verse_data.get('sa_verse'):
                chandas_features = extract_chandas_features(verse_data['sa_verse'])
                verse_data['chandas'] = chandas_features
            else:
                verse_data['chandas'] = None
                
            verses_with_features.append(verse_data)
    
    return verses_with_features

def main():
    """Main function to demonstrate chandas feature extraction."""
    # Setup paths
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    data_dir = root_dir / 'data' / 'processed'
    
    # Process verses if JSONL exists
    jsonl_file = data_dir / 'bk1_sarga1_verses.jsonl'
    
    if jsonl_file.exists():
        print(f"Processing verses from {jsonl_file}...")
        verses = process_verse_file(str(jsonl_file))
        
        # Output enhanced JSONL with chandas features
        output_file = data_dir / 'bk1_sarga1_verses_with_chandas.jsonl'
        
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            for verse in verses:
                json.dump(verse, f, ensure_ascii=False)
                f.write('\n')
        
        print(f"Enhanced verses written to {output_file}")
        
        # Print sample analysis
        for i, verse in enumerate(verses[:3]):
            print(f"\n--- Verse {verse['id']} ---")
            if verse.get('chandas'):
                chandas = verse['chandas']
                print(f"Sanskrit: {chandas['verse_text']}")
                print(f"Total syllables: {chandas['total_syllables']}")
                print(f"Pattern: {chandas['full_pattern']}")
                
                for pada in chandas['pada_analysis']:
                    print(f"  Pada {pada['pada_number']}: {pada['syllable_count']} syllables, {pada['laghu_guru_pattern']}")
    else:
        print(f"JSONL file not found at {jsonl_file}")
        print("Run parse_ramayana_txt.py first to generate verse data.")

if __name__ == '__main__':
    main()
