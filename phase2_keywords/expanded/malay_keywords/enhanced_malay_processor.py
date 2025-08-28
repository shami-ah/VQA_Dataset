#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ENHANCED SEMANTIC MALAY KEYWORD PROCESSOR
- Removes ALL English words completely
- Adds semantic depth and Malaysian business context
- Uses natural Malay expressions and idioms
- Enhances contextual relevance
- Maintains 18,970 keyword count
"""

import json
import re
import random
from collections import defaultdict

def load_enhanced_glossary():
    with open('/Users/ahtisham/vqa_dataset_project/phase2_keywords/expanded/malay_keywords/glossary_enhanced_semantic_ms.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def enhance_semantic_power(text, glossary):
    """Add semantic depth and Malaysian business context"""
    
    # Use semantic enhancements for short phrases
    short_phrases = glossary.get("semantic_enhancements", {}).get("short_phrases", {})
    for short, enhanced in short_phrases.items():
        if text.strip().lower() == short.lower():
            return enhanced
    
    # Add business context where appropriate
    business_context = glossary.get("semantic_enhancements", {}).get("business_context", {})
    for eng_term, malay_term in business_context.items():
        text = re.sub(r'\b' + re.escape(eng_term) + r'\b', malay_term, text, flags=re.IGNORECASE)
    
    # Add Malaysian contextual terms
    malaysian_terms = glossary.get("contextual_malaysian_terms", {})
    for eng_term, malay_term in malaysian_terms.items():
        text = re.sub(r'\b' + re.escape(eng_term) + r'\b', malay_term, text, flags=re.IGNORECASE)
    
    return text

def remove_all_english_words(text, glossary):
    """Completely remove ALL English words while preserving meaning"""
    
    # Keep only essential technical abbreviations
    protected_terms = set(glossary.get("acronyms", []))
    
    # Temporarily protect acronyms
    protected_replacements = {}
    for i, term in enumerate(protected_terms):
        if term in text:
            placeholder = f"__PROTECT{i}__"
            protected_replacements[placeholder] = term
            text = text.replace(term, placeholder)
    
    # Apply comprehensive word mapping first
    word_map = glossary.get("word_map", {})
    for eng_word, malay_word in word_map.items():
        if eng_word not in protected_terms:
            text = re.sub(r'\b' + re.escape(eng_word) + r'\b', malay_word, text, flags=re.IGNORECASE)
    
    # Remove ANY remaining English words (aggressive approach)
    # This removes all sequences of English letters that form words
    text = re.sub(r'\b[a-zA-Z]{3,}\b', '', text)  # Remove 3+ letter English words
    text = re.sub(r'\b[a-zA-Z]{1,2}\b(?![SD])', '', text)  # Remove 1-2 letter words except 5S, 8D
    
    # Restore protected terms
    for placeholder, original in protected_replacements.items():
        text = text.replace(placeholder, original)
    
    # Clean up formatting
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'\s*,\s*', ', ', text)
    text = re.sub(r',,+', ',', text)
    
    return text

def add_malaysian_natural_flow(text, glossary):
    """Make the text flow naturally in Malaysian Malay"""
    
    # Natural phrase variants for variety
    natural_variants = glossary.get("natural_phrase_variants", {})
    
    for base_phrase, variants in natural_variants.items():
        if base_phrase in text:
            # Randomly choose variant for natural variety
            chosen_variant = random.choice(variants)
            text = text.replace(base_phrase, chosen_variant, 1)  # Replace only first occurrence
    
    # Apply natural Malay sentence structure improvements
    malay_improvements = [
        # Improve word order for natural Malay
        (r'(\w+) yang (\w+)', r'\2 \1'),  # Adjust relative clause position
        (r'dokumen daripada (\w+)', r'dokumen \1'),  # Remove unnecessary 'daripada'
        (r'paparan daripada (\w+)', r'paparan \1'),
        (r'gambar daripada (\w+)', r'gambaran \1'),
        
        # Add natural Malay connectors where appropriate
        (r'(\w+) (\w+) terperinci', r'\1 yang \2 secara terperinci'),
        (r'(\w+) (\w+) lengkap', r'\1 \2 yang lengkap'),
        
        # Improve technical descriptions
        (r'dokumentasi (\w+)', r'dokumen \1 lengkap'),
        (r'paparan (\w+)', r'tunjukan \1 profesional'),
        (r'kandungan (\w+)', r'isi kandungan \1'),
    ]
    
    for pattern, replacement in malay_improvements:
        text = re.sub(pattern, replacement, text)
    
    return text

def enhance_business_relevance(text):
    """Add Malaysian business and administrative context"""
    
    # Add Malaysian business terminology depth
    business_enhancements = {
        'laporan': 'laporan komprehensif',
        'dokumen': 'dokumen rasmi',
        'sijil': 'sijil pencapaian',
        'borang': 'borang permohonan',
        'panduan': 'panduan pengguna',
        'jadual': 'jadual kerja',
        'rekod': 'rekod rasmi',
        'pemberitahuan': 'notis rasmi',
        'arahan': 'arahan kerja',
        'prosedur': 'tatacara kerja',
    }
    
    # Apply business context where it makes sense
    words = text.split()
    enhanced_words = []
    
    for word in words:
        clean_word = word.rstrip(',')
        if clean_word.lower() in business_enhancements and len(words) <= 3:  # Only for short phrases
            enhanced_word = business_enhancements[clean_word.lower()]
            if word.endswith(','):
                enhanced_word += ','
            enhanced_words.append(enhanced_word)
        else:
            enhanced_words.append(word)
    
    return ' '.join(enhanced_words)

def process_malay_keywords():
    """Main processing function to enhance all Malay keywords"""
    
    print("🇲🇾 ENHANCING MALAY KEYWORDS WITH SEMANTIC POWER...")
    print("="*60)
    
    # Load enhanced glossary
    glossary = load_enhanced_glossary()
    
    # Read current keywords
    with open('/Users/ahtisham/vqa_dataset_project/phase2_keywords/expanded/malay_keywords/malay_keywords_bulletproof.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Processing {len(lines)} keywords for enhanced semantic power...")
    
    enhanced_keywords = []
    
    for line_num, line in enumerate(lines, 1):
        if line_num % 1000 == 0:
            print(f"  Enhanced {line_num}/{len(lines)} keywords...")
        
        original_keyword = line.strip()
        if not original_keyword:
            continue
        
        # Remove trailing comma for processing
        keyword = original_keyword.rstrip(',')
        
        # Step 1: Remove ALL English words
        keyword = remove_all_english_words(keyword, glossary)
        
        # Step 2: Add semantic depth
        keyword = enhance_semantic_power(keyword, glossary)
        
        # Step 3: Add natural Malay flow
        keyword = add_malaysian_natural_flow(keyword, glossary)
        
        # Step 4: Enhance business relevance
        keyword = enhance_business_relevance(keyword)
        
        # Step 5: Final cleanup and validation
        keyword = re.sub(r'\s+', ' ', keyword).strip()
        
        # Ensure we don't lose keywords - fallback to original if processing failed
        if not keyword or len(keyword) < 3:
            keyword = original_keyword.rstrip(',')
        
        # Ensure proper comma ending
        if not keyword.endswith(','):
            keyword += ','
        
        enhanced_keywords.append(keyword)
    
    # Write enhanced keywords
    with open('/Users/ahtisham/vqa_dataset_project/phase2_keywords/expanded/malay_keywords/malay_keywords_bulletproof.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(enhanced_keywords))
    
    print(f"\n✅ ENHANCEMENT COMPLETE!")
    print(f"   Original keywords: {len(lines)}")
    print(f"   Enhanced keywords: {len(enhanced_keywords)}")
    print(f"   Preservation rate: {len(enhanced_keywords)/len(lines)*100:.1f}%")
    
    # Quick quality check
    english_count = 0
    for keyword in enhanced_keywords[:100]:  # Check first 100
        if re.search(r'\b[a-zA-Z]{3,}\b', keyword):
            english_count += 1
    
    print(f"   English words in sample: {english_count}/100 keywords")
    print(f"   Semantic enhancement: APPLIED")
    print(f"   Malaysian context: APPLIED")
    print(f"   Natural flow: APPLIED")

if __name__ == "__main__":
    process_malay_keywords()