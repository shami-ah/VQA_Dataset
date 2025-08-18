#!/usr/bin/env python3
"""
Enhanced keyword expansion script for VQA dataset generation.

This script expands a pruned seed list into high-yield search phrases
by intelligently adding prefixes and suffixes that are likely to surface
images containing text elements suitable for VQA training.

Features:
- Type-safe implementation with comprehensive error handling
- Intelligent seed classification and expansion
- Configurable expansion parameters
- Progress tracking and detailed logging
- Duplicate prevention and validation

Input:
  phase2_keywords/seed/english_seed_terms_pruned.txt
Output:
  phase2_keywords/expanded/keywords_english_master_offline.txt
"""

import logging
import argparse
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class BucketGroup:
    """Configuration for a specific type of document/image bucket."""
    tokens: Set[str]
    prefixes: List[str]
    suffixes: List[str]
    
    def matches(self, text: str) -> bool:
        """Check if text contains any of the bucket tokens."""
        text_lower = f" {text.lower()} "
        return any(f" {token} " in text_lower for token in self.tokens)


@dataclass
class ExpansionConfig:
    """Configuration for keyword expansion parameters."""
    max_prefixes_per_seed: int = 6
    max_suffixes_per_seed: int = 6
    min_seed_length: int = 3
    max_seed_length: int = 100
    enable_special_combinations: bool = True


# Define bucket groups with type safety
BUCKET_GROUPS: Dict[str, BucketGroup] = {
    "poster_like": BucketGroup(
        tokens={"poster", "placard", "broadside", "banner", "billboard", 
                "advertisement", "ad", "commercial"},
        prefixes=["printable", "editable", "A4", "A3", "US letter", "pdf"],
        suffixes=["template", "design", "layout", "mockup", "sample", "example"]
    ),
    "diagram_like": BucketGroup(
        tokens={"infographic", "flowchart", "diagram", "chart", "graph", 
                "plot", "schematic", "blueprint", "visualization"},
        prefixes=["printable", "editable", "vector", "svg", "pdf", "HD"],
        suffixes=["template", "design", "layout", "sample", "example", "guide"]
    ),
    "doc_like": BucketGroup(
        tokens={"document", "paper", "text file", "form", "application", 
                "certificate", "diploma", "credential", "menu", "menu card"},
        prefixes=["printable", "editable", "blank", "fillable", "A4", "pdf"],
        suffixes=["template", "sample", "example", "blank form", "fillable form", "official"]
    ),
    "label_sign_like": BucketGroup(
        tokens={"label", "tag", "sticker", "plaque", "tablet", "sign", 
                "signboard", "signal", "notice", "bulletin", "memo", "announcement"},
        prefixes=["printable", "editable", "vector", "svg", "pdf", "laminated"],
        suffixes=["template", "sticker sheet", "set", "sample", "example", "guide"]
    ),
    "brochure_like": BucketGroup(
        tokens={"brochure", "leaflet", "flyer", "pamphlet", "handbill"},
        prefixes=["printable", "editable", "A4", "US letter", "pdf", "tri-fold"],
        suffixes=["template", "bi-fold", "tri-fold template", "mockup", "sample", "example"]
    )
}

# Fallback configuration for unclassified seeds
DEFAULT_PREFIXES = ["printable", "editable", "pdf", "A4", "sample", "template"]
DEFAULT_SUFFIXES = ["template", "sample", "example", "design", "layout", "guide"]

# Safety filters to avoid redundant combinations
BAD_SUFFIX_IF_CONTAINS = {
    "form": {"form", "blank form", "fillable form"},
    "menu": {"menu", "menu card"},
    "poster": {"poster"},
    "template": {"template"},
}

