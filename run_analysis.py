import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter, defaultdict
from datetime import datetime
import warnings
from pathlib import Path
warnings.filterwarnings('ignore')

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

def analyze_content(entry: dict) -> str:
    """Analyze entry content for cultural indicators."""
    text_fields = [
        entry.get('pratijna', ''),
        entry.get('hetu', ''),
        entry.get('udaharana', ''),
        entry.get('grounding_authority', ''),
        entry.get('domain', '')
    ]

    combined_text = ' '.join(text_fields).lower()

    western_score = 0
    non_western_score = 0

    for keyword in CULTURAL_INDICATORS['Non-Western']['keywords']:
        if keyword.lower() in combined_text:
            non_western_score += 1

    for keyword in CULTURAL_INDICATORS['Western']['keywords']:
        if keyword.lower() in combined_text:
            western_score += 1

    authority = entry.get('grounding_authority', '').lower()
    for auth in CULTURAL_INDICATORS['Non-Western']['authorities']:
        if auth.lower() in authority:
            non_western_score += 2

    for auth in CULTURAL_INDICATORS['Western']['authorities']:
        if auth.lower() in authority:
            western_score += 2

    domain = entry.get('domain', '').lower()
    if any(term in domain for term in ['sanskrit', 'pāṇinian', 'islamic', 'chinese']):
        non_western_score += 1
    elif any(term in domain for term in ['western', 'analytic', 'continental']):
        western_score += 1

    if non_western_score > western_score:
        return 'Non-Western'
    elif western_score > non_western_score:
        return 'Western'
    else:
        return 'Unknown'

# Set style for better visualizations
plt.style.use('default')
sns.set_palette("husl")

