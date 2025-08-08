import os
import requests
from duckduckgo_search import DDGS
from PIL import Image
from io import BytesIO
from tqdm import tqdm

SAVE_DIR = "data/raw_images"
MAX_IMAGES = 3000
IMAGES_PER_KEYWORD = 100

keywords = [
    "بطاقات تعليمية", "أنشطة مدرسية مصورة", "خريطة ذهنية", "شرح دروس مصور", "ورقة عمل بالعربية",
    "رسومات تعليمية بالعربية", "تمرين محلول بالرسم", "شروحات بلغة عربية", "تصميم تعليمي بالعربية",
    "بطاقات الإملاء المصورة", "شرح القواعد بالكاريكاتير", "أنشطة التعلم الذاتي المرئية",
    "خرائط المفاهيم الرقمية", "دروس الواقع المعزز", "تصميم الخطوط العربية", "زخرفة نصوص قديمة",
    "بوسترات كاليغرافيا حديثة", "نصوص متحركة بالعربية", "تصميم الشعارات النصية", "نماذج جوازات سفر",
    "شهادات مطبوعة", "فواتير كهرباء", "إعلانات قانونية", "تذاكر أحداث", "واجهات قواعد البيانات"
]

os.makedirs(SAVE_DIR, exist_ok=True)
index = 0

with DDGS() as ddgs:
    for keyword in tqdm(keywords, desc="🔍 Scraping Keywords"):
        try:
            results = ddgs.images(keyword, max_results=IMAGES_PER_KEYWORD)
            for r in results:
                if index >= MAX_IMAGES:
                    break
                url = r.get("image")
                if not url or not url.lower().endswith((".jpg", ".jpeg", ".png")):
                    continue

                try:
                    response = requests.get(url, timeout=10)
                    img = Image.open(BytesIO(response.content)).convert("RGB")
                    filename = f"{index:05d}.jpg"
                    img.save(os.path.join(SAVE_DIR, filename))
                    index += 1
                except:
                    continue
        except Exception as e:
            print(f"⚠️ {keyword} skipped: {e}")
        if index >= MAX_IMAGES:
            break

print(f"\n✅ Scraping completed. Total images saved: {index}")