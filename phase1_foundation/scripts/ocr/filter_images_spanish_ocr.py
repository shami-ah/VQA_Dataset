#!/usr/bin/env python3
import os
import argparse
import json
import shutil
import hashlib
import easyocr
import re
import logging
from typing import List, Dict, Set, Tuple, Optional
from collections import Counter
from pathlib import Path

from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('spanish_ocr_filter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Spanish language constants
SPANISH_COMMON_WORDS = {
    'el', 'la', 'los', 'las', 'de', 'en', 'con', 'por', 'para', 'es', 'son', 
    'está', 'están', 'un', 'una', 'unos', 'unas', 'y', 'o', 'pero', 'si', 'no',
    'que', 'se', 'le', 'me', 'te', 'nos', 'les', 'del', 'al', 'este', 'esta',
    'estos', 'estas', 'ese', 'esa', 'esos', 'esas', 'aquel', 'aquella',
    'aquellos', 'aquellas', 'todo', 'toda', 'todos', 'todas', 'su', 'sus',
    'mi', 'mis', 'tu', 'tus', 'nuestro', 'nuestra', 'nuestros', 'nuestras'
}

SPANISH_EDUCATIONAL_KEYWORDS = {
    # Learning and education
    'aprender', 'estudiar', 'educación', 'escuela', 'lección', 'estudiante', 
    'profesor', 'maestro', 'enseñar', 'aprendizaje', 'conocimiento', 'saber',
    'universidad', 'colegio', 'instituto', 'clase', 'curso', 'materia',
    'asignatura', 'disciplina', 'formación', 'capacitación', 'entrenamiento',
    
    # Subjects
    'matemáticas', 'ciencias', 'física', 'química', 'biología', 'historia', 
    'geografía', 'literatura', 'lengua', 'idioma', 'español', 'inglés',
    'francés', 'alemán', 'informática', 'computación', 'tecnología',
    'filosofía', 'psicología', 'sociología', 'economía', 'política',
    'arte', 'música', 'deportes', 'educación física', 'religión',
    
    # Academic terms
    'problema', 'solución', 'respuesta', 'pregunta', 'examen', 'prueba', 
    'tarea', 'ejercicio', 'actividad', 'práctica', 'teoría', 'método',
    'técnica', 'proceso', 'análisis', 'síntesis', 'evaluación', 'calificación',
    'nota', 'puntuación', 'resultado', 'conclusión', 'investigación',
    'estudio', 'ensayo', 'proyecto', 'trabajo', 'presentación',
    
    # Academic levels and degrees
    'primaria', 'secundaria', 'bachillerato', 'licenciatura', 'maestría',
    'doctorado', 'grado', 'título', 'diploma', 'certificado', 'acreditación',
    
    # Educational materials
    'libro', 'texto', 'manual', 'guía', 'cuaderno', 'apuntes', 'notas',
    'diccionario', 'enciclopedia', 'atlas', 'mapa', 'gráfico', 'diagrama',
    'tabla', 'fórmula', 'ecuación', 'definición', 'concepto', 'ejemplo'
}

SPANISH_WATERMARK_TERMS = {
    'marca de agua', 'derechos reservados', 'muestra', 'vista previa', 'ejemplo',
    'copyright', 'watermark', 'sample', 'demo', 'preview', 'stock photo',
    'getty images', 'shutterstock', 'istockphoto', 'adobe stock',
    'dreamstime', 'alamy', 'depositphotos', '123rf', 'bigstock',
    'fotolia', 'stockphoto', 'stockimage', 'royalty free', 'rf',
    'todos los derechos reservados', 'propiedad intelectual',
    'uso comercial', 'licencia', 'autorización', 'permitido',
    'prohibido', 'sin autorización', 'no autorizado'
}

SPANISH_NOISE_PATTERNS = {
    'social media': {'facebook', 'twitter', 'instagram', 'whatsapp', 'telegram',
                     'youtube', 'tiktok', 'snapchat', 'linkedin', 'pinterest'},
    'urls_domains': {'www.', 'http://', 'https://', '.com', '.es', '.org', '.net',
                     '.edu', '.gov', '.mx', '.ar', '.co', '.pe', '.cl', '.ve'},
    'technical': {'html', 'css', 'javascript', 'php', 'mysql', 'api', 'url',
                  'json', 'xml', 'csv', 'pdf', 'doc', 'docx', 'xls', 'xlsx'},
    'spam_indicators': {'click aquí', 'haz clic', 'regístrate', 'suscríbete',
                        'compra ahora', 'oferta especial', 'descuento',
                        'gratis', 'regalo', 'promoción', 'ganador'}
}

# Spanish accented characters pattern
SPANISH_ACCENTS_PATTERN = re.compile(r'[áéíóúñü]', re.IGNORECASE)

# Minimum thresholds
MIN_SPANISH_RATIO = 0.70
MIN_TEXT_LENGTH = 10
MIN_WORD_COUNT = 3
MAX_WATERMARK_RATIO = 0.15
MIN_EDUCATIONAL_SCORE = 0.20


def is_spanish_text(text: str) -> Tuple[bool, float, Dict[str, any]]:
    """
    Determine if text is Spanish with detailed analysis.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Tuple of (is_spanish, confidence_score, analysis_details)
    """
    if not text or len(text.strip()) < MIN_TEXT_LENGTH:
        return False, 0.0, {'reason': 'text_too_short'}
    
    # Clean and tokenize text
    cleaned_text = re.sub(r'[^\w\sáéíóúñü]', ' ', text.lower())
    words = [w for w in cleaned_text.split() if len(w) > 1]
    
    if len(words) < MIN_WORD_COUNT:
        return False, 0.0, {'reason': 'insufficient_words', 'word_count': len(words)}
    
    # Count Spanish indicators
    spanish_words = sum(1 for word in words if word in SPANISH_COMMON_WORDS)
    accent_matches = len(SPANISH_ACCENTS_PATTERN.findall(text))
    
    # Calculate ratios
    spanish_word_ratio = spanish_words / len(words) if words else 0
    accent_ratio = accent_matches / len(text) if text else 0
    
    # Spanish confidence scoring
    confidence_factors = {
        'common_words': spanish_word_ratio * 0.6,
        'accents': min(accent_ratio * 20, 0.3),  # Cap accent contribution
        'length_bonus': min(len(words) / 50, 0.1)  # Longer texts get slight bonus
    }
    
    total_confidence = sum(confidence_factors.values())
    
    # Check for non-Spanish indicators
    penalties = 0
    if re.search(r'\b(the|and|or|but|with|for|in|on|at|by|from)\b', text.lower()):
        penalties += 0.2  # English words
    if re.search(r'\b(le|la|les|des|du|avec|pour|dans)\b', text.lower()):
        penalties += 0.2  # French words
    if re.search(r'\b(der|die|das|und|oder|aber|mit|für|in|an|von)\b', text.lower()):
        penalties += 0.2  # German words
    
    final_confidence = max(0, total_confidence - penalties)
    
    analysis = {
        'word_count': len(words),
        'spanish_words': spanish_words,
        'spanish_word_ratio': spanish_word_ratio,
        'accent_count': accent_matches,
        'accent_ratio': accent_ratio,
        'confidence_factors': confidence_factors,
        'penalties': penalties,
        'final_confidence': final_confidence
    }
    
    is_spanish = final_confidence >= MIN_SPANISH_RATIO
    return is_spanish, final_confidence, analysis


def has_spanish_educational_keywords(text: str) -> Tuple[bool, float, List[str]]:
    """
    Check for Spanish educational keywords in text.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Tuple of (has_keywords, educational_score, found_keywords)
    """
    if not text:
        return False, 0.0, []
    
    text_lower = text.lower()
    words = set(re.findall(r'\b\w+\b', text_lower))
    
    # Find educational keywords
    found_keywords = []
    for keyword in SPANISH_EDUCATIONAL_KEYWORDS:
        if keyword in text_lower:
            found_keywords.append(keyword)
    
    # Calculate educational score
    unique_keywords = len(set(found_keywords))
    total_keywords = len(found_keywords)
    word_count = len(words)
    
    if word_count == 0:
        educational_score = 0.0
    else:
        # Score based on keyword density and variety
        density_score = min(total_keywords / word_count, 0.3)  # Cap at 30%
        variety_score = min(unique_keywords / 10, 0.2)  # Cap at 20%
        educational_score = density_score + variety_score
    
    has_educational_content = educational_score >= MIN_EDUCATIONAL_SCORE
    
    return has_educational_content, educational_score, found_keywords


def detect_watermarks_spanish(text: str) -> Tuple[bool, float, List[str]]:
    """
    Detect Spanish watermarks and copyright indicators.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Tuple of (has_watermarks, watermark_ratio, found_watermarks)
    """
    if not text:
        return False, 0.0, []
    
    text_lower = text.lower()
    words = text_lower.split()
    
    # Find watermark terms
    found_watermarks = []
    for watermark_term in SPANISH_WATERMARK_TERMS:
        if watermark_term in text_lower:
            found_watermarks.append(watermark_term)
    
    # Calculate watermark ratio
    watermark_words = sum(len(term.split()) for term in found_watermarks)
    total_words = len(words)
    
    watermark_ratio = watermark_words / total_words if total_words > 0 else 0
    has_watermarks = watermark_ratio > MAX_WATERMARK_RATIO
    
    return has_watermarks, watermark_ratio, found_watermarks


def detect_noise_content(text: str) -> Tuple[bool, float, Dict[str, List[str]]]:
    """
    Detect noise content that might indicate non-educational images.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Tuple of (has_noise, noise_ratio, noise_details)
    """
    if not text:
        return False, 0.0, {}
    
    text_lower = text.lower()
    words = text_lower.split()
    
    noise_found = {category: [] for category in SPANISH_NOISE_PATTERNS}
    total_noise_words = 0
    
    for category, noise_terms in SPANISH_NOISE_PATTERNS.items():
        for term in noise_terms:
            if term in text_lower:
                noise_found[category].append(term)
                total_noise_words += len(term.split())
    
    noise_ratio = total_noise_words / len(words) if words else 0
    has_significant_noise = noise_ratio > 0.3  # More than 30% noise
    
    return has_significant_noise, noise_ratio, noise_found


def calculate_image_quality_score(img_path: str) -> Tuple[float, Dict[str, any]]:
    """
    Calculate image quality score based on dimensions and file size.
    
    Args:
        img_path: Path to image file
        
    Returns:
        Tuple of (quality_score, quality_metrics)
    """
    try:
        with Image.open(img_path) as img:
            width, height = img.size
            file_size = os.path.getsize(img_path)
            
            # Quality metrics
            total_pixels = width * height
            aspect_ratio = width / height if height > 0 else 0
            
            # Scoring factors
            resolution_score = min(total_pixels / (1920 * 1080), 1.0)  # Normalize to 1080p
            size_score = min(file_size / (500 * 1024), 1.0)  # Normalize to 500KB
            aspect_score = 1.0 if 0.5 <= aspect_ratio <= 2.0 else 0.5  # Reasonable aspect ratios
            
            quality_score = (resolution_score * 0.4 + size_score * 0.3 + aspect_score * 0.3)
            
            metrics = {
                'width': width,
                'height': height,
                'total_pixels': total_pixels,
                'file_size': file_size,
                'aspect_ratio': aspect_ratio,
                'resolution_score': resolution_score,
                'size_score': size_score,
                'aspect_score': aspect_score,
                'quality_score': quality_score
            }
            
            return quality_score, metrics
            
    except Exception as e:
        logger.warning(f"Failed to analyze image quality for {img_path}: {e}")
        return 0.0, {'error': str(e)}


def comprehensive_spanish_filter(text: str, img_path: str) -> Tuple[bool, Dict[str, any]]:
    """
    Comprehensive filtering for Spanish educational content.
    
    Args:
        text: OCR extracted text
        img_path: Path to image file
        
    Returns:
        Tuple of (should_keep, analysis_results)
    """
    analysis = {
        'text_length': len(text),
        'word_count': len(text.split()) if text else 0
    }
    
    # Spanish language analysis
    is_spanish, spanish_confidence, spanish_details = is_spanish_text(text)
    analysis['spanish_analysis'] = {
        'is_spanish': is_spanish,
        'confidence': spanish_confidence,
        'details': spanish_details
    }
    
    # Educational content analysis
    has_educational, edu_score, edu_keywords = has_spanish_educational_keywords(text)
    analysis['educational_analysis'] = {
        'has_educational_content': has_educational,
        'educational_score': edu_score,
        'found_keywords': edu_keywords
    }
    
    # Watermark detection
    has_watermarks, watermark_ratio, watermark_terms = detect_watermarks_spanish(text)
    analysis['watermark_analysis'] = {
        'has_watermarks': has_watermarks,
        'watermark_ratio': watermark_ratio,
        'found_watermarks': watermark_terms
    }
    
    # Noise detection
    has_noise, noise_ratio, noise_details = detect_noise_content(text)
    analysis['noise_analysis'] = {
        'has_significant_noise': has_noise,
        'noise_ratio': noise_ratio,
        'noise_details': noise_details
    }
    
    # Image quality
    quality_score, quality_metrics = calculate_image_quality_score(img_path)
    analysis['quality_analysis'] = {
        'quality_score': quality_score,
        'metrics': quality_metrics
    }
    
    # Decision logic
    keep_criteria = {
        'spanish_language': is_spanish,
        'sufficient_length': len(text.strip()) >= MIN_TEXT_LENGTH,
        'educational_content': has_educational or edu_score > 0.1,  # Lower threshold for potential
        'no_watermarks': not has_watermarks,
        'low_noise': not has_noise,
        'adequate_quality': quality_score > 0.3
    }
    
    analysis['keep_criteria'] = keep_criteria
    
    # Final decision
    critical_failures = [
        not keep_criteria['spanish_language'],
        not keep_criteria['sufficient_length'],
        keep_criteria['no_watermarks'] is False,  # Reject if watermarks
        keep_criteria['low_noise'] is False       # Reject if high noise
    ]
    
    should_keep = not any(critical_failures) and (
        keep_criteria['educational_content'] or
        (spanish_confidence > 0.8 and quality_score > 0.5)  # High quality Spanish text
    )
    
    analysis['should_keep'] = should_keep
    analysis['rejection_reasons'] = []
    
    if not should_keep:
        if not keep_criteria['spanish_language']:
            analysis['rejection_reasons'].append('not_spanish_language')
        if not keep_criteria['sufficient_length']:
            analysis['rejection_reasons'].append('insufficient_text_length')
        if not keep_criteria['no_watermarks']:
            analysis['rejection_reasons'].append('contains_watermarks')
        if not keep_criteria['low_noise']:
            analysis['rejection_reasons'].append('high_noise_content')
        if not keep_criteria['educational_content'] and not (spanish_confidence > 0.8 and quality_score > 0.5):
            analysis['rejection_reasons'].append('low_educational_value')
    
    return should_keep, analysis


def process_images(source_dir, save_dir):
    """
    Advanced OCR-filter for Spanish educational images with comprehensive analysis.
    
    Args:
        source_dir: Directory containing raw scraped images
        save_dir: Directory to store filtered images and metadata
    """
    logger.info(f"Starting Spanish OCR filtering: {source_dir} -> {save_dir}")
    
    # Ensure output directory exists
    os.makedirs(save_dir, exist_ok=True)
    
    # Create subdirectories for organization
    accepted_dir = os.path.join(save_dir, 'accepted')
    rejected_dir = os.path.join(save_dir, 'rejected')
    os.makedirs(accepted_dir, exist_ok=True)
    os.makedirs(rejected_dir, exist_ok=True)
    
    # Initialize Spanish EasyOCR reader
    try:
        reader = easyocr.Reader(['es'], gpu=True)
        logger.info("EasyOCR Spanish reader initialized with GPU support")
    except Exception as e:
        logger.warning(f"Failed to initialize GPU, falling back to CPU: {e}")
        reader = easyocr.Reader(['es'], gpu=False)
    
    # Processing counters and metadata
    seen_hashes = set()
    accepted_metadata = []
    rejected_metadata = []
    processing_stats = {
        'total_images': 0,
        'processed': 0,
        'accepted': 0,
        'rejected': 0,
        'duplicates': 0,
        'ocr_errors': 0,
        'rejection_reasons': Counter()
    }
    
    # Get all image files
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
    image_files = []
    
    for root, _, files in os.walk(source_dir):
        for fname in files:
            if any(fname.lower().endswith(ext) for ext in image_extensions):
                image_files.append(os.path.join(root, fname))
    
    processing_stats['total_images'] = len(image_files)
    logger.info(f"Found {len(image_files)} images to process")
    
    for i, img_path in enumerate(image_files, 1):
        logger.info(f"Processing image {i}/{len(image_files)}: {os.path.basename(img_path)}")
        
        # Perform OCR
        try:
            result = reader.readtext(img_path, detail=0, paragraph=True)
            ocr_text = " ".join(result).strip() if result else ""
        except Exception as e:
            logger.error(f"OCR error on {img_path}: {e}")
            processing_stats['ocr_errors'] += 1
            continue
        
        processing_stats['processed'] += 1
        
        # Skip empty OCR results
        if not ocr_text:
            logger.debug(f"No text detected in {img_path}")
            rejected_metadata.append({
                'image_path': img_path,
                'ocr_text': '',
                'rejection_reason': 'no_text_detected',
                'analysis': None
            })
            processing_stats['rejected'] += 1
            processing_stats['rejection_reasons']['no_text_detected'] += 1
            continue
        
        # Comprehensive Spanish filtering
        should_keep, analysis = comprehensive_spanish_filter(ocr_text, img_path)
        
        # Deduplicate by file content hash
        try:
            with open(img_path, 'rb') as f:
                data = f.read()
            file_hash = hashlib.sha256(data).hexdigest()  # Use SHA-256 for better security
        except Exception as e:
            logger.error(f"Hash calculation error on {img_path}: {e}")
            continue
        
        if file_hash in seen_hashes:
            logger.debug(f"Duplicate image detected: {img_path}")
            processing_stats['duplicates'] += 1
            continue
        
        seen_hashes.add(file_hash)
        
        # Determine destination based on filtering result
        rel_path = os.path.relpath(img_path, source_dir)
        
        if should_keep:
            dest_path = os.path.join(accepted_dir, rel_path)
            dest_dir = os.path.dirname(dest_path)
            os.makedirs(dest_dir, exist_ok=True)
            
            try:
                shutil.copy2(img_path, dest_path)
                logger.info(f"Accepted: {os.path.basename(img_path)}")
                
                # Record accepted metadata
                metadata_entry = {
                    'original_path': img_path,
                    'processed_path': dest_path,
                    'file_hash': file_hash,
                    'ocr_text': ocr_text,
                    'analysis': analysis,
                    'processing_timestamp': str(os.path.getctime(img_path))
                }
                accepted_metadata.append(metadata_entry)
                processing_stats['accepted'] += 1
                
            except Exception as e:
                logger.error(f"Failed to copy accepted image {img_path}: {e}")
                continue
        else:
            # Optionally copy rejected images for analysis
            dest_path = os.path.join(rejected_dir, rel_path)
            dest_dir = os.path.dirname(dest_path)
            os.makedirs(dest_dir, exist_ok=True)
            
            try:
                shutil.copy2(img_path, dest_path)
            except Exception as e:
                logger.warning(f"Failed to copy rejected image {img_path}: {e}")
            
            logger.debug(f"Rejected: {os.path.basename(img_path)} - {analysis.get('rejection_reasons', [])}")
            
            # Record rejected metadata
            metadata_entry = {
                'original_path': img_path,
                'processed_path': dest_path,
                'file_hash': file_hash,
                'ocr_text': ocr_text,
                'rejection_reasons': analysis.get('rejection_reasons', []),
                'analysis': analysis
            }
            rejected_metadata.append(metadata_entry)
            processing_stats['rejected'] += 1
            
            # Update rejection reason statistics
            for reason in analysis.get('rejection_reasons', []):
                processing_stats['rejection_reasons'][reason] += 1
    
    # Write comprehensive metadata
    accepted_meta_file = os.path.join(save_dir, 'accepted_spanish_metadata.json')
    rejected_meta_file = os.path.join(save_dir, 'rejected_spanish_metadata.json')
    stats_file = os.path.join(save_dir, 'processing_statistics.json')
    
    try:
        with open(accepted_meta_file, 'w', encoding='utf-8') as f:
            json.dump(accepted_metadata, f, ensure_ascii=False, indent=2, default=str)
        
        with open(rejected_meta_file, 'w', encoding='utf-8') as f:
            json.dump(rejected_metadata, f, ensure_ascii=False, indent=2, default=str)
        
        # Convert Counter to dict for JSON serialization
        stats_for_json = dict(processing_stats)
        stats_for_json['rejection_reasons'] = dict(stats_for_json['rejection_reasons'])
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_for_json, f, ensure_ascii=False, indent=2)
        
        logger.info("Metadata files written successfully")
        
    except Exception as e:
        logger.error(f"Failed to write metadata files: {e}")
    
    # Final summary
    acceptance_rate = (processing_stats['accepted'] / processing_stats['processed'] * 100) if processing_stats['processed'] > 0 else 0
    
    logger.info("=" * 60)
    logger.info("SPANISH OCR FILTERING COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total images found: {processing_stats['total_images']}")
    logger.info(f"Successfully processed: {processing_stats['processed']}")
    logger.info(f"Accepted images: {processing_stats['accepted']}")
    logger.info(f"Rejected images: {processing_stats['rejected']}")
    logger.info(f"Duplicates removed: {processing_stats['duplicates']}")
    logger.info(f"OCR errors: {processing_stats['ocr_errors']}")
    logger.info(f"Acceptance rate: {acceptance_rate:.1f}%")
    logger.info(f"")
    logger.info(f"Output directories:")
    logger.info(f"  Accepted: {accepted_dir}")
    logger.info(f"  Rejected: {rejected_dir}")
    logger.info(f"")
    logger.info(f"Metadata files:")
    logger.info(f"  Accepted: {accepted_meta_file}")
    logger.info(f"  Rejected: {rejected_meta_file}")
    logger.info(f"  Statistics: {stats_file}")
    
    if processing_stats['rejection_reasons']:
        logger.info(f"")
        logger.info(f"Top rejection reasons:")
        for reason, count in processing_stats['rejection_reasons'].most_common(5):
            logger.info(f"  {reason}: {count}")
    
    logger.info("=" * 60)
    
    print(f"\n✅ Spanish OCR filtering complete!")
    print(f"📊 Processed {processing_stats['processed']} images")
    print(f"✅ Accepted: {processing_stats['accepted']} ({acceptance_rate:.1f}%)")
    print(f"❌ Rejected: {processing_stats['rejected']}")
    print(f"🔄 Duplicates: {processing_stats['duplicates']}")
    print(f"📁 Results saved to: {save_dir}")


