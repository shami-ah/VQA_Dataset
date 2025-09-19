import os
import shutil
import argparse
import json
import hashlib
import re
from typing import Dict, List, Tuple
from PIL import Image
from tqdm import tqdm
import easyocr


def is_arabic_text(text: str, min_arabic_ratio: float = 0.6) -> bool:
    """
    Check if text is predominantly Arabic
    
    Args:
        text: Text to analyze
        min_arabic_ratio: Minimum ratio of Arabic characters required
        
    Returns:
        True if text is predominantly Arabic
    """
    if not text or len(text.strip()) < 3:
        return False
    
    # Count Arabic characters (including Arabic-Indic digits and punctuation)
    arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF' or '\u0750' <= c <= '\u077F')
    # Count Arabic-Indic numerals
    arabic_numerals = sum(1 for c in text if '\u0660' <= c <= '\u0669')
    
    total_chars = len(text.replace(' ', '').replace('\n', ''))
    
    if total_chars == 0:
        return False
    
    arabic_ratio = (arabic_chars + arabic_numerals) / total_chars
    return arabic_ratio >= min_arabic_ratio


def has_arabic_educational_keywords(text: str) -> bool:
    """
    Check if text contains Arabic educational keywords
    
    Args:
        text: Text to analyze
        
    Returns:
        True if text contains Arabic educational keywords
    """
    arabic_educational_keywords = [
        # Learning and education
        'تعلم', 'تعليم', 'دراسة', 'مدرسة', 'درس', 'طالب', 'معلم', 'تلميذ',
        # Subjects
        'رياضيات', 'علوم', 'فيزياء', 'كيمياء', 'أحياء', 'تاريخ', 'جغرافيا',
        'لغة', 'أدب', 'نحو', 'قواعد', 'مفردات', 'معادلة', 'صيغة',
        # Academic terms
        'مسألة', 'حل', 'جواب', 'سؤال', 'امتحان', 'اختبار', 'واجب',
        'فصل', 'وحدة', 'رسم', 'مخطط', 'جدول', 'شكل', 'مثال',
        # Numbers and math
        'عدد', 'حساب', 'جمع', 'طرح', 'ضرب', 'قسمة', 'كسر', 'نسبة'
    ]
    
    return any(keyword in text for keyword in arabic_educational_keywords)


def detect_watermarks_arabic(image_path: str, ocr_text: str) -> Tuple[bool, str]:
    """
    Detect watermarks in Arabic images using OCR text and filename analysis
    
    Args:
        image_path: Path to the image
        ocr_text: OCR extracted text
        
    Returns:
        Tuple of (has_watermark, watermark_source)
    """
    # Check for Getty Images watermarks
    getty_indicators = [
        'getty', 'gettyimages', 'getty images', 'watermark'
    ]
    
    # Check for other stock photo watermarks
    stock_indicators = [
        'shutterstock', 'istockphoto', 'adobe stock', 'depositphotos',
        'dreamstime', 'bigstock', 'alamy', 'corbis', 'fotolia'
    ]
    
    # Arabic watermark indicators
    arabic_watermark_indicators = [
        'علامة مائية', 'حقوق محفوظة', 'نموذج', 'عينة'
    ]
    
    # Check filename for watermark indicators
    filename = os.path.basename(image_path).lower()
    
    # Check OCR text for watermarks
    text_lower = ocr_text.lower() if ocr_text else ""
    
    # Getty Images detection
    if any(indicator in text_lower for indicator in getty_indicators):
        return True, "Getty Images"
    
    if any(indicator in filename for indicator in getty_indicators):
        return True, "Getty Images"
    
    # Other stock photo detection
    for indicator in stock_indicators:
        if indicator in text_lower or indicator in filename:
            return True, f"Stock Photo ({indicator.title()})"
    
    # Arabic watermark detection
    for indicator in arabic_watermark_indicators:
        if indicator in ocr_text:
            return True, "Arabic Watermark"
    
    # Copyright patterns
    watermark_patterns = [
        r'©\s*\d{4}',  # Copyright with year
        r'copyright\s+\d{4}',
        r'all rights reserved',
        r'watermark',
        r'preview',
        r'sample'
    ]
    
    for pattern in watermark_patterns:
        if re.search(pattern, text_lower):
            return True, "Copyright/Watermark"
    
    return False, ""


def is_high_quality_arabic_educational_image(image_path: str, ocr_text: str) -> Dict:
    """
    Comprehensive quality check for Arabic educational images
    
    Args:
        image_path: Path to the image
        ocr_text: OCR extracted text
        
    Returns:
        Dictionary with quality assessment results
    """
    assessment = {
        'is_quality': True,
        'reasons': [],
        'arabic_text': False,
        'educational_content': False,
        'has_watermark': False,
        'watermark_source': '',
        'text_length': len(ocr_text) if ocr_text else 0
    }
    
    # Check if predominantly Arabic text
    assessment['arabic_text'] = is_arabic_text(ocr_text)
    if not assessment['arabic_text']:
        assessment['is_quality'] = False
        assessment['reasons'].append("Not predominantly Arabic text")
    
    # Check for educational content
    assessment['educational_content'] = has_arabic_educational_keywords(ocr_text)
    if not assessment['educational_content']:
        assessment['reasons'].append("No Arabic educational keywords detected")
    
    # Check for watermarks
    has_watermark, watermark_source = detect_watermarks_arabic(image_path, ocr_text)
    assessment['has_watermark'] = has_watermark
    assessment['watermark_source'] = watermark_source
    if has_watermark:
        assessment['is_quality'] = False
        assessment['reasons'].append(f"Watermark detected: {watermark_source}")
    
    # Check text length (minimum meaningful content)
    if assessment['text_length'] < 8:  # Shorter for Arabic due to compact writing
        assessment['is_quality'] = False
        assessment['reasons'].append("Insufficient text content")
    
    return assessment


