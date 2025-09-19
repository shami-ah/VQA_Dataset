#!/usr/bin/env python3
"""
Integrated Deduplication Pipeline
Combines hash-based and CLIP embedding-based deduplication methods
"""

import os
import json
import logging
import shutil
from typing import Dict, List, Set, Optional
from pathlib import Path
from datetime import datetime

# Import deduplication modules
try:
    from .hash_filtering.hash_deduplicator import HashDeduplicator
    from .embedding_clustering.clip_deduplicator import CLIPDeduplicator
except ImportError:
    try:
        from hash_filtering.hash_deduplicator import HashDeduplicator
        from embedding_clustering.clip_deduplicator import CLIPDeduplicator
    except ImportError:
        # Create fallback classes if imports fail
        class HashDeduplicator:
            def __init__(self, perceptual_threshold=8, exact_hash_check=True, **kwargs):
                self.logger = logging.getLogger('FallbackHashDedup')
                self.logger.warning("Using fallback hash deduplicator")
                self.perceptual_threshold = perceptual_threshold
                self.exact_hash_check = exact_hash_check
            
            def batch_deduplicate(self, image_paths, output_dir=None, **kwargs):
                return {
                    'unique_images': image_paths, 
                    'duplicates_removed': [],
                    'duplicate_groups': {},
                    'statistics': {'total_processed': len(image_paths), 'unique_images': len(image_paths)}
                }
            
            def deduplicate_images(self, image_paths, **kwargs):
                return self.batch_deduplicate(image_paths, **kwargs)
            
            def copy_unique_images(self, image_paths, output_dir):
                """Copy unique images to output directory"""
                os.makedirs(output_dir, exist_ok=True)
                copied_count = 0
                for img_path in image_paths:
                    try:
                        filename = os.path.basename(img_path)
                        dest_path = os.path.join(output_dir, filename)
                        if os.path.abspath(img_path) != os.path.abspath(dest_path):
                            shutil.copy2(img_path, dest_path)
                        copied_count += 1
                    except Exception as e:
                        self.logger.warning(f"Failed to copy {img_path}: {e}")
                return copied_count
        
        class CLIPDeduplicator:
            def __init__(self, model_name="ViT-B/32", similarity_threshold=0.90, batch_size=32, **kwargs):
                self.logger = logging.getLogger('FallbackCLIPDedup')
                self.logger.warning("Using fallback CLIP deduplicator")
                self.model_name = model_name
                self.similarity_threshold = similarity_threshold
                self.batch_size = batch_size
            
            def batch_deduplicate(self, image_paths, output_dir=None, **kwargs):
                return {
                    'unique_images': image_paths, 
                    'duplicates_removed': [],
                    'clusters': {},
                    'statistics': {'total_processed': len(image_paths), 'unique_images': len(image_paths)}
                }
            
            def deduplicate_images(self, image_paths, **kwargs):
                return self.batch_deduplicate(image_paths, **kwargs)