class KeywordExpander:
    """Handles intelligent keyword expansion with validation and logging."""
    
    def __init__(self, config: ExpansionConfig = ExpansionConfig()):
        """Initialize the keyword expander with configuration.
        
        Args:
            config: Expansion configuration parameters
        """
        self.config = config
        self.stats = {
            'seeds_processed': 0,
            'keywords_generated': 0,
            'classification_hits': 0,
            'classification_misses': 0
        }
    
    def classify_seed(self, seed: str) -> Optional[Tuple[str, BucketGroup]]:
        """Classify a seed into an appropriate bucket group.
        
        Args:
            seed: The seed phrase to classify
            
        Returns:
            Tuple of (bucket_name, bucket_group) if match found, None otherwise
        """
        if not seed or len(seed) < self.config.min_seed_length:
            return None
        
        for bucket_name, bucket_group in BUCKET_GROUPS.items():
            if bucket_group.matches(seed):
                return bucket_name, bucket_group
        
        return None
    
    def validate_seed(self, seed: str) -> bool:
        """Validate that a seed meets quality criteria.
        
        Args:
            seed: Seed phrase to validate
            
        Returns:
            True if seed is valid, False otherwise
        """
        if not seed or not isinstance(seed, str):
            return False
        
        seed = seed.strip()
        
        # Length checks
        if len(seed) < self.config.min_seed_length:
            logger.debug(f"Seed too short: '{seed}'")
            return False
        
        if len(seed) > self.config.max_seed_length:
            logger.debug(f"Seed too long: '{seed}'")
            return False
        
        # Content checks
        if seed.isdigit():
            logger.debug(f"Seed is only numbers: '{seed}'")
            return False
        
        # Check for minimum meaningful content
        words = seed.split()
        if len(words) < 2:
            logger.debug(f"Seed has insufficient words: '{seed}'")
            return False
        
        return True
    
    def generate_for_seed(self, seed: str) -> List[str]:
        """Generate expanded keywords for a single seed.
        
        Args:
            seed: The seed phrase to expand
            
        Returns:
            List of expanded keywords
            
        Raises:
            ValueError: If seed is invalid
        """
        if not self.validate_seed(seed):
            raise ValueError(f"Invalid seed: '{seed}'")
        
        # Classify the seed
        classification = self.classify_seed(seed)
        if classification:
            bucket_name, bucket_group = classification
            prefixes = bucket_group.prefixes
            suffixes = bucket_group.suffixes
            self.stats['classification_hits'] += 1
            logger.debug(f"Classified '{seed}' as {bucket_name}")
        else:
            prefixes = DEFAULT_PREFIXES
            suffixes = DEFAULT_SUFFIXES
            self.stats['classification_misses'] += 1
            logger.debug(f"Using default classification for '{seed}'")
        
        generated_keywords = set()
        
        # Generate prefix combinations
        for prefix in prefixes[:self.config.max_prefixes_per_seed]:
            keyword = f"{prefix} {seed}".strip()
            if self._is_valid_combination(keyword):
                generated_keywords.add(keyword)
        
        # Generate suffix combinations with safety checks
        seed_lower = seed.lower()
        blocked_suffixes = set()
        
        # Build blocked suffixes list
        for key, bad_suffixes in BAD_SUFFIX_IF_CONTAINS.items():
            if key in seed_lower:
                blocked_suffixes.update(s.lower() for s in bad_suffixes)
        
        added_suffixes = 0
        for suffix in suffixes:
            if added_suffixes >= self.config.max_suffixes_per_seed:
                break
            
            suffix_lower = suffix.lower()
            
            # Skip blocked suffixes
            if suffix_lower in blocked_suffixes:
                continue
            
            # Avoid word duplication
            if any(suffix_lower == word.lower() for word in seed.split()):
                continue
            
            keyword = f"{seed} {suffix}".strip()
            if self._is_valid_combination(keyword):
                generated_keywords.add(keyword)
                added_suffixes += 1
        
        # Add special combinations for high-value buckets
        if (classification and self.config.enable_special_combinations and 
            classification[0] in ("poster_like", "diagram_like")):
            
            special_keywords = [
                f"printable {seed} template",
                f"{seed} template pdf"
            ]
            
            for keyword in special_keywords:
                if self._is_valid_combination(keyword):
                    generated_keywords.add(keyword)
        
        self.stats['seeds_processed'] += 1
        result = sorted(generated_keywords)
        self.stats['keywords_generated'] += len(result)
        
        return result
    
    def _is_valid_combination(self, keyword: str) -> bool:
        """Check if a generated keyword combination is valid.
        
        Args:
            keyword: Generated keyword to validate
            
        Returns:
            True if combination is valid, False otherwise
        """
        if not keyword or len(keyword.strip()) < self.config.min_seed_length:
            return False
        
        # Check for excessive repetition
        words = keyword.lower().split()
        if len(set(words)) < len(words) * 0.7:  # Too much repetition
            return False
        
        return True
    
    def get_stats(self) -> Dict[str, int]:
        """Get expansion statistics.
        
        Returns:
            Dictionary containing processing statistics
        """
        return self.stats.copy()

def load_seeds(input_file: Path) -> List[str]:
    """Load and validate seeds from input file.
    
    Args:
        input_file: Path to seeds file
        
    Returns:
        List of valid seed phrases
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If no valid seeds found
    """
    if not input_file.exists():
        raise FileNotFoundError(f"Seeds file not found: {input_file}")
    
    try:
        content = input_file.read_text(encoding="utf-8")
        lines = content.splitlines()
    except (OSError, UnicodeDecodeError) as e:
        raise ValueError(f"Failed to read seeds file: {e}")
    
    seeds = []
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if line and not line.startswith('#'):  # Skip empty lines and comments
            seeds.append(line)
        elif line.startswith('#'):
            logger.debug(f"Skipped comment line {line_num}: {line}")
    
    if not seeds:
        raise ValueError("No valid seeds found in input file")
    
    logger.info(f"Loaded {len(seeds)} seeds from {input_file}")
    return seeds


