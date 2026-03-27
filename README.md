# 🧠 VQA Dataset Project

This project builds a **comprehensive, multilingual Visual Question Answering (VQA) dataset** enriched with semantic image-text pairs across diverse domains (medicine, education, environment, culture, etc.).

The pipeline integrates **API-free intelligent scraping**, OCR-based filtering, advanced keyword generation, and scalable metadata generation. The goal is to serve robust training data for VQA and foundational vision-language models.

---

## 🌍 Vision & Scope

- **🌐 Multilingual**: Complete support for 13+ languages (Arabic, English, Chinese, Japanese, Korean, Hindi, Urdu, Bengali, Malay, Portuguese, Spanish, French, German)
- **🔄 API-Free Scraping**: Advanced scraping from Google Images, Bing, Pinterest, DuckDuckGo without any API dependencies
- **🤖 Smart Anti-Detection**: Sophisticated measures to ensure reliable, respectful scraping
- **🎯 Domain-Specific**: Intelligent keyword expansion targeting educational, medical, and cultural content
- **📊 Production-Ready**: Enterprise-grade code with comprehensive error handling, logging, and configuration management

---

## 🔁 End-to-End Pipeline

### **Phase 1: Foundation Pipeline**
1. **🔎 Intelligent Image Scraping**
   - **Sources**: Google Images (API-free), Bing, Pinterest, DuckDuckGo, Baidu, Naver, Yahoo Japan
   - **Anti-Detection**: User agent rotation, human-like delays, stealth browsing
   - **Quality Filtering**: Size validation, format checking, duplicate prevention
   - **Language-Specific**: Specialized scrapers for regional platforms (Baidu for Chinese, Naver for Korean)

2. **📝 OCR Processing & Filtering**
   - **Multi-language OCR**: EasyOCR integration for 13+ languages
   - **Content Validation**: Text quality checks, Unicode filtering
   - **Educational Focus**: Targeting images with educational/instructional text content

3. **📊 Metadata Enrichment**
   - **Comprehensive Annotation**: Source, dimensions, OCR text, quality metrics
   - **Structured Storage**: JSON-based metadata with taxonomy mapping
   - **Deduplication**: Hash-based and visual similarity detection

### **Phase 2: Advanced Keyword Engine**
4. **🎯 Intelligent Keyword Generation**
   - **Seed-Based Expansion**: Domain-specific seed terms with intelligent growth
   - **Contextual Enhancement**: Educational poster templates, diagrams, worksheets
   - **Quality Validation**: Automated filtering of low-value combinations
   - **Scale**: 19k+ high-quality English keywords generated

---

## 🏗️ Project Architecture

