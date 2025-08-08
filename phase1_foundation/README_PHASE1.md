## Phase 1: Automatic Image Collection Pipeline

### 1. Introduction

This document covers the first phase of the VQA Dataset Project: an end-to-end, automated pipeline to scrape multilingual image sources and filter them via OCR for downstream VQA tasks. It provides architecture details, module descriptions, CLI references, configuration guidelines, troubleshooting tips, and actionable best practices for clean, optimized, and shareable code.

---

### 2. Project Structure

```
vqa_dataset_project/
├── data/
│   ├── raw_<source>/
│   └── processed_<source>/
├── metadata/
│   └── annotations.json
├── scripts/
│   ├── scrapers/
│   │   ├── image_scraper_google_cli.py
│   │   ├── image_scraper_bing_cli.py
│   │   ├── image_scraper_duckduckgo_cli.py
│   │   └── image_scraper_pinterest_cli.py
│   ├── filter_images_easyocr_arabic.py
│   ├── filter_images_easyocr_french.py
│   └── pipeline_template.py
├── scripts/config/
│   ├── keywords_arabic.txt
│   ├── keywords_french.txt
│   └── (other languages).txt
├── qa_data/
│   └── <domain>_<subdomain>.jsonl
├── docs/
│   └── (generated MkDocs/Sphinx files)
├── CONTRIBUTING.md
└── README.md
```

---

### 3. Prerequisites

- **Python** 3.8+
- **Virtual environment** (venv or conda)
- **Dependencies**: listed in `requirements.txt` (requests, BeautifulSoup or selenium, EasyOCR, Pillow, PyYAML, tenacity)

---

### 4. Installation & Setup

```bash
git clone https://github.com/shami-ah/VQA_Dataset.git
cd VQA_Dataset
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### 5. Configuration

**Keyword lists**: one UTF‑8 keyword per line in `scripts/config/keywords_<lang>.txt`.

\*\*Optional \*\*\`\` (to override defaults):

```yaml
ocr:
  resolution_min: 300  # minimum DPI
  languages:
    arabic: 'ar'
    french: 'fr'
scraper:
  timeout: 10          # seconds
  retries: 3
  backoff_factor: 0.5
```

Place `config.yaml` in project root; the pipeline loads overrides automatically.

---

### 6. Pipeline Workflow

1. **Scraping**: language‑agnostic CLI for each source.
2. **OCR Filtering**: dedicated scripts per language (`filter_images_easyocr_<lang>.py`) use EasyOCR and Unicode‑range checks.
3. **Metadata Enrichment**: capture dimensions, format, source URL.
4. **Storage**: raw vs. processed folders; append to `metadata/annotations.json`.

---

### 7. Module Descriptions

- \`\`: wraps a shared `ScraperBase`, downloads images for keywords with rate‑limit handling.
- \`\`: loads raw images, extracts text, filters by Unicode ranges, resolution thresholds.
- \`\`: orchestrates scrapers + filters; supports `--category all|google|bing|...`, multiprocessing, and config overrides.

---

### 8. Usage Examples

- **Google scraper**:

  ```bash
  python scripts/scrapers/image_scraper_google_cli.py \
    --keywords scripts/config/keywords_arabic.txt \
    --save_dir data/raw_google_arabic \
    --images_per_keyword 10
  ```

- **Full Arabic pipeline**:

  ```bash
  python scripts/pipeline_template.py \
    --keywords scripts/config/keywords_arabic.txt \
    --save_dir data/raw_arabic \
    --images_per_keyword 5 \
    --category all
  ```

---

### 9. CLI Reference

| Script                            | Flags                                              | Description                        | Defaults                                 | Example Invocation                                                       |
| --------------------------------- | -------------------------------------------------- | ---------------------------------- | ---------------------------------------- | ------------------------------------------------------------------------ |
| `image_scraper_google_cli.py`     | `--keywords`, `--save_dir`, `--images_per_keyword` | Google image scraping              | `--images_per_keyword=10`                | see Usage Examples                                                       |
| `image_scraper_bing_cli.py`       | same as above                                      | Bing image scraping                |                                          |                                                                          |
| `image_scraper_duckduckgo_cli.py` | same as above                                      | DuckDuckGo scraping                |                                          |                                                                          |
| `image_scraper_pinterest_cli.py`  | same as above                                      | Pinterest scraping                 |                                          |                                                                          |
| `filter_images_easyocr_<lang>.py` | `--input_dir`, `--output_dir`, `--config`          | OCR‑filter for `<lang>`            | resolution\_min, languages from `config` | `python filter_images_easyocr_arabic.py --input_dir data/raw_arabic ...` |
| `pipeline_template.py`            | all above + `--category`                           | Unified scrape + filter + annotate | category=`all`                           | see Usage Examples                                                       |

---

### 10. Sample Outputs

- **Directory structure** (after run):

  ```
  data/
    raw_arabic/
      img_001.jpg
      img_002.jpg
    processed_arabic/
      img_001.jpg
  ```

- \`\` snippet:

  ```json
  [
    {
      "image_id": "edu_001",
      "image_path": "data/processed_arabic/img_001.jpg",
      "domain": "education",
      "language": "ar",
      "image_metadata": {"width": 1024, "height": 768, "format": "JPEG"},
      "ocr_text": "مخطط توضيحي لقواعد اللغة"
    }
  ]
  ```

---

### 11. Error Handling & Troubleshooting

- **EasyOCR hangs**: enable `--timeout` or process images in batches.
- **HTTP 429**: implement exponential backoff (`tenacity` recommended).
- **Encoding issues**: ensure keyword files are UTF‑8; convert with `iconv` if necessary.
- **Missing fonts**: install language fonts (e.g. `fonts-arabic` on Linux) for better OCR accuracy.

---

### 12. Testing & CI

- **Unit tests**: located in `tests/`, covering scraper logic, filter functions, and metadata parsing.
- **Running tests**:
  ```bash
  pytest --maxfail=1 --disable-warnings -q
  ```
- **GitHub Actions** (`.github/workflows/ci.yml`):
  1. checkout + setup Python
  2. install deps + lint (Black, Flake8)
  3. run unit tests
  4. build and publish docs to GitHub Pages

---

### 13. Contribution Guidelines

See `CONTRIBUTING.md` for:

- Branching model (Git Flow)
- Code style (Black, isort)
- PR and issue templates
- Review checklist (tests, docs, type hints)

---

### 14. Diagrams & Roadmap

- **Pipeline Flowchart**: included in `docs/images/pipeline_flow.png` (or ASCII in docs).
- **Phase 2 Roadmap**: deduplication, multilingual OCR expansion (CJK, Urdu, Hindi), automated VQA question generation.

---

### 15. Contact

- **Maintainer**: @shami-ah (GitHub), email: `iamshami1996@gmail.com`.
- **Issues & Feature Requests**: use GitHub Issues.