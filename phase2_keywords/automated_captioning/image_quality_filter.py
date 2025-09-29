#!/usr/bin/env python3
"""
Image Quality Filter - Filters images based on quality metrics
Ensures only high-quality images suitable for dataset creation
"""

import os
import logging
import numpy as np
from typing import Dict, List, Tuple
from PIL import Image
import cv2

class ImageQualityFilter:
    def __init__(self, min_resolution: int = 100000, min_quality_score: float = 60.0):
        self.min_resolution = min_resolution  # Minimum total pixels
        self.min_quality_score = min_quality_score  # Minimum quality score
        self.logger = self._setup_logger()
        
        self.logger.info(f"🔍 Image Quality Filter initialized")
        self.logger.info(f"   Min resolution: {min_resolution} pixels")
        self.logger.info(f"   Min quality score: {min_quality_score}/100")
    
    def _setup_logger(self):
        """Setup logging"""
        logger = logging.getLogger('ImageQualityFilter')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def assess_image_quality(self, image_path: str) -> Dict:
        """Comprehensive image quality assessment"""
        try:
            if not os.path.exists(image_path):
                return {
                    'quality_score': 0.0,
                    'suitable': False,
                    'issues': ['file_not_found'],
                    'resolution_info': {},
                    'error': 'File not found'
                }
            
            # Load image
            with Image.open(image_path) as img:
                # Basic image info
                width, height = img.size
                total_pixels = width * height
                aspect_ratio = width / height
                format_info = img.format or 'unknown'
                
                # Convert to array for analysis
                img_array = np.array(img.convert('RGB'))
            
            # Quality assessment components
            quality_metrics = {
                'resolution_score': self._assess_resolution(width, height, total_pixels),
                'aspect_ratio_score': self._assess_aspect_ratio(aspect_ratio),
                'sharpness_score': self._assess_sharpness(img_array),
                'brightness_score': self._assess_brightness(img_array),
                'contrast_score': self._assess_contrast(img_array),
                'noise_score': self._assess_noise(img_array)
            }
            
            # Calculate overall quality score
            weights = {
                'resolution_score': 0.25,
                'aspect_ratio_score': 0.15,
                'sharpness_score': 0.25,
                'brightness_score': 0.15,
                'contrast_score': 0.15,
                'noise_score': 0.05
            }
            
            overall_score = sum(score * weights[metric] for metric, score in quality_metrics.items())
            
            # Identify quality issues
            issues = self._identify_quality_issues(quality_metrics, width, height, total_pixels)
            
            # Determine suitability
            suitable = (overall_score >= self.min_quality_score and 
                       total_pixels >= self.min_resolution and
                       'severe_quality_issue' not in issues)
            
            return {
                'quality_score': round(overall_score, 1),
                'suitable': suitable,
                'issues': issues,
                'quality_metrics': quality_metrics,
                'resolution_info': {
                    'width': width,
                    'height': height,
                    'total_pixels': total_pixels,
                    'aspect_ratio': round(aspect_ratio, 2),
                    'format': format_info
                }
            }
            
        except Exception as e:
            self.logger.error(f"Quality assessment failed for {image_path}: {e}")
            return {
                'quality_score': 0.0,
                'suitable': False,
                'issues': ['assessment_failed'],
                'error': str(e)
            }
    
    def _assess_resolution(self, width: int, height: int, total_pixels: int) -> float:
        """Assess image resolution quality"""
        # Score based on total pixels
        if total_pixels >= 1000000:  # 1MP+
            resolution_score = 100.0
        elif total_pixels >= 500000:  # 500K+
            resolution_score = 90.0
        elif total_pixels >= 200000:  # 200K+
            resolution_score = 80.0
        elif total_pixels >= 100000:  # 100K+
            resolution_score = 70.0
        elif total_pixels >= 50000:   # 50K+
            resolution_score = 50.0
        elif total_pixels >= 25000:   # 25K+
            resolution_score = 30.0
        else:
            resolution_score = 10.0
        
        # Penalty for very small dimensions
        if width < 150 or height < 150:
            resolution_score -= 20
        
        return max(0.0, min(100.0, resolution_score))
    
    def _assess_aspect_ratio(self, aspect_ratio: float) -> float:
        """Assess aspect ratio appropriateness"""
        # Prefer common aspect ratios, penalize extreme ratios
        if 0.5 <= aspect_ratio <= 2.0:
            return 100.0
        elif 0.3 <= aspect_ratio <= 3.0:
            return 80.0
        elif 0.2 <= aspect_ratio <= 5.0:
            return 60.0
        else:
            return 30.0  # Very extreme aspect ratios
    
    def _assess_sharpness(self, img_array: np.ndarray) -> float:
        """Assess image sharpness using Laplacian variance"""
        try:
            # Convert to grayscale
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Calculate Laplacian variance (higher = sharper)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Scale to 0-100 score
            if laplacian_var >= 1000:
                return 100.0
            elif laplacian_var >= 500:
                return 90.0
            elif laplacian_var >= 200:
                return 80.0
            elif laplacian_var >= 100:
                return 70.0
            elif laplacian_var >= 50:
                return 50.0
            elif laplacian_var >= 20:
                return 30.0
            else:
                return 10.0
                
        except Exception as e:
            self.logger.debug(f"Sharpness assessment failed: {e}")
            return 50.0  # Default middle score
    
    def _assess_brightness(self, img_array: np.ndarray) -> float:
        """Assess image brightness appropriateness"""
        try:
            # Calculate mean brightness
            if len(img_array.shape) == 3:
                brightness = np.mean(img_array)
            else:
                brightness = np.mean(img_array)
            
            # Optimal brightness range (not too dark, not too bright)
            if 80 <= brightness <= 180:
                return 100.0
            elif 60 <= brightness <= 200:
                return 90.0
            elif 40 <= brightness <= 220:
                return 70.0
            elif 20 <= brightness <= 240:
                return 50.0
            else:
                return 20.0  # Too dark or too bright
                
        except Exception as e:
            self.logger.debug(f"Brightness assessment failed: {e}")
            return 50.0
    
    def _assess_contrast(self, img_array: np.ndarray) -> float:
        """Assess image contrast quality"""
        try:
            # Calculate standard deviation as contrast measure
            if len(img_array.shape) == 3:
                contrast = np.std(img_array)
            else:
                contrast = np.std(img_array)
            
            # Higher contrast is generally better for clarity
            if contrast >= 60:
                return 100.0
            elif contrast >= 45:
                return 90.0
            elif contrast >= 30:
                return 80.0
            elif contrast >= 20:
                return 60.0
            elif contrast >= 10:
                return 40.0
            else:
                return 20.0  # Very low contrast
                
        except Exception as e:
            self.logger.debug(f"Contrast assessment failed: {e}")
            return 50.0
    
    def _assess_noise(self, img_array: np.ndarray) -> float:
        """Assess image noise level (lower noise = higher score)"""
        try:
            # Simple noise estimation using high-frequency content
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Calculate noise using difference from median filtered image
            median_filtered = cv2.medianBlur(gray, 5)
            noise_estimate = np.mean(np.abs(gray.astype(float) - median_filtered.astype(float)))
            
            # Lower noise = higher score
            if noise_estimate <= 5:
                return 100.0
            elif noise_estimate <= 10:
                return 90.0
            elif noise_estimate <= 15:
                return 80.0
            elif noise_estimate <= 25:
                return 60.0
            elif noise_estimate <= 40:
                return 40.0
            else:
                return 20.0  # Very noisy
                
        except Exception as e:
            self.logger.debug(f"Noise assessment failed: {e}")
            return 70.0  # Default good score
    
    def _identify_quality_issues(self, quality_metrics: Dict, width: int, height: int, total_pixels: int) -> List[str]:
        """Identify specific quality issues"""
        issues = []
        
        # Resolution issues
        if total_pixels < self.min_resolution:
            issues.append('low_resolution')
        if width < 150 or height < 150:
            issues.append('too_small_dimensions')
        
        # Quality metric issues
        if quality_metrics['sharpness_score'] < 30:
            issues.append('blurry')
        if quality_metrics['brightness_score'] < 30:
            issues.append('poor_brightness')
        if quality_metrics['contrast_score'] < 30:
            issues.append('low_contrast')
        if quality_metrics['noise_score'] < 30:
            issues.append('noisy')
        if quality_metrics['aspect_ratio_score'] < 40:
            issues.append('extreme_aspect_ratio')
        
        # Severe quality issues
        severe_issues = sum(1 for score in quality_metrics.values() if score < 25)
        if severe_issues >= 3:
            issues.append('severe_quality_issue')
        
        return issues
    
    def filter_image_list(self, image_paths: List[str]) -> Dict:
        """Filter a list of images based on quality"""
        self.logger.info(f"🔍 Filtering {len(image_paths)} images for quality...")
        
        suitable_images = []
        unsuitable_images = []
        quality_stats = {
            'total_processed': 0,
            'suitable_count': 0,
            'unsuitable_count': 0,
            'issues_summary': {},
            'average_quality_score': 0.0
        }
        
        total_quality_score = 0.0
        
        for image_path in image_paths:
            try:
                assessment = self.assess_image_quality(image_path)
                quality_stats['total_processed'] += 1
                total_quality_score += assessment['quality_score']
                
                if assessment['suitable']:
                    suitable_images.append(image_path)
                    quality_stats['suitable_count'] += 1
                else:
                    unsuitable_images.append({
                        'path': image_path,
                        'issues': assessment['issues'],
                        'quality_score': assessment['quality_score']
                    })
                    quality_stats['unsuitable_count'] += 1
                
                # Track issue frequency
                for issue in assessment.get('issues', []):
                    quality_stats['issues_summary'][issue] = quality_stats['issues_summary'].get(issue, 0) + 1
                
            except Exception as e:
                self.logger.warning(f"Failed to assess {image_path}: {e}")
                quality_stats['unsuitable_count'] += 1
        
        # Calculate statistics
        if quality_stats['total_processed'] > 0:
            quality_stats['average_quality_score'] = round(total_quality_score / quality_stats['total_processed'], 1)
            quality_stats['suitable_percentage'] = round((quality_stats['suitable_count'] / quality_stats['total_processed']) * 100, 1)
        
        # Log results
        self.logger.info(f"✅ Quality filtering completed:")
        self.logger.info(f"   Suitable images: {quality_stats['suitable_count']}/{quality_stats['total_processed']} ({quality_stats.get('suitable_percentage', 0)}%)")
        self.logger.info(f"   Average quality score: {quality_stats['average_quality_score']}/100")
        
        if quality_stats['issues_summary']:
            self.logger.info(f"   Common issues: {dict(list(quality_stats['issues_summary'].items())[:5])}")
        
        return {
            'suitable_images': suitable_images,
            'unsuitable_images': unsuitable_images,
            'quality_stats': quality_stats
        }
    
    def batch_assess_quality(self, image_paths: List[str]) -> List[Dict]:
        """Assess quality for multiple images and return detailed results"""
        results = []
        
        for image_path in image_paths:
            assessment = self.assess_image_quality(image_path)
            assessment['image_path'] = image_path
            results.append(assessment)
        
        return results


