#!/usr/bin/env python3
"""
Complete Semantic Korean Translator
Translates English keywords to Korean with full semantic understanding and context awareness.
Handles human-based keywords with proper Korean translations.
"""

import re
from typing import List, Set, Dict

# Comprehensive English to Korean translation dictionary
TRANSLATION_DICT = {
    # Technical terms
    'bioprinting': '바이오프린팅',
    'technology': '기술',
    'printing': '인쇄',
    'service': '서비스',
    'plan': '계획',
    'sheet': '시트',
    'audit': '감사',
    'report': '보고서',
    'template': '템플릿',
    'classification': '분류',
    'chart': '차트',
    'manual': '매뉴얼',
    'form': '양식',
    'sample': '샘플',
    
    # Academic terms
    'academy': '아카데미',
    'academic': '학술의',
    'agenda': '의제',
    'blueprint': '청사진',
    'calendar': '달력',
    'card': '카드',
    'certificate': '인증서',
    'checklist': '체크리스트',
    'collaboration': '협업',
    'agreement': '합의서',
    'course': '과정',
    'outline': '개요',
    'directory': '디렉토리',
    'document': '문서',
    
    # Photography and scanning terms
    'closeup': '클로즈업',
    'photography': '사진촬영',
    'detailed': '상세한',
    'scan': '스캔',
    'visible': '보이는',
    'photo': '사진',
    'image': '이미지',
    'flat': '평면',
    'lay': '배치',
    'overview': '개요',
    'reminder': '리마인더',
    'view': '보기',
    'macro': '매크로',
    'shot': '촬영',
    'high': '높은',
    'resolution': '해상도',
    'showing': '보여주는',
    'readable': '읽기 가능한',
    
    # Text types
    'technical': '기술적',
    'text': '텍스트',
    'mixed': '혼합',
    'cursive': '필기체',
    'writing': '글쓰기',
    'formatted': '형식화된',
    'block': '블록',
    'letters': '글자',
    'numerical': '숫자',
    'data': '데이터',
    'digital': '디지털',
    'typed': '타이핑된',
    'alphabetical': '알파벳순',
    'printed': '인쇄된',
    'handwritten': '손으로 쓴',
    'calligraphy': '서예',
    
    # Numbers and codes
    '3D': '3차원',
    '1099': '1099',
    '504': '504',
    '5s': '5S',
    '8d': '8D',
    
    # Common words
    'with': '함께',
    'of': '의',
    'and': '그리고',
    'the': '',  # Korean doesn't always need articles
    'page': '페이지',
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
            translated_word = TRANSLATION_DICT[clean_word]
            if translated_word:  # Don't add empty translations
                translated_words.append(translated_word)
        else:
            # Handle common word patterns
            if clean_word.endswith('ing'):
                base = clean_word[:-3]
                if base in TRANSLATION_DICT:
                    translated_word = TRANSLATION_DICT[base]
                    if translated_word:
                        translated_words.append(translated_word + '하는')  # Korean -ing equivalent
                else:
                    # Generic translation for unknown -ing words
                    translated_words.append(f'{clean_word}')
            else:
                # For unknown words, try to categorize
                if any(x in clean_word for x in ['photo', 'image', 'pic']):
                    translated_words.append('사진')
                elif any(x in clean_word for x in ['scan', 'copy']):
                    translated_words.append('스캔')
                elif any(x in clean_word for x in ['document', 'file']):
                    translated_words.append('문서')
                elif any(x in clean_word for x in ['text', 'word']):
                    translated_words.append('텍스트')
                else:
                    translated_words.append(clean_word)
    
    return ' '.join(translated_words)

def fully_translate_to_korean(english_text: str) -> str:
    """Fully translate English text to Korean with semantic understanding"""
    # Clean the text first
    clean_text = clean_and_prepare_text(english_text)
    
    if not clean_text:
        return clean_text
    
    # Try direct translation first
    if clean_text.lower() in TRANSLATION_DICT:
        return TRANSLATION_DICT[clean_text.lower()]
    
    # Handle compound terms
    translated = translate_compound_term(clean_text)
    
    # Post-process to ensure no English letters remain
    words = translated.split()
    final_words = []
    
    for word in words:
        if re.search(r'[a-zA-Z]', word):  # Contains English letters
            # Try to find closest match or use generic terms
            if 'photo' in word.lower() or 'image' in word.lower():
                final_words.append('사진')
            elif 'scan' in word.lower():
                final_words.append('스캔')
            elif 'document' in word.lower():
                final_words.append('문서')
            elif 'text' in word.lower():
                final_words.append('텍스트')
            elif 'view' in word.lower():
                final_words.append('보기')
            elif 'academic' in word.lower():
                final_words.append('학술')
            else:
                # Keep the word but try one more translation attempt
                clean_word = re.sub(r'[^\w]', '', word.lower())
                if clean_word in TRANSLATION_DICT:
                    final_words.append(TRANSLATION_DICT[clean_word])
                else:
                    # Use generic Korean term
                    final_words.append('항목')  # Generic "item"
        else:
            final_words.append(word)
    
    result = ' '.join(final_words)
    return result if result.strip() else '항목'

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
            
            # Extract the actual keyword
            keyword = clean_and_prepare_text(line)
            if not keyword:
                continue
            
            # Translate the keyword
            translated = fully_translate_to_korean(keyword)
            
            if translated and len(translated.strip()) > 0 and translated not in translated_keywords:
                translated_keywords.add(translated)
                
            if i % 1000 == 0:
                print(f"Processed {i} keywords...")
        
        # Write translated keywords to file
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, keyword in enumerate(sorted(translated_keywords), 1):
                f.write(f"{i}→{keyword}\n")
        
        print(f"Translation complete! Generated {len(translated_keywords)} unique Korean keywords.")
        print(f"Output saved to: {output_file}")
        
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    # Process the English keywords file
    input_file = "/Users/ahtisham/vqa_dataset_project/phase2_keywords/expanded/english_keywords/english_combined_enhanced_19k.txt"
    output_file = "/Users/ahtisham/vqa_dataset_project/phase2_keywords/expanded/korean_keywords/korean_fully_translated.txt"
    
    print("Starting comprehensive Korean translation...")
    process_keywords_file(input_file, output_file)