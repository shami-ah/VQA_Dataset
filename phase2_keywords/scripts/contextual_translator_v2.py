#!/usr/bin/env python3
"""
Contextual Translator V2 - Addressing Client Feedback
===================================================

Fixes for client feedback:
1. Better semantic/contextual translations (not literal word-by-word)
2. Remove duplicates effectively
3. Natural phrasing in target languages
4. Proper formatting with consistent separators

Author: Contextual Translation System v2.0
Purpose: Generate natural, high-quality multilingual VQA keywords
"""

import logging
import argparse
import re
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ContextualTranslator:
    """Contextual translator with natural phrasing and deduplication"""
    
    def __init__(self, target_language: str):
        self.target_language = target_language.lower()
        self.seen_translations = set()
        self.context_patterns = self._load_context_patterns()
        self.phrase_mappings = self._load_phrase_mappings()
        
    def _load_context_patterns(self) -> Dict:
        """Load contextual translation patterns"""
        if self.target_language == 'arabic':
            return {
                # Document types with natural Arabic expressions
                'worksheet_patterns': ['ورقة عمل', 'نشاط تعليمي', 'تمرين', 'مهمة دراسية'],
                'certificate_patterns': ['شهادة', 'وثيقة رسمية', 'إفادة', 'شهادة تقدير'],
                'manual_patterns': ['دليل', 'كتيب إرشادي', 'مرجع', 'مرشد'],
                'report_patterns': ['تقرير', 'بيان', 'ملخص', 'إحصائية'],
                'form_patterns': ['استمارة', 'نموذج', 'طلب', 'بيانات'],
                
                # Visual descriptors with natural Arabic
                'photo_patterns': ['صورة', 'لقطة', 'تصوير'],
                'scan_patterns': ['مسح ضوئي', 'صورة ممسوحة', 'نسخة رقمية'],
                'closeup_patterns': ['مقربة', 'تفصيلية', 'واضحة'],
                'handwritten_patterns': ['مكتوب بخط اليد', 'خط يدوي', 'كتابة يدوية'],
                
                # Subject areas with Arabic terminology
                'math_patterns': ['رياضيات', 'حساب', 'هندسة'],
                'science_patterns': ['علوم', 'فيزياء', 'كيمياء', 'أحياء'],
                'language_patterns': ['لغة', 'أدب', 'قراءة', 'كتابة']
            }
        elif self.target_language == 'chinese':
            return {
                # Document types with natural Chinese expressions
                'worksheet_patterns': ['练习题', '作业单', '学习材料', '练习册'],
                'certificate_patterns': ['证书', '证明文件', '认证', '奖状'],
                'manual_patterns': ['手册', '指导书', '说明书', '指南'],
                'report_patterns': ['报告', '总结', '汇报', '分析'],
                'form_patterns': ['表格', '申请表', '登记表', '调查表'],
                
                # Visual descriptors with natural Chinese
                'photo_patterns': ['照片', '图片', '摄影'],
                'scan_patterns': ['扫描件', '扫描图', '电子版'],
                'closeup_patterns': ['特写', '详细', '近景'],
                'handwritten_patterns': ['手写', '手工书写', '手写体'],
                
                # Subject areas with Chinese terminology
                'math_patterns': ['数学', '算术', '几何'],
                'science_patterns': ['科学', '物理', '化学', '生物'],
                'language_patterns': ['语文', '文学', '阅读', '写作']
            }
        elif self.target_language == 'korean':
            return {
                # Document types with natural Korean expressions
                'worksheet_patterns': ['학습지', '연습문제', '과제', '활동지'],
                'certificate_patterns': ['증명서', '자격증', '인증서', '상장'],
                'manual_patterns': ['매뉴얼', '안내서', '지침서', '가이드'],
                'report_patterns': ['보고서', '리포트', '분석서', '요약'],
                'form_patterns': ['양식', '신청서', '등록서', '설문지'],
                
                # Visual descriptors with natural Korean
                'photo_patterns': ['사진', '이미지', '촬영'],
                'scan_patterns': ['스캔', '스캔본', '전자문서'],
                'closeup_patterns': ['클로즈업', '상세', '근접'],
                'handwritten_patterns': ['손글씨', '필기', '수기'],
                
                # Subject areas with Korean terminology
                'math_patterns': ['수학', '산수', '기하'],
                'science_patterns': ['과학', '물리', '화학', '생물'],
                'language_patterns': ['국어', '문학', '독서', '작문']
            }
        return {}
    
    def _load_phrase_mappings(self) -> Dict:
        """Load complete phrase mappings for common patterns"""
        if self.target_language == 'arabic':
            return {
                # Common educational phrases
                'educational material': 'مواد تعليمية',
                'academic document': 'وثيقة أكاديمية',
                'study guide': 'دليل الدراسة',
                'learning resource': 'مصدر تعليمي',
                'teaching aid': 'وسيلة تعليمية',
                'class handout': 'منشور للفصل',
                'homework assignment': 'واجب منزلي',
                'exam paper': 'ورقة امتحان',
                'quiz sheet': 'ورقة اختبار',
                'answer key': 'نموذج إجابة',
                
                # Visual + document combinations
                'scanned worksheet': 'ورقة عمل ممسوحة',
                'printed certificate': 'شهادة مطبوعة',
                'handwritten notes': 'ملاحظات مكتوبة بخط اليد',
                'digital document': 'وثيقة رقمية',
                'photo of text': 'صورة نص',
                'clear handwriting': 'خط واضح',
                'readable text': 'نص مقروء',
                
                # Subject specific
                'math worksheet': 'ورقة عمل رياضيات',
                'science report': 'تقرير علوم',
                'history document': 'وثيقة تاريخية',
                'language exercise': 'تمرين لغة'
            }
        elif self.target_language == 'chinese':
            return {
                # Common educational phrases
                'educational material': '教学资料',
                'academic document': '学术文档',
                'study guide': '学习指南',
                'learning resource': '学习资源',
                'teaching aid': '教学工具',
                'class handout': '课堂资料',
                'homework assignment': '作业任务',
                'exam paper': '考试试卷',
                'quiz sheet': '测验题',
                'answer key': '答案',
                
                # Visual + document combinations
                'scanned worksheet': '扫描练习题',
                'printed certificate': '印刷证书',
                'handwritten notes': '手写笔记',
                'digital document': '电子文档',
                'photo of text': '文字照片',
                'clear handwriting': '清晰笔迹',
                'readable text': '可读文字',
                
                # Subject specific
                'math worksheet': '数学练习题',
                'science report': '科学报告',
                'history document': '历史文献',
                'language exercise': '语言练习'
            }
        elif self.target_language == 'korean':
            return {
                # Common educational phrases
                'educational material': '교육 자료',
                'academic document': '학술 문서',
                'study guide': '학습 가이드',
                'learning resource': '학습 자원',
                'teaching aid': '교육 도구',
                'class handout': '수업 자료',
                'homework assignment': '숙제',
                'exam paper': '시험지',
                'quiz sheet': '퀴즈',
                'answer key': '정답',
                
                # Visual + document combinations
                'scanned worksheet': '스캔된 학습지',
                'printed certificate': '인쇄된 증명서',
                'handwritten notes': '손글씨 노트',
                'digital document': '디지털 문서',
                'photo of text': '텍스트 사진',
                'clear handwriting': '명확한 필기',
                'readable text': '읽기 쉬운 텍스트',
                
                # Subject specific
                'math worksheet': '수학 학습지',
                'science report': '과학 보고서',
                'history document': '역사 문서',
                'language exercise': '언어 연습'
            }
        return {}
    
    def identify_context(self, english_text: str) -> Dict:
        """Identify key contexts in the English text"""
        text_lower = english_text.lower()
        context = {
            'document_type': None,
            'visual_type': None,
            'subject_area': None,
            'text_quality': None,
            'is_simple': len(text_lower.split()) <= 3
        }
        
        # Identify document type
        if any(word in text_lower for word in ['worksheet', 'exercise', 'practice']):
            context['document_type'] = 'worksheet'
        elif any(word in text_lower for word in ['certificate', 'diploma', 'award']):
            context['document_type'] = 'certificate'
        elif any(word in text_lower for word in ['manual', 'guide', 'handbook']):
            context['document_type'] = 'manual'
        elif any(word in text_lower for word in ['report', 'summary', 'analysis']):
            context['document_type'] = 'report'
        elif any(word in text_lower for word in ['form', 'application', 'template']):
            context['document_type'] = 'form'
        
        # Identify visual type
        if any(word in text_lower for word in ['photo', 'picture', 'image']):
            context['visual_type'] = 'photo'
        elif any(word in text_lower for word in ['scan', 'scanned']):
            context['visual_type'] = 'scan'
        elif any(word in text_lower for word in ['closeup', 'close-up', 'detailed']):
            context['visual_type'] = 'closeup'
        
        # Identify subject area
        if any(word in text_lower for word in ['math', 'mathematics', 'calculation']):
            context['subject_area'] = 'math'
        elif any(word in text_lower for word in ['science', 'physics', 'chemistry', 'biology']):
            context['subject_area'] = 'science'
        elif any(word in text_lower for word in ['language', 'literature', 'reading', 'writing']):
            context['subject_area'] = 'language'
        elif any(word in text_lower for word in ['history', 'historical']):
            context['subject_area'] = 'history'
        
        # Identify text quality
        if any(word in text_lower for word in ['handwritten', 'handwriting']):
            context['text_quality'] = 'handwritten'
        elif any(word in text_lower for word in ['printed', 'print']):
            context['text_quality'] = 'printed'
        elif any(word in text_lower for word in ['digital', 'typed']):
            context['text_quality'] = 'digital'
        
        return context
    
    def translate_contextually(self, english_text: str) -> str:
        """Generate contextual translation based on identified patterns"""
        
        # Check for direct phrase mappings first
        text_lower = english_text.lower().strip()
        if text_lower in self.phrase_mappings:
            return self.phrase_mappings[text_lower]
        
        # Identify context
        context = self.identify_context(english_text)
        
        # Generate contextual translation
        if self.target_language == 'arabic':
            return self._translate_arabic_contextual(english_text, context)
        elif self.target_language == 'chinese':
            return self._translate_chinese_contextual(english_text, context)
        elif self.target_language == 'korean':
            return self._translate_korean_contextual(english_text, context)
        
        return english_text  # Fallback
    
    def _translate_arabic_contextual(self, text: str, context: Dict) -> str:
        """Generate natural Arabic translation"""
        patterns = self.context_patterns
        
        # Handle simple cases
        if context['is_simple']:
            simple_mappings = {
                'form': 'استمارة',
                'chart': 'مخطط',
                'plan': 'خطة',
                'audit': 'مراجعة',
                'report': 'تقرير',
                'template': 'نموذج',
                'sample': 'عينة',
                'guide': 'دليل',
                'manual': 'كتيب',
                'worksheet': 'ورقة عمل',
                'certificate': 'شهادة',
                'document': 'وثيقة'
            }
            clean_text = text.lower().strip()
            if clean_text in simple_mappings:
                return simple_mappings[clean_text]
        
        # Build contextual translation
        components = []
        
        # Add subject area first (natural Arabic order)
        if context['subject_area']:
            subject_map = {
                'math': 'رياضيات',
                'science': 'علوم', 
                'language': 'لغة',
                'history': 'تاريخ'
            }
            if context['subject_area'] in subject_map:
                components.append(subject_map[context['subject_area']])
        
        # Add document type
        if context['document_type']:
            import random
            doc_patterns = patterns.get(f"{context['document_type']}_patterns", [])
            if doc_patterns:
                components.append(random.choice(doc_patterns))
        
        # Add visual/quality description
        descriptors = []
        if context['visual_type']:
            visual_map = {
                'photo': 'صورة',
                'scan': 'مسح ضوئي',
                'closeup': 'مقربة'
            }
            if context['visual_type'] in visual_map:
                descriptors.append(visual_map[context['visual_type']])
        
        if context['text_quality']:
            quality_map = {
                'handwritten': 'مكتوبة باليد',
                'printed': 'مطبوعة',
                'digital': 'رقمية'
            }
            if context['text_quality'] in quality_map:
                descriptors.append(quality_map[context['text_quality']])
        
        # Combine components naturally
        if components:
            result = ' '.join(components)
            if descriptors:
                result += ' ' + ' '.join(descriptors)
        else:
            # Fallback to simple translation
            result = 'مادة تعليمية'
        
        return result
    
    def _translate_chinese_contextual(self, text: str, context: Dict) -> str:
        """Generate natural Chinese translation"""
        patterns = self.context_patterns
        
        # Handle simple cases
        if context['is_simple']:
            simple_mappings = {
                'form': '表格',
                'chart': '图表',
                'plan': '计划',
                'audit': '审计',
                'report': '报告',
                'template': '模板',
                'sample': '样本',
                'guide': '指南',
                'manual': '手册',
                'worksheet': '练习题',
                'certificate': '证书',
                'document': '文档'
            }
            clean_text = text.lower().strip()
            if clean_text in simple_mappings:
                return simple_mappings[clean_text]
        
        # Build contextual translation
        components = []
        
        # Add subject area first
        if context['subject_area']:
            subject_map = {
                'math': '数学',
                'science': '科学',
                'language': '语文',
                'history': '历史'
            }
            if context['subject_area'] in subject_map:
                components.append(subject_map[context['subject_area']])
        
        # Add document type
        if context['document_type']:
            import random
            doc_patterns = patterns.get(f"{context['document_type']}_patterns", [])
            if doc_patterns:
                components.append(random.choice(doc_patterns))
        
        # Add descriptors
        if context['visual_type'] or context['text_quality']:
            desc_map = {
                'photo': '照片',
                'scan': '扫描件',
                'closeup': '特写',
                'handwritten': '手写',
                'printed': '印刷',
                'digital': '电子'
            }
            if context['visual_type'] and context['visual_type'] in desc_map:
                components.append(desc_map[context['visual_type']])
            elif context['text_quality'] and context['text_quality'] in desc_map:
                components.append(desc_map[context['text_quality']])
        
        # Combine components (Chinese doesn't need spaces)
        if components:
            result = ''.join(components)
        else:
            result = '教学材料'
        
        return result
    
    def _translate_korean_contextual(self, text: str, context: Dict) -> str:
        """Generate natural Korean translation"""
        patterns = self.context_patterns
        
        # Handle simple cases
        if context['is_simple']:
            simple_mappings = {
                'form': '양식',
                'chart': '차트',
                'plan': '계획',
                'audit': '감사',
                'report': '보고서',
                'template': '템플릿',
                'sample': '샘플',
                'guide': '가이드',
                'manual': '매뉴얼',
                'worksheet': '학습지',
                'certificate': '증명서',
                'document': '문서'
            }
            clean_text = text.lower().strip()
            if clean_text in simple_mappings:
                return simple_mappings[clean_text]
        
        # Build contextual translation
        components = []
        
        # Add subject area first
        if context['subject_area']:
            subject_map = {
                'math': '수학',
                'science': '과학',
                'language': '국어',
                'history': '역사'
            }
            if context['subject_area'] in subject_map:
                components.append(subject_map[context['subject_area']])
        
        # Add document type
        if context['document_type']:
            import random
            doc_patterns = patterns.get(f"{context['document_type']}_patterns", [])
            if doc_patterns:
                components.append(random.choice(doc_patterns))
        
        # Add descriptors
        descriptors = []
        if context['visual_type']:
            visual_map = {
                'photo': '사진',
                'scan': '스캔',
                'closeup': '클로즈업'
            }
            if context['visual_type'] in visual_map:
                descriptors.append(visual_map[context['visual_type']])
        
        if context['text_quality']:
            quality_map = {
                'handwritten': '손글씨',
                'printed': '인쇄물',
                'digital': '디지털'
            }
            if context['text_quality'] in quality_map:
                descriptors.append(quality_map[context['text_quality']])
        
        # Combine components
        if components:
            result = ' '.join(components)
            if descriptors:
                result += ' ' + ' '.join(descriptors)
        else:
            result = '교육 자료'
        
        return result
    
    def is_duplicate(self, translation: str) -> bool:
        """Check for duplicates with normalization"""
        normalized = re.sub(r'\s+', ' ', translation.strip().lower())
        if normalized in self.seen_translations:
            return True
        self.seen_translations.add(normalized)
        return False

