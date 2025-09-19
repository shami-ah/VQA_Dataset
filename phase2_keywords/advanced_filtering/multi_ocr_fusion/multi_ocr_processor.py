#!/usr/bin/env python3
"""
Multi-OCR Fusion System
Combines EasyOCR and Tesseract to ensure both engines detect meaningful text
"""

import cv2
import numpy as np
import easyocr
import pytesseract
from PIL import Image
import re
import logging
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path

class MultiOCRProcessor:
    def __init__(self, supported_languages: List[str] = None):
        """
        Initialize Multi-OCR processor with supported languages
        
        Args:
            supported_languages: List of language codes supported
        """
        self.supported_languages = supported_languages or [
            'en', 'ar', 'zh', 'hi', 'bn', 'fr', 'de', 'ja', 'ko', 'ms', 'pt', 'es', 'ur'
        ]
        
        # Language mapping for EasyOCR
        self.easyocr_lang_map = {
            'en': 'en', 'ar': 'ar', 'zh': 'ch_sim', 'hi': 'hi', 
            'bn': 'bn', 'fr': 'fr', 'de': 'de', 'ja': 'ja', 
            'ko': 'ko', 'ms': 'ms', 'pt': 'pt', 'es': 'es', 'ur': 'ur'
        }
        
        # Language mapping for Tesseract
        self.tesseract_lang_map = {
            'en': 'eng', 'ar': 'ara', 'zh': 'chi_sim', 'hi': 'hin',
            'bn': 'ben', 'fr': 'fra', 'de': 'deu', 'ja': 'jpn',
            'ko': 'kor', 'ms': 'msa', 'pt': 'por', 'es': 'spa', 'ur': 'urd'
        }
        
        self.easyocr_readers = {}
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """Setup logging for the processor"""
        logger = logging.getLogger('MultiOCRProcessor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _get_easyocr_reader(self, language: str):
        """Get or create EasyOCR reader for specific language"""
        if language not in self.easyocr_readers:
            easy_lang = self.easyocr_lang_map.get(language, 'en')
            try:
                self.easyocr_readers[language] = easyocr.Reader([easy_lang])
                self.logger.info(f"Initialized EasyOCR reader for {language}")
            except Exception as e:
                self.logger.error(f"Failed to initialize EasyOCR for {language}: {e}")
                return None
                
        return self.easyocr_readers[language]
    
    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for better OCR results"""
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            return thresh
            
        except Exception as e:
            self.logger.error(f"Image preprocessing failed for {image_path}: {e}")
            return None
    
    def _extract_text_easyocr(self, image_path: str, language: str) -> Optional[str]:
        """Extract text using EasyOCR"""
        try:
            reader = self._get_easyocr_reader(language)
            if reader is None:
                return None
                
            results = reader.readtext(image_path)
            
            # Extract text from results
            extracted_text = []
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # Filter low confidence results
                    extracted_text.append(text.strip())
            
            return ' '.join(extracted_text) if extracted_text else ""
            
        except Exception as e:
            self.logger.error(f"EasyOCR extraction failed for {image_path}: {e}")
            return None
    
    def _extract_text_tesseract(self, image_path: str, language: str) -> Optional[str]:
        """Extract text using Tesseract"""
        try:
            tesseract_lang = self.tesseract_lang_map.get(language, 'eng')
            
            # Preprocess image
            processed_image = self._preprocess_image(image_path)
            if processed_image is None:
                return None
            
            # Convert to PIL Image
            pil_image = Image.fromarray(processed_image)
            
            # Extract text with custom config
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
            
            if language in ['ar', 'ur']:
                # Arabic/Urdu specific config
                custom_config = r'--oem 3 --psm 6'
            elif language in ['zh', 'ja', 'ko']:
                # CJK specific config
                custom_config = r'--oem 3 --psm 6'
            
            text = pytesseract.image_to_string(
                pil_image, 
                lang=tesseract_lang,
                config=custom_config
            )
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"Tesseract extraction failed for {image_path}: {e}")
            return None
    
    def _is_meaningful_text(self, text: str, language: str) -> bool:
        """Check if extracted text is meaningful"""
        if not text or len(text.strip()) < 3:
            return False
        
        # Remove whitespace and special characters for length check
        clean_text = re.sub(r'[^\w]', '', text)
        if len(clean_text) < 2:
            return False
        
        # Language-specific checks
        if language == 'en':
            # Check for mostly alphabetic characters
            alpha_ratio = sum(c.isalpha() for c in text) / len(text)
            return alpha_ratio > 0.5
        
        elif language in ['ar', 'ur']:
            # Check for Arabic/Urdu script
            arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
            return arabic_chars > 0
        
        elif language == 'zh':
            # Check for Chinese characters
            chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
            return chinese_chars > 0
        
        elif language in ['hi', 'bn']:
            # Check for Devanagari/Bengali script
            devanagari_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
            bengali_chars = sum(1 for c in text if '\u0980' <= c <= '\u09FF')
            return (devanagari_chars + bengali_chars) > 0
        
        elif language in ['ja']:
            # Check for Japanese characters (Hiragana, Katakana, Kanji)
            hiragana = sum(1 for c in text if '\u3040' <= c <= '\u309F')
            katakana = sum(1 for c in text if '\u30A0' <= c <= '\u30FF')
            kanji = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
            return (hiragana + katakana + kanji) > 0
        
        elif language == 'ko':
            # Check for Korean characters
            korean_chars = sum(1 for c in text if '\uAC00' <= c <= '\uD7AF')
            return korean_chars > 0
        
        else:
            # For other languages, check for reasonable character distribution
            alpha_ratio = sum(c.isalpha() for c in text) / len(text)
            return alpha_ratio > 0.3
    
    def process_image(self, image_path: str, language: str) -> Dict:
        """
        Process image with both OCR engines and return fusion result
        
        Args:
            image_path: Path to the image file
            language: Target language code
            
        Returns:
            Dictionary with OCR results and fusion decision
        """
        result = {
            'image_path': image_path,
            'language': language,
            'easyocr_text': None,
            'tesseract_text': None,
            'fusion_decision': False,
            'confidence_score': 0.0,
            'error_message': None
        }
        
        try:
            # Extract text with both engines
            easy_text = self._extract_text_easyocr(image_path, language)
            tesseract_text = self._extract_text_tesseract(image_path, language)
            
            result['easyocr_text'] = easy_text
            result['tesseract_text'] = tesseract_text
            
            # Check if both engines found meaningful text
            easy_meaningful = self._is_meaningful_text(easy_text or "", language)
            tesseract_meaningful = self._is_meaningful_text(tesseract_text or "", language)
            
            # Fusion decision: Keep image only if both engines detect meaningful text
            result['fusion_decision'] = easy_meaningful and tesseract_meaningful
            
            # Calculate confidence score
            confidence = 0.0
            if easy_meaningful:
                confidence += 0.5
            if tesseract_meaningful:
                confidence += 0.5
                
            result['confidence_score'] = confidence
            
            self.logger.info(f"Processed {image_path}: EasyOCR={easy_meaningful}, Tesseract={tesseract_meaningful}, Decision={result['fusion_decision']}")
            
        except Exception as e:
            result['error_message'] = str(e)
            self.logger.error(f"Error processing {image_path}: {e}")
        
        return result
    
    def batch_process(self, image_paths: List[str], language: str, output_file: str = None) -> List[Dict]:
        """
        Process multiple images in batch
        
        Args:
            image_paths: List of image file paths
            language: Target language code
            output_file: Optional file to save results
            
        Returns:
            List of processing results
        """
        results = []
        
        self.logger.info(f"Starting batch processing of {len(image_paths)} images for language: {language}")
        
        for i, image_path in enumerate(image_paths):
            self.logger.info(f"Processing image {i+1}/{len(image_paths)}: {image_path}")
            result = self.process_image(image_path, language)
            results.append(result)
        
        # Save results if output file specified
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                self.logger.info(f"Results saved to {output_file}")
            except Exception as e:
                self.logger.error(f"Failed to save results: {e}")
        
        # Log summary
        passed_count = sum(1 for r in results if r['fusion_decision'])
        self.logger.info(f"Batch processing complete: {passed_count}/{len(results)} images passed fusion test")
        
        return results


def main():
    """Example usage"""
    processor = MultiOCRProcessor()
    
    # Example image paths (replace with actual paths)
    sample_images = [
        "/path/to/image1.jpg",
        "/path/to/image2.png"
    ]
    
    # Process single image
    result = processor.process_image(sample_images[0], 'en')
    print(f"Single image result: {result}")
    
    # Batch processing
    batch_results = processor.batch_process(sample_images, 'en', 'fusion_results.json')
    print(f"Batch processing completed: {len(batch_results)} images processed")


if __name__ == "__main__":
    main()