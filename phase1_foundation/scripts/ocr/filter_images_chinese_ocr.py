import os
import shutil
import argparse
import json
import hashlib
import re
from typing import Dict, List, Tuple
from PIL import Image
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore", message=".*pin_memory.*")
import easyocr


def is_chinese_text(text: str, min_chinese_ratio: float = 0.6) -> bool:
    """
    Check if text is predominantly Chinese
    
    Args:
        text: Text to analyze
        min_chinese_ratio: Minimum ratio of Chinese characters required
        
    Returns:
        True if text is predominantly Chinese
    """
    if not text or len(text.strip()) < 3:
        return False
    
    # Count Chinese characters (CJK Unified Ideographs)
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    # Count other CJK characters
    cjk_chars = sum(1 for c in text if '\u3400' <= c <= '\u4dbf' or '\u20000' <= c <= '\u2a6df')
    
    total_chars = len(text.replace(' ', '').replace('\n', ''))
    
    if total_chars == 0:
        return False
    
    chinese_ratio = (chinese_chars + cjk_chars) / total_chars
    return chinese_ratio >= min_chinese_ratio


def has_chinese_educational_keywords(text: str) -> bool:
    """
    Check if text contains Chinese educational keywords
    
    Args:
        text: Text to analyze
        
    Returns:
        True if text contains Chinese educational keywords
    """
    chinese_educational_keywords = [
        # Learning and education
        '学习', '教育', '学校', '课程', '学生', '老师', '教师', '同学',
        # Subjects
        '数学', '科学', '物理', '化学', '生物', '历史', '地理',
        '语文', '文学', '语法', '词汇', '方程', '公式',
        # Academic terms
        '问题', '解答', '答案', '考试', '测试', '作业',
        '章节', '单元', '图表', '图形', '例子', '练习',
        # Numbers and math
        '数字', '计算', '加法', '减法', '乘法', '除法', '分数', '比例',
        # Education related
        '知识', '理解', '掌握', '复习', '预习', '讲解'
    ]
    
    return any(keyword in text for keyword in chinese_educational_keywords)


