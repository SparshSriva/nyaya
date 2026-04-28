import json
import os
from enrich_corpus import enrich_entries, load_dewey_data

def add_new_data():
    # Load the Dewey Decimal data
    # Construct the path to the data file relative to this script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dewey_data_path = os.path.join(script_dir, '..', 'dewey_decimal_data.json')
    dewey_data = load_dewey_data(filepath=dewey_data_path)

    # List of new data files
    new_data_files = [
        os.path.join(script_dir, '..', 'uploads', 'four_conditions_batch_20250815.json'),
        os.path.join(script_dir, '..', 'uploads', 'hanuman_chalisa_batch_20250815.json')
    ]

    new_entries = []
    for filepath in new_data_files:
        with open(filepath, 'r') as f:
            new_entries.extend(json.load(f))

    enriched_entries = enrich_entries(new_entries, dewey_data)

    # Define corpus file paths relative to the project root
    project_root = os.path.join(script_dir, '..', '..')
    clean_corpus_path = os.path.join(project_root, 'nyaya_corpus_clean.jsonl')
    enriched_corpus_path = os.path.join(project_root, 'nyaya_corpus_enriched.jsonl')

    # Append to the main corpus files
    with open(clean_corpus_path, 'a') as f_clean:
        # Create a copy to avoid modifying the list while iterating
        for entry in new_entries:
            clean_entry = entry.copy()
            if "dewey_code" in clean_entry:
                del clean_entry["dewey_code"]
            f_clean.write(json.dumps(clean_entry) + '\n')

    with open(enriched_corpus_path, 'a') as f_enriched:
        for entry in enriched_entries:
            f_enriched.write(json.dumps(entry) + '\n')

    print(f"Added {len(new_entries)} new entries to the corpus.")

if __name__ == "__main__":
    add_new_data()
