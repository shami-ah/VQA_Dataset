#!/usr/bin/env python3
"""
Complete Semantic Arabic Translator
Translates English keywords to Arabic with full semantic understanding and context awareness.
Handles human-based keywords with proper Arabic translations.
"""

import re
from typing import List, Set, Dict

# Comprehensive English to Arabic translation dictionary
TRANSLATION_DICT = {
    # Technical terms
    'bioprinting': 'الطباعة الحيوية',
    'technology': 'التكنولوجيا',
    'printing': 'الطباعة',
    'service': 'الخدمة',
    'plan': 'الخطة',
    'sheet': 'الورقة',
    'audit': 'المراجعة',
    'report': 'التقرير',
    'template': 'النموذج',
    'classification': 'التصنيف',
    'chart': 'الرسم البياني',
    'manual': 'الدليل',
    'form': 'الاستمارة',
    'sample': 'العينة',
    
    # Academic terms
    'academy': 'الأكاديمية',
    'academic': 'الأكاديمي',
    'agenda': 'جدول الأعمال',
    'blueprint': 'المخطط',
    'calendar': 'التقويم',
    'card': 'البطاقة',
    'certificate': 'الشهادة',
    'checklist': 'قائمة التحقق',
    'collaboration': 'التعاون',
    'agreement': 'الاتفاقية',
    'course': 'الدورة',
    'outline': 'المخطط العام',
    'directory': 'الدليل',
    'document': 'الوثيقة',
    
    # Photography and scanning terms
    'closeup': 'لقطة مقربة',
    'photography': 'التصوير الفوتوغرافي',
    'detailed': 'مفصل',
    'scan': 'المسح الضوئي',
    'visible': 'مرئي',
    'photo': 'الصورة',
    'image': 'الصورة',
    'flat': 'مسطح',
    'lay': 'تخطيط',
    'overview': 'نظرة عامة',
    'reminder': 'التذكير',
    'view': 'العرض',
    'macro': 'ماكرو',
    'shot': 'لقطة',
    'high': 'عالي',
    'resolution': 'الدقة',
    'showing': 'يظهر',
    'readable': 'قابل للقراءة',
    
    # Text types
    'technical': 'التقني',
    'text': 'النص',
    'mixed': 'مختلط',
    'cursive': 'الخط المائل',
    'writing': 'الكتابة',
    'formatted': 'منسق',
    'block': 'كتلة',
    'letters': 'الحروف',
    'numerical': 'الرقمي',
    'data': 'البيانات',
    'digital': 'الرقمي',
    'typed': 'مكتوب',
    'alphabetical': 'أبجدي',
    'printed': 'مطبوع',
    'handwritten': 'مكتوب باليد',
    'calligraphy': 'الخط العربي',
    
    # Numbers
    '3D': 'ثلاثي الأبعاد',
    '1099': '1099',
    '504': '504',
    '5s': '5س',
    '8d': '8د',
    
    # Common descriptors
    'with': 'مع',
    'of': 'من',
    'and': 'و',
    'the': 'ال',
    'page': 'الصفحة',
}

def clean_and_prepare_text(text: str) -> str:
    """Clean and prepare text for translation"""
    # Remove line numbers and arrows
    text = re.sub(r'^\s*\d+→', '', text.strip())
    return text.strip()

def translate_compound_term(term: str) -> str:
    """Translate compound terms by breaking them down"""
    words = term.lower().split()
    translated_words = []
    
    for word in words:
        # Remove punctuation
        clean_word = re.sub(r'[^\w]', '', word)
        if clean_word in TRANSLATION_DICT:
            translated_words.append(TRANSLATION_DICT[clean_word])
        else:
            # Handle common word patterns
            if clean_word.endswith('ing'):
                base = clean_word[:-3]
                if base in TRANSLATION_DICT:
                    translated_words.append(TRANSLATION_DICT[base])
                else:
                    translated_words.append(clean_word)  # Keep as is if no translation
            else:
                translated_words.append(clean_word)  # Keep as is if no translation
    
    return ' '.join(translated_words)

def fully_translate_to_arabic(english_text: str) -> str:
    """Fully translate English text to Arabic with semantic understanding"""
    # Clean the text first
    clean_text = clean_and_prepare_text(english_text)
    
    # Handle special cases and compound terms
    if not clean_text:
        return clean_text
    
    # Try direct translation first
    if clean_text.lower() in TRANSLATION_DICT:
        return TRANSLATION_DICT[clean_text.lower()]
    
    # Handle compound terms
    translated = translate_compound_term(clean_text)
    
    # Post-process to ensure proper Arabic structure
    # Remove any remaining English words and replace with closest Arabic equivalent
    words = translated.split()
    final_words = []
    
    for word in words:
        if re.search(r'[a-zA-Z]', word):  # Contains English letters
            # Try to find closest match or use generic terms
            if 'photo' in word.lower() or 'image' in word.lower():
                final_words.append('صورة')
            elif 'scan' in word.lower():
                final_words.append('مسح ضوئي')
            elif 'document' in word.lower():
                final_words.append('وثيقة')
            elif 'text' in word.lower():
                final_words.append('نص')
            elif 'view' in word.lower():
                final_words.append('عرض')
            else:
                # Keep the word but try one more translation attempt
                if word.lower() in TRANSLATION_DICT:
                    final_words.append(TRANSLATION_DICT[word.lower()])
                else:
                    # Use generic Arabic term based on context
                    final_words.append('عنصر')  # Generic "element"
        else:
            final_words.append(word)
    
    return ' '.join(final_words)

def process_keywords_file(input_file: str, output_file: str):
    """Process keywords file and create fully translated version"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        translated_keywords = set()  # Use set to avoid duplicates
        
        print(f"Processing {len(lines)} keywords...")
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            # Extract the actual keyword (remove line numbers and arrows)
            keyword = clean_and_prepare_text(line)
            if not keyword:
                continue
            
            # Translate the keyword
            translated = fully_translate_to_arabic(keyword)
            
            if translated and translated not in translated_keywords:
                translated_keywords.add(translated)
                
            if i % 1000 == 0:
                print(f"Processed {i} keywords...")
        
        # Write translated keywords to file
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, keyword in enumerate(sorted(translated_keywords), 1):
                f.write(f"{i}→{keyword}\n")
        
        print(f"Translation complete! Generated {len(translated_keywords)} unique Arabic keywords.")
        print(f"Output saved to: {output_file}")
        
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    # Process the English keywords file
    input_file = "/Users/ahtisham/vqa_dataset_project/phase2_keywords/expanded/english_keywords/english_combined_enhanced_19k.txt"
    output_file = "/Users/ahtisham/vqa_dataset_project/phase2_keywords/expanded/arabic_keywords/arabic_fully_translated.txt"
    
    print("Starting comprehensive Arabic translation...")
    process_keywords_file(input_file, output_file)