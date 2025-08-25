Non-AI Keyword Mapper (English → Arabic)
=======================================

This toolkit creates an Arabic keyword file that matches your English file
1:1 in length and order, while preserving your taxonomy and human-style
phrasing as much as possible using deterministic rules (no model calls).

Files:
  - keyword_mapper.py
  - glossary_ar.json

Run (example):
  python keyword_mapper.py \
    --input "/path/to/english_keywords_cleaned_comma_19k.txt" \
    --output "/path/to/arabic_keywords_19k.txt" \
    --glossary "/path/to/glossary_ar.json" \
    --report "/path/to/qa_report.txt"

What you get:
  - arabic_keywords_19k.txt  : Arabic-only keywords (acronyms kept), every line ends with Arabic comma "،"
  - qa_report.txt            : lines that still contain Latin tokens (non-whitelisted), for quick fixes

Customize:
  - Edit glossary_ar.json to add/adjust phrase_map and word_map entries.
  - Add domain-specific heads to "feminine_heads" for correct adjective agreement.
  - To disable digit conversion, set "digit_convert" to false in glossary.

Notes:
  - Unknown bare English tokens are deliberately skipped (not transliterated) to keep output clean.
  - A placeholder "—،" is used if an input line collapses to empty after mapping, so line counts stay aligned.
  - You can run again after expanding the glossary to minimize placeholders and QA report items.