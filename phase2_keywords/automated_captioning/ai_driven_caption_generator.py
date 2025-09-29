#!/usr/bin/env python3
"""
AI-Driven Caption Generator - Professional, OCR-based approach
No subject templates, pure content analysis
"""

import logging
import re
from typing import Dict
from PIL import Image

class AIDriverCaptionGenerator:
    def __init__(self, language: str = 'english'):
        self.language = language
        self.logger = self._setup_logger()
        self.logger.info(f"📝 AI-Driven Caption Generator initialized for {language}")
    
    def _setup_logger(self):
        """Setup logging"""
        logger = logging.getLogger('AIDriverCaption')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def generate_caption(self, image_path: str, ocr_text: str = None, **kwargs) -> Dict:
        """Generate caption based purely on image characteristics and OCR content"""
        try:
            # Get image dimensions and format
            image_info = self._get_image_info(image_path)
            
            # Analyze OCR content if available
            content_analysis = self._analyze_ocr_content(ocr_text) if ocr_text else {}
            
            # Generate clean, professional caption
            caption = self._create_content_aware_caption(image_info, content_analysis, ocr_text)
            
            return {
                'caption': caption,
                'image_info': image_info,
                'content_confidence': content_analysis.get('confidence', 0.5)
            }
            
        except Exception as e:
            self.logger.warning(f"Caption generation failed: {e}")
            return {
                'caption': "Educational material",
                'image_info': {'size': 'unknown', 'aspect': 'unknown'},
                'content_confidence': 0.3
            }
    
    def _get_image_info(self, image_path: str) -> Dict:
        """Get basic image information"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                aspect_ratio = width / height
                
                # Determine size category
                total_pixels = width * height
                if total_pixels > 800000:  # > 800K pixels
                    size_desc = "large"
                elif total_pixels > 200000:  # > 200K pixels
                    size_desc = "medium"
                else:
                    size_desc = "small"
                
                # Determine aspect ratio description
                if aspect_ratio > 1.3:
                    aspect_desc = "wide landscape"
                elif aspect_ratio < 0.8:
                    aspect_desc = "tall portrait"
                else:
                    aspect_desc = "square"
                
                return {
                    'width': width,
                    'height': height,
                    'size': size_desc,
                    'aspect': aspect_desc,
                    'format': img.format or 'unknown'
                }
        except Exception as e:
            self.logger.debug(f"Could not read image info: {e}")
            return {
                'width': 400,
                'height': 300,
                'size': 'medium',
                'aspect': 'landscape',
                'format': 'JPEG'
            }
    
    def _analyze_ocr_content(self, ocr_text: str) -> Dict:
        """Analyze OCR content to understand material type"""
        if not ocr_text or not ocr_text.strip():
            return {'type': 'unknown', 'confidence': 0.0}
        
        text = ocr_text.lower().strip()
        
        # Calculate text quality
        words = text.split()
        if not words:
            return {'type': 'unknown', 'confidence': 0.0}
        
        # Quality assessment
        recognizable_words = sum(1 for word in words 
                               if len(word) >= 2 and 
                               sum(c.isalpha() for c in word) / len(word) >= 0.7)
        
        text_quality = recognizable_words / len(words) if words else 0.0
        
        # Content type detection (minimal, evidence-based)
        content_indicators = {
            'reference': ['chart', 'table', 'diagram', 'formula', 'list'],
            'instructional': ['lesson', 'tutorial', 'guide', 'how to', 'step'],
            'worksheet': ['solve', 'answer', 'question', 'exercise', 'problem'],
            'informational': ['about', 'information', 'facts', 'data', 'overview']
        }
        
        detected_type = 'material'
        max_matches = 0
        
        for content_type, indicators in content_indicators.items():
            matches = sum(1 for indicator in indicators if indicator in text)
            if matches > max_matches:
                max_matches = matches
                detected_type = content_type
        
        # Only use detected type if we have strong evidence
        confidence = min(text_quality + (max_matches * 0.1), 1.0)
        
        if confidence < 0.4:
            detected_type = 'material'  # Generic fallback
        
        return {
            'type': detected_type,
            'confidence': confidence,
            'text_quality': text_quality
        }
    
    def _create_content_aware_caption(self, image_info: Dict, content_analysis: Dict, ocr_text: str) -> str:
        """Create caption based on actual content, not assumptions"""
        
        # Base description from image properties
        size_desc = image_info['size']
        aspect_desc = image_info['aspect']
        
        # Content type from analysis
        content_type = content_analysis.get('type', 'material')
        confidence = content_analysis.get('confidence', 0.5)
        
        # Professional caption construction
        if confidence > 0.6 and content_type != 'material':
            content_desc = f"educational {content_type}"
        else:
            # Generic but professional
            content_desc = "educational material"
        
        # Format description
        format_desc = f"in a {aspect_desc} format" if aspect_desc != 'square' else ""
        
        # Construct final caption
        caption_parts = [
            f"This {size_desc} image shows",
            content_desc
        ]
        
        if format_desc:
            caption_parts.append(format_desc)
        
        caption = " ".join(caption_parts)
        
        # Ensure proper capitalization and punctuation
        if not caption.endswith('.'):
            caption += ""
        
        return caption
    
    def _analyze_image_content(self, image_path: str, ocr_text: str) -> Dict:
        """Legacy method for compatibility"""
        return self.generate_caption(image_path, ocr_text)


def main():
    """Test the AI-driven caption generator"""
    generator = AIDriverCaptionGenerator()
    
    test_cases = [
        {
            'image_path': '/tmp/test1.jpg',
            'ocr_text': 'Function Notation Worksheet f(x) = 2x + 3'
        },
        {
            'image_path': '/tmp/test2.jpg', 
            'ocr_text': 'STIS SM eed ers La edpethes'
        },
        {
            'image_path': '/tmp/test3.jpg',
            'ocr_text': 'Chemical Formula Chart H2O NaCl'
        }
    ]
    
    for i, test in enumerate(test_cases):
        print(f"\n=== Test {i+1} ===")
        result = generator.generate_caption(test['image_path'], test['ocr_text'])
        print(f"OCR: {test['ocr_text']}")
        print(f"Caption: {result['caption']}")
        print(f"Confidence: {result['content_confidence']:.2f}")

if __name__ == "__main__":
    main()