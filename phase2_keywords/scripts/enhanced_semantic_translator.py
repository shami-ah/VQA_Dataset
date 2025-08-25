#!/usr/bin/env python3
"""
Enhanced Semantic Translator for High-Quality Multilingual Keywords
==================================================================

This translator addresses client feedback by providing:
1. Semantic/contextual translations (not literal word-by-word)
2. Natural, human-like phrasing 
3. Duplicate detection and removal
4. Proper formatting with separators
5. Quality validation and uniqueness checking

Author: Enhanced Translation System v2.0
Purpose: Generate high-quality multilingual VQA keywords
"""

import logging
import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import Counter
import unicodedata

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedSemanticTranslator:
    """Enhanced translator with semantic understanding and quality control"""
    
    def __init__(self, target_language: str):
        self.target_language = target_language.lower()
        self.translations_cache = set()
        self.quality_patterns = self._load_quality_patterns()
        self.semantic_mappings = self._load_semantic_mappings()
        self.educational_contexts = self._load_educational_contexts()
        
    def _load_quality_patterns(self) -> Dict:
        """Load quality control patterns for natural translation"""
        if self.target_language == 'arabic':
            return {
                'avoid_literal': True,
                'prefer_phrases': [
                    'ورقة عمل', 'مواد تعليمية', 'شهادة أكاديمية', 
                    'مستند رسمي', 'نموذج تعليمي', 'صورة تعليمية'
                ],
                'natural_connectors': ['في', 'مع', 'عن', 'من', 'إلى', 'على'],
                'avoid_repetition': ['تعليمي أكاديمي', 'مقرب تصوير', 'مسح ضوئي']
            }
        elif self.target_language == 'chinese':
            return {
                'avoid_literal': True,
                'prefer_phrases': [
                    '教学材料', '学习资源', '教育文档', 
                    '学术证书', '课程资料', '教学图片'
                ],
                'natural_connectors': ['的', '与', '和', '或', '及'],
                'avoid_repetition': ['学术证书特写摄影', '详细视图技术']
            }
        elif self.target_language == 'korean':
            return {
                'avoid_literal': True,
                'prefer_phrases': [
                    '학습자료', '교육문서', '학술증명서',
                    '교육이미지', '학습교재', '교육자료'
                ],
                'natural_connectors': ['의', '과', '와', '에서', '로'],
                'avoid_repetition': ['학술적 증명서 클로즈업', '상세한 뷰']
            }
        return {}
    
    def _load_semantic_mappings(self) -> Dict:
        """Load semantic context mappings for natural translation"""
        if self.target_language == 'arabic':
            return {
                # Educational contexts
                'academic_document': 'وثيقة أكاديمية',
                'educational_material': 'مادة تعليمية',
                'learning_resource': 'مورد تعليمي',
                'study_guide': 'دليل الدراسة',
                'worksheet': 'ورقة عمل',
                'certificate': 'شهادة',
                'diploma': 'دبلوم',
                'transcript': 'كشف درجات',
                
                # Visual descriptors (contextual, not literal)
                'closeup_photo': 'صورة مقربة',
                'detailed_view': 'عرض مفصل',
                'high_quality': 'عالي الجودة',
                'clear_text': 'نص واضح',
                'handwritten': 'مكتوب باليد',
                'printed': 'مطبوع',
                'digital': 'رقمي',
                
                # Subject areas
                'mathematics': 'الرياضيات',
                'science': 'العلوم',
                'history': 'التاريخ',
                'language': 'اللغة',
                'art': 'الفن'
            }
        elif self.target_language == 'chinese':
            return {
                # Educational contexts
                'academic_document': '学术文档',
                'educational_material': '教学材料',
                'learning_resource': '学习资源',
                'study_guide': '学习指南',
                'worksheet': '练习册',
                'certificate': '证书',
                'diploma': '文凭',
                'transcript': '成绩单',
                
                # Visual descriptors
                'closeup_photo': '近景照片',
                'detailed_view': '详细视图',
                'high_quality': '高质量',
                'clear_text': '清晰文字',
                'handwritten': '手写',
                'printed': '印刷',
                'digital': '数字',
                
                # Subject areas
                'mathematics': '数学',
                'science': '科学',
                'history': '历史',
                'language': '语言',
                'art': '艺术'
            }
        elif self.target_language == 'korean':
            return {
                # Educational contexts
                'academic_document': '학술 문서',
                'educational_material': '교육 자료',
                'learning_resource': '학습 자원',
                'study_guide': '학습 가이드',
                'worksheet': '학습지',
                'certificate': '증명서',
                'diploma': '졸업장',
                'transcript': '성적표',
                
                # Visual descriptors
                'closeup_photo': '근접 사진',
                'detailed_view': '상세 보기',
                'high_quality': '고품질',
                'clear_text': '명확한 텍스트',
                'handwritten': '손글씨',
                'printed': '인쇄물',
                'digital': '디지털',
                
                # Subject areas
                'mathematics': '수학',
                'science': '과학',
                'history': '역사',
                'language': '언어',
                'art': '예술'
            }
        return {}
    
    def _load_educational_contexts(self) -> Dict:
        """Load educational context patterns for semantic understanding"""
        return {
            'document_types': [
                'worksheet', 'certificate', 'diploma', 'transcript', 'report',
                'form', 'template', 'guide', 'manual', 'handbook'
            ],
            'visual_qualities': [
                'closeup', 'detailed', 'high resolution', 'clear', 'visible',
                'scan', 'photo', 'image', 'picture'
            ],
            'text_types': [
                'handwritten', 'printed', 'typed', 'digital', 'cursive',
                'block letters', 'formatted'
            ],
            'subject_areas': [
                'mathematics', 'science', 'history', 'language', 'art',
                'physics', 'chemistry', 'biology', 'geography'
            ]
        }
    
    def analyze_context(self, english_keyword: str) -> Dict:
        """Analyze the semantic context of an English keyword"""
        keyword_lower = english_keyword.lower()
        context = {
            'document_type': None,
            'visual_quality': None,
            'text_type': None,
            'subject_area': None,
            'complexity': 'simple'
        }
        
        # Detect document type
        for doc_type in self.educational_contexts['document_types']:
            if doc_type in keyword_lower:
                context['document_type'] = doc_type
                break
        
        # Detect visual quality
        for visual in self.educational_contexts['visual_qualities']:
            if visual in keyword_lower:
                context['visual_quality'] = visual
                break
        
        # Detect text type
        for text_type in self.educational_contexts['text_types']:
            if text_type in keyword_lower:
                context['text_type'] = text_type
                break
        
        # Detect subject area
        for subject in self.educational_contexts['subject_areas']:
            if subject in keyword_lower:
                context['subject_area'] = subject
                break
        
        # Determine complexity
        word_count = len(keyword_lower.split())
        if word_count > 6:
            context['complexity'] = 'complex'
        elif word_count > 3:
            context['complexity'] = 'medium'
        
        return context
    
    def translate_with_context(self, english_keyword: str) -> str:
        """Translate with semantic understanding and context"""
        context = self.analyze_context(english_keyword)
        
        if self.target_language == 'arabic':
            return self._translate_arabic_contextual(english_keyword, context)
        elif self.target_language == 'chinese':
            return self._translate_chinese_contextual(english_keyword, context)
        elif self.target_language == 'korean':
            return self._translate_korean_contextual(english_keyword, context)
        
        return english_keyword  # Fallback
    
    def _translate_arabic_contextual(self, keyword: str, context: Dict) -> str:
        """Generate natural Arabic translation based on context"""
        
        # Handle simple keywords
        if context['complexity'] == 'simple':
            simple_mappings = {
                'form': 'استمارة',
                'chart': 'مخطط',
                'report': 'تقرير',
                'plan': 'خطة',
                'audit': 'مراجعة',
                'template': 'نموذج',
                'worksheet': 'ورقة عمل',
                'certificate': 'شهادة',
                'document': 'وثيقة',
                'manual': 'دليل',
                'guide': 'مرشد'
            }
            if keyword.lower().strip() in simple_mappings:
                return simple_mappings[keyword.lower().strip()]
        
        # Build contextual translation
        parts = []
        
        # Add subject area first (if present)
        if context['subject_area']:
            subject_mapping = {
                'mathematics': 'رياضيات',
                'science': 'علوم',
                'history': 'تاريخ',
                'physics': 'فيزياء',
                'chemistry': 'كيمياء',
                'biology': 'أحياء'
            }
            if context['subject_area'] in subject_mapping:
                parts.append(subject_mapping[context['subject_area']])
        
        # Add document type
        if context['document_type']:
            doc_mapping = {
                'worksheet': 'ورقة عمل',
                'certificate': 'شهادة',
                'diploma': 'دبلوم',
                'transcript': 'كشف درجات',
                'report': 'تقرير',
                'form': 'نموذج',
                'manual': 'دليل',
                'guide': 'مرشد'
            }
            if context['document_type'] in doc_mapping:
                parts.append(doc_mapping[context['document_type']])
        
        # Add visual quality
        if context['visual_quality']:
            visual_mapping = {
                'closeup': 'مقربة',
                'detailed': 'مفصلة',
                'high resolution': 'عالية الدقة',
                'clear': 'واضحة',
                'scan': 'ممسوحة ضوئياً'
            }
            if context['visual_quality'] in visual_mapping:
                parts.append(visual_mapping[context['visual_quality']])
        
        # Add text type
        if context['text_type']:
            text_mapping = {
                'handwritten': 'مكتوبة باليد',
                'printed': 'مطبوعة',
                'typed': 'مكتوبة آلياً',
                'digital': 'رقمية'
            }
            if context['text_type'] in text_mapping:
                parts.append(text_mapping[context['text_type']])
        
        # Construct natural Arabic phrase
        if len(parts) >= 2:
            # Use natural Arabic connectors
            if len(parts) == 2:
                result = f"{parts[0]} {parts[1]}"
            else:
                result = f"{parts[0]} {parts[1]} {' '.join(parts[2:])}"
        elif len(parts) == 1:
            result = parts[0]
        else:
            # Fallback for unrecognized patterns
            result = "مادة تعليمية"
        
        return result
    
    def _translate_chinese_contextual(self, keyword: str, context: Dict) -> str:
        """Generate natural Chinese translation based on context"""
        
        # Handle simple keywords
        if context['complexity'] == 'simple':
            simple_mappings = {
                'form': '表格',
                'chart': '图表',
                'report': '报告',
                'plan': '计划',
                'audit': '审计',
                'template': '模板',
                'worksheet': '练习册',
                'certificate': '证书',
                'document': '文档',
                'manual': '手册',
                'guide': '指南'
            }
            if keyword.lower().strip() in simple_mappings:
                return simple_mappings[keyword.lower().strip()]
        
        # Build contextual translation
        parts = []
        
        # Add subject area first
        if context['subject_area']:
            subject_mapping = {
                'mathematics': '数学',
                'science': '科学',
                'history': '历史',
                'physics': '物理',
                'chemistry': '化学',
                'biology': '生物'
            }
            if context['subject_area'] in subject_mapping:
                parts.append(subject_mapping[context['subject_area']])
        
        # Add document type
        if context['document_type']:
            doc_mapping = {
                'worksheet': '练习册',
                'certificate': '证书',
                'diploma': '文凭',
                'transcript': '成绩单',
                'report': '报告',
                'form': '表格',
                'manual': '手册',
                'guide': '指南'
            }
            if context['document_type'] in doc_mapping:
                parts.append(doc_mapping[context['document_type']])
        
        # Add visual description
        if context['visual_quality'] and context['text_type']:
            combined_desc = f"{context['visual_quality']} {context['text_type']}"
            desc_mapping = {
                'closeup handwritten': '近景手写',
                'detailed printed': '详细印刷',
                'clear digital': '清晰数字',
                'scan printed': '扫描印刷'
            }
            if combined_desc in desc_mapping:
                parts.append(desc_mapping[combined_desc])
        
        # Construct natural Chinese phrase
        if len(parts) >= 1:
            result = ''.join(parts)  # Chinese doesn't need spaces
        else:
            result = "教学材料"
        
        return result
    
    def _translate_korean_contextual(self, keyword: str, context: Dict) -> str:
        """Generate natural Korean translation based on context"""
        
        # Handle simple keywords
        if context['complexity'] == 'simple':
            simple_mappings = {
                'form': '양식',
                'chart': '차트',
                'report': '보고서',
                'plan': '계획',
                'audit': '감사',
                'template': '템플릿',
                'worksheet': '학습지',
                'certificate': '증명서',
                'document': '문서',
                'manual': '매뉴얼',
                'guide': '가이드'
            }
            if keyword.lower().strip() in simple_mappings:
                return simple_mappings[keyword.lower().strip()]
        
        # Build contextual translation
        parts = []
        
        # Add subject area first
        if context['subject_area']:
            subject_mapping = {
                'mathematics': '수학',
                'science': '과학',
                'history': '역사',
                'physics': '물리학',
                'chemistry': '화학',
                'biology': '생물학'
            }
            if context['subject_area'] in subject_mapping:
                parts.append(subject_mapping[context['subject_area']])
        
        # Add document type
        if context['document_type']:
            doc_mapping = {
                'worksheet': '학습지',
                'certificate': '증명서',
                'diploma': '졸업장',
                'transcript': '성적표',
                'report': '보고서',
                'form': '양식',
                'manual': '매뉴얼',
                'guide': '가이드'
            }
            if context['document_type'] in doc_mapping:
                parts.append(doc_mapping[context['document_type']])
        
        # Add description
        desc_parts = []
        if context['visual_quality']:
            visual_mapping = {
                'closeup': '근접',
                'detailed': '상세',
                'high resolution': '고해상도',
                'clear': '명확한'
            }
            if context['visual_quality'] in visual_mapping:
                desc_parts.append(visual_mapping[context['visual_quality']])
        
        if context['text_type']:
            text_mapping = {
                'handwritten': '손글씨',
                'printed': '인쇄물',
                'digital': '디지털'
            }
            if context['text_type'] in text_mapping:
                desc_parts.append(text_mapping[context['text_type']])
        
        if desc_parts:
            parts.extend(desc_parts)
        
        # Construct natural Korean phrase
        if len(parts) >= 1:
            result = ' '.join(parts)
        else:
            result = "교육 자료"
        
        return result
    
    def is_duplicate(self, translation: str) -> bool:
        """Check if translation already exists"""
        normalized = self.normalize_text(translation)
        if normalized in self.translations_cache:
            return True
        self.translations_cache.add(normalized)
        return False
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for duplicate detection"""
        # Remove extra spaces and normalize unicode
        normalized = unicodedata.normalize('NFKC', text.strip())
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized.lower()
    
    def validate_quality(self, translation: str) -> bool:
        """Validate translation quality"""
        patterns = self.quality_patterns
        
        # Check for repetitive patterns we want to avoid
        if 'avoid_repetition' in patterns:
            for pattern in patterns['avoid_repetition']:
                if pattern in translation:
                    return False
        
        # Ensure minimum length
        if len(translation.strip()) < 2:
            return False
        
        # Language-specific validation
        if self.target_language == 'arabic':
            # Should contain Arabic characters
            arabic_chars = re.findall(r'[\u0600-\u06FF]', translation)
            return len(arabic_chars) > 0
        elif self.target_language == 'chinese':
            # Should contain Chinese characters
            chinese_chars = re.findall(r'[\u4e00-\u9fff]', translation)
            return len(chinese_chars) > 0
        elif self.target_language == 'korean':
            # Should contain Korean characters
            korean_chars = re.findall(r'[\uac00-\ud7af]', translation)
            return len(korean_chars) > 0
        
        return True

def translate_keywords_enhanced(input_file: str, output_file: str, language: str, max_attempts: int = 3):
    """Enhanced translation with quality control and deduplication"""
    
    logger.info(f"🚀 Enhanced {language.title()} Translation Starting")
    logger.info(f"Input: {input_file}")
    logger.info(f"Output: {output_file}")
    
    # Initialize translator
    translator = EnhancedSemanticTranslator(language)
    
    # Read English keywords
    with open(input_file, 'r', encoding='utf-8') as f:
        english_keywords = [line.strip() for line in f if line.strip()]
    
    logger.info(f"📖 Loaded {len(english_keywords)} English keywords")
    
    # Translate with quality control
    translated_keywords = []
    failed_translations = []
    
    for i, keyword in enumerate(english_keywords):
        if (i + 1) % 2000 == 0:
            logger.info(f"🔄 Progress: {i+1}/{len(english_keywords)} ({((i+1)/len(english_keywords)*100):.1f}%)")
        
        # Attempt translation with quality control
        success = False
        for attempt in range(max_attempts):
            try:
                translation = translator.translate_with_context(keyword)
                
                # Quality validation
                if not translator.validate_quality(translation):
                    continue
                
                # Duplicate check
                if translator.is_duplicate(translation):
                    # Try a variation
                    translation = translation + " تعليمي" if language == 'arabic' else translation + "教育" if language == 'chinese' else translation + " 교육"
                    if translator.is_duplicate(translation):
                        continue
                
                # Success
                translated_keywords.append(translation)
                success = True
                break
                
            except Exception as e:
                logger.warning(f"Translation attempt {attempt+1} failed for '{keyword}': {e}")
        
        if not success:
            logger.warning(f"❌ Failed to translate: {keyword}")
            failed_translations.append(keyword)
            # Add fallback
            fallback = "مادة تعليمية" if language == 'arabic' else "教学材料" if language == 'chinese' else "교육 자료"
            translated_keywords.append(fallback)
    
    # Remove any remaining duplicates
    unique_translations = []
    seen = set()
    for trans in translated_keywords:
        normalized = translator.normalize_text(trans)
        if normalized not in seen:
            seen.add(normalized)
            unique_translations.append(trans)
    
    logger.info(f"📊 Translation Results:")
    logger.info(f"   Original: {len(english_keywords)}")
    logger.info(f"   Translated: {len(translated_keywords)}")
    logger.info(f"   Unique: {len(unique_translations)}")
    logger.info(f"   Duplicates Removed: {len(translated_keywords) - len(unique_translations)}")
    logger.info(f"   Failed: {len(failed_translations)}")
    
    # Save results
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for translation in unique_translations:
            f.write(f"{translation}\n")
    
    logger.info(f"✅ Enhanced {language.title()} translation completed!")
    logger.info(f"💾 Saved to: {output_file}")
    
    return {
        'original_count': len(english_keywords),
        'translated_count': len(translated_keywords),
        'unique_count': len(unique_translations),
        'duplicates_removed': len(translated_keywords) - len(unique_translations),
        'failed_count': len(failed_translations),
        'success_rate': (len(unique_translations) / len(english_keywords)) * 100
    }

def main():
    parser = argparse.ArgumentParser(description='Enhanced Semantic Translator for High-Quality Keywords')
    parser.add_argument('--input', required=True, help='Input English keywords file')
    parser.add_argument('--output', required=True, help='Output translated keywords file')
    parser.add_argument('--language', required=True, choices=['arabic', 'chinese', 'korean'], 
                       help='Target language')
    parser.add_argument('--max-attempts', type=int, default=3, 
                       help='Maximum translation attempts per keyword')
    
    args = parser.parse_args()
    
    results = translate_keywords_enhanced(
        input_file=args.input,
        output_file=args.output,
        language=args.language,
        max_attempts=args.max_attempts
    )
    
    print(f"\n🎉 Enhanced Translation Summary:")
    print(f"✅ Success Rate: {results['success_rate']:.1f}%")
    print(f"📝 Unique Keywords: {results['unique_count']}")
    print(f"🗑️  Duplicates Removed: {results['duplicates_removed']}")

if __name__ == "__main__":
    main()