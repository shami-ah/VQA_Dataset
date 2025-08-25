#!/usr/bin/env python3
"""
Advanced English to Arabic Keywords Translation Script
Translates educational and technical keywords with optimized batching for large datasets.
Designed specifically for high-quality image scraping with native Arabic terms.
"""

import os
import sys
import json
import time
import logging
from typing import List, Dict, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ArabicKeywordTranslator:
    """Professional English to Arabic keyword translator optimized for image scraping."""
    
    def __init__(self):
        """Initialize the translator with educational domain expertise."""
        # Common educational/technical terms mapping for consistency
        self.technical_terms = {
            "worksheet": "ورقة عمل",
            "template": "نموذج", 
            "form": "استمارة",
            "document": "وثيقة",
            "chart": "مخطط",
            "diagram": "رسم بياني",
            "poster": "ملصق",
            "manual": "دليل",
            "guide": "مرشد",
            "report": "تقرير",
            "certificate": "شهادة",
            "academic": "أكاديمي",
            "educational": "تعليمي",
            "training": "تدريب",
            "learning": "تعلم",
            "study": "دراسة",
            "course": "دورة",
            "lesson": "درس",
            "textbook": "كتاب مدرسي",
            "reference": "مرجع",
            "curriculum": "منهج",
            "syllabus": "مقرر",
            "assessment": "تقييم",
            "examination": "امتحان",
            "assignment": "مهمة",
            "project": "مشروع",
            "presentation": "عرض تقديمي",
            "research": "بحث",
            "analysis": "تحليل",
            "summary": "ملخص",
            "outline": "مخطط",
            "overview": "نظرة عامة",
            "introduction": "مقدمة",
            "conclusion": "خاتمة",
            "methodology": "منهجية",
            "bibliography": "ببليوغرافيا",
            "glossary": "مسرد",
            "index": "فهرس",
            "appendix": "ملحق",
            "table": "جدول",
            "figure": "شكل",
            "image": "صورة",
            "illustration": "رسم توضيحي",
            "graph": "رسم بياني",
            "flowchart": "مخطط انسيابي",
            "timeline": "خط زمني",
            "calendar": "تقويم",
            "schedule": "جدول زمني",
            "agenda": "جدول أعمال",
            "checklist": "قائمة مراجعة",
            "inventory": "جرد",
            "catalog": "فهرس",
            "directory": "دليل",
            "list": "قائمة",
            "menu": "قائمة",
            "recipe": "وصفة",
            "instructions": "تعليمات",
            "procedure": "إجراء",
            "process": "عملية",
            "method": "طريقة",
            "technique": "تقنية",
            "strategy": "استراتيجية",
            "approach": "نهج",
            "framework": "إطار عمل",
            "model": "نموذج",
            "theory": "نظرية",
            "concept": "مفهوم",
            "principle": "مبدأ",
            "rule": "قاعدة",
            "law": "قانون",
            "formula": "صيغة",
            "equation": "معادلة",
            "calculation": "حساب",
            "solution": "حل",
            "answer": "إجابة",
            "result": "نتيجة",
            "outcome": "مخرج",
            "output": "ناتج",
            "input": "مدخل",
            "data": "بيانات",
            "information": "معلومات",
            "knowledge": "معرفة",
            "skill": "مهارة",
            "ability": "قدرة",
            "competency": "كفاءة",
            "objective": "هدف",
            "goal": "غاية",
            "target": "هدف",
            "purpose": "غرض",
            "function": "وظيفة",
            "role": "دور",
            "responsibility": "مسؤولية",
            "task": "مهمة",
            "job": "عمل",
            "work": "عمل",
            "activity": "نشاط",
            "exercise": "تمرين",
            "practice": "ممارسة",
            "drill": "تدريب",
            "quiz": "اختبار قصير",
            "test": "اختبار",
            "exam": "امتحان",
            "evaluation": "تقييم",
            "review": "مراجعة",
            "feedback": "تغذية راجعة",
            "comment": "تعليق",
            "note": "ملاحظة",
            "annotation": "تعليق توضيحي",
            "label": "تسمية",
            "title": "عنوان",
            "heading": "عنوان فرعي",
            "subtitle": "عنوان فرعي",
            "caption": "تسمية توضيحية",
            "description": "وصف",
            "definition": "تعريف",
            "explanation": "شرح",
            "clarification": "توضيح",
            "interpretation": "تفسير",
            "translation": "ترجمة",
            "version": "نسخة",
            "edition": "طبعة",
            "copy": "نسخة",
            "sample": "عينة",
            "example": "مثال",
            "instance": "حالة",
            "case": "حالة",
            "scenario": "سيناريو",
            "situation": "موقف",
            "context": "سياق",
            "background": "خلفية",
            "history": "تاريخ",
            "origin": "أصل",
            "source": "مصدر",
            "reference": "مرجع",
            "citation": "اقتباس",
            "quote": "اقتباس",
            "excerpt": "مقتطف",
            "passage": "مقطع",
            "section": "قسم",
            "chapter": "فصل",
            "unit": "وحدة",
            "module": "وحدة",
            "component": "مكون",
            "element": "عنصر",
            "factor": "عامل",
            "variable": "متغير",
            "parameter": "معامل",
            "criterion": "معيار",
            "standard": "معيار",
            "benchmark": "معيار مرجعي",
            "indicator": "مؤشر",
            "measure": "مقياس",
            "metric": "مقياس",
            "scale": "مقياس",
            "range": "نطاق",
            "scope": "نطاق",
            "extent": "مدى",
            "degree": "درجة",
            "level": "مستوى",
            "grade": "درجة",
            "rank": "رتبة",
            "position": "موضع",
            "location": "موقع",
            "place": "مكان",
            "site": "موقع",
            "area": "منطقة",
            "region": "منطقة",
            "zone": "منطقة",
            "field": "مجال",
            "domain": "نطاق",
            "sector": "قطاع",
            "industry": "صناعة",
            "business": "أعمال",
            "company": "شركة",
            "organization": "منظمة",
            "institution": "مؤسسة",
            "agency": "وكالة",
            "department": "قسم",
            "division": "شعبة",
            "branch": "فرع",
            "office": "مكتب",
            "center": "مركز",
            "facility": "منشأة",
            "building": "مبنى",
            "structure": "هيكل",
            "system": "نظام",
            "network": "شبكة",
            "platform": "منصة",
            "interface": "واجهة",
            "application": "تطبيق",
            "software": "برنامج",
            "program": "برنامج",
            "tool": "أداة",
            "device": "جهاز",
            "equipment": "معدات",
            "machine": "آلة",
            "instrument": "أداة",
            "apparatus": "جهاز",
            "technology": "تقنية",
            "innovation": "ابتكار",
            "development": "تطوير",
            "improvement": "تحسين",
            "enhancement": "تحسين",
            "upgrade": "ترقية",
            "update": "تحديث",
            "revision": "مراجعة",
            "modification": "تعديل",
            "change": "تغيير",
            "adjustment": "تعديل",
            "correction": "تصحيح",
            "fix": "إصلاح",
            "repair": "إصلاح",
            "maintenance": "صيانة",
            "service": "خدمة",
            "support": "دعم",
            "assistance": "مساعدة",
            "help": "مساعدة",
            "guidance": "توجيه",
            "advice": "نصيحة",
            "recommendation": "توصية",
            "suggestion": "اقتراح",
            "proposal": "اقتراح",
            "plan": "خطة",
            "scheme": "مخطط",
            "design": "تصميم",
            "layout": "تخطيط",
            "format": "تنسيق",
            "style": "نمط",
            "pattern": "نمط",
            "template": "قالب",
            "framework": "إطار عمل",
            "structure": "هيكل",
            "organization": "تنظيم",
            "arrangement": "ترتيب",
            "order": "ترتيب",
            "sequence": "تسلسل",
            "series": "سلسلة",
            "set": "مجموعة",
            "group": "مجموعة",
            "category": "فئة",
            "class": "فئة",
            "type": "نوع",
            "kind": "نوع",
            "sort": "نوع",
            "variant": "متغير",
            "option": "خيار",
            "alternative": "بديل",
            "choice": "اختيار",
            "selection": "اختيار",
            "pick": "اختيار",
            "preference": "تفضيل",
            "priority": "أولوية",
            "importance": "أهمية",
            "significance": "أهمية",
            "relevance": "صلة",
            "connection": "ارتباط",
            "relationship": "علاقة",
            "association": "ارتباط",
            "link": "رابط",
            "bond": "رابطة",
            "tie": "رابطة",
            "attachment": "مرفق",
            "addition": "إضافة",
            "supplement": "مكمل",
            "extension": "امتداد",
            "expansion": "توسع",
            "growth": "نمو",
            "increase": "زيادة",
            "rise": "ارتفاع",
            "improvement": "تحسن",
            "progress": "تقدم",
            "advancement": "تقدم",
            "achievement": "إنجاز",
            "success": "نجاح",
            "accomplishment": "إنجاز",
            "completion": "إكمال",
            "finish": "انتهاء",
            "end": "نهاية",
            "conclusion": "خاتمة",
            "result": "نتيجة",
            "outcome": "مخرج",
            "consequence": "عواقب",
            "effect": "تأثير",
            "impact": "تأثير",
            "influence": "تأثير",
            "power": "قوة",
            "strength": "قوة",
            "capacity": "سعة",
            "capability": "قدرة",
            "potential": "إمكانية",
            "possibility": "احتمال",
            "opportunity": "فرصة",
            "chance": "فرصة",
            "prospect": "احتمال",
            "future": "مستقبل",
            "tomorrow": "غدا",
            "next": "التالي",
            "following": "التالي",
            "subsequent": "لاحق",
            "later": "لاحقا",
            "after": "بعد",
            "before": "قبل",
            "previous": "سابق",
            "prior": "سابق",
            "earlier": "أسبق",
            "first": "أول",
            "initial": "أولي",
            "beginning": "بداية",
            "start": "بداية",
            "opening": "افتتاح",
            "introduction": "مقدمة",
            "preface": "مقدمة",
            "foreword": "تمهيد",
            "prologue": "مقدمة",
            "preamble": "ديباجة",
            "abstract": "ملخص",
            "summary": "ملخص",
            "overview": "نظرة عامة",
            "synopsis": "ملخص",
            "brief": "موجز",
            "outline": "مخطط",
            "sketch": "رسم تخطيطي",
            "draft": "مسودة",
            "prototype": "نموذج أولي",
            "model": "نموذج",
            "sample": "عينة",
            "specimen": "عينة",
            "example": "مثال",
            "illustration": "مثال",
            "demonstration": "عرض توضيحي",
            "presentation": "عرض",
            "display": "عرض",
            "exhibition": "معرض",
            "show": "عرض",
            "performance": "أداء",
            "execution": "تنفيذ",
            "implementation": "تطبيق",
            "application": "تطبيق",
            "use": "استخدام",
            "usage": "استخدام",
            "utilization": "استغلال",
            "employment": "توظيف",
            "operation": "تشغيل",
            "function": "وظيفة",
            "purpose": "غرض",
            "aim": "هدف",
            "objective": "هدف",
            "goal": "هدف",
            "target": "هدف",
            "intention": "قصد",
            "plan": "خطة",
            "strategy": "استراتيجية",
            "approach": "نهج",
            "method": "طريقة",
            "technique": "تقنية",
            "procedure": "إجراء",
            "process": "عملية",
            "system": "نظام",
            "mechanism": "آلية",
            "means": "وسيلة",
            "way": "طريقة",
            "route": "طريق",
            "path": "مسار",
            "course": "مسار",
            "direction": "اتجاه",
            "orientation": "توجه",
            "perspective": "منظور",
            "viewpoint": "وجهة نظر",
            "opinion": "رأي",
            "view": "رؤية",
            "belief": "اعتقاد",
            "thought": "فكر",
            "idea": "فكرة",
            "concept": "مفهوم",
            "notion": "مفهوم",
            "understanding": "فهم",
            "comprehension": "فهم",
            "knowledge": "معرفة",
            "awareness": "وعي",
            "consciousness": "وعي",
            "recognition": "اعتراف",
            "acknowledgment": "اعتراف",
            "acceptance": "قبول",
            "approval": "موافقة",
            "agreement": "اتفاق",
            "consent": "موافقة",
            "permission": "إذن",
            "authorization": "تفويض",
            "license": "رخصة",
            "certificate": "شهادة",
            "diploma": "دبلوم",
            "degree": "درجة",
            "qualification": "مؤهل",
            "credential": "بيانات اعتماد",
            "certification": "شهادة",
            "validation": "تحقق",
            "verification": "تحقق",
            "confirmation": "تأكيد",
            "proof": "دليل",
            "evidence": "دليل",
            "testimony": "شهادة",
            "witness": "شاهد",
            "observer": "مراقب",
            "spectator": "مشاهد",
            "audience": "جمهور",
            "viewer": "مشاهد",
            "reader": "قارئ",
            "user": "مستخدم",
            "client": "عميل",
            "customer": "زبون",
            "consumer": "مستهلك",
            "buyer": "مشتري",
            "purchaser": "مشتري",
            "seller": "بائع",
            "vendor": "بائع",
            "supplier": "مورد",
            "provider": "مقدم",
            "source": "مصدر",
            "origin": "أصل",
            "beginning": "بداية",
            "start": "بداية",
            "commencement": "بداية",
            "initiation": "بداية",
            "launch": "إطلاق",
            "release": "إصدار",
            "publication": "نشر",
            "issue": "إصدار",
            "edition": "طبعة",
            "version": "نسخة",
            "copy": "نسخة",
            "duplicate": "نسخة مكررة",
            "replica": "نسخة طبق الأصل",
            "reproduction": "نسخة مستنسخة",
            "print": "طباعة",
            "publication": "منشور",
            "document": "وثيقة",
            "paper": "ورقة",
            "file": "ملف",
            "record": "سجل",
            "archive": "أرشيف",
            "database": "قاعدة بيانات",
            "collection": "مجموعة",
            "compilation": "تجميع",
            "anthology": "مختارات",
            "selection": "مختارات",
            "assortment": "تشكيلة",
            "variety": "تنوع",
            "diversity": "تنوع",
            "range": "نطاق",
            "spectrum": "طيف",
            "array": "مصفوفة",
            "series": "سلسلة",
            "sequence": "تسلسل",
            "order": "ترتيب",
            "arrangement": "ترتيب",
            "organization": "تنظيم",
            "structure": "هيكل",
            "layout": "تخطيط",
            "design": "تصميم",
            "plan": "خطة",
            "blueprint": "مخطط",
            "scheme": "مخطط",
            "pattern": "نمط",
            "template": "قالب",
            "format": "تنسيق",
            "style": "نمط"
        }
        
        # Domain-specific prefixes/suffixes
        self.educational_prefixes = {
            "academic": "أكاديمي",
            "educational": "تعليمي", 
            "learning": "تعلم",
            "study": "دراسة",
            "training": "تدريب",
            "teaching": "تدريس",
            "instructional": "تعليمي",
            "tutorial": "تعليمي",
            "course": "دورة",
            "lesson": "درس",
            "class": "فصل",
            "school": "مدرسة",
            "university": "جامعة",
            "college": "كلية",
            "student": "طالب",
            "teacher": "معلم",
            "instructor": "مدرب",
            "professor": "أستاذ"
        }
        
        # Visual/media related terms
        self.visual_terms = {
            "closeup": "لقطة مقربة",
            "detailed": "مفصل", 
            "photography": "تصوير فوتوغرافي",
            "image": "صورة",
            "photo": "صورة",
            "picture": "صورة",
            "scan": "مسح ضوئي",
            "view": "منظر",
            "overview": "نظرة عامة",
            "macro": "كبير",
            "flat lay": "تخطيط مسطح",
            "high resolution": "دقة عالية",
            "visible": "مرئي",
            "readable": "قابل للقراءة",
            "clear": "واضح",
            "sharp": "حاد",
            "focused": "مركز"
        }
        
        # Text type descriptors
        self.text_types = {
            "handwritten": "مكتوب بخط اليد",
            "typed": "مطبوع",
            "printed": "مطبوع", 
            "digital": "رقمي",
            "cursive": "خط متصل",
            "block letters": "أحرف مربعة",
            "calligraphy": "خط جميل",
            "alphabetical": "أبجدي",
            "numerical": "رقمي",
            "technical": "تقني",
            "formatted": "منسق",
            "mixed": "مختلط"
        }

    def translate_keyword_batch(self, keywords: List[str]) -> List[str]:
        """
        Translate a batch of English keywords to Arabic.
        Optimized for educational/technical terms commonly found in images.
        """
        translated = []
        
        for keyword in keywords:
            try:
                arabic_translation = self._translate_single_keyword(keyword)
                if arabic_translation:
                    translated.append(arabic_translation)
                    logger.debug(f"Translated: '{keyword}' -> '{arabic_translation}'")
                else:
                    logger.warning(f"Could not translate keyword: '{keyword}'")
            except Exception as e:
                logger.error(f"Error translating '{keyword}': {e}")
                continue
        
        return translated

    def _translate_single_keyword(self, keyword: str) -> Optional[str]:
        """
        Translate a single keyword with domain-specific intelligence.
        Handles complex educational phrases and technical terminology.
        """
        keyword = keyword.strip()
        if not keyword:
            return None
            
        # Handle simple direct mappings first
        if keyword in self.technical_terms:
            return self.technical_terms[keyword]
        
        # Break down complex phrases
        words = keyword.split()
        translated_words = []
        
        for word in words:
            # Clean up word
            clean_word = word.lower().strip()
            
            # Direct mapping
            if clean_word in self.technical_terms:
                translated_words.append(self.technical_terms[clean_word])
            elif clean_word in self.educational_prefixes:
                translated_words.append(self.educational_prefixes[clean_word])
            elif clean_word in self.visual_terms:
                translated_words.append(self.visual_terms[clean_word])
            elif clean_word in self.text_types:
                translated_words.append(self.text_types[clean_word])
            else:
                # Apply intelligent translation for common patterns
                translated_word = self._intelligent_word_translation(clean_word)
                if translated_word:
                    translated_words.append(translated_word)
                else:
                    # Fallback: use basic translation
                    basic_translation = self._basic_translate(clean_word)
                    if basic_translation:
                        translated_words.append(basic_translation)
        
        # Join translated words
        if translated_words:
            return " ".join(translated_words)
        
        return None

    def _intelligent_word_translation(self, word: str) -> Optional[str]:
        """Apply intelligent translation patterns for educational terms."""
        
        # Common educational suffixes
        if word.endswith('ing'):
            base = word[:-3]
            if base in self.technical_terms:
                return self.technical_terms[base]
        
        # Plural forms
        if word.endswith('s') and len(word) > 3:
            singular = word[:-1]
            if singular in self.technical_terms:
                return self.technical_terms[singular]
        
        # Technical suffixes
        if word.endswith('ment'):
            return f"إدارة {word[:-4]}" if len(word) > 4 else None
        
        if word.endswith('tion'):
            base = word[:-4]
            return f"عملية {base}" if base else None
            
        # Size/quality descriptors
        size_quality_map = {
            "small": "صغير",
            "large": "كبير", 
            "big": "كبير",
            "tiny": "صغير جداً",
            "huge": "ضخم",
            "mini": "مصغر",
            "micro": "مجهري",
            "macro": "كبير",
            "standard": "قياسي",
            "regular": "عادي",
            "normal": "عادي",
            "basic": "أساسي",
            "advanced": "متقدم",
            "professional": "مهني",
            "expert": "خبير",
            "beginner": "مبتدئ",
            "intermediate": "متوسط"
        }
        
        if word in size_quality_map:
            return size_quality_map[word]
            
        return None

    def _basic_translate(self, word: str) -> Optional[str]:
        """Basic translation for common English words."""
        basic_dict = {
            # Colors
            "red": "أحمر", "blue": "أزرق", "green": "أخضر", "yellow": "أصفر",
            "black": "أسود", "white": "أبيض", "orange": "برتقالي", "purple": "بنفسجي",
            "pink": "وردي", "brown": "بني", "gray": "رمادي", "grey": "رمادي",
            
            # Numbers
            "one": "واحد", "two": "اثنان", "three": "ثلاثة", "four": "أربعة",
            "five": "خمسة", "six": "ستة", "seven": "سبعة", "eight": "ثمانية", 
            "nine": "تسعة", "ten": "عشرة",
            
            # Basic adjectives
            "new": "جديد", "old": "قديم", "good": "جيد", "bad": "سيء",
            "big": "كبير", "small": "صغير", "long": "طويل", "short": "قصير",
            "high": "عالي", "low": "منخفض", "fast": "سريع", "slow": "بطيء",
            "hot": "ساخن", "cold": "بارد", "warm": "دافئ", "cool": "بارد",
            
            # Common nouns
            "book": "كتاب", "page": "صفحة", "line": "سطر", "word": "كلمة",
            "letter": "حرف", "number": "رقم", "text": "نص", "writing": "كتابة",
            "title": "عنوان", "name": "اسم", "date": "تاريخ", "time": "وقت",
            "year": "سنة", "month": "شهر", "day": "يوم", "week": "أسبوع",
            
            # Subjects
            "math": "رياضيات", "mathematics": "رياضيات", "science": "علوم",
            "english": "إنجليزية", "arabic": "عربية", "history": "تاريخ",
            "geography": "جغرافيا", "biology": "أحياء", "chemistry": "كيمياء",
            "physics": "فيزياء", "art": "فن", "music": "موسيقى", "sports": "رياضة",
            
            # Actions
            "read": "قراءة", "write": "كتابة", "learn": "تعلم", "teach": "تدريس",
            "study": "دراسة", "practice": "ممارسة", "exercise": "تمرين", "work": "عمل",
            "play": "لعب", "draw": "رسم", "paint": "رسم", "create": "إنشاء",
            
            # Common prepositions/articles
            "with": "مع", "and": "و", "or": "أو", "for": "لـ", "to": "إلى",
            "from": "من", "in": "في", "on": "على", "at": "في", "by": "بواسطة"
        }
        
        return basic_dict.get(word.lower())

    def process_large_file(self, input_file: str, output_file: str, batch_size: int = 100):
        """
        Process large keyword file in batches to manage memory and token usage.
        """
        logger.info(f"Starting translation of {input_file}")
        logger.info(f"Processing in batches of {batch_size} keywords")
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                all_keywords = [line.strip() for line in f if line.strip()]
            
            total_keywords = len(all_keywords)
            logger.info(f"Total keywords to translate: {total_keywords}")
            
            translated_keywords = []
            processed = 0
            
            # Process in batches
            for i in range(0, total_keywords, batch_size):
                batch = all_keywords[i:i + batch_size]
                
                logger.info(f"Processing batch {i//batch_size + 1}/{(total_keywords + batch_size - 1)//batch_size}")
                
                batch_translated = self.translate_keyword_batch(batch)
                translated_keywords.extend(batch_translated)
                processed += len(batch)
                
                # Progress update
                progress = (processed / total_keywords) * 100
                logger.info(f"Progress: {processed}/{total_keywords} ({progress:.1f}%)")
                
                # Add small delay to be respectful
                time.sleep(0.1)
            
            # Save translated keywords
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                for keyword in translated_keywords:
                    f.write(keyword + '\n')
            
            logger.info(f"Translation completed successfully!")
            logger.info(f"Original keywords: {total_keywords}")
            logger.info(f"Translated keywords: {len(translated_keywords)}")
            logger.info(f"Success rate: {(len(translated_keywords)/total_keywords)*100:.1f}%")
            logger.info(f"Output saved to: {output_file}")
            
            return len(translated_keywords)
            
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            raise


def main():
    """Main function to handle command line execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Translate English educational keywords to native Arabic for image scraping'
    )
    parser.add_argument(
        '--input', 
        required=True,
        help='Path to input English keywords file'
    )
    parser.add_argument(
        '--output',
        required=True, 
        help='Path to output Arabic keywords file'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Number of keywords to process in each batch (default: 100)'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        sys.exit(1)
    
    # Initialize translator
    translator = ArabicKeywordTranslator()
    
    # Process the file
    try:
        translated_count = translator.process_large_file(
            args.input,
            args.output, 
            args.batch_size
        )
        
        logger.info(f"✅ Translation completed successfully!")
        logger.info(f"📊 {translated_count} Arabic keywords generated")
        
    except Exception as e:
        logger.error(f"❌ Translation failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()