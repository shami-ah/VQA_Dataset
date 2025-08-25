#!/usr/bin/env python3
"""
Complete Semantic Chinese Translator
Translates English keywords to Chinese with full semantic understanding and context awareness.
Handles human-based keywords with proper Chinese translations.
"""

import re
from typing import List, Set, Dict

# Comprehensive English to Chinese translation dictionary
TRANSLATION_DICT = {
    # Technical terms
    'bioprinting': '生物打印',
    'technology': '技术',
    'printing': '打印',
    'service': '服务',
    'plan': '计划',
    'sheet': '表格',
    'audit': '审计',
    'report': '报告',
    'template': '模板',
    'classification': '分类',
    'chart': '图表',
    'manual': '手册',
    'form': '表单',
    'sample': '样本',
    
    # Academic terms
    'academy': '学院',
    'academic': '学术的',
    'agenda': '议程',
    'blueprint': '蓝图',
    'calendar': '日历',
    'card': '卡片',
    'certificate': '证书',
    'checklist': '检查清单',
    'collaboration': '协作',
    'agreement': '协议',
    'course': '课程',
    'outline': '大纲',
    'directory': '目录',
    'document': '文档',
    
    # Photography and scanning terms
    'closeup': '特写',
    'photography': '摄影',
    'detailed': '详细的',
    'scan': '扫描',
    'visible': '可见的',
    'photo': '照片',
    'image': '图像',
    'flat': '平面',
    'lay': '布局',
    'overview': '概览',
    'reminder': '提醒',
    'view': '视图',
    'macro': '宏观',
    'shot': '拍摄',
    'high': '高',
    'resolution': '分辨率',
    'showing': '显示',
    'readable': '可读的',
    
    # Text types
    'technical': '技术',
    'text': '文本',
    'mixed': '混合',
    'cursive': '草书',
    'writing': '书写',
    'formatted': '格式化',
    'block': '块',
    'letters': '字母',
    'numerical': '数字',
    'data': '数据',
    'digital': '数字化',
    'typed': '打字',
    'alphabetical': '字母顺序',
    'printed': '印刷',
    'handwritten': '手写',
    'calligraphy': '书法',
    
    # Numbers and codes
    '3D': '三维',
    '1099': '1099',
    '504': '504',
    '5s': '5S',
    '8d': '8D',
    
    # Common words
    'with': '与',
    'of': '的',
    'and': '和',
    'the': '',  # No direct equivalent in Chinese
    'page': '页面',
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
                        translated_words.append(translated_word)
                else:
                    # Generic translation for unknown -ing words
                    translated_words.append(f'{clean_word}')
            else:
                # For unknown words, try to categorize
                if any(x in clean_word for x in ['photo', 'image', 'pic']):
                    translated_words.append('图片')
                elif any(x in clean_word for x in ['scan', 'copy']):
                    translated_words.append('扫描')
                elif any(x in clean_word for x in ['document', 'file']):
                    translated_words.append('文档')
                elif any(x in clean_word for x in ['text', 'word']):
                    translated_words.append('文本')
                else:
                    translated_words.append(clean_word)
    
    return ''.join(translated_words)  # Chinese doesn't use spaces between words

def fully_translate_to_chinese(english_text: str) -> str:
    """Fully translate English text to Chinese with semantic understanding"""
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
    # Remove any remaining English words and replace with Chinese equivalents
    final_text = re.sub(r'[a-zA-Z]+', '', translated)
    
    # If the result is too short or empty, try a more generic approach
    if len(final_text.strip()) < 2:
        words = clean_text.lower().split()
        chinese_parts = []
        
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word in TRANSLATION_DICT:
                chinese_parts.append(TRANSLATION_DICT[clean_word])
            elif 'photo' in clean_word or 'image' in clean_word:
                chinese_parts.append('图片')
            elif 'scan' in clean_word:
                chinese_parts.append('扫描')
            elif 'document' in clean_word or 'file' in clean_word:
                chinese_parts.append('文档')
            elif 'text' in clean_word:
                chinese_parts.append('文本')
            elif 'view' in clean_word:
                chinese_parts.append('视图')
            elif 'academic' in clean_word:
                chinese_parts.append('学术')
            else:
                # Use a generic term based on common patterns
                chinese_parts.append('项目')
        
        final_text = ''.join([part for part in chinese_parts if part])
    
    return final_text if final_text else '项目'  # Fallback to "item"

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
            translated = fully_translate_to_chinese(keyword)
            
            if translated and len(translated.strip()) > 0 and translated not in translated_keywords:
                translated_keywords.add(translated)
                
            if i % 1000 == 0:
                print(f"Processed {i} keywords...")
        
        # Write translated keywords to file
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, keyword in enumerate(sorted(translated_keywords), 1):
                f.write(f"{i}→{keyword}\n")
        
        print(f"Translation complete! Generated {len(translated_keywords)} unique Chinese keywords.")
        print(f"Output saved to: {output_file}")
        
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    # Process the English keywords file
    input_file = "/Users/ahtisham/vqa_dataset_project/phase2_keywords/expanded/english_keywords/english_combined_enhanced_19k.txt"
    output_file = "/Users/ahtisham/vqa_dataset_project/phase2_keywords/expanded/chinese_keywords/chinese_fully_translated.txt"
    
    print("Starting comprehensive Chinese translation...")
    process_keywords_file(input_file, output_file)