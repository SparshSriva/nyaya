import json
import re

def clean_keywords(text):
    # Remove punctuation and split into words
    words = re.findall(r'\b\w+\b', text.lower())
    # Remove common words that are not very descriptive
    stop_words = {'a', 'an', 'the', 'of', 'and', 'in', 'on', 'at', 'for', 'with', 'to', 'by'}
    return set(words) - stop_words

def find_best_dewey_code(domain_string, dewey_data):
    domain_keywords = clean_keywords(domain_string)

    best_match = {"score": -1, "code": "000"}

    for class_code, class_info in dewey_data.items():
        class_name_keywords = clean_keywords(class_info['name'])
        # Jaccard similarity
        union_len = len(domain_keywords.union(class_name_keywords))
        if union_len == 0:
            score = 0
        else:
            score = len(domain_keywords.intersection(class_name_keywords)) / union_len

        if score > best_match["score"]:
            best_match = {"score": score, "code": class_code}

        for division_code, division_info in class_info['divisions'].items():
            division_name_keywords = clean_keywords(division_info['name'])
            union_len = len(domain_keywords.union(division_name_keywords))
            if union_len == 0:
                score = 0
            else:
                score = len(domain_keywords.intersection(division_name_keywords)) / union_len

            score += 0.01 # Add a small bonus for being a division
            if score > best_match["score"]:
                best_match = {"score": score, "code": division_code}

            for section_code, section_info in division_info['sections'].items():
                section_name = section_info.get('name', '')
                if '[unassigned]' in section_name.lower() or 'no longer used' in section_name.lower():
                    continue
                section_name_keywords = clean_keywords(section_name)
                if not section_name_keywords:
                    continue

                union_len = len(domain_keywords.union(section_name_keywords))
                if union_len == 0:
                    score = 0
                else:
                    score = len(domain_keywords.intersection(section_name_keywords)) / union_len

                score += 0.02 # Add a bigger bonus for being a section
                if score > best_match["score"]:
                    best_match = {"score": score, "code": section_code}

    return best_match["code"]


def load_dewey_data(filepath="Datasets/dewey_decimal_data.json"):
    with open(filepath, 'r') as f:
        return json.load(f)

def enrich_corpus(corpus_filepath="nyaya_corpus_clean.jsonl", dewey_data=None, output_filepath="nyaya_corpus_enriched.jsonl"):
    if dewey_data is None:
        dewey_data = load_dewey_data()

    with open(corpus_filepath, 'r') as f_in, open(output_filepath, 'w') as f_out:
        for line in f_in:
            entry = json.loads(line)
            domain = entry.get("domain", "")
            dewey_code = find_best_dewey_code(domain, dewey_data)
            entry["dewey_code"] = dewey_code
            f_out.write(json.dumps(entry) + '\n')


if __name__ == "__main__":
    enrich_corpus()
    print(f"Corpus enrichment complete. Enriched corpus saved to nyaya_corpus_enriched.jsonl")
