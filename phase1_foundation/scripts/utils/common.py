"""
Common utility functions for VQA dataset scraping project.

This module provides shared functionality to eliminate code duplication
across scraper scripts and improve maintainability.
"""

import os
import re
import time
import logging
import requests
from pathlib import Path
from typing import List, Optional, Union
from PIL import Image
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
MIN_IMAGE_SIZE = 100
DEFAULT_TIMEOUT = 10
DEFAULT_IMAGE_QUALITY = 90
USER_AGENT = 'Mozilla/5.0 (VQA Dataset Scraper)'


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    # Limit length
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    return sanitized if sanitized else 'unnamed'


def download_image(img_url: str, save_path: Union[str, Path], 
                  min_size: int = MIN_IMAGE_SIZE,
                  timeout: int = DEFAULT_TIMEOUT,
                  quality: int = DEFAULT_IMAGE_QUALITY) -> bool:
    """Download and save an image from URL with validation.
    
    Args:
        img_url: Image URL to download
        save_path: Local path to save the image
        min_size: Minimum image dimension (width or height)
        timeout: Request timeout in seconds
        quality: JPEG quality (1-100)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(img_url, timeout=timeout, headers=headers)
        response.raise_for_status()
        
        # Validate content type
        content_type = response.headers.get('content-type', '').lower()
        if not content_type.startswith('image/'):
            logger.debug(f"Invalid content type: {content_type}")
            return False
        
        # Validate image
        img = Image.open(BytesIO(response.content))
        
        # Skip very small images
        if img.width < min_size or img.height < min_size:
            logger.debug(f"Skipping small image: {img.width}x{img.height}")
            return False
        
        # Convert to RGB and save
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create white background for transparent images
            bg = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            bg.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Ensure directory exists
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save image
        img.save(save_path, "JPEG", quality=quality, optimize=True)
        return True
        
    except (requests.RequestException, OSError, ValueError) as e:
        logger.debug(f"Failed to download {img_url}: {e}")
        return False


def load_keywords(keywords_file: Union[str, Path]) -> List[str]:
    """Load keywords from file with validation.
    
    Args:
        keywords_file: Path to keywords file
        
    Returns:
        List of valid keywords
        
    Raises:
        FileNotFoundError: If keywords file doesn't exist
        ValueError: If no valid keywords found
    """
    keywords_path = Path(keywords_file)
    
    if not keywords_path.exists():
        raise FileNotFoundError(f"Keywords file not found: {keywords_path}")
    
    try:
        keywords = []
        with open(keywords_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines and comments
                    keywords.append(line)
    except (OSError, UnicodeDecodeError) as e:
        raise ValueError(f"Failed to read keywords file: {e}")
    
    if not keywords:
        raise ValueError("No valid keywords found in file")
    
    logger.info(f"Loaded {len(keywords)} keywords from {keywords_path}")
    return keywords


def setup_logging(verbose: bool = False, log_file: Optional[str] = None) -> logging.Logger:
    """Setup logging configuration.
    
    Args:
        verbose: Enable debug level logging
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    return logging.getLogger(__name__)


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator for retrying functions on failure.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {e}")
                        raise
                    
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
                    
            return None  # Should never reach here
        return wrapper
    return decorator


def validate_directory(directory: Union[str, Path], create: bool = True) -> Path:
    """Validate and optionally create directory.
    
    Args:
        directory: Directory path to validate
        create: Whether to create directory if it doesn't exist
        
    Returns:
        Validated Path object
        
    Raises:
        ValueError: If directory validation fails
    """
    dir_path = Path(directory)
    
    if dir_path.exists() and not dir_path.is_dir():
        raise ValueError(f"Path exists but is not a directory: {dir_path}")
    
    if create and not dir_path.exists():
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
        except OSError as e:
            raise ValueError(f"Failed to create directory {dir_path}: {e}")
    
    return dir_path


def get_project_root() -> Path:
    """Get the project root directory.
    
    Returns:
        Path to project root
    """
    # Start from current file and go up until we find the project root
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / 'README.md').exists() and (parent / 'requirements.txt').exists():
            return parent
    
    # Fallback to grandparent of this file
    return current.parents[2]


def count_files_in_directory(directory: Union[str, Path], pattern: str = "*") -> int:
    """Count files in directory matching pattern.
    
    Args:
        directory: Directory to count files in
        pattern: Glob pattern to match files
        
    Returns:
        Number of matching files
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return 0
    
    return len(list(dir_path.glob(pattern)))


class ProgressTracker:
    """Simple progress tracking utility."""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
    
    def update(self, increment: int = 1) -> None:
        """Update progress counter."""
        self.current += increment
        if self.current % 10 == 0 or self.current == self.total:
            self._log_progress()
    
    def _log_progress(self) -> None:
        """Log current progress."""
        percentage = (self.current / self.total) * 100 if self.total > 0 else 0
        elapsed = time.time() - self.start_time
        
        if self.current > 0 and elapsed > 0:
            rate = self.current / elapsed
            eta = (self.total - self.current) / rate if rate > 0 else 0
            logger.info(f"{self.description}: {self.current}/{self.total} "
                       f"({percentage:.1f}%) - ETA: {eta:.0f}s")
        else:
            logger.info(f"{self.description}: {self.current}/{self.total} ({percentage:.1f}%)")
    
    def finish(self) -> None:
        """Mark progress as complete."""
        elapsed = time.time() - self.start_time
        logger.info(f"{self.description} completed: {self.current}/{self.total} "
                   f"in {elapsed:.1f}s")


# Environment variable helpers
def get_env_var(var_name: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """Get environment variable with validation.
    
    Args:
        var_name: Environment variable name
        default: Default value if not found
        required: Whether the variable is required
        
    Returns:
        Environment variable value or default
        
    Raises:
        ValueError: If required variable is missing
    """
    value = os.getenv(var_name, default)
    
    if required and not value:
        raise ValueError(f"Required environment variable '{var_name}' is not set")
    
    return value