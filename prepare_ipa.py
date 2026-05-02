import os
import requests
import numpy as np
import pickle

# We wrap the phonemizer import. If you don't have espeak installed, 
# it will fall back to a naive mock mapping just so the pipeline doesn't crash.
try:
    from phonemizer import phonemize
    from phonemizer.separator import Separator
    HAS_PHONEMIZER = True
except ImportError:
    HAS_PHONEMIZER = False
    print("Warning: 'phonemizer' not found. Falling back to naive orthography-to-IPA mapping for testing.")
    print("Run `pip install phonemizer` and install espeak-ng for true phonetic transcription.")

# Import your IPATokenizer (assuming it's in the root or accessible path)
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
try:
    from ipa_tokenizer import IPATokenizer
except ImportError:
    print("Error: Could not import IPATokenizer. Ensure ipa_tokenizer.py is in the parent directory.")
    sys.exit(1)

def download_dataset(input_file_path):
    """Downloads TinyShakespeare if no custom dataset is provided."""
    if not os.path.exists(input_file_path):
        data_url = 'https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt'
        print(f"Downloading TinyShakespeare to {input_file_path}...")
        with open(input_file_path, 'w', encoding='utf-8') as f:
            f.write(requests.get(data_url).text)

def naive_phonemize(text):
    """A highly simplified fallback if the real phonemizer isn't available."""
    # Maps basic English chars to rough IPA equivalents to allow the pipeline to run.
    mapping = {
        'a': 'a', 'b': 'b', 'c': 'k', 'd': 'd', 'e': 'e', 'f': 'f',
        'g': 'g', 'h': 'h', 'i': 'i', 'j': 'dʒ', 'k': 'k', 'l': 'l',
        'm': 'm', 'n': 'n', 'o': 'o', 'p': 'p', 'q': 'k', 'r': 'r',
        's': 's', 't': 't', 'u': 'u', 'v': 'v', 'w': 'w', 'x': 'ks',
        'y': 'j', 'z': 'z', ' ': ' ', '\n': '\n'
    }
    return ''.join(mapping.get(c.lower(), '') for c in text)

def main():
    print("=== Pāṇinian Phase Space: IPA Dataset Compiler ===")
    
    # 1. Setup paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file_path = os.path.join(current_dir, 'input.txt')
    
    download_dataset(input_file_path)
    
    with open(input_file_path, 'r', encoding='utf-8') as f:
        data = f.read()
    
    print(f"Loaded dataset: {len(data):,} characters.")
    
    # 2. Phonemize the text
    print("Phonemizing text into pure articulatory space (IPA)...")
    if HAS_PHONEMIZER:
        # We chunk the data because passing 1MB of text to espeak at once can hang
        chunk_size = 50000
        ipa_chunks = []
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i+chunk_size]
            # preserve_punctuation=False to keep strictly to phonemes, 
            # but we keep spaces for word boundaries.
            ipa_chunk = phonemize(
                chunk, 
                language='en-us', 
                backend='espeak',
                separator=Separator(phone='', word=' ', syllable=''),
                strip=True,
                preserve_punctuation=True
            )
            ipa_chunks.append(ipa_chunk)
            print(f"  ... processed {min(i+chunk_size, len(data)):,} / {len(data):,} chars")
        ipa_text = "".join(ipa_chunks)
    else:
        ipa_text = naive_phonemize(data)
        
    print(f"Phonemization complete. IPA stream length: {len(ipa_text):,} phonemes.")
    
    # 3. Tokenize using the exact Kochen-Specker incidence basis
    print("Tokenizing via IPATokenizer (Mapping to fermionic basis states)...")
    tokenizer = IPATokenizer()
    
    # The tokenizer must convert the IPA string into a list of integers
    # representing the row index in the Incidence Matrix A.
    train_ids = tokenizer.encode(ipa_text)
    
    print(f"Tokenization complete. Generated {len(train_ids):,} topological tokens.")
    print(f"Vocabulary Size: {tokenizer.vocab_size}")
    
    # 4. Create Train/Val splits (90% / 10%)
    n = len(train_ids)
    train_data = train_ids[:int(n*0.9)]
    val_data = train_ids[int(n*0.9):]
    
    # 5. Export to binary for nanoGPT memory-mapped dataloader
    # uint16 is perfect since our vocab is ~107 (fits well within 65,535)
    train_data_np = np.array(train_data, dtype=np.uint16)
    val_data_np = np.array(val_data, dtype=np.uint16)
    
    train_data_np.tofile(os.path.join(current_dir, 'train.bin'))
    val_data_np.tofile(os.path.join(current_dir, 'val.bin'))
    
    # Save the meta information (vocab size) so train.py knows the matrix dimensions
    meta = {
        'vocab_size': tokenizer.vocab_size,
        'tokenizer_type': 'IPA_Sparsa_Basis'
    }
    with open(os.path.join(current_dir, 'meta.pkl'), 'wb') as f:
        pickle.dump(meta, f)
        
    print("\n[SUCCESS] Dataset compiled.")
    print(f"train.bin: {len(train_data_np):,} tokens")
    print(f"val.bin:   {len(val_data_np):,} tokens")
    print("Ready for nanoGPT training: `python train.py config/train_ipa.py`")

if __name__ == '__main__':
    main()