```
vqa_dataset_project/
├── 📁 phase1_foundation/           # Core scraping and processing pipeline
│   ├── 📁 data/                    # Raw and processed image storage
│   ├── 📁 metadata/               # Dataset metadata and annotations
│   │   ├── arabic_image_metadata.json
│   │   ├── chinese_image_metadata.json
│   │   ├── taxonomy.json          # Domain/subdomain structure
│   │   └── link_dataset.json      # Source URL mappings
│   ├── 📁 notebooks/              # Jupyter analysis notebooks
│   │   ├── OCR_Images_Cleaned_Arabic.ipynb
│   │   └── Scraper_plus_easyocr.ipynb
│   └── 📁 scripts/
│       ├── 📁 scrapers/           # Source-specific image scrapers
│       │   ├── image_scraper_google_cli.py      # 🆕 API-free Google Images
│       │   ├── simple_google_scraper.py         # 🆕 Lightweight fallback
│       │   ├── image_scraper_bing_cli.py
│       │   ├── image_scraper_pinterest_cli.py
│       │   ├── image_scraper_baidu_selenium_chinese.py
│       │   ├── image_scraper_naver_selenium_korean.py
│       │   └── [18 more specialized scrapers]
│       ├── 📁 ocr/                # Language-specific OCR processors
│       │   ├── filter_images_arabic_ocr.py
│       │   ├── filter_images_english_ocr.py
│       │   └── [11 more language filters]
│       ├── 📁 pipeline/           # End-to-end automation
│       │   ├── pipeline_arabic.py
│       │   ├── pipeline_english.py
│       │   └── [11 more language pipelines]
│       ├── 📁 utils/              # 🆕 Shared utilities
│       │   ├── common.py          # Core functions (download, sanitize, etc.)
│       │   └── zip.py
│       └── 📁 config/             # Language keyword files
│           ├── keywords.txt       # Base English keywords
│           ├── keywords_arabic.txt
│           └── [12 more language files]
├── 📁 phase2_keywords/            # 🆕 Advanced keyword generation engine
│   ├── 📁 scripts/
│   │   ├── generate_keywords_english.py     # 🆕 Enhanced with type safety
│   │   ├── build_seed_tree_extended.py
│   │   └── prune_seeds.py
│   ├── 📁 seed/                   # Base seed terms
│   │   ├── english_seed_terms_pruned.txt    # Curated 1.4k terms
│   │   └── english_seed_termsv1.txt
│   └── 📁 expanded/               # Generated keyword sets
│       ├── english_combined_enhanced_19k.txt  # 🎯 19k high-quality keywords
│       ├── english_expanded.txt              # 9.8k base expansion
│       └── generate_additional_keywords.py
├── 📁 qa_data/                    # VQA question-answer pairs
│   ├── chinese_qa_data.jsonl
│   └── medical_radiology.jsonl
├── 📁 config/                     # 🆕 Global configuration
│   ├── keywords_google.txt
│   ├── keywords_pinterest.txt
│   └── keywords_stock.txt
├── 🛠️ config.py                   # 🆕 Centralized configuration management
├── 📋 requirements.txt            # 🆕 Updated dependencies (API-free)
├── 🧪 test_google_scraper.py      # 🆕 Comprehensive testing
├── 📚 DEVELOPMENT.md              # 🆕 Developer guide
├── 🔧 .env.example               # 🆕 Environment configuration template
└── 📖 README.md                  # This file
```

---

## 🚀 Quick Start

### **Prerequisites**
- Python 3.9+ (recommended: 3.11)
- Chrome/Chromium browser
- No API keys required! 🎉

### **Installation**
```bash
# Clone and setup
git clone <your-repo-url>
cd vqa_dataset_project

# Install dependencies
pip install -r requirements.txt

# Optional: Configure environment (all settings have defaults)
cp .env.example .env
```

### **Test the System**
```bash
# Test the new API-free Google scraper
python3 test_google_scraper.py

# Test simple scraper (backup method)
python3 phase1_foundation/scripts/scrapers/simple_google_scraper.py
```

### **Run Image Scraping**
```bash
# Google Images (API-free)
python3 phase1_foundation/scripts/scrapers/image_scraper_google_cli.py \
  --keywords config/keywords_google.txt \
  --images_per_keyword 10 \
  --save_dir data/raw_google

# Other sources
python3 phase1_foundation/scripts/scrapers/image_scraper_bing_cli.py \
  --keywords config/keywords_test.txt \
  --save_dir data/raw_bing

# Pinterest
python3 phase1_foundation/scripts/scrapers/image_scraper_pinterest_cli.py \
  --keywords config/keywords_pinterest.txt \
  --save_dir data/raw_pinterest
```

### **Generate Advanced Keywords**
```bash
# Generate expanded English keywords
python3 phase2_keywords/scripts/generate_keywords_english.py \
  --input phase2_keywords/seed/english_seed_terms_pruned.txt \
  --output phase2_keywords/expanded/new_keywords.txt \
  --max-prefixes 6 \
  --max-suffixes 6
```

### **Run Language-Specific Pipelines**
```bash
# Arabic pipeline
python3 phase1_foundation/scripts/pipeline/pipeline_arabic.py

# English pipeline  
python3 phase1_foundation/scripts/pipeline/pipeline_english.py

# Chinese pipeline
python3 phase1_foundation/scripts/pipeline/pipeline_chinese.py
```

---

## 🎯 Key Features

