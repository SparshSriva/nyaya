#!/usr/bin/env python3
"""
Nyāya Quantum NLP Data Entry GUI
=====================================

Streamlit-based GUI for structured data entry of Sanskrit verses, translations,
and metadata. Integrates with existing parsing/diagram backend.

Features:
- Sanskrit (Devanagari) and English text entry
- Auto-fill for chandas/akshara analysis
- Manual fields for commentary/interpretation
- Backend integration for diagram generation
- Simple segmentation suggestions (placeholder for model integration)

Usage:
    streamlit run gui_app.py
"""

import streamlit as st
import json
import yaml
from pathlib import Path
import sys
import os
from datetime import datetime

# Add src to path for backend imports
sys.path.append(str(Path(__file__).parent / 'src'))

# Import our existing backend modules
try:
    from scripts.parse_ramayana_txt import extract_akshara, extract_syllables
    from scripts.chandas_features import extract_syllables, analyze_meter_pattern
    BACKEND_AVAILABLE = True
except ImportError as e:
    st.warning(f"Backend modules not fully available: {e}")
    BACKEND_AVAILABLE = False

# Configuration
DATA_DIR = Path(__file__).parent / 'data'
PROCESSED_DIR = DATA_DIR / 'processed'
DIAGRAMS_DIR = PROCESSED_DIR / 'diagrams'

# Ensure directories exist
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)

# --- New: Aṣṭādhyāyī data paths and helpers ---
ASHTA_RAW_PATH = PROCESSED_DIR / 'ashtadhyayi.jsonl'
ASHTA_RULES_PATH = PROCESSED_DIR / 'ashtadhyayi_rules.jsonl'


