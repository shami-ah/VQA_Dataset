# 🛠️ VQA Dataset Project - Development Guide

This guide provides comprehensive information for developers working on the VQA Dataset Project. It covers setup, best practices, code standards, and maintenance procedures.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Development Environment Setup](#development-environment-setup)
- [Code Standards & Best Practices](#code-standards--best-practices)
- [Project Architecture](#project-architecture)
- [Security Guidelines](#security-guidelines)
- [Testing & Quality Assurance](#testing--quality-assurance)
- [Deployment & Production](#deployment--production)
- [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### Prerequisites

- Python 3.9+ (recommended: 3.11)
- Git
- Chrome/Chromium browser (for Selenium-based scrapers)
- ChromeDriver (automatically managed with webdriver-manager)

### Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd vqa_dataset_project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional)
cp .env.example .env
# Edit .env with your preferences (all settings have sensible defaults)
```

### Environment Variables

Create a `.env` file in the project root (optional - all have defaults):

```env
# Scraping configuration
REQUESTS_PER_SECOND=2.0
MAX_CONCURRENT_DOWNLOADS=5
IMAGES_PER_KEYWORD=10

# Google Images scraping (API-free)
GOOGLE_SCROLL_ATTEMPTS=10
GOOGLE_MIN_DELAY=1.0
GOOGLE_MAX_DELAY=3.0

# Selenium configuration
SELENIUM_HEADLESS=true
SELENIUM_PAGE_TIMEOUT=30

# Logging configuration
LOG_LEVEL=INFO
LOG_TO_FILE=true
```

## 🏗️ Development Environment Setup

### IDE Configuration

**VS Code Settings** (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=88"],
    "python.sortImports.args": ["--profile", "black"]
}
```

### Pre-commit Hooks

Install pre-commit hooks for consistent code quality:

```bash
pip install pre-commit
pre-commit install
```

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black]
```

## 📏 Code Standards & Best Practices

### Python Style Guide

1. **Follow PEP 8** with Black formatting (line length: 88 characters)
2. **Use type hints** for all function parameters and return values
3. **Write comprehensive docstrings** in Google style
4. **Use meaningful variable and function names**
5. **Organize imports** according to PEP 8 (standard library, third-party, local)

### Example Code Structure

```python
#!/usr/bin/env python3
"""
Module description here.

This module provides functionality for...
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Optional

import requests
from PIL import Image

from phase1_foundation.scripts.utils.common import sanitize_filename

# Configure logging
logger = logging.getLogger(__name__)


class ExampleClass:
    """Example class following project conventions."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the class.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self._validate_config()
    
    def process_data(self, input_data: List[str]) -> Optional[Dict[str, int]]:
        """Process input data and return results.
        
        Args:
            input_data: List of data items to process
            
        Returns:
            Dictionary with processing results, None if failed
            
        Raises:
            ValueError: If input data is invalid
        """
        if not input_data:
            raise ValueError("Input data cannot be empty")
        
        try:
            # Processing logic here
            return {"processed": len(input_data)}
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            return None
```

### Error Handling Standards

1. **Use specific exception types** instead of bare `except:`
2. **Log errors with context** using the logging module
3. **Provide meaningful error messages** to help with debugging
4. **Use validation functions** for input parameters
5. **Implement retry mechanisms** for network operations

### Logging Standards

```python
import logging

# Module-level logger
logger = logging.getLogger(__name__)

# Example usage
logger.debug("Detailed debugging information")
logger.info("General information about program execution")
logger.warning("Something unexpected happened")
logger.error("A serious problem occurred")
logger.critical("The program cannot continue")
```

## 🏛️ Project Architecture

### Directory Structure

```
vqa_dataset_project/
├── phase1_foundation/          # Core scraping and processing
│   ├── scripts/
│   │   ├── scrapers/          # Web scraping modules
│   │   ├── ocr/               # OCR processing
│   │   ├── pipeline/          # End-to-end pipelines
│   │   └── utils/             # Shared utilities
│   ├── data/                  # Raw and processed data
│   └── metadata/              # Dataset metadata
├── phase2_keywords/            # Keyword generation and expansion
│   ├── scripts/               # Processing scripts
│   ├── seed/                  # Seed keyword files
│   └── expanded/              # Generated keyword lists
├── qa_data/                   # QA dataset files
├── config/                    # Configuration files
├── logs/                      # Log files
├── config.py                  # Configuration management
├── requirements.txt           # Python dependencies
└── DEVELOPMENT.md            # This file
```

### Key Components

1. **Scrapers** (`phase1_foundation/scripts/scrapers/`):
   - Individual scrapers for different sources (Google, Bing, Pinterest, etc.)
   - Language-specific implementations
   - Selenium-based and API-based scrapers

2. **OCR Processing** (`phase1_foundation/scripts/ocr/`):
   - Language-specific text extraction
   - Image filtering based on text content
   - Quality validation

3. **Keyword Generation** (`phase2_keywords/`):
   - Seed keyword management
   - Intelligent keyword expansion
   - Domain-specific categorization

4. **Utilities** (`phase1_foundation/scripts/utils/`):
   - Common functions shared across modules
   - Image processing utilities
   - File management helpers

### Configuration System

The project uses a centralized configuration system (`config.py`) that supports:

- Environment variables
- YAML/JSON configuration files
- Default values with validation
- Type-safe configuration classes

Example usage:
```python
from config import get_config

config = get_config()
api_key = config.google.api_key
max_images = config.scraping.images_per_keyword
```

## 🔒 Security Guidelines

### Data and Credentials

1. **No API keys required** - all scraping is API-free
2. **Use environment variables** for configuration
3. **Never commit sensitive data** to version control
4. **Respect website terms of service** and rate limits

### Safe Coding Practices

1. **Validate all user inputs** before processing
2. **Use parameterized queries** for any database operations
3. **Sanitize file paths** to prevent directory traversal
4. **Implement rate limiting** for API calls
5. **Use HTTPS** for all external requests

### Security Checklist

- [x] No API keys or credentials required
- [ ] All external inputs are validated
- [ ] File paths are sanitized
- [x] Rate limiting is implemented
- [ ] Error messages don't leak sensitive information
- [ ] Dependencies are kept up to date
- [x] Respectful scraping with delays and anti-detection

## 🧪 Testing & Quality Assurance

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=phase1_foundation --cov=phase2_keywords

# Run specific test file
pytest tests/test_scrapers.py

# Run with verbose output
pytest -v
```

### Code Quality Checks

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .

# Type checking
mypy phase1_foundation/ phase2_keywords/

# Run all quality checks
make quality  # If Makefile is available
```

### Test Structure

```python
import pytest
from unittest.mock import Mock, patch

from phase1_foundation.scripts.utils.common import sanitize_filename


class TestSanitizeFilename:
    """Test cases for filename sanitization."""
    
    def test_removes_invalid_characters(self):
        """Test that invalid characters are removed."""
        result = sanitize_filename('file<>name?.txt')
        assert result == 'file__name_.txt'
    
    def test_handles_empty_string(self):
        """Test handling of empty strings."""
        result = sanitize_filename('')
        assert result == 'unnamed'
    
    @pytest.mark.parametrize("input_name,expected", [
        ("normal_file.txt", "normal_file.txt"),
        ("file with spaces.jpg", "file with spaces.jpg"),
        ("file/with/slashes.png", "file_with_slashes.png"),
    ])
    def test_various_inputs(self, input_name, expected):
        """Test various input scenarios."""
        assert sanitize_filename(input_name) == expected
```

## 🚀 Deployment & Production

### Production Checklist

- [ ] All dependencies are pinned to specific versions
- [ ] Environment variables are configured
- [ ] Logging is properly configured
- [ ] Error monitoring is set up
- [ ] Resource limits are defined
- [ ] Data backup procedures are in place

### Performance Monitoring

1. **Monitor scraping rates** and success rates
2. **Track API usage** and quota consumption
3. **Monitor disk space** for image storage
4. **Log processing times** for performance optimization

### Scaling Considerations

1. **Parallel processing** for multiple scrapers
2. **Distributed storage** for large datasets
3. **Load balancing** for high-volume operations
4. **Caching strategies** for frequently accessed data

## 🔧 Troubleshooting

### Common Issues

#### 1. Selenium WebDriver Issues

**Problem**: ChromeDriver not found or version mismatch

**Solution**:
```bash
# Install ChromeDriver manager
pip install webdriver-manager

# Use in code:
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(ChromeDriverManager().install())
```

#### 2. Google Images Blocking

**Problem**: Google blocking the scraper or returning no results

**Solution**:
- Increase delays between requests
- Use `--visible` flag to see what's happening
- Rotate user agents (automatically done)
- Take breaks between scraping sessions
- Use different keywords if some are blocked

#### 3. Image Download Failures

**Problem**: High failure rate for image downloads

**Solution**:
- Implement retry mechanisms
- Use different User-Agent headers
- Add delays between requests
- Validate image content before saving

#### 4. Memory Issues with Large Datasets

**Problem**: Out of memory errors during processing

**Solution**:
- Process data in chunks
- Use generators instead of loading all data
- Implement pagination for large result sets
- Clear unused variables explicitly

### Debugging Tips

1. **Enable verbose logging** with `-v` flag
2. **Use debugger breakpoints** in IDEs
3. **Check log files** in the `logs/` directory
4. **Validate input data** before processing
5. **Test with small datasets** first

### Performance Optimization

1. **Profile code** to identify bottlenecks
2. **Use async/await** for I/O operations
3. **Implement connection pooling** for HTTP requests
4. **Cache frequently accessed data**
5. **Optimize image processing** with appropriate libraries

## 📞 Support & Contributing

### Getting Help

1. Check this development guide
2. Review the main README.md
3. Search existing issues in the repository
4. Create a new issue with detailed information

### Contributing Guidelines

1. **Fork the repository** and create a feature branch
2. **Follow code standards** outlined in this guide
3. **Write tests** for new functionality
4. **Update documentation** as needed
5. **Submit a pull request** with clear description

### Code Review Process

1. All code must be reviewed before merging
2. Automated tests must pass
3. Code quality checks must pass
4. Documentation must be updated if needed

---

## 📚 Additional Resources

- [Python PEP 8 Style Guide](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [Requests Documentation](https://docs.python-requests.org/)
- [PIL/Pillow Documentation](https://pillow.readthedocs.io/)

---

**Last Updated**: 2025-08-15
**Version**: 2.0.0
**Maintainer**: VQA Dataset Team