### **🆕 API-Free Innovation**
- **Zero Setup**: No API keys, no configuration hassles
- **Cost-Free**: Unlimited scraping without usage fees
- **Full Access**: Complete Google Images results, not limited API responses
- **Reliable**: Advanced anti-detection ensures consistent performance

### **🤖 Production-Grade Architecture**
- **Type Safety**: Comprehensive type hints throughout
- **Error Handling**: Robust error recovery and validation
- **Logging**: Structured logging with configurable levels
- **Testing**: Comprehensive test suites and debugging tools
- **Documentation**: Enterprise-level documentation and guides

### **🌐 Multilingual Excellence**
- **13+ Languages**: Arabic, English, Chinese, Japanese, Korean, Hindi, Urdu, Bengali, Malay, Portuguese, Spanish, French, German
- **Cultural Awareness**: Region-specific platforms (Baidu, Naver, Yahoo Japan)
- **Script Support**: Advanced Unicode handling for diverse writing systems

### **📊 Dataset Quality**
- **Educational Focus**: Optimized for learning materials, diagrams, worksheets
- **Quality Metrics**: Size validation, format checking, text content analysis
- **Deduplication**: Multiple algorithms to ensure unique content
- **Metadata Rich**: Comprehensive annotation for ML training

---

## 📄 Output Format

### **Image Metadata Structure**
```json
{
  "image_id": "edu_math_poster_001",
  "image_path": "data/processed_google/edu_math_poster_001.jpg",
  "source": "google_images",
  "domain": "education",
  "subdomain": "mathematics",
  "language": "en", 
  "keyword": "math worksheet printable",
  "image_metadata": {
    "width": 1200,
    "height": 800,
    "format": "JPEG",
    "size_bytes": 156789,
    "quality_score": 0.85
  },
  "ocr_text": "Addition and Subtraction Practice Sheet",
  "scraping_metadata": {
    "scraped_at": "2025-08-15T10:30:00Z",
    "scraper_version": "2.0.0",
    "source_url": "https://example.com/worksheet.jpg"
  }
}
```

### **VQA Question Format (Planned)**
```json
{
  "image_id": "edu_math_poster_001",
  "questions": [
    {
      "question_id": "q1",
      "question": "What type of mathematical operations are shown in this worksheet?",
      "answer": "Addition and subtraction",
      "question_type": "content_identification",
      "difficulty": "easy",
      "language": "en"
    },
    {
      "question_id": "q2", 
      "question": "What grade level is this worksheet designed for?",
      "answer": "Elementary school, grades 1-3",
      "question_type": "educational_analysis",
      "difficulty": "medium",
      "language": "en"
    }
  ]
}
```

---

## 🔧 Configuration

### **Environment Variables** (Optional)
```bash
# Scraping behavior
REQUESTS_PER_SECOND=2.0
MAX_CONCURRENT_DOWNLOADS=5
IMAGES_PER_KEYWORD=10

# Google scraping (API-free)
GOOGLE_SCROLL_ATTEMPTS=10
GOOGLE_MIN_DELAY=1.0
GOOGLE_MAX_DELAY=3.0

# Selenium settings
SELENIUM_HEADLESS=true
SELENIUM_PAGE_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
LOG_TO_FILE=true
```

### **Advanced Configuration**
The project uses a sophisticated configuration system (`config.py`) supporting:
- Environment variables
- YAML/JSON configuration files  
- Type-safe dataclasses
- Validation and defaults

---

## 🎭 Supported Languages & Platforms

