#!/usr/bin/env python3
"""
Enhanced EasyOCR for Japanese Text Detection with Educational Content Filtering

This script provides comprehensive Japanese text detection and filtering capabilities:
- Japanese language validation (Hiragana, Katakana, Kanji)
- Educational keyword detection
- Watermark detection
- Quality assessment
- Statistical reporting
"""

import os
import argparse
import json
import shutil
import re
import logging
from datetime import datetime
from collections import Counter
from PIL import Image
from tqdm import tqdm
import easyocr

def is_japanese_text(text, min_ratio=0.6):
    """
    Validate if text contains sufficient Japanese characters.
    
    Args:
        text (str): Text to validate
        min_ratio (float): Minimum ratio of Japanese characters (default: 0.6)
        
    Returns:
        dict: Validation results with ratio and character counts
    """
    if not text or not text.strip():
        return {'is_japanese': False, 'ratio': 0.0, 'details': {}}
    
    # Clean text for analysis
    clean_text = re.sub(r'\s+', '', text)
    total_chars = len(clean_text)
    
    if total_chars == 0:
        return {'is_japanese': False, 'ratio': 0.0, 'details': {}}
    
    # Count Japanese character types
    hiragana_count = len(re.findall(r'[\u3040-\u309F]', clean_text))
    katakana_count = len(re.findall(r'[\u30A0-\u30FF]', clean_text))
    kanji_count = len(re.findall(r'[\u4e00-\u9fff]', clean_text))
    japanese_punct_count = len(re.findall(r'[\u3002\u3001\uff1f\uff01]', clean_text))
    
    # Total Japanese characters
    japanese_chars = hiragana_count + katakana_count + kanji_count + japanese_punct_count
    japanese_ratio = japanese_chars / total_chars
    
    details = {
        'total_chars': total_chars,
        'japanese_chars': japanese_chars,
        'hiragana': hiragana_count,
        'katakana': katakana_count,
        'kanji': kanji_count,
        'japanese_punctuation': japanese_punct_count
    }
    
    return {
        'is_japanese': japanese_ratio >= min_ratio,
        'ratio': japanese_ratio,
        'details': details
    }

def has_japanese_educational_keywords(text):
    """
    Check for Japanese educational keywords in the text.
    
    Args:
        text (str): Text to analyze
        
    Returns:
        dict: Educational keyword analysis results
    """
    if not text:
        return {'has_educational_content': False, 'keywords_found': [], 'categories': {}}
    
    # Educational keyword categories
    educational_keywords = {
        'learning': ['学習', '勉強', '教育', '学校', '授業', '学生', '先生', '生徒'],
        'subjects': ['数学', '科学', '物理', '化学', '生物', '歴史', '地理', '国語', '文学'],
        'academic': ['問題', '解答', '答え', '質問', '試験', 'テスト', '宿題', '課題']
    }
    
    found_keywords = []
    category_counts = {}
    
    for category, keywords in educational_keywords.items():
        category_matches = []
        for keyword in keywords:
            if keyword in text:
                found_keywords.append(keyword)
                category_matches.append(keyword)
        category_counts[category] = len(category_matches)
    
    total_educational_keywords = len(found_keywords)
    
    return {
        'has_educational_content': total_educational_keywords > 0,
        'keywords_found': found_keywords,
        'keyword_count': total_educational_keywords,
        'categories': category_counts
    }