class IntegratedDeduplicationPipeline:
    def __init__(self,
                 # Hash filtering parameters
                 perceptual_threshold: int = 5,
                 exact_hash_check: bool = True,
                 # CLIP parameters
                 clip_model: str = "ViT-B/32",
                 clip_similarity_threshold: float = 0.90,
                 clip_batch_size: int = 32,
                 # Pipeline parameters
                 use_both_methods: bool = True,
                 prioritize_method: str = "hash"):  # "hash" or "clip"
        """
        Initialize Integrated Deduplication Pipeline
        
        Args:
            perceptual_threshold: Hamming distance threshold for hash similarity
            exact_hash_check: Whether to check exact file hashes
            clip_model: CLIP model name
            clip_similarity_threshold: CLIP cosine similarity threshold
            clip_batch_size: Batch size for CLIP processing
            use_both_methods: Whether to use both hash and CLIP methods
            prioritize_method: Which method to prioritize for conflicts
        """
        self.use_both_methods = use_both_methods
        self.prioritize_method = prioritize_method
        self.logger = self._setup_logger()
        
        # Initialize deduplication methods
        self.hash_deduplicator = HashDeduplicator(
            perceptual_threshold=perceptual_threshold,
            exact_hash_check=exact_hash_check
        )
        
        self.clip_deduplicator = None
        if use_both_methods or prioritize_method == "clip":
            try:
                self.clip_deduplicator = CLIPDeduplicator(
                    model_name=clip_model,
                    similarity_threshold=clip_similarity_threshold,
                    batch_size=clip_batch_size
                )
            except Exception as e:
                self.logger.warning(f"CLIP deduplicator initialization failed: {e}")
                if prioritize_method == "clip":
                    self.logger.info("Falling back to hash-only deduplication")
                    self.prioritize_method = "hash"
                    self.use_both_methods = False
        
        # Results storage
        self.hash_results = {}
        self.clip_results = {}
        self.integrated_results = {}
        
    def _setup_logger(self):
        """Setup logging for the pipeline"""
        logger = logging.getLogger('IntegratedDeduplication')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _merge_deduplication_results(self, 
                                   hash_unique: List[str], 
                                   hash_duplicates: Dict,
                                   clip_unique: List[str], 
                                   clip_duplicates: Dict) -> Dict:
        """
        Merge results from hash and CLIP deduplication methods
        
        Args:
            hash_unique: Unique images from hash method
            hash_duplicates: Duplicate groups from hash method
            clip_unique: Unique images from CLIP method  
            clip_duplicates: Duplicate groups from CLIP method
            
        Returns:
            Merged deduplication results
        """
        # Convert to sets for easier operations
        hash_unique_set = set(hash_unique)
        clip_unique_set = set(clip_unique) if clip_unique else set()
        
        # Collect all duplicates from both methods
        hash_all_duplicates = set()
        for original, dups in hash_duplicates.items():
            hash_all_duplicates.update(dups)
            
        clip_all_duplicates = set()
        if clip_duplicates:
            for original, dups in clip_duplicates.items():
                clip_all_duplicates.update(dups)
        
        if self.prioritize_method == "hash":
            # Hash method takes priority
            final_unique = list(hash_unique_set)
            final_duplicates = dict(hash_duplicates)
            
            # Add CLIP-detected duplicates not caught by hash
            if clip_duplicates:
                for clip_original, clip_dups in clip_duplicates.items():
                    # Only add if hash method didn't mark these as duplicates
                    if (clip_original in hash_unique_set and 
                        not any(dup in hash_all_duplicates for dup in clip_dups)):
                        
                        # Remove from unique if CLIP found duplicates
                        if clip_original in final_unique:
                            final_unique.remove(clip_original)
                        
                        # Add CLIP duplicates
                        final_duplicates[clip_original] = clip_dups
                        
                        # Remove CLIP duplicates from unique list
                        for dup in clip_dups:
                            if dup in final_unique:
                                final_unique.remove(dup)
                                
        else:  # prioritize_method == "clip"
            # CLIP method takes priority
            final_unique = list(clip_unique_set) if clip_unique_set else []
            final_duplicates = dict(clip_duplicates) if clip_duplicates else {}
            
            # Add hash-detected duplicates not caught by CLIP
            for hash_original, hash_dups in hash_duplicates.items():
                # Only add if CLIP method didn't mark these as duplicates
                if (hash_original in clip_unique_set and 
                    not any(dup in clip_all_duplicates for dup in hash_dups)):
                    
                    # Remove from unique if hash found duplicates
                    if hash_original in final_unique:
                        final_unique.remove(hash_original)
                    
                    # Add hash duplicates
                    final_duplicates[hash_original] = hash_dups
                    
                    # Remove hash duplicates from unique list
                    for dup in hash_dups:
                        if dup in final_unique:
                            final_unique.remove(dup)
        
        # Create agreement analysis
        agreement_analysis = self._analyze_method_agreement(
            hash_unique, hash_duplicates, clip_unique, clip_duplicates
        )
        
        return {
            'final_unique_images': final_unique,
            'final_duplicate_groups': final_duplicates,
            'method_agreement': agreement_analysis,
            'integration_stats': {
                'hash_unique_count': len(hash_unique),
                'clip_unique_count': len(clip_unique) if clip_unique else 0,
                'final_unique_count': len(final_unique),
                'hash_duplicate_groups': len(hash_duplicates),
                'clip_duplicate_groups': len(clip_duplicates) if clip_duplicates else 0,
                'final_duplicate_groups': len(final_duplicates),
                'prioritized_method': self.prioritize_method
            }
        }
    
    def _analyze_method_agreement(self, 
                                hash_unique: List[str], 
                                hash_duplicates: Dict,
                                clip_unique: List[str], 
                                clip_duplicates: Dict) -> Dict:
        """Analyze agreement between hash and CLIP methods"""
        
        hash_unique_set = set(hash_unique)
        clip_unique_set = set(clip_unique) if clip_unique else set()
        
        # Find images both methods agree are unique
        agreed_unique = hash_unique_set.intersection(clip_unique_set) if clip_unique_set else set()
        
        # Find images with conflicting classifications
        hash_marked_dup = set()
        for original, dups in hash_duplicates.items():
            hash_marked_dup.update(dups)
            hash_marked_dup.add(original)  # Include the representative
            
        clip_marked_dup = set()
        if clip_duplicates:
            for original, dups in clip_duplicates.items():
                clip_marked_dup.update(dups)
                clip_marked_dup.add(original)
        
        conflicts = {
            'hash_unique_clip_duplicate': list(hash_unique_set.intersection(clip_marked_dup)),
            'clip_unique_hash_duplicate': list(clip_unique_set.intersection(hash_marked_dup)) if clip_unique_set else []
        }
        
        return {
            'agreed_unique': list(agreed_unique),
            'agreed_unique_count': len(agreed_unique),
            'conflicts': conflicts,
            'conflict_count': len(conflicts['hash_unique_clip_duplicate']) + len(conflicts['clip_unique_hash_duplicate']),
            'agreement_rate': len(agreed_unique) / max(len(hash_unique), 1)
        }
    
    def deduplicate_images(self, 
                         image_paths: List[str],
                         output_dir: str = "phase2_keywords/outputs/deduplication_results",
                         save_intermediate: bool = True,
                         copy_unique_images: bool = True) -> Dict:
        """
        Run integrated deduplication pipeline
        
        Args:
            image_paths: List of image file paths to deduplicate
            output_dir: Output directory for results
            save_intermediate: Whether to save intermediate results from each method
            copy_unique_images: Whether to copy unique images to output directory
            
        Returns:
            Dictionary with integrated deduplication results
        """
        start_time = datetime.now()
        
        os.makedirs(output_dir, exist_ok=True)
        
        self.logger.info(f"Starting integrated deduplication of {len(image_paths)} images")
        self.logger.info(f"Methods: {'Hash + CLIP' if self.use_both_methods else self.prioritize_method.upper()}")
        
        # Step 1: Hash-based deduplication
        self.logger.info("Step 1: Hash-based deduplication...")
        hash_output_dir = os.path.join(output_dir, "hash_results") if save_intermediate else output_dir
        
        self.hash_results = self.hash_deduplicator.batch_deduplicate(
            image_paths, hash_output_dir
        )
        
        # Step 2: CLIP-based deduplication (if enabled)
        clip_results = {'unique_images': [], 'clusters': {}}
        if self.use_both_methods or self.prioritize_method == "clip":
            if self.clip_deduplicator is not None:
                self.logger.info("Step 2: CLIP embedding-based deduplication...")
                clip_output_dir = os.path.join(output_dir, "clip_results") if save_intermediate else output_dir
                
                try:
                    clip_results = self.clip_deduplicator.batch_deduplicate(
                        image_paths, 
                        clip_output_dir,
                        save_similarity_matrix=save_intermediate
                    )
                    self.clip_results = clip_results
                except Exception as e:
                    self.logger.error(f"CLIP deduplication failed: {e}")
                    self.logger.info("Continuing with hash-only results")
        
        # Step 3: Integrate results
        self.logger.info("Step 3: Integrating deduplication results...")
        
        if self.use_both_methods and self.clip_results:
            merged_results = self._merge_deduplication_results(
                self.hash_results['unique_images'],
                self.hash_results['duplicate_groups'],
                clip_results['unique_images'], 
                clip_results['clusters']
            )
        else:
            # Use single method results
            primary_results = self.hash_results if self.prioritize_method == "hash" else clip_results
            merged_results = {
                'final_unique_images': primary_results['unique_images'],
                'final_duplicate_groups': primary_results.get('duplicate_groups', primary_results.get('clusters', {})),
                'method_agreement': {'single_method_used': self.prioritize_method},
                'integration_stats': {
                    'final_unique_count': len(primary_results['unique_images']),
                    'final_duplicate_groups': len(primary_results.get('duplicate_groups', primary_results.get('clusters', {}))),
                    'method_used': self.prioritize_method
                }
            }
        
        # Calculate processing time
        end_time = datetime.now()
        processing_time = str(end_time - start_time)
        
        # Create comprehensive results
        self.integrated_results = {
            'integrated_deduplication_completed': True,
            'timestamp': end_time.isoformat(),
            'configuration': {
                'use_both_methods': self.use_both_methods,
                'prioritized_method': self.prioritize_method,
                'hash_perceptual_threshold': self.hash_deduplicator.perceptual_threshold,
                'clip_similarity_threshold': self.clip_deduplicator.similarity_threshold if self.clip_deduplicator else None
            },
            'processing_stats': {
                'total_input_images': len(image_paths),
                'final_unique_images': len(merged_results['final_unique_images']),
                'total_duplicates_removed': len(image_paths) - len(merged_results['final_unique_images']),
                'duplicate_groups_found': len(merged_results['final_duplicate_groups']),
                'processing_time': processing_time,
                'deduplication_rate': (len(image_paths) - len(merged_results['final_unique_images'])) / len(image_paths)
            },
            'results': merged_results,
            'hash_method_stats': self.hash_results['statistics'] if 'statistics' in self.hash_results else {},
            'clip_method_stats': clip_results.get('statistics', {}) if clip_results else {}
        }
        
        # Save integrated results
        results_file = os.path.join(output_dir, 'integrated_deduplication_results.json')
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.integrated_results, f, ensure_ascii=False, indent=2)
        
        # Save final unique images list
        unique_images_file = os.path.join(output_dir, 'final_unique_images.json')
        with open(unique_images_file, 'w', encoding='utf-8') as f:
            json.dump(merged_results['final_unique_images'], f, ensure_ascii=False, indent=2)
        
        # Copy unique images if requested
        copied_count = 0
        if copy_unique_images and merged_results['final_unique_images']:
            unique_images_dir = os.path.join(output_dir, 'unique_images')
            copied_count = self.hash_deduplicator.copy_unique_images(
                merged_results['final_unique_images'], unique_images_dir
            )
        
        # Log final results
        self.logger.info(f"Integrated deduplication completed:")
        self.logger.info(f"  Input images: {len(image_paths)}")
        self.logger.info(f"  Final unique images: {len(merged_results['final_unique_images'])}")
        self.logger.info(f"  Duplicates removed: {len(image_paths) - len(merged_results['final_unique_images'])}")
        self.logger.info(f"  Duplicate groups: {len(merged_results['final_duplicate_groups'])}")
        if copied_count > 0:
            self.logger.info(f"  Unique images copied: {copied_count}")
        self.logger.info(f"  Processing time: {processing_time}")
        self.logger.info(f"  Results saved to: {output_dir}")
        
        return {
            'unique_images': merged_results['final_unique_images'],
            'duplicate_groups': merged_results['final_duplicate_groups'],
            'statistics': self.integrated_results['processing_stats'],
            'method_agreement': merged_results.get('method_agreement', {}),
            'output_directory': output_dir
        }
    
    def deduplicate_by_keyword_groups(self, 
                                    keyword_image_mapping: Dict[str, List[str]],
                                    output_base_dir: str = "keyword_dedup_results") -> Dict:
        """
        Deduplicate images grouped by keywords (within each keyword batch)
        
        Args:
            keyword_image_mapping: Dictionary mapping keywords to image lists
            output_base_dir: Base directory for all results
            
        Returns:
            Dictionary with per-keyword deduplication results
        """
        all_results = {}
        
        for keyword, image_paths in keyword_image_mapping.items():
            self.logger.info(f"Deduplicating images for keyword: '{keyword}' ({len(image_paths)} images)")
            
            keyword_output_dir = os.path.join(output_base_dir, keyword.replace(' ', '_').replace('/', '_'))
            
            keyword_results = self.deduplicate_images(
                image_paths,
                keyword_output_dir,
                save_intermediate=False,
                copy_unique_images=True
            )
            
            all_results[keyword] = keyword_results
        
        # Save combined summary
        combined_stats = {
            'keywords_processed': len(keyword_image_mapping),
            'total_input_images': sum(len(paths) for paths in keyword_image_mapping.values()),
            'total_unique_images': sum(len(result['unique_images']) for result in all_results.values()),
            'per_keyword_results': {
                keyword: {
                    'input_count': len(keyword_image_mapping[keyword]),
                    'unique_count': len(result['unique_images']),
                    'duplicates_removed': len(keyword_image_mapping[keyword]) - len(result['unique_images'])
                }
                for keyword, result in all_results.items()
            }
        }
        
        summary_file = os.path.join(output_base_dir, 'keyword_deduplication_summary.json')
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(combined_stats, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Keyword-based deduplication completed:")
        self.logger.info(f"  Keywords processed: {combined_stats['keywords_processed']}")
        self.logger.info(f"  Total input images: {combined_stats['total_input_images']}")
        self.logger.info(f"  Total unique images: {combined_stats['total_unique_images']}")
        self.logger.info(f"  Overall duplicates removed: {combined_stats['total_input_images'] - combined_stats['total_unique_images']}")
        
        return all_results


def main():
    """CLI interface for integrated deduplication"""
    import argparse
    import glob
    
    parser = argparse.ArgumentParser(description="Integrated Image Deduplication Pipeline")
    parser.add_argument("--input_dir", required=True, help="Input directory containing images")
    parser.add_argument("--output_dir", required=True, help="Output directory for results")
    parser.add_argument("--method", default="integrated", choices=["hash", "clip", "integrated"], 
                       help="Deduplication method")
    parser.add_argument("--similarity_threshold", type=float, default=0.90, 
                       help="CLIP similarity threshold")
    parser.add_argument("--perceptual_threshold", type=int, default=5,
                       help="Hash perceptual threshold")
    
    args = parser.parse_args()
    
    # Find all image files in input directory
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.webp', '*.gif']
    image_paths = []
    
    for ext in image_extensions:
        pattern = os.path.join(args.input_dir, '**', ext)
        image_paths.extend(glob.glob(pattern, recursive=True))
    
    if not image_paths:
        print(f"❌ No images found in {args.input_dir}")
        return
    
    print(f"📊 Found {len(image_paths)} images to process")
    
    # Initialize pipeline
    use_both = args.method == "integrated"
    pipeline = IntegratedDeduplicationPipeline(
        perceptual_threshold=args.perceptual_threshold,
        clip_similarity_threshold=args.similarity_threshold,
        use_both_methods=use_both,
        prioritize_method="hash"
    )
    
    # Run deduplication
    results = pipeline.deduplicate_images(
        image_paths,
        args.output_dir,
        save_intermediate=True,
        copy_unique_images=True
    )
    
    print(f"Integrated deduplication completed:")
    print(f"  Unique images: {len(results['unique_images'])}")
    print(f"  Duplicate groups: {len(results['duplicate_groups'])}")
    print(f"  Statistics: {results['statistics']}")


if __name__ == "__main__":
    main()