#!/usr/bin/env python3
import os
import argparse
import json
import shutil
import hashlib
import easyocr
import re
from typing import Dict, List, Tuple

from PIL import Image


def is_korean_text(text: str, min_korean_ratio: float = 0.7) -> bool:
    """
    Check if text is predominantly Korean (Hangul)
    
    Args:
        text: Text to analyze
        min_korean_ratio: Minimum ratio of Korean characters required
        
    Returns:
        True if text is predominantly Korean
    """
    if not text or len(text.strip()) < 3:
        return False
    
    # Remove whitespace and punctuation for analysis
    clean_text = re.sub(r'[^\w\s]', '', text)
    if len(clean_text) < 2:
        return False
    
    # Count Korean Hangul characters
    korean_chars = sum(1 for c in clean_text if '\uAC00' <= c <= '\uD7AF')  # Hangul syllables
    total_chars = len(clean_text.replace(' ', ''))
    
    if total_chars == 0:
        return False
    
    korean_ratio = korean_chars / total_chars
    return korean_ratio >= min_korean_ratio


def has_educational_keywords(text: str) -> bool:
    """
    Check if text contains Korean educational keywords that indicate learning content
    
    Args:
        text: Text to analyze
        
    Returns:
        True if text contains educational keywords
    """
    educational_keywords = [
        '학습', '공부', '교육', '학교', '수업', '가르치다', '학생',
        '수학', '과학', '물리', '화학', '생물', '역사',
        '지리', '문학', '문법', '어휘', '방정식',
        '공식', '문제', '해답', '답', '질문', '시험',
        '테스트', '퀴즈', '숙제', '과제', '장', '단원',
        '도표', '그래프', '차트', '표', '그림', '예제',
        '지식', '과목', '강의', '교수', '선생님', '배우다'
    ]
    
    # Korean text analysis
    return any(keyword in text for keyword in educational_keywords)