print(f"Analysis generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Load the corpus (robust JSON/JSONL loader with diagnostics)
clean_path = Path(r"nyaya_corpus_clean.jsonl")
orig_path = Path(r"nyaya_corpus.jsonl")
corpus_path = clean_path if clean_path.exists() else orig_path
entries = []

print(f"📂 Using {'cleaned' if corpus_path == clean_path else 'original'} corpus: {corpus_path}")

def load_json_or_jsonl(path: Path):
    if not path.exists():
        raise FileNotFoundError(path)
    raw = path.read_text(encoding='utf-8-sig')
    stripped = raw.lstrip()
    if stripped.startswith('[') or stripped.startswith('{'):
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                return data, {"mode": "json-array", "invalid": 0, "skipped": 0}
            if isinstance(data, dict):
                if 'entries' in data and isinstance(data['entries'], list):
                    return data['entries'], {"mode": "json-object", "invalid": 0, "skipped": 0}
        except json.JSONDecodeError:
            pass
    results = []
    invalid_lines = []
    skipped = 0
    for ln, line in enumerate(raw.splitlines(), 1):
        s = line.strip()
        if not s or s.startswith('//') or s.startswith('#'):
            skipped += 1
            continue
        if s.endswith(','):
            s = s[:-1]
        try:
            results.append(json.loads(s))
        except json.JSONDecodeError as e:
            if (s.startswith("{") and "'" in s and '"' not in s) or s.startswith("{'"):
                try:
                    s_fixed = s.replace("\\'", "'").replace("'", '"')
                    results.append(json.loads(s_fixed))
                    continue
                except Exception:
                    pass
            invalid_lines.append((ln, str(e), s[:160]))
    if invalid_lines:
        print(f"⚠️ Skipped {len(invalid_lines)} invalid JSONL lines. Showing first 3:")
        for ln, msg, snippet in invalid_lines[:3]:
            print(f"  • Line {ln}: {msg} | Snippet: {snippet}")
    return results, {"mode": "jsonl", "invalid": len(invalid_lines), "skipped": skipped}

try:
    entries, load_stats = load_json_or_jsonl(corpus_path)
    print(f"✅ Loaded {len(entries)} entries from {corpus_path} [{load_stats['mode']}]")
    if load_stats.get('skipped', 0) or load_stats.get('invalid', 0):
        print(f"   (Skipped: {load_stats.get('skipped', 0)}, Invalid: {load_stats.get('invalid', 0)})")

    # Classify entries that are missing the field
    for entry in entries:
        if 'cultural_tradition' not in entry or entry['cultural_tradition'] == 'Unknown':
            entry['cultural_tradition'] = analyze_content(entry)

    required_fields = ['domain', 'pratijna', 'hetu', 'udaharana', 'upanaya', 'nigamana', 'grounding_authority']
    valid_entries = []
    invalid_count = 0
    for i, entry in enumerate(entries):
        # Handle multiple schemas
        is_nyaya = all(field in entry for field in required_fields)
        is_other = all(field in entry for field in ['domain', 'major_premise', 'minor_premise', 'conclusion'])
        if is_nyaya or is_other:
             valid_entries.append(entry)
        else:
            invalid_count += 1
            missing = []
            if isinstance(entry, dict):
                if not is_nyaya and not is_other:
                    missing = required_fields
            print(f"⚠️ Entry {i+1} invalid or missing fields: {missing}")
    entries = valid_entries
    print(f"📊 Valid entries: {len(entries)} (Invalid: {invalid_count})")
except FileNotFoundError:
    print(f"❌ File {corpus_path} not found. Please ensure the file exists.")
    entries = []
except Exception as e:
    print(f"❌ Error loading corpus: {e}")
    entries = []

if entries:
    domains = [entry['domain'] for entry in entries]
    domain_counts = Counter(domains)
    domain_categories = defaultdict(list)
    category_stats = defaultdict(dict)
    for domain in domains:
        if '/' in domain:
            category = domain.split('/')[0].strip()
            subcategory = domain.split('/')[1].strip()
            domain_categories[category].append(subcategory)
        else:
            domain_categories['General'].append(domain)
    for category, subcategories in domain_categories.items():
        unique_subcats = list(set(subcategories))
        category_stats[category] = {
            'total_entries': len(subcategories),
            'unique_subcategories': len(unique_subcats),
            'subcategories': dict(Counter(subcategories))
        }
    print("🎯 DOMAIN COVERAGE ANALYSIS")
    print("=" * 50)
    print(f"Total unique domains: {len(domain_counts)}")
    print(f"Total philosophical categories: {len(category_stats)}")
    print()
    category_summary = []
    for category, stats in sorted(category_stats.items(), key=lambda x: x[1]['total_entries'], reverse=True):
        category_summary.append({
            'Category': category,
            'Total Entries': stats['total_entries'],
            'Unique Subcategories': stats['unique_subcategories'],
            'Avg Entries/Subcat': round(stats['total_entries'] / stats['unique_subcategories'], 2)
        })
    df_categories = pd.DataFrame(category_summary)
    print("📈 Category Coverage Summary:")
    print(df_categories.to_string(index=False))
    print()
    print("🔝 Top 15 Most Represented Domains:")
    for domain, count in domain_counts.most_common(15):
        print(f"  {domain}: {count} entries")
else:
    print("❌ No valid entries to analyze")

if entries:
    authorities = [entry['grounding_authority'] for entry in entries if 'grounding_authority' in entry]
    authority_counts = Counter(authorities)
    authority_types = defaultdict(list)
    source_mapping = defaultdict(dict)
    for authority in authorities:
        if '/' in authority:
            auth_type = authority.split('/')[0].strip()
            specific_source = authority.split('/')[1].strip()
            authority_types[auth_type].append(specific_source)
        else:
            authority_types['General'].append(authority)
    for auth_type, sources in authority_types.items():
        unique_sources = list(set(sources))
        source_mapping[auth_type] = {
            'total_citations': len(sources),
            'unique_sources': len(unique_sources),
            'source_distribution': dict(Counter(sources))
        }
    print("📚 GROUNDING AUTHORITY ANALYSIS")
    print("=" * 50)
    print(f"Total unique authorities: {len(authority_counts)}")
    print(f"Total authority types: {len(source_mapping)}")
    print()
    authority_summary = []
    for auth_type, stats in sorted(source_mapping.items(), key=lambda x: x[1]['total_citations'], reverse=True):
        authority_summary.append({
            'Authority Type': auth_type,
            'Total Citations': stats['total_citations'],
            'Unique Sources': stats['unique_sources'],
            'Citation Density': round(stats['total_citations'] / stats['unique_sources'], 2)
        })
    df_authorities = pd.DataFrame(authority_summary)
    print("📊 Authority Type Summary:")
    print(df_authorities.to_string(index=False))
    print()
    print("🏆 Top 15 Most Cited Sources:")
    for authority, count in authority_counts.most_common(15):
        print(f"  {authority}: {count} citations")
    print()
    print("🔍 RAG Integration Metrics:")
    specific_source_count = sum(1 for auth in authorities if '/' in auth)
    general_source_count = len(authorities) - specific_source_count
    specificity_ratio = specific_source_count / len(authorities) * 100
    print(f"  Source Specificity: {specificity_ratio:.1f}% ({specific_source_count}/{len(authorities)})")
    print(f"  Average citations per source: {len(authorities) / len(authority_counts):.2f}")
    print(f"  Source diversity index: {len(authority_counts) / len(authorities):.3f}")
else:
    print("❌ No valid entries to analyze")

if entries:
    cultural_distribution = defaultdict(int)
    for entry in entries:
        cultural_distribution[entry.get('cultural_tradition', 'Unknown')] += 1

    print("🌍 CULTURAL DIVERSITY ANALYSIS")
    print("=" * 50)
    total_entries = len(entries)
    cultural_summary = []
    for culture, count in sorted(cultural_distribution.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_entries) * 100
        cultural_summary.append({
            'Cultural Tradition': culture,
            'Entries': count,
            'Percentage': f"{percentage:.1f}%"
        })
    df_cultural = pd.DataFrame(cultural_summary)
    print("📊 Cultural Representation:")
    print(df_cultural.to_string(index=False))
    print()
else:
    print("❌ No valid entries to analyze")
