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


def is_french_text(text: str, min_french_ratio: float = 0.7) -> bool:
    """
    Check if text is predominantly French
    
    Args:
        text: Text to analyze
        min_french_ratio: Minimum ratio of French characters required
        
    Returns:
        True if text is predominantly French
    """
    if not text or len(text.strip()) < 3:
        return False
    
    # Remove whitespace and punctuation for analysis
    clean_text = re.sub(r'[^\w\s]', '', text)
    if len(clean_text) < 2:
        return False
    
    # French accent characters and patterns
    french_accents = set('àâäéèêëîïôöùûüÿçÀÂÄÉÈÊËÎÏÔÖÙÛÜŸÇ')
    french_patterns = [
        r'\bqu[aeiou]',  # que, qui, qua, etc.
        r'\bde\b', r'\ble\b', r'\bla\b', r'\bun\b', r'\bune\b',
        r'\bdu\b', r'\bdes\b', r'\baux\b', r'\bpar\b', r'\bpour\b',
        r'\bavec\b', r'\bsans\b', r'\bsur\b', r'\bsous\b', r'\bdans\b',
        r'\bent\b', r'\btion\b', r'\bment\b'
    ]
    
    # Count French indicators
    text_lower = text.lower()
    french_score = 0
    total_chars = len(clean_text.replace(' ', ''))
    
    if total_chars == 0:
        return False
    
    # Count accent characters
    accent_count = sum(1 for c in text if c in french_accents)
    
    # Count French patterns
    pattern_count = sum(len(re.findall(pattern, text_lower)) for pattern in french_patterns)
    
    # Calculate French ratio (accents + patterns relative to text length)
    french_indicators = accent_count + pattern_count
    french_ratio = min(french_indicators / max(len(text.split()), 1), 1.0)
    
    # Also check for basic Latin characters (French uses Latin alphabet)
    latin_chars = sum(1 for c in clean_text if c.isalpha() and ord(c) < 256)
    latin_ratio = latin_chars / total_chars if total_chars > 0 else 0
    
    return (french_ratio >= 0.1 or accent_count >= 2) and latin_ratio >= min_french_ratio


def has_french_educational_keywords(text: str) -> bool:
    """
    Check if text contains French educational keywords that indicate learning content
    
    Args:
        text: Text to analyze
        
    Returns:
        True if text contains French educational keywords
    """
    educational_keywords = [
        # Learning and education
        'apprendre', 'étudier', 'éducation', 'école', 'leçon', 'élève', 'étudiant',
        'professeur', 'enseignant', 'maître', 'instituteur', 'cours', 'classe',
        
        # Subjects
        'mathématiques', 'maths', 'sciences', 'physique', 'chimie', 'biologie',
        'histoire', 'géographie', 'littérature', 'grammaire', 'vocabulaire',
        'français', 'anglais', 'allemand', 'espagnol', 'informatique',
        
        # Academic terms
        'problème', 'solution', 'réponse', 'question', 'examen', 'test',
        'devoir', 'exercice', 'chapitre', 'unité', 'livre', 'manuel',
        'équation', 'formule', 'théorème', 'définition', 'exemple',
        
        # Visual elements
        'diagramme', 'graphique', 'tableau', 'figure', 'schéma',
        'illustration', 'carte', 'plan'
    ]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in educational_keywords)


def detect_watermarks_french(image_path: str, ocr_text: str) -> Tuple[bool, str]:
    """
    Detect watermarks in images using OCR text and filename analysis (French-specific)
    
    Args:
        image_path: Path to the image
        ocr_text: OCR extracted text
        
    Returns:
        Tuple of (has_watermark, watermark_source)
    """
    # Getty Images and international watermarks
    getty_indicators = [
        'getty', 'gettyimages', 'getty images', 'watermark', 'filigrane'
    ]
    
    # Stock photo watermarks
    stock_indicators = [
        'shutterstock', 'istockphoto', 'adobe stock', 'depositphotos',
        'dreamstime', 'bigstock', 'alamy', 'corbis', 'fotolia', 'pixabay'
    ]
    
    # French-specific watermark terms
    french_watermarks = [
        'filigrane', 'droits réservés', 'tous droits réservés',
        'échantillon', 'aperçu', 'exemple', 'démonstration',
        'propriété de', 'copyright', 'marque déposée'
    ]
    
    filename = os.path.basename(image_path).lower()
    text_lower = ocr_text.lower() if ocr_text else ""
    
    # Getty Images detection
    if any(indicator in text_lower for indicator in getty_indicators):
        return True, "Getty Images"
    
    if any(indicator in filename for indicator in getty_indicators):
        return True, "Getty Images"
    
    # Stock photo detection
    for indicator in stock_indicators:
        if indicator in text_lower or indicator in filename:
            return True, f"Stock Photo ({indicator.title()})"
    
    # French watermark detection
    for indicator in french_watermarks:
        if indicator in text_lower:
            return True, f"French Watermark ({indicator})"
    
    # Copyright patterns (French and international)
    watermark_patterns = [
        r'©\s*\d{4}',  # Copyright with year
        r'copyright\s+\d{4}',
        r'tous\s+droits\s+réservés',
        r'droits?\s+réservés?',
        r'propriété\s+de',
        r'filigrane',
        r'échantillon',
        r'aperçu',
        r'preview',
        r'sample'
    ]
    
    for pattern in watermark_patterns:
        if re.search(pattern, text_lower):
            return True, "Copyright/Watermark"
    
    return False, ""