def main():
    """Test the image quality filter"""
    filter_system = ImageQualityFilter(min_resolution=50000, min_quality_score=50.0)
    
    # Test with sample images directory
    test_dir = "/Users/ahtisham/vqa_dataset_project/phase2_full_demo/images"
    
    if os.path.exists(test_dir):
        import glob
        test_images = glob.glob(os.path.join(test_dir, "*.jpg"))[:5]  # Test first 5
        
        print(f"🔍 Testing Image Quality Filter with {len(test_images)} images...")
        
        results = filter_system.filter_image_list(test_images)
        
        print(f"\nResults:")
        print(f"Suitable: {len(results['suitable_images'])}")
        print(f"Unsuitable: {len(results['unsuitable_images'])}")
        print(f"Quality Stats: {results['quality_stats']}")
        
        # Show details for first few images
        for i, image_path in enumerate(test_images[:3]):
            assessment = filter_system.assess_image_quality(image_path)
            print(f"\nImage {i+1}: {os.path.basename(image_path)}")
            print(f"  Quality Score: {assessment['quality_score']}/100")
            print(f"  Suitable: {assessment['suitable']}")
            print(f"  Issues: {assessment.get('issues', [])}")
    else:
        print(f"Test directory not found: {test_dir}")

if __name__ == "__main__":
    main()