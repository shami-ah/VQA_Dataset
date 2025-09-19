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


def is_german_text(text: str, min_german_ratio: float = 0.7) -> bool:
    """
    Check if text is predominantly German
    
    Args:
        text: Text to analyze
        min_german_ratio: Minimum ratio of German characteristics required
        
    Returns:
        True if text is predominantly German
    """
    if not text or len(text.strip()) < 3:
        return False
    
    # Remove whitespace and punctuation for analysis
    clean_text = re.sub(r'[^\w\s]', '', text)
    if len(clean_text) < 2:
        return False
    
    text_lower = text.lower()
    
    # German-specific characters (umlauts and ß)
    german_chars = re.findall(r'[äöüßÄÖÜ]', text)
    german_char_score = len(german_chars) * 2  # Weight German chars more
    
    # Common German words
    german_words = [
        'der', 'die', 'das', 'und', 'ist', 'sind', 'haben', 'werden',
        'mit', 'für', 'auf', 'ein', 'eine', 'einen', 'einem', 'einer',
        'nicht', 'auch', 'oder', 'aber', 'wenn', 'dann', 'kann',
        'will', 'soll', 'wird', 'war', 'waren', 'wurde', 'wurden'
    ]
    
    german_word_count = sum(1 for word in german_words if word in text_lower)
    
    # Calculate German characteristics ratio
    total_words = len(text_lower.split())
    if total_words == 0:
        return False
    
    german_score = (german_char_score + german_word_count) / max(total_words, 1)
    return german_score >= min_german_ratio


def has_german_educational_keywords(text: str) -> bool:
    """
    Check if text contains German educational keywords that indicate learning content
    
    Args:
        text: Text to analyze
        
    Returns:
        True if text contains German educational keywords
    """
    educational_keywords = [
        # Learning and education
        'lernen', 'studieren', 'bildung', 'schule', 'unterricht', 'schüler', 'lehrer',
        'student', 'studentin', 'professor', 'dozent', 'ausbildung', 'weiterbildung',
        
        # Subjects
        'mathematik', 'mathe', 'wissenschaft', 'physik', 'chemie', 'biologie',
        'geschichte', 'geographie', 'deutsch', 'englisch', 'literatur', 'grammatik',
        'wortschatz', 'vokabeln', 'sprache', 'fremdsprache',
        
        # Academic terms
        'problem', 'lösung', 'antwort', 'frage', 'prüfung', 'test', 'aufgabe',
        'übung', 'beispiel', 'regel', 'formel', 'gleichung', 'definition',
        'erklärung', 'diagramm', 'grafik', 'tabelle', 'figur', 'abbildung',
        'kapitel', 'einheit', 'lektion', 'kurs', 'seminar', 'vorlesung',
        'hausaufgabe', 'projekt', 'experiment', 'analyse', 'theorie'
    ]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in educational_keywords)