def deduplicate_keywords(keywords: List[str]) -> List[str]:
    """Remove duplicates while preserving order and case.
    
    Args:
        keywords: List of keywords that may contain duplicates
        
    Returns:
        Deduplicated list of keywords
    """
    seen = set()
    deduplicated = []
    
    for keyword in keywords:
        key = keyword.lower().strip()
        if key and key not in seen:
            seen.add(key)
            deduplicated.append(keyword.strip())
    
    return deduplicated


def save_keywords(keywords: List[str], output_file: Path) -> None:
    """Save keywords to output file with error handling.
    
    Args:
        keywords: List of keywords to save
        output_file: Output file path
        
    Raises:
        OSError: If file writing fails
    """
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        output_file.write_text("\n".join(keywords), encoding="utf-8")
        logger.info(f"Successfully wrote {len(keywords)} keywords to {output_file}")
    except OSError as e:
        raise OSError(f"Failed to write keywords to {output_file}: {e}")


def print_summary(stats: Dict[str, int], total_keywords: int, 
                 input_file: Path, output_file: Path) -> None:
    """Print processing summary with statistics.
    
    Args:
        stats: Processing statistics
        total_keywords: Total number of output keywords
        input_file: Input file path
        output_file: Output file path
    """
    print("\n" + "="*60)
    print("🎯 KEYWORD EXPANSION SUMMARY")
    print("="*60)
    print(f"📁 Input file:     {input_file}")
    print(f"📁 Output file:    {output_file}")
    print(f"🌱 Seeds processed: {stats['seeds_processed']}")
    print(f"🎯 Keywords generated: {stats['keywords_generated']}")
    print(f"✨ Final keywords (deduplicated): {total_keywords}")
    print(f"📊 Classification hits: {stats['classification_hits']}")
    print(f"📊 Classification misses: {stats['classification_misses']}")
    
    if stats['seeds_processed'] > 0:
        hit_rate = (stats['classification_hits'] / stats['seeds_processed']) * 100
        expansion_rate = stats['keywords_generated'] / stats['seeds_processed']
        print(f"📈 Classification hit rate: {hit_rate:.1f}%")
        print(f"📈 Average expansion rate: {expansion_rate:.1f}x")
    
    print("="*60)


def main():
    """Main entry point for keyword expansion script."""
    parser = argparse.ArgumentParser(
        description="Expand seed keywords for VQA dataset generation",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--input", "-i", 
        type=str,
        help="Input seeds file path (relative to project root)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output keywords file path (relative to project root)"
    )
    parser.add_argument(
        "--max-prefixes", 
        type=int, 
        default=6,
        help="Maximum prefixes per seed"
    )
    parser.add_argument(
        "--max-suffixes", 
        type=int, 
        default=6,
        help="Maximum suffixes per seed"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Determine file paths
    project_root = Path(__file__).resolve().parents[2]
    
    if args.input:
        input_file = project_root / args.input
    else:
        input_file = project_root / "phase2_keywords" / "seed" / "english_seed_terms_pruned.txt"
    
    if args.output:
        output_file = project_root / args.output
    else:
        output_file = project_root / "phase2_keywords" / "expanded" / "keywords_english_master_offline.txt"
    
    try:
        # Load seeds
        logger.info(f"Loading seeds from: {input_file}")
        seeds = load_seeds(input_file)
        
        # Configure expansion
        config = ExpansionConfig(
            max_prefixes_per_seed=args.max_prefixes,
            max_suffixes_per_seed=args.max_suffixes
        )
        
        # Initialize expander
        expander = KeywordExpander(config)
        
        # Process seeds
        logger.info("Starting keyword expansion...")
        all_keywords = []
        
        for i, seed in enumerate(seeds, 1):
            if i % 100 == 0:
                logger.info(f"Processed {i}/{len(seeds)} seeds...")
            
            try:
                expanded = expander.generate_for_seed(seed)
                all_keywords.extend(expanded)
            except ValueError as e:
                logger.warning(f"Skipped invalid seed '{seed}': {e}")
                continue
        
        # Deduplicate keywords
        logger.info("Deduplicating keywords...")
        final_keywords = deduplicate_keywords(all_keywords)
        
        # Save results
        logger.info(f"Saving {len(final_keywords)} keywords...")
        save_keywords(final_keywords, output_file)
        
        # Print summary
        stats = expander.get_stats()
        print_summary(stats, len(final_keywords), input_file, output_file)
        
        print("\n✅ Keyword expansion completed successfully!")
        
    except Exception as e:
        logger.error(f"Keyword expansion failed: {e}")
        print(f"\n❌ Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()