def process_images(source_dir, save_dir):
    """
    Enhanced OCR-filter for Arabic educational images with watermark detection.
    Only high-quality images with Arabic educational text and no watermarks are saved.
    """
    annotation_path = os.path.join(save_dir, "annotations.json")
    filter_arabic_images(source_dir, save_dir, annotation_path)


def filter_arabic_images(input_dir, output_dir, annotation_path):
    """
    Enhanced Arabic OCR filter with educational content validation and watermark detection
    """
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        reader = easyocr.Reader(['ar'], verbose=False, gpu=False)
    except Exception as e:
        print(f"⚠️ Failed to initialize Arabic EasyOCR: {e}")
        print("💡 Install EasyOCR: pip install easyocr")
        return

    # Recursive image file search
    files = []
    for root, _, filenames in os.walk(input_dir):
        for fname in filenames:
            if fname.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                files.append(os.path.join(root, fname))

    seen_hashes = set()
    annotations = []
    
    # Statistics tracking
    stats = {
        'total_processed': 0,
        'ocr_successful': 0,
        'arabic_text': 0,
        'educational_content': 0,
        'watermark_rejected': 0,
        'final_accepted': 0
    }

    print("🔍 Starting enhanced Arabic OCR processing...")
    print("✅ Filtering for: Arabic text + Educational content + No watermarks")

    for src_path in tqdm(files, desc="🔍 Processing Arabic images"):
        stats['total_processed'] += 1
        
        try:
            img = Image.open(src_path)
            result = reader.readtext(img)
            ocr_text = " ".join([x[1] for x in result])
            stats['ocr_successful'] += 1
        except Exception as e:
            print(f"⚠️ OCR error on {os.path.basename(src_path)}: {e}")
            continue

        if not ocr_text:
            continue

        # Enhanced quality assessment
        quality_check = is_high_quality_arabic_educational_image(src_path, ocr_text)
        
        # Update statistics
        if quality_check['arabic_text']:
            stats['arabic_text'] += 1
        if quality_check['educational_content']:
            stats['educational_content'] += 1
        if quality_check['has_watermark']:
            stats['watermark_rejected'] += 1
            continue

        # Only process high-quality images
        if not quality_check['is_quality']:
            continue

        # Deduplicate by content hash
        try:
            with open(src_path, 'rb') as f:
                h = hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            continue

        if h in seen_hashes:
            continue
        seen_hashes.add(h)

        # Copy high-quality image
        dst_path = os.path.join(output_dir, os.path.basename(src_path))
        shutil.copy(src_path, dst_path)

        annotations.append({
            "filename": os.path.basename(src_path),
            "image_path": dst_path,
            "original_path": src_path,
            "text": ocr_text,
            "quality_assessment": quality_check,
            "text_length": len(ocr_text),
            "educational_score": 1.0 if quality_check['educational_content'] else 0.0
        })
        
        stats['final_accepted'] += 1

    # Save enhanced annotations
    with open(annotation_path, "w", encoding="utf-8") as f:
        json.dump({
            'annotations': annotations,
            'statistics': stats,
            'processing_summary': {
                'total_images_processed': stats['total_processed'],
                'images_with_text': stats['ocr_successful'],
                'arabic_text_images': stats['arabic_text'],
                'educational_content_images': stats['educational_content'],
                'watermarked_rejected': stats['watermark_rejected'],
                'final_high_quality_images': stats['final_accepted'],
                'quality_rate': f"{(stats['final_accepted']/max(stats['total_processed'], 1))*100:.1f}%"
            }
        }, f, indent=2, ensure_ascii=False)

    # Print comprehensive summary
    print("\n🎯 ENHANCED ARABIC OCR PROCESSING COMPLETE!")
    print("=" * 60)
    print(f"📊 Total images processed: {stats['total_processed']}")
    print(f"🔍 OCR successful: {stats['ocr_successful']}")
    print(f"🇸🇦 Arabic text detected: {stats['arabic_text']}")
    print(f"📚 Educational content: {stats['educational_content']}")
    print(f"🚫 Watermarks rejected: {stats['watermark_rejected']}")
    print(f"✅ Final high-quality images: {stats['final_accepted']}")
    print(f"📈 Quality rate: {(stats['final_accepted']/max(stats['total_processed'], 1))*100:.1f}%")
    print("=" * 60)
    print(f"📁 High-quality images saved to: {output_dir}")
    print(f"📄 Detailed annotations saved to: {annotation_path}")
    print("🎉 Ready for Phase 2 VQA generation!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🧠 Filter Arabic Images with EasyOCR")
    parser.add_argument("--input_dir", type=str, required=True, help="Directory of scraped images")
    parser.add_argument("--output_dir", type=str, required=True, help="Where to save filtered Arabic images")
    args = parser.parse_args()

    annotation_path = os.path.join(args.output_dir, "annotations.json")
    filter_arabic_images(args.input_dir, args.output_dir, annotation_path)