def detect_watermarks_japanese(text):
    """
    Detect Japanese watermarks and unwanted text.
    
    Args:
        text (str): Text to analyze
        
    Returns:
        dict: Watermark detection results
    """
    if not text:
        return {'has_watermarks': False, 'watermarks_found': [], 'confidence': 0.0}
    
    # Japanese watermark terms
    watermark_terms = [
        '透かし',      # watermark
        '著作権',      # copyright
        'サンプル',     # sample
        'プレビュー',   # preview
        '見本',        # sample/specimen
        'コピーライト', # copyright
        '無断転載禁止', # unauthorized reproduction prohibited
        'Getty Images',
        'Shutterstock',
        'Adobe Stock',
        'iStock'
    ]
    
    found_watermarks = []
    for term in watermark_terms:
        if term.lower() in text.lower():
            found_watermarks.append(term)
    
    # Calculate confidence based on number of watermark terms found
    confidence = min(len(found_watermarks) * 0.3, 1.0)
    
    return {
        'has_watermarks': len(found_watermarks) > 0,
        'watermarks_found': found_watermarks,
        'confidence': confidence
    }

def assess_text_quality_japanese(text):
    """
    Assess the quality of Japanese text for educational purposes.
    
    Args:
        text (str): Text to assess
        
    Returns:
        dict: Quality assessment results
    """
    if not text:
        return {'quality_score': 0.0, 'issues': ['No text detected']}
    
    issues = []
    quality_factors = []
    
    # Check text length
    if len(text.strip()) < 10:
        issues.append('Text too short')
        quality_factors.append(0.3)
    elif len(text.strip()) > 1000:
        issues.append('Text very long')
        quality_factors.append(0.7)
    else:
        quality_factors.append(1.0)
    
    # Check for balanced character usage
    japanese_analysis = is_japanese_text(text)
    if japanese_analysis['is_japanese']:
        details = japanese_analysis['details']
        
        # Prefer text with mix of character types
        char_type_count = sum(1 for count in [details['hiragana'], details['katakana'], details['kanji']] if count > 0)
        if char_type_count >= 2:
            quality_factors.append(1.0)
        elif char_type_count == 1:
            quality_factors.append(0.7)
        else:
            quality_factors.append(0.3)
            issues.append('Limited character type diversity')
    else:
        quality_factors.append(0.2)
        issues.append('Insufficient Japanese content')
    
    # Check for excessive repetition
    words = text.split()
    if len(words) > 5:
        word_freq = Counter(words)
        most_common_freq = word_freq.most_common(1)[0][1] if word_freq else 0
        repetition_ratio = most_common_freq / len(words)
        
        if repetition_ratio > 0.5:
            issues.append('High word repetition')
            quality_factors.append(0.4)
        elif repetition_ratio > 0.3:
            quality_factors.append(0.7)
        else:
            quality_factors.append(1.0)
    else:
        quality_factors.append(0.8)  # Short text penalty
    
    # Calculate overall quality score
    quality_score = sum(quality_factors) / len(quality_factors) if quality_factors else 0.0
    
    return {
        'quality_score': round(quality_score, 2),
        'issues': issues,
        'text_length': len(text.strip()),
        'word_count': len(text.split())
    }