def detect_watermarks_chinese(image_path: str, ocr_text: str) -> Tuple[bool, str]:
    """
    Detect watermarks in Chinese images using OCR text and filename analysis
    
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
    
    # Chinese watermark indicators
    chinese_watermark_indicators = [
        '水印', '版权所有', '样本', '示例', '预览'
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
    
    # Chinese watermark detection
    for indicator in chinese_watermark_indicators:
        if indicator in ocr_text:
            return True, "Chinese Watermark"
    
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


def is_high_quality_chinese_educational_image(image_path: str, ocr_text: str) -> Dict:
    """
    Comprehensive quality check for Chinese educational images
    
    Args:
        image_path: Path to the image
        ocr_text: OCR extracted text
        
    Returns:
        Dictionary with quality assessment results
    """
    assessment = {
        'is_quality': True,
        'reasons': [],
        'chinese_text': False,
        'educational_content': False,
        'has_watermark': False,
        'watermark_source': '',
        'text_length': len(ocr_text) if ocr_text else 0
    }
    
    # Check if predominantly Chinese text
    assessment['chinese_text'] = is_chinese_text(ocr_text)
    if not assessment['chinese_text']:
        assessment['is_quality'] = False
        assessment['reasons'].append("Not predominantly Chinese text")
    
    # Check for educational content
    assessment['educational_content'] = has_chinese_educational_keywords(ocr_text)
    if not assessment['educational_content']:
        assessment['reasons'].append("No Chinese educational keywords detected")
    
    # Check for watermarks
    has_watermark, watermark_source = detect_watermarks_chinese(image_path, ocr_text)
    assessment['has_watermark'] = has_watermark
    assessment['watermark_source'] = watermark_source
    if has_watermark:
        assessment['is_quality'] = False
        assessment['reasons'].append(f"Watermark detected: {watermark_source}")
    
    # Check text length (minimum meaningful content)
    if assessment['text_length'] < 6:  # Shorter for Chinese due to compact writing
        assessment['is_quality'] = False
        assessment['reasons'].append("Insufficient text content")
    
    return assessment


def normalize_text(text):
    return "".join(c for c in text if c.isalnum())


def process_images(source_dir, save_dir):
    """
    Enhanced OCR-filter for Chinese educational images with watermark detection.
    Only high-quality images with Chinese educational text and no watermarks are saved.
    """
    filter_chinese_images(source_dir, save_dir)


def filter_chinese_images(input_dir, output_dir):
    """
    Enhanced Chinese OCR filter with educational content validation and watermark detection
    """
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        reader = easyocr.Reader(['ch_sim'], verbose=False, gpu=False)
    except Exception as e:
        print(f"⚠️ Failed to initialize Chinese EasyOCR: {e}")
        print("💡 Install EasyOCR: pip install easyocr")
        return

    seen_hashes = set()
    annotations = []
    
    # Statistics tracking
    stats = {
        'total_processed': 0,
        'ocr_successful': 0,
        'chinese_text': 0,
        'educational_content': 0,
        'watermark_rejected': 0,
        'final_accepted': 0
    }

    # Recursive file search
    files = []
    for root, _, filenames in os.walk(input_dir):
        for fname in filenames:
            if fname.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                files.append(os.path.join(root, fname))

    print("🔍 Starting enhanced Chinese OCR processing...")
    print("✅ Filtering for: Chinese text + Educational content + No watermarks")

    for src_path in tqdm(files, desc="🔍 Processing Chinese images"):
        stats['total_processed'] += 1
        fname = os.path.basename(src_path)
        
        try:
            img = Image.open(src_path)
            result = reader.readtext(img)
            ocr_text = " ".join([x[1] for x in result])
            stats['ocr_successful'] += 1
        except Exception as e:
            print(f"⚠️ OCR error on {fname}: {e}")
            continue

        if not ocr_text:
            continue

        # Enhanced quality assessment
        quality_check = is_high_quality_chinese_educational_image(src_path, ocr_text)
        
        # Update statistics
        if quality_check['chinese_text']:
            stats['chinese_text'] += 1
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
        dst_path = os.path.join(output_dir, fname)
        shutil.copy(src_path, dst_path)

        annotations.append({
            "image_filename": fname,
            "image_path": dst_path,
            "original_path": src_path,
            "ocr_text": ocr_text,
            "quality_assessment": quality_check,
            "text_length": len(ocr_text),
            "educational_score": 1.0 if quality_check['educational_content'] else 0.0
        })
        
        stats['final_accepted'] += 1

    # Save enhanced annotations
    annotations_path = os.path.join(output_dir, "annotations.json")
    with open(annotations_path, "w", encoding="utf-8") as f:
        json.dump({
            'annotations': annotations,
            'statistics': stats,
            'processing_summary': {
                'total_images_processed': stats['total_processed'],
                'images_with_text': stats['ocr_successful'],
                'chinese_text_images': stats['chinese_text'],
                'educational_content_images': stats['educational_content'],
                'watermarked_rejected': stats['watermark_rejected'],
                'final_high_quality_images': stats['final_accepted'],
                'quality_rate': f"{(stats['final_accepted']/max(stats['total_processed'], 1))*100:.1f}%"
            }
        }, f, ensure_ascii=False, indent=2)

    # Print comprehensive summary
    print("\n🎯 ENHANCED CHINESE OCR PROCESSING COMPLETE!")
    print("=" * 60)
    print(f"📊 Total images processed: {stats['total_processed']}")
    print(f"🔍 OCR successful: {stats['ocr_successful']}")
    print(f"🇨🇳 Chinese text detected: {stats['chinese_text']}")
    print(f"📚 Educational content: {stats['educational_content']}")
    print(f"🚫 Watermarks rejected: {stats['watermark_rejected']}")
    print(f"✅ Final high-quality images: {stats['final_accepted']}")
    print(f"📈 Quality rate: {(stats['final_accepted']/max(stats['total_processed'], 1))*100:.1f}%")
    print("=" * 60)
    print(f"📁 High-quality images saved to: {output_dir}")
    print(f"📄 Detailed annotations saved to: {annotations_path}")
    print("🎉 Ready for Phase 2 VQA generation!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🔍 Filter Chinese images using EasyOCR")
    parser.add_argument("--input_dir", type=str, required=True)
    parser.add_argument("--output_dir", type=str, required=True)
    args = parser.parse_args()

    filter_chinese_images(args.input_dir, args.output_dir)