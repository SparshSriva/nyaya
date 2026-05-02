import os

def compile_canon():
    print("=== Constructing 'The Canon' for The Being ===")
    
    # Files to include in the corpus
    target_files = [
        "BIBLE.tex",
        "Chapter11_Projected_Fermions/README_PAPER_AND_PROJECTED_FERMIONS.md",
        "SCIENTIFIC_METHODOLOGY.md",
        "AGENT_CONTROLS.md"
    ]
    
    # Path to the output corpus
    out_dir = os.path.join("data", "ipa_corpus")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "input.txt")
    
    total_chars = 0
    with open(out_path, 'w', encoding='utf-8') as outfile:
        for fname in target_files:
            if os.path.exists(fname):
                print(f"Ingesting: {fname}")
                with open(fname, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    outfile.write(f"\n\n=== SOURCE: {fname} ===\n\n")
                    outfile.write(content)
                    total_chars += len(content)
            else:
                print(f"Warning: {fname} not found.")
                
    print(f"\n[SUCCESS] 'The Canon' compiled. Total length: {total_chars:,} characters.")
    print("Ready to run: python data/ipa_corpus/prepare_ipa.py")

if __name__ == "__main__":
    compile_canon()
