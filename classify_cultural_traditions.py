#!/usr/bin/env python3
"""
Cultural Tradition Classification Tool
Automatically classifies entries based on content analysis and cultural indicators.
"""

import json
import re
from typing import Dict, List, Set

# Cultural classification indicators
CULTURAL_INDICATORS = {
    'Non-Western': {
        'keywords': [
            'Pāṇini', 'Sanskrit', 'Aṣṭādhyāyī', 'sūtra', 'kāraka', 'samāsa',
            'Islamic', 'Al-Ghazali', 'Sufism', 'Chinese', 'Confucian', 'ren', 'li',
            'Hindu', 'Buddhist', 'Vedic', 'dharma', 'karma', 'moksha',
            'Taoism', 'Zen', 'Madhyamaka', 'Advaita'
        ],
        'authorities': [
            'Pāṇinian Grammar', 'Islamic Philosophy', 'Chinese Philosophy',
            'Hindu Philosophy', 'Buddhist Philosophy', 'Comparative Method'
        ]
    },
    'Western': {
        'keywords': [
            'Aristotelian', 'Kantian', 'Cartesian', 'Thomistic', 'Platonic',
            'analytical', 'phenomenology', 'existentialism', 'pragmatism',
            'logical positivism', 'speech acts', 'Austin', 'Searle'
        ],
        'authorities': [
            'Stanford Encyclopedia', 'Contemporary Philosophy', 'Western Philosophy',
            'Analytic Philosophy', 'Continental Philosophy'
        ]
    }
}

def analyze_content(entry: Dict) -> str:
    """Analyze entry content for cultural indicators."""
    text_fields = [
        entry.get('pratijna', ''),
        entry.get('hetu', ''),
        entry.get('udaharana', ''),
        entry.get('grounding_authority', ''),
        entry.get('domain', '')
    ]
    
    combined_text = ' '.join(text_fields).lower()
    
    # Score by keyword presence
    western_score = 0
    non_western_score = 0
    
    for keyword in CULTURAL_INDICATORS['Non-Western']['keywords']:
        if keyword.lower() in combined_text:
            non_western_score += 1
    
    for keyword in CULTURAL_INDICATORS['Western']['keywords']:
        if keyword.lower() in combined_text:
            western_score += 1
    
    # Authority-based classification
    authority = entry.get('grounding_authority', '').lower()
    for auth in CULTURAL_INDICATORS['Non-Western']['authorities']:
        if auth.lower() in authority:
            non_western_score += 2
    
    for auth in CULTURAL_INDICATORS['Western']['authorities']:
        if auth.lower() in authority:
            western_score += 2
    
    # Domain-based classification
    domain = entry.get('domain', '').lower()
    if any(term in domain for term in ['sanskrit', 'pāṇinian', 'islamic', 'chinese']):
        non_western_score += 1
    elif any(term in domain for term in ['western', 'analytic', 'continental']):
        western_score += 1
    
    # Determine classification
    if non_western_score > western_score:
        return 'Non-Western'
    elif western_score > non_western_score:
        return 'Western'
    else:
        return 'Unknown'

def classify_entries():
    """Main classification function."""
    print("🔍 Analyzing cultural traditions in staging entries...")
    
    # Load staging data
    entries = []
    with open('nyaya_corpus_staging.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            entries.append(json.loads(line))
    
    # Classify entries
    classified_count = 0
    cultural_stats = {'Western': 0, 'Non-Western': 0, 'Unknown': 0}
    
    for entry in entries:
        current_tradition = entry.get('cultural_tradition', 'Unknown')
        
        if current_tradition == 'Unknown':
            predicted_tradition = analyze_content(entry)
            entry['cultural_tradition'] = predicted_tradition
            classified_count += 1
            
            print(f"📝 Classified: {entry.get('id', 'No ID')[:8]}... -> {predicted_tradition}")
            if len(entry.get('domain', '')) > 50:
                print(f"   Domain: {entry['domain'][:50]}...")
            else:
                print(f"   Domain: {entry['domain']}")
        
        cultural_stats[entry['cultural_tradition']] += 1
    
    # Save updated entries
    if classified_count > 0:
        with open('nyaya_corpus_staging.jsonl', 'w', encoding='utf-8') as f:
            for entry in entries:
                f.write(json.dumps(entry, ensure_ascii=False) + '\\n')
    
    # Report results
    print(f"\\n✅ Classification Complete!")
    print(f"📊 Classified {classified_count} entries")
    print(f"📈 Cultural Distribution:")
    for tradition, count in cultural_stats.items():
        percentage = (count / len(entries)) * 100
        print(f"   {tradition}: {count} ({percentage:.1f}%)")
    
    if classified_count > 0:
        print(f"\\n💾 Updated nyaya_corpus_staging.jsonl with classifications")
    else:
        print(f"\\n✨ All entries already classified!")

if __name__ == "__main__":
    classify_entries()
