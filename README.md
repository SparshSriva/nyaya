# Nyāya Corpus Project

A comprehensive corpus of syllogistic reasoning following the classical Indian Nyāya tradition, designed for AI training and logical reasoning research.

## 📚 Overview

This repository contains a carefully curated corpus of **339 Nyāya syllogisms** covering diverse domains including Philosophy of Religion, Sanskrit Grammar, and general logical reasoning. Each entry follows the traditional five-part structure (Pañcāvayava) of Nyāya logic:

- **Pratijñā** (Proposition): The statement to be proven
- **Hetu** (Reason): The logical basis for the proposition  
- **Udāharaṇa** (Example): Illustrative case supporting the reason
- **Upanaya** (Application): Connection between the example and current case
- **Nigamana** (Conclusion): Final restatement confirming the proposition

## 🏗️ Repository Structure

```
nyaya/
├── nyaya_corpus_clean.jsonl          # Main corpus (339 entries)
├── corpus_analysis.ipynb             # Comprehensive analysis notebook
├── sanskrit_staging_pipeline.py      # Validation pipeline for new entries
├── HANDOFF_PROMPT.md                 # Development context and guidelines
├── corpus_statistics.json            # Detailed corpus metrics
├── Datasets/                         # Training and evaluation splits
└── staging_round_*/                  # Historical development phases
```

## 📊 Corpus Statistics

- **Total Entries**: 339 syllogisms
- **Cultural Distribution**: 73% Non-Western, 27% Western traditions
- **Primary Domains**: Philosophy (45%), Logic (32%), Sanskrit Grammar (12%)
- **Authority Sources**: Pāṇini, Aristotle, Kant, Aquinas, and contemporary scholars
- **Quality Assurance**: 100% validation through multi-round staging pipeline

## 🎯 Key Features

### Multi-Cultural Coverage
- **Sanskrit Grammar**: 39 entries covering morphology, syntax, and phonology
- **Philosophy of Religion**: 33 entries on theological reasoning
- **Classical Logic**: Traditional syllogistic forms and contemporary applications

### Quality Standards
- Rigorous validation pipeline with cultural sensitivity checks
- Proper authority attribution and scholarly grounding
- Balanced representation across logical domains and cultural traditions

### Research Applications
- AI training for logical reasoning
- Cross-cultural logic comparison studies
- Educational resources for Nyāya logic
- Computational argumentation research

## 🚀 Quick Start

### Loading the Corpus

```python
import json

# Load the main corpus
corpus = []
with open('nyaya_corpus_clean.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        corpus.append(json.loads(line))

print(f"Loaded {len(corpus)} Nyāya syllogisms")
```

### Analyzing Entries

```python
# Example: Examine a Sanskrit grammar entry
sanskrit_entries = [entry for entry in corpus 
                   if 'Pāṇini' in entry.get('grounding_authority', '')]

for entry in sanskrit_entries[:3]:
    print(f"Proposition: {entry['pratijna']}")
    print(f"Authority: {entry['grounding_authority']}")
    print("---")
```

## 📈 Development Phases

### Phase 1: Foundation (300 entries)
- Established core Nyāya structure
- Balanced cultural representation
- Quality validation framework

### Phase 2: Philosophy of Religion (33 entries)
- Theological reasoning patterns
- Cross-cultural religious logic
- Contemporary philosophical applications

### Phase 3: Sanskrit Grammar (39 entries)
- Pāṇinian grammatical analysis
- Morphological and syntactic reasoning
- Traditional Indian linguistic logic

### Future Phases
- Quantum logic applications
- Contemporary ethical reasoning
- Interdisciplinary domain expansion

## 🔧 Validation Pipeline

The repository includes `sanskrit_staging_pipeline.py` for processing new entries:

```bash
python sanskrit_staging_pipeline.py
```

**Validation Criteria:**
- Schema compliance (5-part Nyāya structure)
- Authority grounding verification
- Cultural classification accuracy
- Logical coherence assessment

## 📝 Contributing

### Adding New Entries

1. Format entries according to Nyāya schema:
```json
{
    "id": "unique_identifier",
    "pratijna": "Statement to be proven",
    "hetu": "Logical reason",
    "udaharana": "Supporting example",
    "upanaya": "Application to current case",
    "nigamana": "Concluding statement",
    "grounding_authority": "Scholarly source",
    "cultural_tradition": "Western/Non-Western",
    "stage": "production",
    "batch_id": "batch_identifier"
}
```

2. Add to `nyaya_corpus_staging.jsonl`
3. Run validation pipeline
4. Review and integrate approved entries

### Research Standards

- **Cultural Sensitivity**: Respectful representation of all traditions
- **Scholarly Rigor**: Proper attribution and authority grounding
- **Logical Validity**: Adherence to Nyāya syllogistic structure
- **Quality Assurance**: Multi-round validation and peer review

## 📚 Background & Theory

### Nyāya Logic Tradition

Nyāya (न्याय) is one of the six orthodox schools of Hindu philosophy, primarily concerned with logic, epistemology, and methodology. The five-part syllogism (Pañcāvayava) represents a complete logical argument structure that includes:

1. **Hypothesis presentation** (Pratijñā)
2. **Causal reasoning** (Hetu)  
3. **Empirical support** (Udāharaṇa)
4. **Analogical application** (Upanaya)
5. **Logical conclusion** (Nigamana)

This structure provides a more comprehensive logical framework than the three-part Aristotelian syllogism, making it valuable for AI reasoning systems.

### Research Applications

- **Computational Argumentation**: Training AI systems in structured reasoning
- **Cross-Cultural Logic**: Comparing reasoning patterns across traditions
- **Educational Technology**: Teaching logical reasoning through diverse examples
- **Philosophy of AI**: Exploring non-Western approaches to machine reasoning

## 📊 Analysis Tools

The repository includes `corpus_analysis.ipynb` with comprehensive analytics:

- Statistical distribution analysis
- Cultural representation metrics
- Authority source mapping
- Domain clustering and patterns
- Quality validation reports

## 🤝 Acknowledgments

This corpus builds upon centuries of Nyāya logical tradition while incorporating contemporary scholarly standards. Special recognition to:

- Classical Nyāya philosophers (Gautama, Vātsyāyana, Udayana)
- Modern Nyāya scholars and translators
- Cross-cultural logic researchers
- Open source community contributors

## 📄 License

This work is released under an open research license. See individual source attributions for specific scholarly works referenced in the corpus.

## 📧 Contact

For research collaboration, corpus extensions, or technical questions, please open an issue in this repository.

---

*Building bridges between ancient wisdom and modern AI through structured logical reasoning.*