| Language | Script | Scrapers | OCR | Pipeline | Keywords |
|----------|---------|----------|-----|----------|----------|
| **Arabic** | العربية | Google, Bing, Pinterest | ✅ | ✅ | ✅ |
| **English** | Latin | Google, Bing, Pinterest, DuckDuckGo | ✅ | ✅ | ✅ 19k |
| **Chinese** | 中文 | Google, Baidu, Bing | ✅ | ✅ | ✅ |
| **Japanese** | 日本語 | Google, Yahoo Japan, Pixabay, Unsplash | ✅ | ✅ | ✅ |
| **Korean** | 한국어 | Google, Naver, Daum | ✅ | ✅ | ✅ |
| **Hindi** | हिन्दी | Google, Flickr, Getty, Yahoo | ✅ | ✅ | ✅ |
| **Urdu** | اردو | Google, Bing, Pinterest | ✅ | ✅ | ✅ |
| **Bengali** | বাংলা | Google, Bing | ✅ | ✅ | ✅ |
| **Malay** | Bahasa | Google, Bing | ✅ | ✅ | ✅ |
| **Portuguese** | Português | Google, Government sites, Blogs | ✅ | ✅ | ✅ |
| **Spanish** | Español | Google, Bing, Pinterest | ✅ | ✅ | ✅ |
| **French** | Français | Google, Bing, Pinterest | ✅ | ✅ | ✅ |
| **German** | Deutsch | Google, News sites | ✅ | ✅ | ✅ |

---

## 🚀 Recent Major Updates

### **v2.0.0 - API-Free Revolution** (August 2025)
- 🎉 **Completely removed API dependencies** - no more Google API keys needed
- 🤖 **Advanced anti-detection** scraping with Selenium automation  
- 🏗️ **Production-grade architecture** with proper error handling and logging
- 📚 **Comprehensive documentation** and testing infrastructure
- 🎯 **19k high-quality English keywords** generated with intelligent expansion
- 🛠️ **Centralized configuration** management system
- 🧪 **Testing and debugging** tools for reliable operation

### **Key Improvements**
- ✅ Zero configuration required
- ✅ No API costs or quotas
- ✅ Enhanced image quality and quantity
- ✅ Robust error handling and recovery
- ✅ Professional code standards with type hints
- ✅ Automated ChromeDriver management

---

## 🔮 Roadmap

### **Short Term**
- [ ] **Image Deduplication**: Advanced SSIM and perceptual hashing
- [ ] **Quality Scoring**: ML-based image quality assessment
- [ ] **Batch Processing**: Parallel scraping across multiple sources
- [ ] **Web UI**: Simple interface for monitoring and control

### **Medium Term**  
- [ ] **Question Generation**: Automated VQA question creation
- [ ] **Data Validation**: Human-in-the-loop quality assurance
- [ ] **API Integration**: RESTful API for dataset access
- [ ] **Cloud Deployment**: Docker containers and Kubernetes support

### **Long Term**
- [ ] **Video Processing**: Extend to video content with frame extraction
- [ ] **Audio Integration**: Speech-to-text for multimedia content
- [ ] **Real-time Processing**: Live scraping and processing pipeline
- [ ] **ML Training Pipeline**: Direct integration with model training

---

## 📖 Documentation

- **[DEVELOPMENT.md](DEVELOPMENT.md)**: Complete developer guide with setup, standards, and troubleshooting
- **[Phase 1 README](phase1_foundation/README_PHASE1.md)**: Detailed foundation pipeline documentation
- **[Scraper Plan](scraper_plan.md)**: Original project planning and strategy

---

## 🤝 Contributing

This is a production-grade project with high code quality standards:

1. **Follow the style guide** in `DEVELOPMENT.md`
2. **Add comprehensive tests** for new features
3. **Update documentation** for any changes
4. **Use type hints** and proper error handling
5. **Test across multiple languages** and sources

---

## 📊 Project Statistics

- **📁 Total Files**: 60+ Python scripts
- **🌐 Languages Supported**: 13+
- **🔗 Scraping Sources**: 15+ platforms
- **🎯 Keywords Generated**: 19,000+ (English)
- **📝 Lines of Code**: 10,000+ (with documentation)
- **🧪 Test Coverage**: Comprehensive scraper testing
- **📚 Documentation**: Enterprise-grade guides

---

## 🏆 Credits

**Lead Developer**: [Ahtesham Ahmad](https://github.com/shami-ah)  
**Architecture**: Production-grade, API-free design  
**Portfolio**: [portfolio-site-alpha.pages.dev](https://portfolio-site-alpha.pages.dev)  
**License**: MIT — Educational/Research use

---

*Built with ❤️ for the ML/AI research community*
