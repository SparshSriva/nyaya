#!/usr/bin/env python3
"""
Batch Organization Tool
Organizes unbatched entries into logical groups for processing.
"""

import json
from datetime import datetime
from collections import defaultdict
from typing import List

def generate_batch_id(domain_category: str) -> str:
    """Generate a batch ID based on domain category."""
    date_str = datetime.now().strftime("%Y%m%d")
    category_map = {
        'sanskrit': f'sanskrit_grammar_{date_str}',
        'philosophy': f'philosophy_expansion_{date_str}',
        'linguistic': f'linguistic_analysis_{date_str}',
        'comparative': f'comparative_studies_{date_str}',
        'theoretical': f'theoretical_frameworks_{date_str}',
        'general': f'general_syllogisms_{date_str}'
    }
    return category_map.get(domain_category, f'mixed_batch_{date_str}')

def categorize_domain(domain: str) -> str:
    """Categorize domain into batch groups."""
    domain_lower = domain.lower()
    
    if any(term in domain_lower for term in ['sanskrit', 'pāṇinian', 'grammar']):
        return 'sanskrit'
    elif any(term in domain_lower for term in ['philosophy', 'epistemology', 'metaphysics']):
        return 'philosophy'
    elif any(term in domain_lower for term in ['linguistic', 'philology', 'language']):
        return 'linguistic'
    elif any(term in domain_lower for term in ['comparative', 'cultural', 'cross-cultural']):
        return 'comparative'
    elif any(term in domain_lower for term in ['theory', 'model', 'sociological']):
        return 'theoretical'
    else:
        return 'general'

def load_entries(filepath: str) -> List[Dict]:
    """Load entries from a JSONL file."""
    entries = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                entries.append(json.loads(line))
    except FileNotFoundError:
        print(f"⚠️  Warning: Could not find {filepath}")
    return entries

def group_unbatched_entries(entries: List[Dict]) -> tuple[Dict[str, List[Dict]], int]:
    """Group unbatched entries by their domain category."""
    domain_groups = defaultdict(list)
    unbatched_count = 0
    
    for entry in entries:
        current_batch = entry.get('batch_id', 'None')
        
        if current_batch == 'None':
            domain = entry.get('domain', 'Unknown')
            category = categorize_domain(domain)
            domain_groups[category].append(entry)
            unbatched_count += 1

    return domain_groups, unbatched_count

def assign_batches(domain_groups: Dict[str, List[Dict]]) -> Dict[str, int]:
    """Assign batch IDs and metadata to entries based on category groups."""
    batch_assignments = {}
    for category, category_entries in domain_groups.items():
        batch_id = generate_batch_id(category)
        batch_assignments[batch_id] = len(category_entries)
        
        for entry in category_entries:
            entry['batch_id'] = batch_id
            entry['batch_metadata'] = {
                'category': category,
                'assigned_date': datetime.now().isoformat(),
                'batch_size': len(category_entries)
            }
    return batch_assignments

def save_entries(entries: List[Dict], filepath: str):
    """Save entries to a JSONL file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

def save_summary(unbatched_count: int, batch_assignments: Dict[str, int], categories: List[str], filepath: str = 'batch_organization_summary.json'):
    """Save summary of batch organization to a JSON file."""
    batch_summary = {
        'organization_date': datetime.now().isoformat(),
        'total_organized': unbatched_count,
        'batch_assignments': batch_assignments,
        'categories_created': categories
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(batch_summary, f, indent=2, ensure_ascii=False)

def print_report(unbatched_count: int, batch_assignments: Dict[str, int], filepath: str):
    """Print a summary report of the batch organization process."""
    print(f"\\n✅ Batch Organization Complete!")
    print(f"📊 Organized {unbatched_count} entries into {len(batch_assignments)} batches:")
    
    for batch_id, count in batch_assignments.items():
        print(f"   📦 {batch_id}: {count} entries")
    
    print(f"\\n💾 Updated {filepath} with batch assignments")
    print(f"📋 Created batch_organization_summary.json")

def organize_batches(filepath: str = 'nyaya_corpus_staging.jsonl'):
    """Main batch organization function."""
    print("📦 Organizing entries into logical batches...")
    
    entries = load_entries(filepath)
    if not entries:
        return

    domain_groups, unbatched_count = group_unbatched_entries(entries)
    
    if unbatched_count == 0:
        print("✨ All entries already have batch IDs!")
        return
    
    batch_assignments = assign_batches(domain_groups)

    save_entries(entries, filepath)
    save_summary(unbatched_count, batch_assignments, list(domain_groups.keys()))
    print_report(unbatched_count, batch_assignments, filepath)

if __name__ == "__main__":
    organize_batches()