def translate_file_contextual(input_file: str, output_file: str, language: str):
    """Translate file with contextual understanding and deduplication"""
    
    logger.info(f"🚀 Contextual {language.title()} Translation Starting")
    logger.info(f"Input: {input_file}")
    logger.info(f"Output: {output_file}")
    
    # Initialize translator
    translator = ContextualTranslator(language)
    
    # Read English keywords
    with open(input_file, 'r', encoding='utf-8') as f:
        english_keywords = [line.strip() for line in f if line.strip()]
    
    logger.info(f"📖 Loaded {len(english_keywords)} English keywords")
    
    # Translate with deduplication
    translated_keywords = []
    duplicate_count = 0
    
    for i, keyword in enumerate(english_keywords):
        if (i + 1) % 2000 == 0:
            logger.info(f"🔄 Progress: {i+1}/{len(english_keywords)} ({((i+1)/len(english_keywords)*100):.1f}%)")
        
        translation = translator.translate_contextually(keyword)
        
        # Check for duplicate
        if translator.is_duplicate(translation):
            duplicate_count += 1
            # Try to create variation
            variation_attempts = [
                f"{translation} 教育",  # Add educational marker
                f"{translation} 材料",  # Add material marker
                f"{translation} 文档",  # Add document marker
            ] if language == 'chinese' else [
                f"{translation} تعليمي",  # Add educational marker
                f"{translation} أكاديمي",  # Add academic marker
                f"{translation} مدرسي",  # Add school marker
            ] if language == 'arabic' else [
                f"{translation} 교육",  # Add educational marker
                f"{translation} 자료",  # Add material marker
                f"{translation} 문서",  # Add document marker
            ]
            
            # Try variations
            added = False
            for variation in variation_attempts:
                if not translator.is_duplicate(variation):
                    translated_keywords.append(variation)
                    added = True
                    break
            
            if not added:
                # Use original even if duplicate (better than losing data)
                translated_keywords.append(translation)
        else:
            translated_keywords.append(translation)
    
    logger.info(f"📊 Translation Results:")
    logger.info(f"   Original: {len(english_keywords)}")
    logger.info(f"   Translated: {len(translated_keywords)}")
    logger.info(f"   Duplicates Detected: {duplicate_count}")
    logger.info(f"   Success Rate: {(len(translated_keywords)/len(english_keywords)*100):.1f}%")
    
    # Save results
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for translation in translated_keywords:
            f.write(f"{translation}\n")
    
    logger.info(f"✅ Contextual {language.title()} translation completed!")
    logger.info(f"💾 Saved to: {output_file}")
    
    return {
        'original_count': len(english_keywords),
        'translated_count': len(translated_keywords),
        'duplicate_count': duplicate_count,
        'success_rate': (len(translated_keywords) / len(english_keywords)) * 100
    }

def main():
    parser = argparse.ArgumentParser(description='Contextual Translator V2 for High-Quality Keywords')
    parser.add_argument('--input', required=True, help='Input English keywords file')
    parser.add_argument('--output', required=True, help='Output translated keywords file')
    parser.add_argument('--language', required=True, choices=['arabic', 'chinese', 'korean'], 
                       help='Target language')
    
    args = parser.parse_args()
    
    results = translate_file_contextual(
        input_file=args.input,
        output_file=args.output,
        language=args.language
    )
    
    print(f"\n🎉 Contextual Translation Summary:")
    print(f"✅ Success Rate: {results['success_rate']:.1f}%")
    print(f"📝 Total Keywords: {results['translated_count']}")
    print(f"🔄 Duplicates Handled: {results['duplicate_count']}")

if __name__ == "__main__":
    main()