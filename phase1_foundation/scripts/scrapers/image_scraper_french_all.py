import os
import argparse
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

FRENCH_SOURCES = {
    "news": [
        "https://www.lemonde.fr/recherche/?search_keywords={}",
        "https://www.lefigaro.fr/recherche?q={}",
        "https://www.20minutes.fr/recherche?q={}",
        "https://www.liberation.fr/recherche/?q={}",
        "https://www.francetvinfo.fr/recherche.html?q={}"
    ],
    "ecommerce": [
        "https://www.laredoute.fr/search?q={}",
        "https://www.cdiscount.com/search/10/{}.html",
        "https://www.fnac.com/SearchResult/ResultList.aspx?SCat=0%211&Search={}",
        "https://www.decathlon.fr/search?Ntt={}",
        "https://www.darty.com/nav/recherche?search={}"
    ],
    "blogs": [
        "https://www.madmoizelle.com/?s={}",
        "https://www.lesnumeriques.com/recherche.html?search={}",
        "https://www.papillesetpupilles.fr/?s={}"
    ],
    "government": [
        "https://www.service-public.fr/recherche?q={}",
        "https://www.gouvernement.fr/recherche?q={}",
        "https://www.insee.fr/fr/recherche/recherche-geographique?champRechercheGeographique={}",
        "https://www.education.gouv.fr/recherche?q={}"
    ]
}

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    return webdriver.Chrome(options=chrome_options)

def save_screenshot(driver, url, save_path):
    try:
        driver.get(url)
        time.sleep(2)
        driver.save_screenshot(save_path)
    except Exception as e:
        print(f"[ERROR] {url}: {e}")

def main(keywords_file, save_dir, images_per_keyword, category):
    os.makedirs(save_dir, exist_ok=True)
    driver = setup_driver()

    with open(keywords_file, 'r', encoding='utf-8') as f:
        keywords = [k.strip() for k in f.readlines() if k.strip()]

    selected_sources = []
    if category == "all":
        for src_list in FRENCH_SOURCES.values():
            selected_sources.extend(src_list)
    else:
        selected_sources = FRENCH_SOURCES.get(category, [])

    for keyword in keywords:
        print(f"[INFO] Searching for: {keyword}")
        for i, url_template in enumerate(selected_sources[:images_per_keyword]):
            url = url_template.format(keyword.replace(" ", "+"))
            save_path = os.path.join(save_dir, f"{keyword.replace(' ', '_')}_{i}.png")
            save_screenshot(driver, url, save_path)

    driver.quit()
    print("[DONE] French scraping complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--keywords", type=str, required=True, help="Path to French keywords .txt")
    parser.add_argument("--save_dir", type=str, required=True, help="Directory to save screenshots")
    parser.add_argument("--images_per_keyword", type=int, default=5, help="How many URLs per keyword")
    parser.add_argument("--category", type=str, default="all", choices=["all", "news", "ecommerce", "blogs", "government"], help="Content category")
    args = parser.parse_args()

    main(args.keywords, args.save_dir, args.images_per_keyword, args.category)