def _read_jsonl(path: Path):
    recs = []
    if not path.exists():
        return recs
    try:
        with path.open('r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict):
                        recs.append(obj)
                except Exception:
                    continue
    except Exception as e:
        st.warning(f"Failed to read {path.name}: {e}")
    return recs


def _load_ashtadhyayi_records():
    # Prefer rules file for enriched labels/types
    recs = _read_jsonl(ASHTA_RULES_PATH)
    if not recs:
        recs = _read_jsonl(ASHTA_RAW_PATH)
    # Normalize minimal fields
    for r in recs:
        r['id'] = str(r.get('id', '')).strip()
        r['book'] = str(r.get('book', '')).strip()
        r['chapter'] = str(r.get('chapter', '')).strip()
        r['sutra'] = str(r.get('sutra', '')).strip()
        r['sa'] = (r.get('sa') or r.get('iast') or '').strip()
        r['iast'] = (r.get('iast') or '').strip()
        r['gloss'] = (r.get('gloss') or '').strip()
        r['labels'] = list(r.get('labels') or [])
        r['rule_type'] = r.get('rule_type') or 'unspecified'
    return recs


def render_panini_mode():
    st.title('🧠 Pāṇini Mode (beta)')
    st.caption('Browse and search Pāṇini\'s Aṣṭādhyāyī. Uses processed files in data/processed/.')

    recs = _load_ashtadhyayi_records()
    if not recs:
        st.info('No Aṣṭādhyāyī data found. Run the ingestion in the notebook to create ashtadhyayi.jsonl (and ashtadhyayi_rules.jsonl).')
        return

    # Sidebar filters
    with st.sidebar:
        st.header('🧠 Pāṇini Filters')
        q = st.text_input('Search (ID or keyword)', value=st.session_state.get('panini_q', ''))
        st.session_state['panini_q'] = q
        book_opt = ['Any'] + [str(i) for i in range(1, 9)]
        chap_opt = ['Any'] + [str(i) for i in range(1, 5)]
        book_sel = st.selectbox('Book (Adhyāya group)', book_opt, index=0)
        chap_sel = st.selectbox('Chapter (Pāda)', chap_opt, index=0)
        # Collect all labels present
        all_labels = sorted({lab for r in recs for lab in (r.get('labels') or [])})
        labels_sel = st.multiselect('Labels', options=all_labels, default=[])
        rule_type_sel = st.selectbox('Rule Type', options=['Any', 'operational', 'meta', 'unspecified'], index=0)
        max_n = st.slider('Max results', min_value=10, max_value=500, value=100, step=10)

    # Apply filters
    def _match(r):
        if book_sel != 'Any' and r.get('book') != book_sel:
            return False
        if chap_sel != 'Any' and r.get('chapter') != chap_sel:
            return False
        if rule_type_sel != 'Any' and r.get('rule_type') != rule_type_sel:
            return False
        if labels_sel:
            rlabs = set(r.get('labels') or [])
            if not set(labels_sel).issubset(rlabs):
                return False
        if q:
            qs = q.strip().lower()
            hay = ' '.join([
                r.get('id', ''),
                r.get('sa', ''),
                r.get('iast', ''),
                r.get('gloss', ''),
                ' '.join(r.get('labels') or [])
            ]).lower()
            if qs not in hay:
                return False
        return True

    filtered = [r for r in recs if _match(r)]
    st.write(f"Found {len(filtered)} matching sūtras.")

    # Sort by numeric id if possible
    def _id_key(sid):
        try:
            a, b, c = sid.split('.')
            return (int(a), int(b), int(c))
        except Exception:
            return (999, 999, 999)

    filtered.sort(key=lambda r: _id_key(r.get('id', '')))

    # Display results
    for r in filtered[:max_n]:
        header = f"{r.get('id', '')} — {r.get('sa', r.get('iast', ''))[:120]}"
        with st.expander(header):
            colA, colB = st.columns([2, 1])
            with colA:
                st.markdown(f"**ID:** {r.get('id','')}")
                if r.get('sa'):
                    st.markdown(f"**Sanskrit:** {r['sa']}")
                if r.get('iast'):
                    st.markdown(f"**IAST:** {r['iast']}")
                if r.get('gloss'):
                    st.markdown(f"**Gloss:** {r['gloss']}")
                if r.get('labels'):
                    st.markdown(f"**Labels:** {', '.join(r['labels'])}")
                st.markdown(f"**Rule Type:** {r.get('rule_type','unspecified')}")
                if r.get('refs'):
                    st.markdown(f"**Refs:** {', '.join(map(str, r.get('refs'))) }")
                if r.get('source_tags'):
                    st.caption(f"Source: {', '.join(map(str, r.get('source_tags')))}")
            with colB:
                # External links
                sid = r.get('id', '')
                ws_link = f"https://sa.wikisource.org/w/index.php?search={sid}"
                st.markdown(f"[🔎 Wikisource search]({ws_link})")
                # Diagram placeholder
                try:
                    preview = generate_diagram_placeholder(r.get('sa', r.get('iast','')), language='sa')
                except Exception:
                    preview = 'Diagram preview unavailable.'
                st.text_area('Diagram preview', value=preview, height=150, key=f"diag_{sid}")
            # Conditions / outputs placeholders if present
            if isinstance(r.get('conditions'), list) or isinstance(r.get('outputs'), list):
                with st.container():
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write('Conditions:')
                        for cond in (r.get('conditions') or []):
                            st.write(f"• {cond}")
                    with c2:
                        st.write('Outputs:')
                        for out in (r.get('outputs') or []):
                            st.write(f"• {out}")

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'verse_data' not in st.session_state:
        st.session_state.verse_data = {}
    if 'current_verse_id' not in st.session_state:
        st.session_state.current_verse_id = '1.1.1'
    if 'saved_verses' not in st.session_state:
        st.session_state.saved_verses = load_existing_verses()
    if 'navigation_mode' not in st.session_state:
        st.session_state.navigation_mode = 'traditional'  # 'traditional' or 'story_units'
    if 'story_units' not in st.session_state:
        st.session_state.story_units = load_story_units()
    if 'current_story_unit' not in st.session_state:
        st.session_state.current_story_unit = 'unit_1'
    # New: app mode default
    if 'app_mode' not in st.session_state:
        st.session_state.app_mode = 'Verse Entry'

def load_story_units():
    """Load story unit definitions from YAML file."""
    units_file = PROCESSED_DIR / 'story_units.yaml'
    default_units = {
        'unit_1': {
            'title': 'Sage\'s Question',
            'description': 'Valmiki asks Narada about the most virtuous person',
            'verses': ['1.1.1', '1.1.2', '1.1.3', '1.1.4', '1.1.5'],
            'themes': ['inquiry', 'virtue', 'dialogue']
        },
        'unit_2': {
            'title': 'Description of Rama',
            'description': 'Narada describes Rama\'s qualities',
            'verses': ['1.1.6', '1.1.7', '1.1.8', '1.1.9', '1.1.10'],
            'themes': ['character', 'heroism', 'divine_qualities']
        }
    }
    
    if units_file.exists():
        try:
            with open(units_file, 'r', encoding='utf-8') as f:
                import yaml
                return yaml.safe_load(f)
        except Exception as e:
            st.warning(f"Error loading story units: {e}")
    
    return default_units

def save_story_units(units):
    """Save story unit definitions to YAML file."""
    units_file = PROCESSED_DIR / 'story_units.yaml'
    try:
        with open(units_file, 'w', encoding='utf-8') as f:
            import yaml
            yaml.dump(units, f, default_flow_style=False, allow_unicode=True)
    except Exception as e:
        st.error(f"Error saving story units: {e}")

def load_existing_verses():
    """Load existing verse data from JSONL file.
    Prefer GUI save file; fall back to seed file if exists.
    """
    gui_file = PROCESSED_DIR / 'gui_verses.jsonl'
    seed_file = PROCESSED_DIR / 'bk1_sarga1_verses.jsonl'
    verses: dict[str, dict] = {}

    # Read seed first, then GUI saves to override
    for jsonl_file in [seed_file, gui_file]:
        if jsonl_file.exists():
            try:
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            verse = json.loads(line.strip())
                            if isinstance(verse, dict) and 'id' in verse:
                                verses[verse['id']] = verse
                        except Exception:
                            # skip bad lines
                            continue
            except Exception as e:
                st.error(f"Error loading {jsonl_file.name}: {e}")
    return verses

def save_verse_data(verse_id, data):
    """Save verse data to session state and persistent storage."""
    st.session_state.saved_verses[verse_id] = data
    
    # Save to JSONL file
    jsonl_file = PROCESSED_DIR / 'gui_verses.jsonl'
    try:
        # Write all verses
        with open(jsonl_file, 'w', encoding='utf-8') as f:
            for vid, vdata in st.session_state.saved_verses.items():
                f.write(json.dumps(vdata, ensure_ascii=False) + '\n')
        st.success(f"Saved verse {verse_id}")
    except Exception as e:
        st.error(f"Error saving verse: {e}")


def build_verse_record(verse_id: str, sanskrit_verse: str, english_translation: str) -> dict:
    """Build a complete verse record from current UI/session state."""
    data = st.session_state.verse_data

    # Navigation context
    nav_ctx = {
        'story_unit': st.session_state.current_story_unit if st.session_state.navigation_mode == 'story_units' else None,
        'themes': st.session_state.story_units.get(st.session_state.current_story_unit, {}).get('themes', []) if st.session_state.navigation_mode == 'story_units' else []
    }

    record = {
        'id': verse_id or 'unknown',
        'book': verse_id.split('.')[0] if verse_id and '.' in verse_id else '1',
        'sarga': verse_id.split('.')[1] if verse_id and '.' in verse_id else '1',
        'sa_verse': (sanskrit_verse or data.get('sa_verse', '')).strip(),
        'en': (english_translation or data.get('en', '')).strip(),
        'sa_segments': data.get('sa_segments', []),
        'en_segments': data.get('en_segments', []),
        'word_analysis': data.get('word_analysis', {}),
        'grammar_config': data.get('grammar_config', {}),
        'commentary': data.get('commentary', ''),
        'word_glosses': data.get('word_glosses', []),
        'chandas': data.get('chandas', {}),
        'akshara_tokens': data.get('akshara_tokens', []),
        'akshara_breakdown': data.get('akshara_breakdown', ''),
        'suggested_sa_tokens': data.get('suggested_sa_tokens', []),
        'suggested_en_tokens': data.get('suggested_en_tokens', []),
        'generated_translations': data.get('generated_translations', {}),
        'translation_matrix': data.get('translation_matrix', {}),
        'navigation_context': nav_ctx,
        'created_time': data.get('created_time') or datetime.now().isoformat(),
        'modified_time': datetime.now().isoformat(),
        'source': 'gui_entry',
        'version': '2.0'
    }
    return record

def auto_fill_chandas(sanskrit_text):
    """Auto-fill chandas analysis using backend."""
    if not BACKEND_AVAILABLE or not sanskrit_text.strip():
        return {"syllables": [], "pattern": [], "meter": "unknown"}
    
    try:
        # Simple syllable extraction (fallback if backend not available)
        import re
        # Basic syllable segmentation for Sanskrit
        syllables = re.findall(r'[अ-ह][्]?[अ-ौ]?', sanskrit_text)
        
        # Simple laghu/guru pattern (L=light, G=heavy)
        pattern = []
        for syl in syllables:
            if len(syl) > 2 or any(long_vowel in syl for long_vowel in ['आ', 'ई', 'ऊ', 'ए', 'ऐ', 'ओ', 'औ']):
                pattern.append('G')  # Heavy/Guru
            else:
                pattern.append('L')  # Light/Laghu
        
        # Simple meter identification
        pattern_str = ''.join(pattern)
        meter = "unknown"
        if len(pattern) == 8:
            if pattern_str == "LGLLGLGL":
                meter = "anuṣṭubh"
            elif pattern_str.startswith("LG"):
                meter = "anuṣṭubh-variant"
        
        return {
            "syllables": syllables,
            "pattern": pattern,
            "meter": meter,
            "analysis_time": datetime.now().isoformat()
        }
    except Exception as e:
        st.error(f"Auto-fill chandas failed: {e}")
        return {"syllables": [], "pattern": [], "meter": "error"}

def auto_fill_akshara(sanskrit_text):
    """Auto-fill akshara tokenization using backend."""
    if not BACKEND_AVAILABLE or not sanskrit_text.strip():
        return []
    
    try:
        # Simple akshara segmentation (fallback)
        import re
        # Split on vowel boundaries and consonant clusters
        tokens = re.findall(r'[अ-ह][्]?[अ-ौ]?|[क-ह][्][क-ह]?', sanskrit_text)
        return [t for t in tokens if t.strip()]
    except Exception as e:
        st.error(f"Auto-fill akshara failed: {e}")
        return []

def generate_lambeq_code(word_assignments):
    """Generate lambeq-ready Python code from word type assignments."""
    
    # Generate word definitions
    word_defs = []
    word_names = []
    
    for word, type_expr in word_assignments.items():
        # Clean word name for Python variable
        clean_name = word.replace('ः', '').replace('ं', '').replace('्', '')
        var_name = f"word_{clean_name}"
        word_names.append((var_name, word))
        
        # Generate Word() definition
        word_def = f"{var_name} = Word('{word}', {type_expr})"
        word_defs.append(word_def)
    
    # Generate imports
    imports = """from lambeq.backend.grammar import Word, Ty, Cup, Cap, Id
from lambeq.backend.drawing import draw

# Type definitions
n = Ty('n')    # noun phrase
s = Ty('s')    # sentence
pi = Ty('pi')  # nominative
o = Ty('o')    # accusative
dh = Ty('dh')  # dhatu/root
p = Ty('p')    # predicate"""
    
    # Generate word definitions section
    word_definitions = "\n# Word definitions\n" + "\n".join(word_defs)
    
    # Generate diagram construction
    if len(word_names) > 1:
        word_vars = [name for name, _ in word_names]
        diagram_construction = f"""
# Diagram construction
words = [{', '.join(word_vars)}]
sentence = {'@ '.join(word_vars)}

# Draw the sentence
draw(sentence)

# Apply connections (add your Cup/Cap rules here)
# Example: cups = Cup(pi, pi.r) @ Id(s) @ Cup(o.l, o)
# diagram = sentence >> cups
# draw(diagram)"""
    else:
        diagram_construction = "\n# Add more words to generate diagram construction"
    
    return {
        'imports': imports,
        'word_definitions': word_definitions,
        'diagram_construction': diagram_construction,
        'full_code': imports + word_definitions + diagram_construction
    }

def simple_segmentation_suggest(text, language='en'):
    """Simple segmentation suggestions (placeholder for model integration)."""
    if not text.strip():
        return []
    
    # Placeholder: basic tokenization
    if language == 'en':
        # Simple English tokenization
        import re
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens
    else:
        # Sanskrit: basic space-based with punctuation removal
        import re
        text = re.sub(r'[।॥]', ' ', text)
        tokens = [t.strip() for t in text.split() if t.strip()]
        return tokens

def generate_diagram_placeholder(text, language='en'):
    """Generate diagram placeholder (backend integration point)."""
    if not text.strip():
        return "No text provided"
    
    # Placeholder for actual diagram generation
    token_count = len(simple_segmentation_suggest(text, language))
    
    placeholder = f"""
    📊 DIAGRAM PLACEHOLDER ({language.upper()})
    
    Text: {text[:50]}{'...' if len(text) > 50 else ''}
    Tokens: {token_count}
    
    [Future: lambeq diagram visualization here]
    Backend Status: {'✓ Available' if BACKEND_AVAILABLE else '⚠ Limited'}
    """
    
    return placeholder

def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Nyāya Quantum NLP Data Entry",
        page_icon="📜",
        layout="wide"
    )
    
    initialize_session_state()
    
    # New: app mode selection early in sidebar
    with st.sidebar:
        st.header('🧭 App Mode')
        app_mode = st.radio(
            'Choose mode',
            options=['Verse Entry', 'Pāṇini Mode'],
            index=0 if st.session_state.app_mode == 'Verse Entry' else 1
        )
        st.session_state.app_mode = app_mode
    
    # If Pāṇini Mode selected, render and exit
    if st.session_state.app_mode == 'Pāṇini Mode':
        render_panini_mode()
        return

    st.title("📜 Nyāya Quantum NLP Data Entry")
    st.markdown("*Structured data entry for Sanskrit verses and translations*")
    
    # Sidebar: Verse selection and navigation
    with st.sidebar:
        st.header("📖 Verse Navigation")
        
        # Verse ID input
        verse_id = st.text_input(
            "Verse ID",
            value=st.session_state.current_verse_id,
            help="Format: book.sarga.verse (e.g., 1.1.1)"
        )
        
        if verse_id != st.session_state.current_verse_id:
            st.session_state.current_verse_id = verse_id
        
        # Load existing verse if available
        if verse_id in st.session_state.saved_verses:
            if st.button("📂 Load Existing"):
                st.session_state.verse_data = st.session_state.saved_verses[verse_id].copy()
                st.success(f"Loaded verse {verse_id}")
        
        # Quick navigation
        st.subheader("Quick Jump")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Previous"):
                # Simple increment logic for demo
                if verse_id:
                    parts = verse_id.split('.')
                    if len(parts) == 3:
                        v = max(1, int(parts[2]) - 1)
                        new_id = f"{parts[0]}.{parts[1]}.{v}"
                        st.session_state.current_verse_id = new_id
                        st.rerun()
        
        with col2:
            if st.button("➡️ Next"):
                if verse_id:
                    parts = verse_id.split('.')
                    if len(parts) == 3:
                        v = int(parts[2]) + 1
                        new_id = f"{parts[0]}.{parts[1]}.{v}"
                        st.session_state.current_verse_id = new_id
                        st.rerun()
        
        # Navigation mode toggle
        st.subheader("📚 Navigation Mode")
        nav_mode = st.radio(
            "View Mode",
            ['traditional', 'story_units'],
            index=0 if st.session_state.navigation_mode == 'traditional' else 1,
            format_func=lambda x: "Book/Chapter/Verse" if x == 'traditional' else "Story Units"
        )
        
        if nav_mode != st.session_state.navigation_mode:
            st.session_state.navigation_mode = nav_mode
            st.rerun()
        
        # Traditional navigation
        if st.session_state.navigation_mode == 'traditional':
            st.write("**Traditional Structure:**")
            
            # Book selection
            book_num = st.selectbox("Book", [1, 2, 3, 4, 5, 6, 7], index=0)
            
            # Chapter/Sarga selection
            if book_num == 1:
                chapter_options = list(range(1, 78))  # Balakanda has 77 sargas
            else:
                chapter_options = list(range(1, 50))  # Placeholder for other books
            
            chapter_num = st.selectbox("Sarga (Chapter)", chapter_options, index=0)
            
            # Verse selection
            verse_num = st.number_input("Verse", min_value=1, max_value=100, value=1)
            
            new_verse_id = f"{book_num}.{chapter_num}.{verse_num}"
            if new_verse_id != st.session_state.current_verse_id:
                if st.button("📍 Go to Verse"):
                    st.session_state.current_verse_id = new_verse_id
                    st.rerun()
        
        # Story units navigation
        else:
            st.write("**Story Units:**")
            
            # Display story units
            for unit_id, unit_data in st.session_state.story_units.items():
                with st.expander(f"📖 {unit_data['title']}", expanded=(unit_id == st.session_state.current_story_unit)):
                    st.write(f"**Description:** {unit_data['description']}")
                    st.write(f"**Verses:** {', '.join(unit_data['verses'])}")
                    st.write(f"**Themes:** {', '.join(unit_data['themes'])}")
                    
                    if st.button(f"Work on {unit_data['title']}", key=f"work_{unit_id}"):
                        st.session_state.current_story_unit = unit_id
                        st.session_state.current_verse_id = unit_data['verses'][0]
                        st.rerun()
                    
                    # Quick verse navigation within unit
                    verse_cols = st.columns(len(unit_data['verses']))
                    for i, v_id in enumerate(unit_data['verses']):
                        with verse_cols[i]:
                            if st.button(v_id, key=f"verse_{unit_id}_{v_id}"):
                                st.session_state.current_verse_id = v_id
                                st.rerun()
            
            # Add new story unit
            if st.button("➕ Add Story Unit"):
                new_unit_id = f"unit_{len(st.session_state.story_units) + 1}"
                st.session_state.story_units[new_unit_id] = {
                    'title': 'New Story Unit',
                    'description': 'Description here',
                    'verses': ['1.1.1'],
                    'themes': ['theme1']
                }
                save_story_units(st.session_state.story_units)
                st.rerun()
        
        # Saved verses list
        st.subheader("💾 Saved Verses")
        for saved_id in sorted(st.session_state.saved_verses.keys()):
            if st.button(f"📄 {saved_id}", key=f"load_{saved_id}"):
                st.session_state.current_verse_id = saved_id
                st.session_state.verse_data = st.session_state.saved_verses[saved_id].copy()
                st.rerun()

    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header(f"✏️ Editing Verse {verse_id}")
        
        # Core text fields
        st.subheader("📝 Core Text")
        
        # Sanskrit verse
        sanskrit_verse = st.text_area(
            "Sanskrit Verse (Devanagari)",
            value=st.session_state.verse_data.get('sa_verse', ''),
            height=100,
            help="Enter the Sanskrit verse in Devanagari script"
        )
        
        # English translation
        english_translation = st.text_area(
            "English Translation",
            value=st.session_state.verse_data.get('en', ''),
            height=80,
            help="Enter the English translation"
        )

    # Akshara and Hierarchical Analysis section
    st.subheader("🔡 Akshara Phonetic Breakdown (Reading Guide)")
    
    # Akshara phonetic breakdown exactly as in source data
    akshara_breakdown = st.text_area(
        "Akshara tokens (line-by-line as in source)",
        value=st.session_state.verse_data.get('akshara_breakdown', ''),
        height=80,
        help="Enter phonetic breakdown exactly as formatted in source data - assists in reading"
    )
    st.session_state.verse_data['akshara_breakdown'] = akshara_breakdown
    
    # Hierarchical Word Analysis
    st.subheader("📚 Hierarchical Word Analysis")
    st.write("**Structure**: Sentence → Words → Word Parts (morphemes/roots/affixes) → Multi-language Translations")
    st.info("💡 **Vision**: Translate at morpheme level for scalable multilingual auto-generation")
    
    # Language configuration
    st.write("**🌐 Language Configuration:**")
    col_lang1, col_lang2 = st.columns([2, 1])
    
    with col_lang1:
        # Get current languages or default
        if 'translation_languages' not in st.session_state.verse_data:
            st.session_state.verse_data['translation_languages'] = ['sanskrit', 'hindi_roman', 'english']
        
        available_languages = ['sanskrit', 'hindi_roman', 'english', 'hindi_devanagari', 'tamil', 'telugu', 'gujarati', 'bengali', 'german', 'french', 'spanish', 'chinese', 'japanese']
        
        selected_languages = st.multiselect(
            "Active Translation Languages",
            options=available_languages,
            default=st.session_state.verse_data['translation_languages'],
            help="Select languages for morpheme-level translation. More languages = more auto-generation possibilities!"
        )
        
        if selected_languages != st.session_state.verse_data['translation_languages']:
            st.session_state.verse_data['translation_languages'] = selected_languages
    
    with col_lang2:
        st.write(f"**Active:** {len(selected_languages)} languages")
        st.write(f"**Morphemes × Languages:** {len(st.session_state.verse_data.get('word_analysis', {})) * len(selected_languages)} translations")
    
    # Initialize word analysis structure if not exists
    if 'word_analysis' not in st.session_state.verse_data:
        st.session_state.verse_data['word_analysis'] = {}
    
    # Number of words control
    num_words = st.number_input("Number of words in verse", min_value=1, max_value=20, 
                               value=len(st.session_state.verse_data['word_analysis']) or 3)
    
    # Adjust word analysis structure
    current_words = len(st.session_state.verse_data['word_analysis'])
    if num_words > current_words:
        for word_idx in range(current_words, num_words):
            word_key = f"word_{word_idx + 1}"
            # Initialize with empty translations for all selected languages
            initial_part = {}
            for lang in selected_languages:
                initial_part[lang] = ''
            initial_part['grammar_type'] = ''
            
            st.session_state.verse_data['word_analysis'][word_key] = {
                'sanskrit_word': '',
                'parts': [initial_part],
                'grammar_type': '',
                'identity_connections': []
            }
    elif num_words < current_words:
        # Remove excess words
        words_to_remove = [f"word_{i+1}" for i in range(num_words, current_words)]
        for word_key in words_to_remove:
            if word_key in st.session_state.verse_data['word_analysis']:
                del st.session_state.verse_data['word_analysis'][word_key]
    
    # Create hierarchical structure for each word
    for word_idx in range(num_words):
        word_key = f"word_{word_idx + 1}"
        
        with st.expander(f"📖 Sn_word_{word_idx + 1}", expanded=word_idx == 0):
            # Ensure word data exists
            if word_key not in st.session_state.verse_data['word_analysis']:
                initial_part = {}
                for lang in selected_languages:
                    initial_part[lang] = ''
                initial_part['grammar_type'] = ''
                
                st.session_state.verse_data['word_analysis'][word_key] = {
                    'sanskrit_word': '',
                    'parts': [initial_part],
                    'grammar_type': '',
                    'identity_connections': []
                }
            
            word_data = st.session_state.verse_data['word_analysis'][word_key]
            
            # Sanskrit word input
            word_data['sanskrit_word'] = st.text_input(
                f"Sanskrit Word {word_idx + 1}",
                value=word_data['sanskrit_word'],
                key=f"sanskrit_{word_idx}",
                help="The complete Sanskrit word"
            )
            
            # Word parts breakdown with multilingual support
            st.write("**📝 Morpheme-Level Multilingual Translation:**")
            st.caption("💡 Each part gets translated in all active languages for maximum reusability")
            
            # Number of parts for this word
            current_parts = len(word_data['parts'])
            num_parts = st.number_input(
                f"Number of morphemes/parts in word {word_idx + 1}",
                min_value=1, max_value=10, value=current_parts,
                key=f"num_parts_{word_idx}",
                help="Break down into meaningful morphological units (root, prefix, suffix, etc.)"
            )
            
            # Adjust parts array and ensure all parts have all languages
            if num_parts > current_parts:
                for _ in range(num_parts - current_parts):
                    new_part = {}
                    for lang in selected_languages:
                        new_part[lang] = ''
                    new_part['grammar_type'] = ''
                    word_data['parts'].append(new_part)
            elif num_parts < current_parts:
                word_data['parts'] = word_data['parts'][:num_parts]
            
            # Ensure all existing parts have all languages
            for part in word_data['parts']:
                for lang in selected_languages:
                    if lang not in part:
                        part[lang] = ''
                if 'grammar_type' not in part:
                    part['grammar_type'] = ''
            
            # Create sub-expandable sections for each part
            for part_idx in range(num_parts):
                with st.expander(f"🔹 Morpheme {part_idx + 1} of word {word_idx + 1}", expanded=part_idx == 0 and word_idx == 0):
                    st.write(f"**Translating morpheme {part_idx + 1} across {len(selected_languages)} languages:**")
                    
                    # Render inputs in rows of up to 3 columns. If <=3, render a single row.
                    if len(selected_languages) <= 3:
                        row_langs = selected_languages
                        cols = st.columns(len(row_langs))
                        for col_idx, lang in enumerate(row_langs):
                            with cols[col_idx]:
                                # Language-specific labels and help text
                                if lang == 'sanskrit':
                                    label = "Sanskrit (root/affix)"
                                    help_text = "Sanskrit morpheme breakdown"
                                elif lang == 'hindi_roman':
                                    label = "Hindi (roman script)"
                                    help_text = "Hindi translation in roman script"
                                elif lang == 'hindi_devanagari':
                                    label = "Hindi (देवनागरी)"
                                    help_text = "Hindi translation in Devanagari script"
                                elif lang == 'english':
                                    label = "English"
                                    help_text = "English translation"
                                else:
                                    label = lang.replace('_', ' ').title()
                                    help_text = f"{lang.title()} translation"
                                
                                word_data['parts'][part_idx][lang] = st.text_input(
                                    label,
                                    value=word_data['parts'][part_idx].get(lang, ''),
                                    key=f"{lang}_{word_idx}_{part_idx}",
                                    help=help_text
                                )
                    else:
                        for row_start in range(0, len(selected_languages), 3):
                            row_langs = selected_languages[row_start:row_start + 3]
                            cols = st.columns(len(row_langs))
                            for col_idx, lang in enumerate(row_langs):
                                with cols[col_idx]:
                                    if lang == 'sanskrit':
                                        label = "Sanskrit (root/affix)"
                                        help_text = "Sanskrit morpheme breakdown"
                                    elif lang == 'hindi_roman':
                                        label = "Hindi (roman script)"
                                        help_text = "Hindi translation in roman script"
                                    elif lang == 'hindi_devanagari':
                                        label = "Hindi (देवनागरी)"
                                        help_text = "Hindi translation in Devanagari script"
                                    elif lang == 'english':
                                        label = "English"
                                        help_text = "English translation"
                                    else:
                                        label = lang.replace('_', ' ').title()
                                        help_text = f"{lang.title()} translation"
                                    
                                    word_data['parts'][part_idx][lang] = st.text_input(
                                        label,
                                        value=word_data['parts'][part_idx].get(lang, ''),
                                        key=f"{lang}_{word_idx}_{part_idx}",
                                        help=help_text
                                    )
                    
                    # Grammar type for this morpheme
                    word_data['parts'][part_idx]['grammar_type'] = st.text_input(
                        "Morpheme Grammar Type",
                        value=word_data['parts'][part_idx].get('grammar_type', ''),
                        key=f"morpheme_grammar_{word_idx}_{part_idx}",
                        help="e.g., root, suffix, prefix, case_marker, verb_ending"
                    )
            
            # Grammar configuration for this word
            st.write("**Grammar & Connections:**")
            col_g1, col_g2 = st.columns([1, 1])
            
            with col_g1:
                word_data['grammar_type'] = st.text_input(
                    f"Grammar Type",
                    value=word_data['grammar_type'],
                    key=f"grammar_{word_idx}",
                    help="e.g., n (noun), pi (nominative), o (accusative), s (sentence), pi.r@s@o.l"
                )
            
            with col_g2:
                # Identity connections for long-range dependencies
                st.write("🔗 Identity Wire Connections:")
                connect_to_word = st.selectbox(
                    "Connect to word",
                    options=["None"] + [f"word_{i+1}" for i in range(num_words) if i != word_idx],
                    key=f"connect_{word_idx}"
                )
                
                if connect_to_word != "None":
                    wire_type = st.selectbox(
                        "Connection type", 
                        ['subject_verb', 'verb_object', 'adj_noun', 'custom'],
                        key=f"wire_type_{word_idx}"
                    )
                    
                    custom_connection = "Cup(type1, type2)"
                    if wire_type == 'custom':
                        custom_connection = st.text_input(
                            "Custom connection", 
                            value="Cup(type1, type2)",
                            key=f"custom_conn_{word_idx}"
                        )
                    
                    if st.button(f"Add Identity Wire", key=f"add_wire_{word_idx}"):
                        connection = {
                            'from_word': word_key,
                            'to_word': connect_to_word,
                            'wire_type': wire_type,
                            'custom_connection': custom_connection
                        }
                        word_data['identity_connections'].append(connection)
                        st.success(f"Added identity wire: {word_key} → {connect_to_word}")
                        st.rerun()
            
            # Display existing connections
            if word_data['identity_connections']:
                st.write("**Existing connections:**")
                for i, conn in enumerate(word_data['identity_connections']):
                    col_conn1, col_conn2 = st.columns([3, 1])
                    with col_conn1:
                        st.write(f"• {conn['from_word']} → {conn['to_word']} ({conn['wire_type']})")
                    with col_conn2:
                        if st.button("Remove", key=f"remove_conn_{word_idx}_{i}"):
                            word_data['identity_connections'].pop(i)
                            st.rerun()
        
        # Grammar Configuration Section
        st.subheader("⚙️ Grammar Configuration")
        
        # Display current grammar assignments from word analysis
        grammar_assignments = []
        for word_key, word_data in st.session_state.verse_data.get('word_analysis', {}).items():
            if word_data.get('grammar_type'):
                grammar_assignments.append(f"{word_data['sanskrit_word']}={word_data['grammar_type']}")
        
        current_grammar = '\n'.join(grammar_assignments)
        st.write("**Current Grammar Assignments:**")
        if current_grammar:
            st.code(current_grammar, language="text")
        else:
            st.write("*No grammar assignments yet. Add words above.*")
        
        # LabeQ Code Generation
        st.subheader("🔧 LambeQ Code Generation")
        if st.button("🐍 Generate Python Code"):
            # Generate lambeq code from current word analysis
            code_lines = ["# Generated lambeq code", "from lambeq import *", ""]
            
            # Add type definitions
            for word_key, word_data in st.session_state.verse_data.get('word_analysis', {}).items():
                if word_data.get('grammar_type'):
                    code_lines.append(f"{word_data['sanskrit_word']}_type = Ty('{word_data['grammar_type']}')")
            
            code_lines.append("")
            
            # Add boxes
            for word_key, word_data in st.session_state.verse_data.get('word_analysis', {}).items():
                if word_data.get('sanskrit_word') and word_data.get('grammar_type'):
                    code_lines.append(f"{word_data['sanskrit_word']}_box = Box('{word_data['sanskrit_word']}', Ty('s'), {word_data['sanskrit_word']}_type)")
            
            code_lines.append("")
            
            # Add identity wires for long-range connections
            for word_key, word_data in st.session_state.verse_data.get('word_analysis', {}).items():
                for conn in word_data.get('identity_connections', []):
                    code_lines.append(f"# Identity wire: {conn['from_word']} -> {conn['to_word']}")
                    code_lines.append(f"id_wire_{conn['from_word']}_{conn['to_word']} = Id(Ty('{conn['wire_type']}'))")
            
            generated_code = '\n'.join(code_lines)
            st.code(generated_code, language="python")
            
            # Save to file option
            if st.button("💾 Save Generated Code"):
                verse_id = st.session_state.get('current_verse_id', '1_1_1')
                code_file = PROCESSED_DIR / f"generated_code_{verse_id.replace('.', '_')}.py"
                try:
                    with open(code_file, 'w', encoding='utf-8') as f:
                        f.write(generated_code)
                    st.success(f"Code saved to {code_file}")
                except Exception as e:
                    st.error(f"Error saving code: {e}")
        
        # Auto-Generation Features
        st.subheader("🤖 Auto-Generation Features")
        st.write("**Leverage morpheme-level translations for powerful auto-generation:**")
        
        col_auto1, col_auto2 = st.columns(2)
        
        with col_auto1:
            if st.button("🔄 Auto-Generate Full Translations", help="Generate complete translations from morpheme translations"):
                if st.session_state.verse_data.get('word_analysis'):
                    generated_translations = {}
                    selected_languages = st.session_state.verse_data.get('translation_languages', ['sanskrit', 'hindi_roman', 'english'])
                    
                    for lang in selected_languages:
                        if lang == 'sanskrit':
                            continue  # Skip Sanskrit as it's the source
                        
                        full_translation_parts = []
                        for word_key, word_data in st.session_state.verse_data['word_analysis'].items():
                            word_parts = []
                            for part in word_data.get('parts', []):
                                if part.get(lang):
                                    word_parts.append(part[lang])
                            
                            if word_parts:
                                full_translation_parts.append(' '.join(word_parts))
                        
                        if full_translation_parts:
                            generated_translations[lang] = ' '.join(full_translation_parts)
                    
                    # Store generated translations
                    if 'generated_translations' not in st.session_state.verse_data:
                        st.session_state.verse_data['generated_translations'] = {}
                    
                    st.session_state.verse_data['generated_translations'].update(generated_translations)
                    
                    st.success(f"Generated full translations in {len(generated_translations)} languages!")
                    st.rerun()
        
        with col_auto2:
            if st.button("📊 Generate Translation Matrix", help="Create morpheme × language translation matrix"):
                if st.session_state.verse_data.get('word_analysis'):
                    selected_languages = st.session_state.verse_data.get('translation_languages', ['sanskrit', 'hindi_roman', 'english'])
                    
                    # Create translation matrix
                    matrix_data = []
                    
                    for word_key, word_data in st.session_state.verse_data['word_analysis'].items():
                        # FIX: enumerate parts to get (index, part)
                        for part_idx, part in enumerate(word_data.get('parts', [])):
                            row = {
                                'word': word_data.get('sanskrit_word', ''),
                                'morpheme_id': f"{word_key}_part_{part_idx + 1}",
                                'grammar_type': part.get('grammar_type', '')
                            }
                            
                            for lang in selected_languages:
                                row[lang] = part.get(lang, '')
                            
                            matrix_data.append(row)
                    
                    # Store matrix
                    st.session_state.verse_data['translation_matrix'] = {
                        'languages': selected_languages,
                        'matrix': matrix_data,
                        'generated_time': datetime.now().isoformat()
                    }
                    
                    st.success("Generated translation matrix for data export!")
                    st.rerun()
        
        # Display generated translations
        if st.session_state.verse_data.get('generated_translations'):
            st.write("**🎯 Auto-Generated Full Translations:**")
            for lang, translation in st.session_state.verse_data['generated_translations'].items():
                with st.expander(f"{lang.replace('_', ' ').title()} Translation"):
                    st.write(translation)
                    
                    # Option to copy to main translation field
                    if lang == 'english' and st.button(f"📋 Use as Main English Translation", key=f"use_{lang}"):
                        # Update the main English field - we'll need to access this from the main section
                        st.success("Translation ready to copy to main field!")
        
        # Display translation matrix
        if st.session_state.verse_data.get('translation_matrix'):
            with st.expander("📊 Translation Matrix (Data View)"):
                matrix = st.session_state.verse_data['translation_matrix']
                st.write(f"**Languages:** {', '.join(matrix['languages'])}")
                st.write(f"**Morphemes:** {len(matrix['matrix'])}")
                
                # Show first few rows
                if matrix['matrix']:
                    st.write("**Sample Data:**")
                    for i, row in enumerate(matrix['matrix'][:5]):
                        st.write(f"**{row['morpheme_id']}:** {row.get('sanskrit', '')} → {row.get('english', '')}")
                    
                    # Export matrix as JSON
                    if st.button("📄 Export Translation Matrix as JSON"):
                        import json
                        json_data = json.dumps(matrix, indent=2, ensure_ascii=False)
                        st.download_button(
                            label="Download JSON",
                            data=json_data,
                            file_name=f"translation_matrix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
    
    # Navigation section
    with st.sidebar:
        st.header("🧭 Navigation")
        
        # Navigation mode selection
        nav_mode = st.radio(
            "Navigation Mode",
            options=["traditional", "story_units"],
            format_func=lambda x: "📖 Traditional (Book/Chapter/Verse)" if x == "traditional" else "📚 Story Units",
            key="nav_mode"
        )
        
        if nav_mode == "traditional":
            # Traditional navigation
            current_book = st.selectbox("📖 Book", options=list(range(1, 8)), index=0, key="book_selector")
            current_chapter = st.selectbox("📑 Chapter", options=list(range(1, 21)), index=0, key="chapter_selector") 
            current_verse = st.selectbox("📝 Verse", options=list(range(1, 101)), index=0, key="verse_selector")
        else:
            # Story units navigation
            story_units = load_story_units()
            
            unit_names = list(story_units.keys())
            if unit_names:
                current_unit = st.selectbox("📚 Story Unit", options=unit_names, key="unit_selector")
                
                if current_unit and current_unit in story_units:
                    unit_info = story_units[current_unit]
                    st.write(f"**Theme:** {unit_info.get('theme', 'Not specified')}")
                    st.write(f"**Verses:** {unit_info.get('verse_range', 'Not specified')}")
                    
                    # Set traditional navigation based on story unit
                    if 'book' in unit_info and 'chapter' in unit_info:
                        current_book = unit_info['book']
                        current_chapter = unit_info['chapter'] 
                        current_verse = unit_info.get('start_verse', 1)
                    else:
                        current_book, current_chapter, current_verse = 1, 1, 1
                else:
                    current_book, current_chapter, current_verse = 1, 1, 1
            else:
                st.info("No story units defined. Use traditional navigation.")
                current_book, current_chapter, current_verse = 1, 1, 1
        
        # Data persistence section
        st.subheader("💾 Data Management")
        
        # Save current verse data
        if st.button("💾 Save Current Verse", help="Save current verse analysis"):
            vid = str(st.session_state.current_verse_id or '')
            record = build_verse_record(vid, (sanskrit_verse or ''), (english_translation or ''))
            save_verse_data(vid, record)
        
        # Load verse data
        if st.button("📂 Load Verse Data", help="Load existing verse analysis"):
            vid = st.session_state.current_verse_id
            if vid in st.session_state.saved_verses:
                st.session_state.verse_data = st.session_state.saved_verses[vid].copy()
                st.success(f"Loaded verse {vid}")
                st.rerun()
            else:
                st.info("No saved data found for this verse.")
        
        st.write("**Export Current Verse:**")
        if st.button("📄 Export as JSON"):
            try:
                import json as _json
                vid = str(st.session_state.current_verse_id or '')
                export_data = build_verse_record(vid, (sanskrit_verse or ''), (english_translation or ''))
                json_str = _json.dumps(export_data, indent=2, ensure_ascii=False)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=f"verse_{(st.session_state.current_verse_id or 'unknown').replace('.', '_')}.json",
                    mime="application/json"
                )
            except Exception as e:
                st.error(f"Export error: {e}")
        
        if st.button("🗑️ Clear Current Data", help="Reset all fields"):
            st.session_state.verse_data = {}
            st.success("Data cleared!")
            st.rerun()

# Run the app
if __name__ == "__main__":
    main()

