"""
Configuration management for VQA Dataset Project.

This module provides centralized configuration management for all scripts
in the project, supporting environment variables, config files, and defaults.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


@dataclass
class ScrapingConfig:
    """Configuration for image scraping operations."""
    
    # Image quality settings
    min_image_size: int = 100
    max_image_size: int = 5000
    image_quality: int = 90
    supported_formats: list = field(default_factory=lambda: ['JPEG', 'PNG', 'WebP'])
    
    # Request settings
    timeout: int = 10
    max_retries: int = 3
    retry_delay: float = 1.0
    user_agent: str = 'Mozilla/5.0 (VQA Dataset Scraper)'
    
    # Rate limiting
    requests_per_second: float = 2.0
    concurrent_downloads: int = 5
    
    # File management
    images_per_keyword: int = 10
    max_images_per_directory: int = 1000


@dataclass
class GoogleConfig:
    """Configuration for Google Images scraping (API-Free)."""
    
    # Scraping behavior settings
    max_results_per_query: int = 20
    scroll_attempts: int = 10
    scroll_delay_min: float = 2.0
    scroll_delay_max: float = 4.0
    
    # Anti-detection settings
    user_agent_rotation: bool = True
    random_delays: bool = True
    min_delay: float = 1.0
    max_delay: float = 3.0
    
    # Image filtering
    min_image_dimension: int = 100
    skip_gifs: bool = True
    skip_icons: bool = True


@dataclass
class SeleniumConfig:
    """Configuration for Selenium-based scrapers."""
    
    # Browser settings
    headless: bool = True
    window_size: tuple = (1920, 1080)
    page_load_timeout: int = 30
    implicit_wait: int = 10
    
    # Chrome options
    chrome_options: list = field(default_factory=lambda: [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-blink-features=AutomationControlled',
        '--user-agent=Mozilla/5.0 (VQA Dataset Scraper)'
    ])


@dataclass
class OCRConfig:
    """Configuration for OCR processing."""
    
    # EasyOCR settings
    languages: list = field(default_factory=lambda: ['ar', 'en'])
    gpu: bool = False
    confidence_threshold: float = 0.5
    
    # Text filtering
    min_text_length: int = 3
    max_text_length: int = 1000
    filter_patterns: list = field(default_factory=lambda: [
        r'^[0-9]+$',  # Only numbers
        r'^[!@#$%^&*(),.?":{}|<>]+$',  # Only special characters
    ])


@dataclass
class KeywordConfig:
    """Configuration for keyword processing."""
    
    # Generation settings
    max_keywords_per_domain: int = 1000
    min_keyword_length: int = 2
    max_keyword_length: int = 50
    
    # Expansion settings
    synonym_expansion: bool = True
    stemming: bool = False
    language_variants: bool = True


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    
    level: str = 'INFO'
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_to_file: bool = True
    log_directory: str = 'logs'
    max_log_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class ProjectConfig:
    """Main project configuration containing all sub-configurations."""
    
    # Sub-configurations
    scraping: ScrapingConfig = field(default_factory=ScrapingConfig)
    google: GoogleConfig = field(default_factory=GoogleConfig)
    selenium: SeleniumConfig = field(default_factory=SeleniumConfig)
    ocr: OCRConfig = field(default_factory=OCRConfig)
    keywords: KeywordConfig = field(default_factory=KeywordConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Project paths
    project_root: Optional[Path] = None
    data_directory: str = 'data'
    output_directory: str = 'output'
    temp_directory: str = 'temp'
    
    def __post_init__(self):
        if self.project_root is None:
            self.project_root = self._find_project_root()
    
    def _find_project_root(self) -> Path:
        """Find the project root directory."""
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / 'README.md').exists() and (parent / 'requirements.txt').exists():
                return parent
        return current.parent
    
    def get_data_path(self, *args) -> Path:
        """Get path within data directory."""
        return self.project_root / self.data_directory / Path(*args)
    
    def get_output_path(self, *args) -> Path:
        """Get path within output directory."""
        return self.project_root / self.output_directory / Path(*args)
    
    def get_temp_path(self, *args) -> Path:
        """Get path within temp directory."""
        return self.project_root / self.temp_directory / Path(*args)


class ConfigManager:
    """Manages configuration loading and saving."""
    
    def __init__(self, config_file: Optional[Union[str, Path]] = None):
        """Initialize configuration manager.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config_file = Path(config_file) if config_file else None
        self._config: Optional[ProjectConfig] = None
    
    def load_config(self) -> ProjectConfig:
        """Load configuration from file or create default.
        
        Returns:
            ProjectConfig instance
        """
        if self._config is not None:
            return self._config
        
        if self.config_file and self.config_file.exists():
            try:
                self._config = self._load_from_file(self.config_file)
            except Exception as e:
                print(f"Warning: Failed to load config from {self.config_file}: {e}")
                print("Using default configuration")
                self._config = ProjectConfig()
        else:
            self._config = ProjectConfig()
        
        return self._config
    
    def _load_from_file(self, config_file: Path) -> ProjectConfig:
        """Load configuration from YAML or JSON file.
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            ProjectConfig instance
        """
        with open(config_file, 'r', encoding='utf-8') as f:
            if config_file.suffix.lower() in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif config_file.suffix.lower() == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported config file format: {config_file.suffix}")
        
        return self._dict_to_config(data)
    
    def _dict_to_config(self, data: Dict[str, Any]) -> ProjectConfig:
        """Convert dictionary to ProjectConfig.
        
        Args:
            data: Configuration dictionary
            
        Returns:
            ProjectConfig instance
        """
        # This is a simplified implementation
        # In practice, you might want to use a library like hydra or pydantic
        config = ProjectConfig()
        
        # Update configuration fields recursively
        for key, value in data.items():
            if hasattr(config, key):
                if isinstance(value, dict):
                    # Handle nested configurations
                    sub_config = getattr(config, key)
                    for sub_key, sub_value in value.items():
                        if hasattr(sub_config, sub_key):
                            setattr(sub_config, sub_key, sub_value)
                else:
                    setattr(config, key, value)
        
        return config
    
    def save_config(self, config: ProjectConfig, config_file: Optional[Path] = None) -> None:
        """Save configuration to file.
        
        Args:
            config: ProjectConfig to save
            config_file: Optional output file path
        """
        output_file = config_file or self.config_file
        if not output_file:
            raise ValueError("No output file specified")
        
        # Convert config to dictionary
        config_dict = self._config_to_dict(config)
        
        # Save to file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            if output_file.suffix.lower() in ['.yaml', '.yml']:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            elif output_file.suffix.lower() == '.json':
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Unsupported config file format: {output_file.suffix}")
    
    def _config_to_dict(self, config: ProjectConfig) -> Dict[str, Any]:
        """Convert ProjectConfig to dictionary.
        
        Args:
            config: ProjectConfig to convert
            
        Returns:
            Configuration dictionary
        """
        # This is a simplified implementation
        result = {}
        for field_name, field_value in config.__dict__.items():
            if hasattr(field_value, '__dict__'):
                result[field_name] = field_value.__dict__.copy()
            else:
                result[field_name] = field_value
        
        # Convert Path objects to strings
        if 'project_root' in result and result['project_root']:
            result['project_root'] = str(result['project_root'])
        
        return result


