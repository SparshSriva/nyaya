Research SOP for Nyāya Corpus Expansion

Purpose
- Standardize how we collect sources, draft entries, and validate quality.

Steps
1) Select priority domains from corpus_analysis.ipynb (underrepresented categories, low source specificity, non-Western balance).
2) Identify 2–3 authoritative sources (SEP, IEP, arxiv, biorvix, APS, American Math Society, Nature, academic monographs, handbooks, textbooks, ect).
3) Create a source note (.txt) in sources/<provider>/ using the naming convention.
   - Include: URL, access date, title, author(s), concise summary, key distinctions/arguments, definitions.
4) Draft entries in nyaya_corpus_staging.jsonl using the Nyāya 5-part structure.
   - Fields required: domain, pratijna, hetu, udaharana, upanaya, nigamana, grounding_authority
   - Optional: complexity_indicators, cultural_tradition, cross_references
5) Check formatting: strict JSONL, valid JSON, double quotes only, no trailing commas.
6) Run the analysis notebook to validate coverage, cultural balance, and source specificity.
7) Iterate until the batch passes quality gates; then merge into the clean corpus.

Tips
- Prefer specific sources (e.g., "SEP: Speech Acts (2021)" + URL) over generic fields.
- Keep non-Western proportion >= 25% per batch.
- Examples should be recognizable and neutral; avoid contentious contemporary politics unless the domain requires it.
- Paraphrase ideas—do not copy long passages.