def is_high_quality_french_educational_image(image_path: str, ocr_text: str) -> Dict:
    """
    Comprehensive quality check for French educational images
    
    Args:
        image_path: Path to the image
        ocr_text: OCR extracted text
        
    Returns:
        Dictionary with quality assessment results
    """
    assessment = {
        'is_quality': True,
        'reasons': [],
        'french_text': False,
        'educational_content': False,
        'has_watermark': False,
        'watermark_source': '',
        'text_length': len(ocr_text) if ocr_text else 0
    }
    
    # Check if predominantly French text
    assessment['french_text'] = is_french_text(ocr_text)
    if not assessment['french_text']:
        assessment['is_quality'] = False
        assessment['reasons'].append("Not predominantly French text")
    
    # Check for educational content
    assessment['educational_content'] = has_french_educational_keywords(ocr_text)
    if not assessment['educational_content']:
        assessment['reasons'].append("No French educational keywords detected")
    
    # Check for watermarks
    has_watermark, watermark_source = detect_watermarks_french(image_path, ocr_text)
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
    Enhanced OCR-filter for French educational images with watermark detection.
    Only high-quality images with French educational text and no watermarks are saved.
    """
    os.makedirs(save_dir, exist_ok=True)

    # Initialize French EasyOCR reader
    try:
        reader = easyocr.Reader(['fr'], gpu=False)  # Use CPU for better compatibility
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
        'french_text': 0,
        'educational_content': 0,
        'watermark_rejected': 0,
        'final_accepted': 0
    }

    print("🔍 Starting enhanced French OCR processing...")
    print("✅ Filtering for: French text + Educational content + No watermarks")

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
            quality_check = is_high_quality_french_educational_image(img_path, ocr_text)
            
            # Update statistics
            if quality_check['french_text']:
                stats['french_text'] += 1
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
            print(f"✅ Accepted: {fname} (French: ✓, Educational: {'✓' if quality_check['educational_content'] else '✗'}, No watermark: ✓)")

    # Write enhanced metadata
    out_file = os.path.join(save_dir, 'ocr_metadata_french.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': metadata,
            'statistics': stats,
            'processing_summary': {
                'total_images_processed': stats['total_processed'],
                'images_with_text': stats['ocr_successful'],
                'french_text_images': stats['french_text'],
                'educational_content_images': stats['educational_content'],
                'watermarked_rejected': stats['watermark_rejected'],
                'final_high_quality_images': stats['final_accepted'],
                'quality_rate': f"{(stats['final_accepted']/max(stats['total_processed'], 1))*100:.1f}%"
            }
        }, f, ensure_ascii=False, indent=2)

    # Print comprehensive summary
    print("\n🎯 ENHANCED FRENCH OCR PROCESSING COMPLETE!")
    print("=" * 60)
    print(f"📊 Total images processed: {stats['total_processed']}")
    print(f"🔍 OCR successful: {stats['ocr_successful']}")
    print(f"🇫🇷 French text detected: {stats['french_text']}")
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
        description="Filter and OCR French educational images using EasyOCR with comprehensive quality filtering."
    )
    parser.add_argument(
        "--source_dir", required=True,
        help="Directory containing raw scraped images"
    )
    parser.add_argument(
        "--save_dir", required=True,
        help="Directory to store OCR-filtered images and metadata"
    )
    args = parser.parse_args()

    process_images(args.source_dir, args.save_dir)


if __name__ == "__main__":
    main()