def should_keep_image_japanese(text, min_japanese_ratio=0.6, min_quality_score=0.5):
    """
    Determine if an image should be kept based on Japanese text analysis.
    
    Args:
        text (str): Extracted text from image
        min_japanese_ratio (float): Minimum Japanese character ratio
        min_quality_score (float): Minimum quality score
        
    Returns:
        dict: Decision results with detailed analysis
    """
    # Perform all analyses
    japanese_analysis = is_japanese_text(text, min_japanese_ratio)
    educational_analysis = has_japanese_educational_keywords(text)
    watermark_analysis = detect_watermarks_japanese(text)
    quality_analysis = assess_text_quality_japanese(text)
    
    # Decision logic
    keep_reasons = []
    reject_reasons = []
    
    # Japanese content check
    if japanese_analysis['is_japanese']:
        keep_reasons.append(f"Japanese content: {japanese_analysis['ratio']:.1%}")
    else:
        reject_reasons.append(f"Insufficient Japanese content: {japanese_analysis['ratio']:.1%}")
    
    # Educational content boost
    if educational_analysis['has_educational_content']:
        keep_reasons.append(f"Educational keywords: {educational_analysis['keyword_count']}")
    
    # Watermark penalty
    if watermark_analysis['has_watermarks']:
        if watermark_analysis['confidence'] > 0.5:
            reject_reasons.append(f"Watermarks detected: {', '.join(watermark_analysis['watermarks_found'])}")
        else:
            keep_reasons.append("Minor watermark concerns")
    
    # Quality check
    if quality_analysis['quality_score'] >= min_quality_score:
        keep_reasons.append(f"Good quality: {quality_analysis['quality_score']}")
    else:
        reject_reasons.append(f"Low quality: {quality_analysis['quality_score']} (issues: {', '.join(quality_analysis['issues'])})")
    
    # Final decision
    should_keep = (
        japanese_analysis['is_japanese'] and
        quality_analysis['quality_score'] >= min_quality_score and
        not (watermark_analysis['has_watermarks'] and watermark_analysis['confidence'] > 0.5)
    )
    
    # Educational content can override some quality issues
    if educational_analysis['has_educational_content'] and educational_analysis['keyword_count'] >= 2:
        if japanese_analysis['is_japanese'] and quality_analysis['quality_score'] >= 0.3:
            should_keep = True
            keep_reasons.append("Educational content override")
    
    return {
        'should_keep': should_keep,
        'keep_reasons': keep_reasons,
        'reject_reasons': reject_reasons,
        'japanese_analysis': japanese_analysis,
        'educational_analysis': educational_analysis,
        'watermark_analysis': watermark_analysis,
        'quality_analysis': quality_analysis
    }

def check_image_integrity(image_path):
    try:
        img = Image.open(image_path)
        img.verify()
        return True
    except (IOError, SyntaxError) as e:
        print(f"⚠️ Corrupted image: {image_path} - {e}")
        return False

def process_images(source_dir, save_dir):
    """
    Enhanced OCR-filter for Japanese educational images with watermark detection.
    Only high-quality images with Japanese educational text and no watermarks are saved.
    """
    annotation_path = os.path.join(save_dir, "annotations.json")
    filter_japanese_images(source_dir, save_dir, annotation_path)