def main():
    parser = argparse.ArgumentParser(
        description='Advanced Spanish OCR filtering with comprehensive language and educational content analysis.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python filter_images_spanish_ocr.py --source_dir /path/to/images --save_dir /path/to/output
  python filter_images_spanish_ocr.py --source_dir ./raw_images --save_dir ./filtered --min_educational_score 0.3

Output Structure:
  save_dir/
  ├── accepted/           # Images that passed all filters
  ├── rejected/           # Images that failed filters (for analysis)
  ├── accepted_spanish_metadata.json
  ├── rejected_spanish_metadata.json
  └── processing_statistics.json

Filtering Criteria:
  - Spanish language detection (70% confidence minimum)
  - Educational content analysis
  - Watermark detection and filtering
  - Noise content filtering
  - Image quality assessment
  - Comprehensive deduplication
        """
    )
    
    parser.add_argument(
        '--source_dir', required=True,
        help='Directory containing raw scraped images to process'
    )
    
    parser.add_argument(
        '--save_dir', required=True,
        help='Directory to store filtered images and comprehensive metadata'
    )
    
    parser.add_argument(
        '--min_spanish_ratio', type=float, default=0.70,
        help='Minimum Spanish language confidence ratio (default: 0.70)'
    )
    
    parser.add_argument(
        '--min_educational_score', type=float, default=0.20,
        help='Minimum educational content score (default: 0.20)'
    )
    
    parser.add_argument(
        '--max_watermark_ratio', type=float, default=0.15,
        help='Maximum allowed watermark ratio (default: 0.15)'
    )
    
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Enable verbose logging output'
    )
    
    parser.add_argument(
        '--log_file', default='spanish_ocr_filter.log',
        help='Log file path (default: spanish_ocr_filter.log)'
    )
    
    args = parser.parse_args()
    
    # Update global thresholds if provided
    global MIN_SPANISH_RATIO, MIN_EDUCATIONAL_SCORE, MAX_WATERMARK_RATIO
    if args.min_spanish_ratio != MIN_SPANISH_RATIO:
        MIN_SPANISH_RATIO = args.min_spanish_ratio
    if args.min_educational_score != MIN_EDUCATIONAL_SCORE:
        MIN_EDUCATIONAL_SCORE = args.min_educational_score
    if args.max_watermark_ratio != MAX_WATERMARK_RATIO:
        MAX_WATERMARK_RATIO = args.max_watermark_ratio
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("Verbose logging enabled")
    
    # Validate input arguments
    if not os.path.exists(args.source_dir):
        logger.error(f"Source directory does not exist: {args.source_dir}")
        return 1
    
    if not os.path.isdir(args.source_dir):
        logger.error(f"Source path is not a directory: {args.source_dir}")
        return 1
    
    # Log configuration
    logger.info("Spanish OCR Filter Configuration:")
    logger.info(f"  Source directory: {args.source_dir}")
    logger.info(f"  Output directory: {args.save_dir}")
    logger.info(f"  Minimum Spanish ratio: {MIN_SPANISH_RATIO}")
    logger.info(f"  Minimum educational score: {MIN_EDUCATIONAL_SCORE}")
    logger.info(f"  Maximum watermark ratio: {MAX_WATERMARK_RATIO}")
    logger.info(f"  Log file: {args.log_file}")
    
    try:
        process_images(args.source_dir, args.save_dir)
        return 0
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Processing failed with error: {e}")
        logger.exception("Full traceback:")
        return 1


if __name__ == '__main__':
    main()
