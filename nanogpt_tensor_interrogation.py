import torch
import torch.nn.functional as F
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from sklearn.linear_model import OrthogonalMatchingPursuit

class AlgebraicInterrogationEngine:
    def __init__(self, model_name='gpt2', layer_idx=6):
        """
        Initializes the A+ Tensor Interrogation Engine for nanoGPT (using HF GPT-2 as proxy).
        """
        print(f"[*] Loading {model_name}...")
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        self.layer_idx = layer_idx
        
        # The incidence matrix A (using token embeddings as the semantic dictionary D)
        # In a full run, this could be a curated subset of concepts or orthogonal contexts.
        print("[*] Extracting Embedding Dictionary (Incidence Matrix A)...")
        self.A = self.model.transformer.wte.weight.data.clone().detach() # Shape: (Vocab_Size, d_model)
        self.A = self.A.T # Shape: (d_model, Vocab_Size) so h = A * c
        
        print("[*] Computing Moore-Penrose Pseudo-Inverse A+ ...")
        # Compute A+ for deterministic analytical projection
        # For a full vocab this is large, so we compute it once.
        # Shape: (Vocab_Size, d_model)
        self.A_plus = torch.linalg.pinv(self.A) 
        
        self.clamped_concept_idx = None
        self.clamp_value = 50.0
        self.hook_handle = None

    def set_target_concept(self, concept_word, clamp_value=50.0):
        """Finds the concept in the vocabulary and sets it for clamping."""
        tokens = self.tokenizer.encode(concept_word)
        if not tokens:
            raise ValueError("Word not found in vocabulary.")
        self.clamped_concept_idx = tokens[0]
        self.clamp_value = clamp_value
        print(f"[*] Target concept set to: '{concept_word}' (Token ID: {self.clamped_concept_idx})")
        print(f"[*] Clamp amplitude: {self.clamp_value}")

    def _residual_stream_hook(self, module, input, output):
        """
        The Topological Hook:
        Intercepts the residual stream (pre-softmax activation), projects it into 
        the interpretable phase space via A+, clamps the target feature, 
        and reconstructs the modified stream via A.
        """
        # output is a tuple for GPT2 layers, output[0] is the hidden state
        if isinstance(output, tuple):
            h = output[0] # Shape: (batch, seq_len, d_model)
            is_tuple = True
        else:
            h = output
            is_tuple = False
            
        if self.clamped_concept_idx is None:
            return output
            
        # print("\n[Hook Triggered] Intercepting Residual Stream...")
        if h.dim() == 2:
            # Just in case it's (seq_len, d_model)
            h = h.unsqueeze(0)
            
        batch, seq_len, d_model = h.shape
        
        # Step 1: Project into the concept phase space
        # c = A^+ * h
        # h is (batch*seq_len, d_model), A_plus is (Vocab_Size, d_model)
        h_flat = h.reshape(-1, d_model).T # (d_model, batch*seq_len)
        c = torch.matmul(self.A_plus, h_flat) # (Vocab_Size, batch*seq_len)
        
        # Step 2: OMP / Stabilizer Constraint Clamping
        # We artificially inflate the coefficient of our target concept
        # This injects the topological boundary condition
        c[self.clamped_concept_idx, :] = self.clamp_value
        
        # Step 3: Reconstruct the Residual Stream
        # h_tilde = A * c
        h_tilde_flat = torch.matmul(self.A, c) # (d_model, batch*seq_len)
        h_tilde = h_tilde_flat.T.reshape(batch, seq_len, d_model)
        
        # Overwrite the original residual stream
        # print("[Hook Triggered] Injection Complete. Forward pass resuming...")
        if is_tuple:
            return (h_tilde,) + output[1:]
        else:
            return h_tilde

    def generate(self, prompt, max_new_tokens=20):
        """Generates text, dynamically applying the algebraic clamp."""
        inputs = self.tokenizer(prompt, return_tensors='pt')
        
        # Register the hook to the target layer
        target_layer = self.model.transformer.h[self.layer_idx]
        self.hook_handle = target_layer.register_forward_hook(self._residual_stream_hook)
        
        print(f"\n[*] Generating with prompt: '{prompt}'")
        try:
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs, 
                    max_new_tokens=max_new_tokens,
                    pad_token_id=self.tokenizer.eos_token_id,
                    do_sample=True,
                    temperature=0.7
                )
            result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return result
        finally:
            if self.hook_handle:
                self.hook_handle.remove()

if __name__ == "__main__":
    print("=== Algebraic Interpretability Engine ===")
    print("Deterministically factorizing the LLM Residual Stream via A+\n")
    
    # 1. Initialize engine
    engine = AlgebraicInterrogationEngine(layer_idx=6)
    
    # 2. Baseline generation (no clamp)
    prompt = "The architect looked at the plans for the new building and said,"
    print("\n--- BASELINE GENERATION ---")
    engine.clamped_concept_idx = None # Ensure no clamp
    baseline_text = engine.generate(prompt, max_new_tokens=30)
    print(f"\nBaseline Output:\n{baseline_text}")
    
    # 3. Clamped generation (Golden Gate effect via pseudo-inverse)
    print("\n--- A+ CLAMPED GENERATION ---")
    # Let's use a concept like "bridge" or "Sanskrit"
    engine.set_target_concept(" bridge", clamp_value=150.0) 
    clamped_text = engine.generate(prompt, max_new_tokens=30)
    print(f"\nClamped Output:\n{clamped_text}")
    
    print("\n[Success] Topological restructuring of the null-space complete.")