def filter_japanese_images(input_dir, output_dir, annotation_path, 
                          min_japanese_ratio=0.6, min_quality_score=0.5, 
                          log_level='INFO', save_rejected=False):
    """
    Enhanced Japanese image filtering with comprehensive text analysis.
    
    Args:
        input_dir (str): Directory containing input images
        output_dir (str): Directory to save filtered images
        annotation_path (str): Path to save annotations JSON
        min_japanese_ratio (float): Minimum Japanese character ratio
        min_quality_score (float): Minimum quality score
        log_level (str): Logging level
        save_rejected (bool): Save rejected images for analysis
    """
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Create directories
    os.makedirs(output_dir, exist_ok=True)
    if save_rejected:
        rejected_dir = os.path.join(os.path.dirname(output_dir), 'rejected_japanese')
        os.makedirs(rejected_dir, exist_ok=True)
    
    # Initialize OCR reader
    logger.info("Initializing Japanese EasyOCR reader...")
    reader = easyocr.Reader(['ja'], verbose=False)
    
    # Get image files
    files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff'))]
    logger.info(f"Found {len(files)} images to process")
    
    # Processing statistics
    stats = {
        'total_processed': 0,
        'kept_images': 0,
        'rejected_images': 0,
        'corrupted_images': 0,
        'error_images': 0,
        'educational_content': 0,
        'watermarked_images': 0,
        'japanese_character_stats': Counter(),
        'rejection_reasons': Counter(),
        'quality_scores': []
    }
    
    annotations = []
    rejected_annotations = []
    
    # Process images
    for fname in tqdm(files, desc="🔍 Processing Japanese Images"):
        src_path = os.path.join(input_dir, fname)
        stats['total_processed'] += 1
        
        # Check image integrity
        if not check_image_integrity(src_path):
            logger.warning(f"Corrupted image: {fname}")
            stats['corrupted_images'] += 1
            continue
        
        try:
            # Perform OCR
            img = Image.open(src_path)
            result = reader.readtext(img)
            
            # Extract and combine text
            detected_texts = []
            for detection in result:
                text = detection[1]
                confidence = detection[2]
                if confidence > 0.3:  # Filter low-confidence detections
                    detected_texts.append(text)
            
            combined_text = " ".join(detected_texts)
            
            # Analyze text
            analysis = should_keep_image_japanese(
                combined_text, 
                min_japanese_ratio=min_japanese_ratio,
                min_quality_score=min_quality_score
            )
            
            # Update statistics
            if analysis['japanese_analysis']['is_japanese']:
                details = analysis['japanese_analysis']['details']
                stats['japanese_character_stats']['hiragana'] += details['hiragana']
                stats['japanese_character_stats']['katakana'] += details['katakana']
                stats['japanese_character_stats']['kanji'] += details['kanji']
            
            if analysis['educational_analysis']['has_educational_content']:
                stats['educational_content'] += 1
            
            if analysis['watermark_analysis']['has_watermarks']:
                stats['watermarked_images'] += 1
            
            stats['quality_scores'].append(analysis['quality_analysis']['quality_score'])
            
            # Create annotation entry
            annotation_entry = {
                'filename': fname,
                'text': combined_text,
                'japanese_ratio': analysis['japanese_analysis']['ratio'],
                'quality_score': analysis['quality_analysis']['quality_score'],
                'educational_keywords': analysis['educational_analysis']['keywords_found'],
                'watermarks': analysis['watermark_analysis']['watermarks_found'],
                'character_counts': analysis['japanese_analysis']['details'],
                'decision': 'kept' if analysis['should_keep'] else 'rejected',
                'reasons': analysis['keep_reasons'] if analysis['should_keep'] else analysis['reject_reasons']
            }
            
            # Decide whether to keep the image
            if analysis['should_keep']:
                dst_path = os.path.join(output_dir, fname)
                shutil.copy(src_path, dst_path)
                annotations.append(annotation_entry)
                stats['kept_images'] += 1
                
                logger.debug(f"Kept {fname}: {', '.join(analysis['keep_reasons'])}")
            else:
                stats['rejected_images'] += 1
                for reason in analysis['reject_reasons']:
                    stats['rejection_reasons'][reason] += 1
                
                if save_rejected:
                    rejected_path = os.path.join(rejected_dir, fname)
                    shutil.copy(src_path, rejected_path)
                    rejected_annotations.append(annotation_entry)
                
                logger.debug(f"Rejected {fname}: {', '.join(analysis['reject_reasons'])}")
        
        except Exception as e:
            logger.error(f"Error processing {fname}: {str(e)}")
            stats['error_images'] += 1
            continue
    
    # Save annotations
    with open(annotation_path, "w", encoding="utf-8") as f:
        json.dump(annotations, f, ensure_ascii=False, indent=2)
    
    # Save rejected annotations if requested
    if save_rejected and rejected_annotations:
        rejected_annotation_path = annotation_path.replace('.json', '_rejected.json')
        with open(rejected_annotation_path, "w", encoding="utf-8") as f:
            json.dump(rejected_annotations, f, ensure_ascii=False, indent=2)
    
    # Generate and save statistics report
    generate_statistics_report(stats, output_dir, logger)
    
    # Print summary
    print(f"\n✅ Japanese OCR filtering completed!")
    print(f"📊 Results: {stats['kept_images']} kept / {stats['total_processed']} total")
    print(f"📄 Annotations saved to: {annotation_path}")
    
    return stats