def detect_watermarks_german(image_path: str, ocr_text: str) -> Tuple[bool, str]:
    """
    Detect watermarks in images using OCR text and filename analysis for German content
    
    Args:
        image_path: Path to the image
        ocr_text: OCR extracted text
        
    Returns:
        Tuple of (has_watermark, watermark_source)
    """
    # Check for Getty Images watermarks
    getty_indicators = [
        'getty', 'gettyimages', 'getty images', 'wasserzeichen'
    ]
    
    # Check for other stock photo watermarks
    stock_indicators = [
        'shutterstock', 'istockphoto', 'adobe stock', 'depositphotos',
        'dreamstime', 'bigstock', 'alamy', 'corbis', 'fotolia'
    ]
    
    # German watermark terms
    german_watermark_terms = [
        'wasserzeichen', 'alle rechte vorbehalten', 'beispiel', 'vorschau',
        'muster', 'demo', 'probe', 'copyright', 'urheberrecht'
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
    
    # German watermark detection
    for term in german_watermark_terms:
        if term in text_lower:
            return True, "German Watermark"
    
    # Additional watermark patterns in text
    watermark_patterns = [
        r'©\s*\d{4}',  # Copyright with year
        r'copyright\s+\d{4}',
        r'urheberrecht\s+\d{4}',
        r'alle rechte vorbehalten',
        r'wasserzeichen',
        r'vorschau',
        r'beispiel',
        r'muster'
    ]
    
    for pattern in watermark_patterns:
        if re.search(pattern, text_lower):
            return True, "Copyright/Watermark"
    
    return False, ""


def is_high_quality_educational_image(image_path: str, ocr_text: str) -> Dict:
    """
    Comprehensive quality check for German educational images
    
    Args:
        image_path: Path to the image
        ocr_text: OCR extracted text
        
    Returns:
        Dictionary with quality assessment results
    """
    assessment = {
        'is_quality': True,
        'reasons': [],
        'german_text': False,
        'educational_content': False,
        'has_watermark': False,
        'watermark_source': '',
        'text_length': len(ocr_text) if ocr_text else 0
    }
    
    # Check if predominantly German text
    assessment['german_text'] = is_german_text(ocr_text)
    if not assessment['german_text']:
        assessment['is_quality'] = False
        assessment['reasons'].append("Not predominantly German text")
    
    # Check for educational content
    assessment['educational_content'] = has_german_educational_keywords(ocr_text)
    if not assessment['educational_content']:
        assessment['reasons'].append("No German educational keywords detected")
    
    # Check for watermarks
    has_watermark, watermark_source = detect_watermarks_german(image_path, ocr_text)
    assessment['has_watermark'] = has_watermark
    assessment['watermark_source'] = watermark_source
    if has_watermark:
        assessment['is_quality'] = False
        assessment['reasons'].append(f"Watermark detected: {watermark_source}")
    
    # Check text length (minimum meaningful content)
    if assessment['text_length'] < 10:
        assessment['is_quality'] = False
        assessment['reasons'].append("Insufficient text content")
    
    return assessment


def process_images(source_dir, save_dir):
    """
    Enhanced OCR-filter for German educational images with watermark detection.
    Only high-quality images with German educational text and no watermarks are saved.
    """
    os.makedirs(save_dir, exist_ok=True)

    # Initialize German EasyOCR reader
    try:
        reader = easyocr.Reader(['de'], gpu=False)  # Use CPU for better compatibility
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
        'german_text': 0,
        'educational_content': 0,
        'watermark_rejected': 0,
        'final_accepted': 0
    }

    print("🔍 Starting enhanced German OCR processing...")
    print("✅ Filtering for: German text + Educational content + No watermarks")

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
            if quality_check['german_text']:
                stats['german_text'] += 1
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
            print(f"✅ Accepted: {fname} (German: ✓, Educational: {'✓' if quality_check['educational_content'] else '✗'}, No watermark: ✓)")

    # Write enhanced metadata
    out_file = os.path.join(save_dir, 'ocr_metadata_german.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': metadata,
            'statistics': stats,
            'processing_summary': {
                'total_images_processed': stats['total_processed'],
                'images_with_text': stats['ocr_successful'],
                'german_text_images': stats['german_text'],
                'educational_content_images': stats['educational_content'],
                'watermarked_rejected': stats['watermark_rejected'],
                'final_high_quality_images': stats['final_accepted'],
                'quality_rate': f"{(stats['final_accepted']/max(stats['total_processed'], 1))*100:.1f}%"
            }
        }, f, ensure_ascii=False, indent=2)

    # Print comprehensive summary
    print("\n🎯 ENHANCED GERMAN OCR PROCESSING COMPLETE!")
    print("=" * 60)
    print(f"📊 Total images processed: {stats['total_processed']}")
    print(f"🔍 OCR successful: {stats['ocr_successful']}")
    print(f"🇩🇪 German text detected: {stats['german_text']}")
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
        description='Filter and OCR German images using EasyOCR.'
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