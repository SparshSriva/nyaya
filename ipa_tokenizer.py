import torch
import numpy as np
import sys
from typing import List, Dict, Tuple

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
import numpy as np
from typing import List, Dict, Tuple

class IPATokenizer:
    """
    Topologically Rigorous International Phonetic Alphabet (IPA) Tokenizer.
    Replaces arbitrary BPE with an invariant coordinate system of the human vocal tract.
    """
    def __init__(self):
        # 1. Define the Universal Phonemic Basis (Simplified for demonstration)
        # We start with the 5x5 Sparsa grid + basic vowels (Svaras)
        self.phonemes = [
            '<PAD>', '<UNK>', '<EOS>', ' ', # Special tokens
            # Sparsa (Stops/Plosives) - The Fermions
            'k', 'kʰ', 'g', 'gʱ', 'ŋ',  # Velar
            'c', 'cʰ', 'ɟ', 'ɟʱ', 'ɲ',  # Palatal
            'ʈ', 'ʈʰ', 'ɖ', 'ɖʱ', 'ɳ',  # Retroflex
            't', 'tʰ', 'd', 'dʱ', 'n',  # Dental
            'p', 'pʰ', 'b', 'bʱ', 'm',  # Labial
            # Svaras (Vowels) - The Bosons
            'a', 'i', 'u', 'e', 'o'
        ]
        
        self.vocab_size = len(self.phonemes)
        self.stoi = {p: i for i, p in enumerate(self.phonemes)}
        self.itos = {i: p for i, p in enumerate(self.phonemes)}
        
        # 2. The Phonetic Feature Matrix (Incidence Matrix A)
        # Columns: [Is_Sparsa, Is_Svara, Velar, Palatal, Retroflex, Dental, Labial, Voiced, Aspirated, Nasal]
        self.feature_names = [
            'is_sparsa', 'is_svara', 
            'velar', 'palatal', 'retroflex', 'dental', 'labial',
            'voiced', 'aspirated', 'nasal'
        ]
        self.A = self._build_feature_matrix()
        
    def _build_feature_matrix(self) -> torch.Tensor:
        """
        Constructs the exact topological coordinate system A.
        Rows: Phoneme vocabulary size
        Cols: Phonetic features
        """
        A = torch.zeros((self.vocab_size, len(self.feature_names)))
        
        for i, p in enumerate(self.phonemes):
            if p in ['<PAD>', '<UNK>', '<EOS>', ' ']:
                continue
                
            # Bosonic vs Fermionic
            if p in ['a', 'i', 'u', 'e', 'o']:
                A[i, self.feature_names.index('is_svara')] = 1.0
            else:
                A[i, self.feature_names.index('is_sparsa')] = 1.0
                
            # Spatial Coordinates (Place of Articulation)
            if p in ['k', 'kʰ', 'g', 'gʱ', 'ŋ']: A[i, self.feature_names.index('velar')] = 1.0
            if p in ['c', 'cʰ', 'ɟ', 'ɟʱ', 'ɲ']: A[i, self.feature_names.index('palatal')] = 1.0
            if p in ['ʈ', 'ʈʰ', 'ɖ', 'ɖʱ', 'ɳ']: A[i, self.feature_names.index('retroflex')] = 1.0
            if p in ['t', 'tʰ', 'd', 'dʱ', 'n']: A[i, self.feature_names.index('dental')] = 1.0
            if p in ['p', 'pʰ', 'b', 'bʱ', 'm']: A[i, self.feature_names.index('labial')] = 1.0
                
            # Spin/Isospin (Effort/Voicing)
            if p in ['g', 'gʱ', 'ɟ', 'ɟʱ', 'ɖ', 'ɖʱ', 'd', 'dʱ', 'b', 'bʱ', 'ŋ', 'ɲ', 'ɳ', 'n', 'm']:
                A[i, self.feature_names.index('voiced')] = 1.0
            if p in ['kʰ', 'gʱ', 'cʰ', 'ɟʱ', 'ʈʰ', 'ɖʱ', 'tʰ', 'dʱ', 'pʰ', 'bʱ']:
                A[i, self.feature_names.index('aspirated')] = 1.0
            if p in ['ŋ', 'ɲ', 'ɳ', 'n', 'm']:
                A[i, self.feature_names.index('nasal')] = 1.0
                
        return A

    def encode(self, ipa_string: str) -> List[int]:
        """Maps an IPA string to its exact invariant coordinate integers."""
        # Note: A real implementation would parse multi-character IPA symbols correctly.
        # This is a naive greed parser for the exact symbols defined above.
        tokens = []
        i = 0
        while i < len(ipa_string):
            # Try to match 2-char phonemes first (like pʰ)
            if i + 1 < len(ipa_string) and ipa_string[i:i+2] in self.stoi:
                tokens.append(self.stoi[ipa_string[i:i+2]])
                i += 2
            elif ipa_string[i] in self.stoi:
                tokens.append(self.stoi[ipa_string[i]])
                i += 1
            else:
                tokens.append(self.stoi['<UNK>'])
                i += 1
        return tokens

    def decode(self, tokens: List[int]) -> str:
        """Translates coordinate integers back to physical articulation."""
        return "".join([self.itos.get(t, '') for t in tokens])

    def get_sparsa_projection(self) -> torch.Tensor:
        """
        Returns the specific topological boundary vector to clamp the 'Sparsa' 
        (discrete/hard plosive) phonetic features.
        """
        boundary = torch.zeros(len(self.feature_names))
        boundary[self.feature_names.index('is_sparsa')] = 1.0
        return boundary

if __name__ == "__main__":
    print("=== IPA Tokenizer & Incidence Matrix Initialized ===")
    tokenizer = IPATokenizer()
    
    print(f"Vocab Size: {tokenizer.vocab_size}")
    print(f"Feature Matrix A Shape: {tokenizer.A.shape}")
    
    # Test encoding/decoding
    test_word = "pʰala" # Sanskrit for fruit
    tokens = tokenizer.encode(test_word)
    decoded = tokenizer.decode(tokens)
    
    print(f"\nTest Encoding: '{test_word}'")
    print(f"Tokens: {tokens}")
    print(f"Decoded: '{decoded}'")
    
    # Show the geometric feature vector for 'pʰ'
    ph_token = tokens[0]
    features = tokenizer.A[ph_token]
    print(f"\nArticulatory Coordinate Vector for 'pʰ' (Token {ph_token}):")
    for name, val in zip(tokenizer.feature_names, features):
        if val > 0:
            print(f"  + {name}")