def generate_statistics_report(stats, output_dir, logger):
    """
    Generate a comprehensive statistics report.
    
    Args:
        stats (dict): Processing statistics
        output_dir (str): Output directory for report
        logger: Logger instance
    """
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_processed': stats['total_processed'],
            'kept_images': stats['kept_images'],
            'rejected_images': stats['rejected_images'],
            'corrupted_images': stats['corrupted_images'],
            'error_images': stats['error_images'],
            'success_rate': round(stats['kept_images'] / max(stats['total_processed'], 1) * 100, 2)
        },
        'content_analysis': {
            'educational_content_images': stats['educational_content'],
            'watermarked_images': stats['watermarked_images'],
            'average_quality_score': round(sum(stats['quality_scores']) / max(len(stats['quality_scores']), 1), 2) if stats['quality_scores'] else 0
        },
        'japanese_characters': dict(stats['japanese_character_stats']),
        'rejection_reasons': dict(stats['rejection_reasons'])
    }
    
    # Save report
    report_path = os.path.join(output_dir, 'japanese_ocr_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Statistics report saved to: {report_path}")
    
    # Log key statistics
    logger.info(f"Processing Summary:")
    logger.info(f"  - Total processed: {stats['total_processed']}")
    logger.info(f"  - Images kept: {stats['kept_images']}")
    logger.info(f"  - Images rejected: {stats['rejected_images']}")
    logger.info(f"  - Success rate: {report['summary']['success_rate']}%")
    logger.info(f"  - Educational content: {stats['educational_content']} images")
    logger.info(f"  - Watermarked: {stats['watermarked_images']} images")

def main():
    parser = argparse.ArgumentParser(
        description="Enhanced Japanese OCR Text Detection and Educational Content Filtering",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python filter_images_japanese_ocr.py --input_dir /path/to/images --output_dir /path/to/filtered --annotation_path annotations.json
  python filter_images_japanese_ocr.py --input_dir /path/to/images --output_dir /path/to/filtered --annotation_path annotations.json --min_japanese_ratio 0.7 --save_rejected
        """
    )
    
    # Required arguments
    parser.add_argument("--input_dir", required=True, 
                       help="Directory containing images to filter")
    parser.add_argument("--output_dir", required=True, 
                       help="Directory to save filtered images")
    parser.add_argument("--annotation_path", required=True, 
                       help="Path to save annotations JSON file")
    
    # Optional arguments
    parser.add_argument("--min_japanese_ratio", type=float, default=0.6,
                       help="Minimum ratio of Japanese characters (default: 0.6)")
    parser.add_argument("--min_quality_score", type=float, default=0.5,
                       help="Minimum quality score threshold (default: 0.5)")
    parser.add_argument("--log_level", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help="Logging level (default: INFO)")
    parser.add_argument("--save_rejected", action='store_true',
                       help="Save rejected images for analysis")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not os.path.exists(args.input_dir):
        print(f"Error: Input directory '{args.input_dir}' does not exist.")
        return 1
    
    if not (0.0 <= args.min_japanese_ratio <= 1.0):
        print(f"Error: min_japanese_ratio must be between 0.0 and 1.0")
        return 1
    
    if not (0.0 <= args.min_quality_score <= 1.0):
        print(f"Error: min_quality_score must be between 0.0 and 1.0")
        return 1
    
    # Run filtering
    try:
        stats = filter_japanese_images(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            annotation_path=args.annotation_path,
            min_japanese_ratio=args.min_japanese_ratio,
            min_quality_score=args.min_quality_score,
            log_level=args.log_level,
            save_rejected=args.save_rejected
        )
        
        print(f"\n🌸 Japanese OCR filtering completed successfully!")
        print(f"📈 Final Statistics:")
        print(f"   - Success rate: {stats['kept_images']}/{stats['total_processed']} ({stats['kept_images']/max(stats['total_processed'],1)*100:.1f}%)")
        print(f"   - Educational content: {stats['educational_content']} images")
        print(f"   - Average quality: {sum(stats['quality_scores'])/max(len(stats['quality_scores']),1):.2f}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️ Processing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error during processing: {str(e)}")
        return 1

if __name__ == "__main__":
    main()