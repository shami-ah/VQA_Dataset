# 🧠 VQA Dataset Project

This project aims to build a **multilingual, multimodal Visual Question Answering (VQA) dataset** — enriched with semantic image-text pairs across diverse domains (medicine, education, environment, culture, etc.).

The pipeline integrates smart scraping, OCR-based filtering, and scalable metadata generation. The long-term goal is to serve robust training data for VQA and foundational vision-language models.

---

## 🌍 Vision & Scope

- **Multilingual**: Starting with Arabic, expanding to Korean, Chinese, Japanese, Urdu, and others.
- **Multisource**: Scraping from Google, Bing, Pinterest, DuckDuckGo, academic sites, forums, and government repositories.
- **Multimodal**: Future integration of video, audio, and text layers.
- **Human-in-the-loop**: Final manual review and curation phase.
- **Scalable**: Modular pipeline (CLI-based) deployable via VS Code or Google Colab Pro+.

---

## 🔁 End-to-End Pipeline

1. **Scrape Images**  
   - Sources: DuckDuckGo, Bing, Google, Pinterest  
   - Language-aware search with curated keyword lists  
   - Custom scripts for each source

2. **OCR Filtering (EasyOCR)**  
   - Arabic-only filter using Unicode ranges  
   - Quality check (low-res image drop planned)

3. **Metadata Enrichment**  
   - Each image is annotated with source, dimensions, and extracted text  
   - Deduplication via hash/SSIM (coming soon)

4. **Packaging & Delivery**  
   - Zipped outputs with image + `annotations.json`  
   - Google Drive sync for client access

---

## 🧠 Project Structure
vqa_dataset_project/
├── data/
│   ├── raw_[source]               # Raw images from each source (bing, pinterest, etc.)
│   └── processed_[source]         # OCR-filtered Arabic images
├── metadata/
│   └── annotations.json           # OCR-based text + image metadata
├── scripts/
│   ├── image_scraper_[source].py  # Individual scrapers for sources
│   ├── filter_images_easyocr.py   # Arabic image filtering with EasyOCR
│   ├── pipeline_template.py       # Full pipeline automation
├── scripts/config/
│   └── keywords_[lang].txt        # Language-specific keyword lists
├── qa_data/
│   └── [domain]_[subdomain].jsonl # Future VQA question generation
└── README.md

---

## 📄 JSONL Output Format (Planned)

Each image will include metadata + 5 diverse VQA questions:

```json
{
  "image_id": "edu_005",
  "image_path": "data/processed_google/edu_005.jpg",
  "domain": "education",
  "subdomain": "infographics",
  "language": "ar",
  "image_metadata": {
    "width": 800,
    "height": 600,
    "format": "JPEG"
  },
  "ocr_text": "مخطط تعليمي لشرح قواعد اللغة",
  "questions": [
    {
      "question": "ما نوع القاعدة النحوية الموضحة؟",
      "answer": "قاعدة الجملة الاسمية",
      "type": "grammar_explanation"
    }
    // ... 4 more diverse question types
  ]
}

🔮 Future Directions
	•	⚙️ Full automation: Language-wise pipelines with CLI arguments
	•	🧹 Image deduplication: Hashing + SSIM + perceptual comparison
	•	🗂️ Taxonomy-driven storage: Domain/subdomain-based organization
	•	🔡 Multilingual OCR: Extended support for CJK, Urdu, Hindi
	•	📦 Data lake architecture: Eventually integrating ETL pipelines and a warehouse

⸻

🚀 Run Locally
	1.	Install requirements:
pip install -r requirements.txt
	2.	Run a test pipeline:
python3 scripts/pipeline_template.py \
  --keywords scripts/config/keywords_arabic.txt \
  --max_images 10 \
  --images_per_keyword 5 \
  --save_dir data/raw_google_test \
  --filtered_dir data/processed_google_test
🤝 Credits

Maintained by @shami-ah
