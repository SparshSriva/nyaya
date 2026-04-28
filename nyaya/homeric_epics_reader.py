import streamlit as st
import json
import os
import re

DATA_FILE = "data/processed/epic_lines.jsonl"

st.set_page_config(page_title="Homeric Epics Reader", layout="wide")

st.title("🏛️ Homeric Epics Reader")
st.markdown("Enter and analyze lines from Classical Epics (Iliad, Odyssey, Aeneid).")

def parse_dactylic_hexameter(text):
    """
    A basic placeholder parser for Dactylic Hexameter.
    In a real application, this would use a proper natural language toolkit
    (like cltk) to analyze syllabic quantity (long vs short) and identify the six metrical feet
    (dactyls: long-short-short or spondees: long-long).
    """
    if not text.strip():
        return "No text provided for meter analysis."

    # Very rudimentary simulation for demonstration
    words = text.split()
    if len(words) < 5:
        return f"Text too short for a full hexameter line ({len(words)} words)."

    # Simulate a pattern representation:
    # - = long, u = short
    # Hexameter: - u u | - u u | - u u | - u u | - u u | - -
    simulated_pattern = "- u u | - u u | - - | - u u | - u u | - x"

    return f"Simulated Meter: {simulated_pattern}"

def load_data():
    """Loads records from the JSONL file."""
    data = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError:
                        st.warning("Found a malformed line in the data file.")
    return data

def save_entry(entry):
    """Appends a new JSON record to the JSONL file."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')

# Input form
with st.form("entry_form"):
    st.subheader("New Entry")

    col1, col2 = st.columns(2)

    with col1:
        source_text_greek = st.text_area("Ancient Greek Text", height=100, help="Enter the original Greek text (if applicable).")
        source_text_latin = st.text_area("Latin Text", height=100, help="Enter the original Latin text (if applicable).")

    with col2:
        english_translation = st.text_area("English Translation", height=100)
        morpheme_breakdown = st.text_area("Morpheme-level Breakdown", height=100, help="Format: word:morpheme1-morpheme2|translation")

    submit_button = st.form_submit_button("Analyze & Save Entry")

if submit_button:
    st.subheader("Analysis Results")

    meter_result_greek = None
    meter_result_latin = None

    # Meter Analysis
    if source_text_greek:
        st.markdown("**Greek Meter Analysis (Dactylic Hexameter):**")
        meter_result_greek = parse_dactylic_hexameter(source_text_greek)
        st.code(meter_result_greek)

    if source_text_latin:
        st.markdown("**Latin Meter Analysis (Dactylic Hexameter):**")
        meter_result_latin = parse_dactylic_hexameter(source_text_latin)
        st.code(meter_result_latin)

    # Save Data
    new_entry = {
        "ancient_greek_text": source_text_greek,
        "latin_text": source_text_latin,
        "english_translation": english_translation,
        "morpheme_breakdown": morpheme_breakdown,
        "greek_meter": meter_result_greek,
        "latin_meter": meter_result_latin
    }

    save_entry(new_entry)
    st.success(f"Entry saved to `{DATA_FILE}` successfully!")

# Display Data
st.markdown("---")
st.subheader("Saved Entries")
entries = load_data()

if entries:
    st.dataframe(entries)
else:
    st.info("No entries found yet. Submit a new entry above.")