def detect_watermarks(image_path: str, ocr_text: str) -> Tuple[bool, str]:
    """
    Detect watermarks in images using OCR text and filename analysis
    
    Args:
        image_path: Path to the image
        ocr_text: OCR extracted text
        
    Returns:
        Tuple of (has_watermark, watermark_source)
    """
    # Check for Getty Images watermarks
    getty_indicators = [
        'getty', 'gettyimages', 'getty images', '워터마크'
    ]
    
    # Check for other stock photo watermarks
    stock_indicators = [
        'shutterstock', 'istockphoto', 'adobe stock', 'depositphotos',
        'dreamstime', 'bigstock', 'alamy', 'corbis', 'fotolia'
    ]
    
    # Korean watermark terms
    korean_watermarks = [
        '워터마크', '저작권', '샘플', '미리보기',
        '견본', '시연', '데모'
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
    
    # Korean watermark detection
    for watermark in korean_watermarks:
        if watermark in ocr_text:  # Korean text, case-sensitive
            return True, f"Korean Watermark ({watermark})"
    
    # Additional watermark patterns in text
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


def is_high_quality_educational_image(image_path: str, ocr_text: str) -> Dict:
    """
    Comprehensive quality check for Korean educational images
    
    Args:
        image_path: Path to the image
        ocr_text: OCR extracted text
        
    Returns:
        Dictionary with quality assessment results
    """
    assessment = {
        'is_quality': True,
        'reasons': [],
        'korean_text': False,
        'educational_content': False,
        'has_watermark': False,
        'watermark_source': '',
        'text_length': len(ocr_text) if ocr_text else 0
    }
    
    # Check if predominantly Korean text
    assessment['korean_text'] = is_korean_text(ocr_text)
    if not assessment['korean_text']:
        assessment['is_quality'] = False
        assessment['reasons'].append("Not predominantly Korean text")
    
    # Check for educational content
    assessment['educational_content'] = has_educational_keywords(ocr_text)
    if not assessment['educational_content']:
        assessment['reasons'].append("No educational keywords detected")
    
    # Check for watermarks
    has_watermark, watermark_source = detect_watermarks(image_path, ocr_text)
    assessment['has_watermark'] = has_watermark
    assessment['watermark_source'] = watermark_source
    if has_watermark:
        assessment['is_quality'] = False
        assessment['reasons'].append(f"Watermark detected: {watermark_source}")
    
    # Check text length (minimum meaningful content)
    if assessment['text_length'] < 5:  # Korean characters can be more dense in meaning
        assessment['is_quality'] = False
        assessment['reasons'].append("Insufficient text content")
    
    return assessment


def process_images(source_dir, save_dir):
    """
    Enhanced OCR-filter for Korean educational images with watermark detection.
    Only high-quality images with Korean educational text and no watermarks are saved.
    """
    os.makedirs(save_dir, exist_ok=True)

    # Initialize Korean EasyOCR reader
    try:
        reader = easyocr.Reader(['ko'], gpu=False)  # Use CPU for better compatibility
    except Exception as e:
        print(f"⚠️ Failed to initialize EasyOCR: {e}")
        print("💡 Install EasyOCR: pip install easyocr")
        return
    
    seen_hashes = set()
    metadata = []
    
    # Statistics tracking
    stats = {
        'total_processed': 0,
        'ocr_successful': 0,
        'korean_text': 0,
        'educational_content': 0,
        'watermark_rejected': 0,
        'final_accepted': 0
    }

    print("🔍 Starting enhanced Korean OCR processing...")
    print("✅ Filtering for: Korean text + Educational content + No watermarks")

    for root, _, files in os.walk(source_dir):
        for fname in files:
            if not fname.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                continue
            
            img_path = os.path.join(root, fname)
            stats['total_processed'] += 1

            # OCR extraction
            try:
                lines = reader.readtext(img_path, detail=0, paragraph=True)
                ocr_text = " ".join(lines).strip()
                stats['ocr_successful'] += 1
            except Exception as e:
                print(f"⚠️ OCR error on {fname}: {e}")
                continue

            if not ocr_text:
                continue

            # Enhanced quality assessment
            quality_check = is_high_quality_educational_image(img_path, ocr_text)
            
            # Update statistics
            if quality_check['korean_text']:
                stats['korean_text'] += 1
            if quality_check['educational_content']:
                stats['educational_content'] += 1
            if quality_check['has_watermark']:
                stats['watermark_rejected'] += 1
                print(f"🚫 Rejected {fname}: {quality_check['watermark_source']}")
                continue

            # Only process high-quality images
            if not quality_check['is_quality']:
                print(f"⚠️ Skipped {fname}: {', '.join(quality_check['reasons'])}")
                continue

            # Deduplicate by content hash
            try:
                with open(img_path, 'rb') as f:
                    h = hashlib.md5(f.read()).hexdigest()
            except Exception as e:
                print(f"⚠️ Hash error on {fname}: {e}")
                continue

            if h in seen_hashes:
                print(f"🔄 Duplicate skipped: {fname}")
                continue
            seen_hashes.add(h)

            # Copy and record high-quality image
            dest_fname = os.path.basename(img_path)
            dest = os.path.join(save_dir, dest_fname)
            shutil.copy2(img_path, dest)
            
            metadata.append({
                'image_path': dest,
                'original_path': img_path,
                'ocr_text': ocr_text,
                'quality_assessment': quality_check,
                'text_length': len(ocr_text),
                'educational_score': 1.0 if quality_check['educational_content'] else 0.0
            })
            
            stats['final_accepted'] += 1
            print(f"✅ Accepted: {fname} (Korean: ✓, Educational: {'✓' if quality_check['educational_content'] else '✗'}, No watermark: ✓)")

    # Write enhanced metadata
    out_file = os.path.join(save_dir, 'ocr_metadata_korean.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': metadata,
            'statistics': stats,
            'processing_summary': {
                'total_images_processed': stats['total_processed'],
                'images_with_text': stats['ocr_successful'],
                'korean_text_images': stats['korean_text'],
                'educational_content_images': stats['educational_content'],
                'watermarked_rejected': stats['watermark_rejected'],
                'final_high_quality_images': stats['final_accepted'],
                'quality_rate': f"{(stats['final_accepted']/max(stats['total_processed'], 1))*100:.1f}%"
            }
        }, f, ensure_ascii=False, indent=2)

    # Print comprehensive summary
    print("\n🎯 ENHANCED KOREAN OCR PROCESSING COMPLETE!")
    print("=" * 60)
    print(f"📊 Total images processed: {stats['total_processed']}")
    print(f"🔍 OCR successful: {stats['ocr_successful']}")
    print(f"🇰🇷 Korean text detected: {stats['korean_text']}")
    print(f"📚 Educational content: {stats['educational_content']}")
    print(f"🚫 Watermarks rejected: {stats['watermark_rejected']}")
    print(f"✅ Final high-quality images: {stats['final_accepted']}")
    print(f"📈 Quality rate: {(stats['final_accepted']/max(stats['total_processed'], 1))*100:.1f}%")
    print("=" * 60)
    print(f"📁 High-quality images saved to: {save_dir}")
    print(f"📄 Detailed metadata saved to: {out_file}")
    print("🎉 Ready for Phase 2 VQA generation!")


def main():
    parser = argparse.ArgumentParser(
        description='Filter and OCR Korean images using EasyOCR.'
    )
    parser.add_argument(
        '--source_dir', required=True,
        help='Directory of raw images'
    )
    parser.add_argument(
        '--save_dir', required=True,
        help='Directory for OCR-filtered images and metadata'
    )
    args = parser.parse_args()
    process_images(args.source_dir, args.save_dir)

if __name__ == '__main__':
    main()