# Global configuration manager instance
_config_manager = ConfigManager()


def get_config(config_file: Optional[Union[str, Path]] = None) -> ProjectConfig:
    """Get project configuration.
    
    Args:
        config_file: Optional path to configuration file
        
    Returns:
        ProjectConfig instance
    """
    if config_file:
        manager = ConfigManager(config_file)
        return manager.load_config()
    
    return _config_manager.load_config()


def create_default_config_file(output_path: Union[str, Path]) -> None:
    """Create a default configuration file.
    
    Args:
        output_path: Path where to save the default config
    """
    config = ProjectConfig()
    manager = ConfigManager()
    manager.save_config(config, Path(output_path))
    print(f"Default configuration saved to: {output_path}")


# Environment variable helpers specific to this project
def get_selenium_config() -> Dict[str, Any]:
    """Get Selenium configuration for web scraping.
    
    Returns:
        Dictionary containing Selenium configuration
    """
    config = get_config()
    
    return {
        'headless': config.selenium.headless,
        'window_size': config.selenium.window_size,
        'page_load_timeout': config.selenium.page_load_timeout,
        'implicit_wait': config.selenium.implicit_wait,
        'chrome_options': config.selenium.chrome_options,
    }


def get_scraping_config() -> Dict[str, Any]:
    """Get general scraping configuration.
    
    Returns:
        Dictionary containing scraping configuration
    """
    config = get_config()
    
    return {
        'min_image_size': config.scraping.min_image_size,
        'timeout': config.scraping.timeout,
        'max_retries': config.scraping.max_retries,
        'requests_per_second': config.scraping.requests_per_second,
        'images_per_keyword': config.scraping.images_per_keyword,
    }


if __name__ == "__main__":
    # Create a sample configuration file
    create_default_config_file("config/default.yaml")