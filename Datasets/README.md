Datasets directory

Structure
- sources/
  - sep/: Source capture notes from Stanford Encyclopedia of Philosophy
  - iep/: Source capture notes from Internet Encyclopedia of Philosophy
- scripts/: Utilities to fetch and clean sources
- instructions/: SOPs and contributor guidance
- nyaya_corpus_staging.jsonl: New entries staged before integration

Naming conventions
- Source note files: <slug>_<provider>_<YYYYMMDD>.txt
  - Example: speech-acts_sep_20250815.txt
- Use provider short codes: sep, iep, psep, etc.

Source notes vs. full text
- We archive bibliographic metadata and researcher notes, not verbatim full-text, to respect copyrights.
- Each note should include: URL, access date, title, author(s), summary, key points/definitions, and quotes only if short and properly marked.

Workflow
1) Collect sources into sources/<provider>/ as .txt notes.
2) Draft entries in nyaya_corpus_staging.jsonl following the required 5-step Nyāya structure.
3) Validate with the analysis notebook (it already reads the clean JSONL and can be pointed to the staging file temporarily).
4) When a batch passes quality gates (complexity >= 8 on average, >=25% non-Western), merge into the main corpus.

Quality gates (quick)
- Domain format: Major Field / Specific Subfield
- Grounding authority: Field / Specific Source with URL
- Cultural tag: Western, Non-Western, or Hybrid
- Logical validity: Conclusion follows from premises; illustrative example is apt
- Consistency: Use double quotes; strict JSONL (one object per line)

Round artifacts (standard)
- Each staging round lives under `Datasets/rounds/<round_id>/` and must include two synchronized files:
  - `nyaya_corpus_<round_id>_pretty.json` (readable): JSON array, indented for manual review.
  - `nyaya_corpus_<round_id>_clean.jsonl` (processing): strict JSONL, one object per line.
- Use `Datasets/scripts/round_tools.py` to convert between formats and to map line numbers.

Utilities
- Convert: to-pretty (JSONL → pretty JSON), to-clean (pretty JSON → JSONL)
- Map: pretty line → clean line for manual disapproval deletion

