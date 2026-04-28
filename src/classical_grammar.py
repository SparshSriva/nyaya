from lambeq.backend.grammar import Ty

# Basic types
n = Ty('n')  # Noun
s = Ty('s')  # Sentence

# Define Lambeq string diagram types (Ty) specifically for Greek/Latin cases
Nominative = Ty('NOM')
Accusative = Ty('ACC')
Genitive = Ty('GEN')
Dative = Ty('DAT')
Ablative = Ty('ABL')
Vocative = Ty('VOC')

# Multilingual identity wires for Sanskrit morphemes (Vibhaktis)
Sanskrit_Prathama = Ty('PRATHAMA')       # 1st case (Nominative)
Sanskrit_Dvitiya = Ty('DVITIYA')         # 2nd case (Accusative)
Sanskrit_Tritiya = Ty('TRITIYA')         # 3rd case (Instrumental)
Sanskrit_Caturthi = Ty('CATURTHI')       # 4th case (Dative)
Sanskrit_Pancami = Ty('PANCAMI')         # 5th case (Ablative)
Sanskrit_Sasthi = Ty('SASTHI')           # 6th case (Genitive)
Sanskrit_Saptami = Ty('SAPTAMI')         # 7th case (Locative)
Sanskrit_Sambodhana = Ty('SAMBODHANA')   # Vocative

# Mapping rules connecting new classical cases to the multi-lingual identity wires used for Sanskrit
classical_to_sanskrit_map = {
    Nominative: Sanskrit_Prathama,
    Accusative: Sanskrit_Dvitiya,
    Genitive: Sanskrit_Sasthi,
    Dative: Sanskrit_Caturthi,
    Ablative: Sanskrit_Pancami,
    Vocative: Sanskrit_Sambodhana,
}

def get_sanskrit_morpheme(classical_case: Ty) -> Ty:
    """
    Returns the corresponding Sanskrit morpheme type for a given Greek/Latin case type.
    """
    return classical_to_sanskrit_map.get(classical_case)

def map_classical_to_sanskrit() -> dict:
    """
    Returns the full cross-linguistic mapping.
    """
    return classical_to_sanskrit_map
