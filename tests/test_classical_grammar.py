import pytest
from lambeq.backend.grammar import Ty
from src import classical_grammar

def test_classical_cases():
    """Test that all Greek/Latin cases are correctly initialized as Ty."""
    assert isinstance(classical_grammar.Nominative, Ty)
    assert isinstance(classical_grammar.Accusative, Ty)
    assert isinstance(classical_grammar.Genitive, Ty)
    assert isinstance(classical_grammar.Dative, Ty)
    assert isinstance(classical_grammar.Ablative, Ty)
    assert isinstance(classical_grammar.Vocative, Ty)

def test_sanskrit_cases():
    """Test that all Sanskrit cases are correctly initialized as Ty."""
    assert isinstance(classical_grammar.Sanskrit_Prathama, Ty)
    assert isinstance(classical_grammar.Sanskrit_Dvitiya, Ty)
    assert isinstance(classical_grammar.Sanskrit_Tritiya, Ty)
    assert isinstance(classical_grammar.Sanskrit_Caturthi, Ty)
    assert isinstance(classical_grammar.Sanskrit_Pancami, Ty)
    assert isinstance(classical_grammar.Sanskrit_Sasthi, Ty)
    assert isinstance(classical_grammar.Sanskrit_Saptami, Ty)
    assert isinstance(classical_grammar.Sanskrit_Sambodhana, Ty)

def test_classical_to_sanskrit_map():
    """Test the cross-linguistic mapping function."""
    mapping = classical_grammar.map_classical_to_sanskrit()
    assert isinstance(mapping, dict)
    assert len(mapping) == 6

    # Verify specific mappings
    assert classical_grammar.get_sanskrit_morpheme(classical_grammar.Nominative) == classical_grammar.Sanskrit_Prathama
    assert classical_grammar.get_sanskrit_morpheme(classical_grammar.Accusative) == classical_grammar.Sanskrit_Dvitiya
    assert classical_grammar.get_sanskrit_morpheme(classical_grammar.Genitive) == classical_grammar.Sanskrit_Sasthi
    assert classical_grammar.get_sanskrit_morpheme(classical_grammar.Dative) == classical_grammar.Sanskrit_Caturthi
    assert classical_grammar.get_sanskrit_morpheme(classical_grammar.Ablative) == classical_grammar.Sanskrit_Pancami
    assert classical_grammar.get_sanskrit_morpheme(classical_grammar.Vocative) == classical_grammar.Sanskrit_Sambodhana
