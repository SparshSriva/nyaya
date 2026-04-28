import json
import re

def clean_keywords(text):
    # Remove punctuation and split into words
    words = re.findall(r'\b\w+\b', text.lower())
    # Remove common words that are not very descriptive
    stop_words = {'a', 'an', 'the', 'of', 'and', 'in', 'on', 'at', 'for', 'with', 'to', 'by'}
    return set(words) - stop_words

def preprocess_dewey_data(dewey_data):
    candidates = []
    for class_code, class_info in dewey_data.items():
        candidates.append({
            "code": class_code,
            "keywords": clean_keywords(class_info['name']),
            "bonus": 0
        })
        for division_code, division_info in class_info['divisions'].items():
            candidates.append({
                "code": division_code,
                "keywords": clean_keywords(division_info['name']),
                "bonus": 0.01
            })
            for section_code, section_info in division_info['sections'].items():
                section_name = section_info.get('name', '')
                if '[unassigned]' in section_name.lower() or 'no longer used' in section_name.lower():
                    continue
                section_keywords = clean_keywords(section_name)
                if not section_keywords:
                    continue
                candidates.append({
                    "code": section_code,
                    "keywords": section_keywords,
                    "bonus": 0.02
                })
    return candidates

def find_best_dewey_code(domain_string, preprocessed_candidates):
    domain_keywords = clean_keywords(domain_string)
    best_match = {"score": -1, "code": "000"}

    for candidate in preprocessed_candidates:
        keywords = candidate["keywords"]
        # Jaccard similarity
        union_len = len(domain_keywords.union(keywords))
        if union_len == 0:
            score = 0
        else:
            score = len(domain_keywords.intersection(keywords)) / union_len

        score += candidate["bonus"]
        if score > best_match["score"]:
            best_match = {"score": score, "code": candidate["code"]}

    return best_match["code"]

def load_dewey_data(filepath="Datasets/dewey_decimal_data.json"):
    with open(filepath, 'r') as f:
        return json.load(f)

def enrich_entries(entries, dewey_data):
    preprocessed_candidates = preprocess_dewey_data(dewey_data)
    enriched_entries = []
    for entry in entries:
        domain = entry.get("domain", "")
        dewey_code = find_best_dewey_code(domain, preprocessed_candidates)
        entry["dewey_code"] = dewey_code
        enriched_entries.append(entry)
    return enriched_entries

def enrich_corpus_file(corpus_filepath="nyaya_corpus_clean.jsonl", dewey_data=None, output_filepath="nyaya_corpus_enriched.jsonl"):
    if dewey_data is None:
        dewey_data = load_dewey_data()

    with open(corpus_filepath, 'r') as f_in:
        entries = [json.loads(line) for line in f_in]

    enriched_entries = enrich_entries(entries, dewey_data)

    with open(output_filepath, 'w') as f_out:
        for entry in enriched_entries:
            f_out.write(json.dumps(entry) + '\n')

if __name__ == "__main__":
    enrich_corpus_file()
    print(f"Corpus enrichment complete. Enriched corpus saved to nyaya_corpus_enriched.jsonl")
