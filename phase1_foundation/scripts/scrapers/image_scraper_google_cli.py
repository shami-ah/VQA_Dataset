#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import hashlib
import html
import logging
import os
import random
import re
import sys
import time
from io import BytesIO
from pathlib import Path
from typing import Iterable, List, Set
from urllib.parse import unquote, urlparse, parse_qs

import requests
from PIL import Image
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

LOG = logging.getLogger("google_scraper")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ---- Hardcoded defaults to keep behavior stable in your pipeline ----
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
]
GOOGLE_DOMAIN = "www.google.com"   # hardcoded domain
REQUEST_TIMEOUT = 25               # seconds
MAX_PAGES = 6                      # per query
SLEEP_PAGE = (1.0, 2.0)            # between page fetches
SLEEP_DL = (0.4, 1.0)              # between downloads
MIN_DIM = 120                      # min width/height
MAX_BYTES = 30_000_000             # ~30MB cap per file
SKIP_DOMAINS = (
    "gstatic.com",
    "googleusercontent.com",
    "google.com/images/",
    "encrypted-tbn0.gstatic.com",
)
IMG_EXTS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tif", ".tiff")

# ---------------- core helpers ----------------
def build_session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=4, connect=4, read=4,
        backoff_factor=1.2,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "HEAD"]),
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=20)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    s.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
        "Upgrade-Insecure-Requests": "1",
        "DNT": "1",
        # close sockets to avoid the occasional hang on keep-alive
        "Connection": "close",
    })
    # Set consent cookie to reduce consent interstitials
    s.cookies.set("CONSENT", "YES+cb", domain=".google.com")
    return s

def sanitize_filename(text: str) -> str:
    return re.sub(r"[^\w\-\.\s]+", "_", text).strip().replace(" ", "_")

def is_sane_url(u: str) -> bool:
    if not u or u.startswith(("data:", "blob:")):
        return False
    low = u.lower()
    if any(bad in low for bad in SKIP_DOMAINS):
        return False
    return low.startswith(("http://", "https://"))

def clean_candidate_url(u: str) -> str:
    u = html.unescape(u)
    u = unquote(u)
    # unwrap Google's imgurl=
    if "imgurl=" in u and "imgrefurl=" in u:
        try:
            qs = parse_qs(urlparse(u).query)
            if "imgurl" in qs and qs["imgurl"]:
                return qs["imgurl"][0]
        except Exception:
            pass
    return u

def looks_like_block(html_text: str) -> bool:
    lower = html_text.lower()
    return (
        "unusual traffic" in lower
        or ("sorry" in lower and "automated queries" in lower)
        or "verify you are a human" in lower
        or "consent.google.com" in lower
    )

def fetch_page(session: requests.Session, url: str, params: dict) -> str:
    # a few short attempts with UA rotation
    for _ in range(3):
        try:
            session.headers.update({"User-Agent": random.choice(USER_AGENTS), "Connection": "close"})
            r = session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            # if redirected to consent once, set cookie and try again immediately
            if "consent.google.com" in r.url:
                session.cookies.set("CONSENT", "YES+cb", domain=".google.com")
                time.sleep(0.6)
                r = session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            txt = r.text
            if looks_like_block(txt):
                time.sleep(random.uniform(1.0, 2.0))
                continue
            return txt
        except Exception:
            time.sleep(random.uniform(0.8, 1.8))
    return ""

def google_images_pages(session: requests.Session, query: str) -> Iterable[str]:
    base = f"https://{GOOGLE_DOMAIN}/search"
    for i in range(MAX_PAGES):
        params = {"q": query, "tbm": "isch", "hl": "en", "safe": "off", "ijn": str(i), "udm": "2", "pws": "0", "source": "lnms"}
        html_text = fetch_page(session, base, params)
        if not html_text:
            break
        yield html_text
        time.sleep(random.uniform(*SLEEP_PAGE))

def extract_image_urls(html_text: str) -> List[str]:
    urls: List[str] = []
    # JSON "ou"
    for m in re.finditer(r'"ou":"(http[^"]+)"', html_text):
        urls.append(m.group(1))
    # ["http...jpg",W,H]
    for m in re.finditer(r'\["(http[^"]+?)",\d+,\d+\]', html_text):
        urls.append(m.group(1))
    # imgurl= links
    for m in re.finditer(r'imgurl=(http[^&"]+)', html_text):
        urls.append(m.group(1))
    # conservative <img src="...">
    for m in re.finditer(r'<img[^>]+src="(http[^">]+)"', html_text):
        urls.append(m.group(1))

    cleaned: List[str] = []
    seen: Set[str] = set()
    for u in urls:
        u = clean_candidate_url(u)
        if not is_sane_url(u):
            continue
        if u in seen:
            continue
        seen.add(u)
        cleaned.append(u)
    return cleaned

def sniff_extension_from_ct(content_type: str) -> str:
    if not content_type:
        return ""
    ct = content_type.lower()
    if "jpeg" in ct: return ".jpg"
    if "png"  in ct: return ".png"
    if "gif"  in ct: return ".gif"
    if "webp" in ct: return ".webp"
    if "bmp"  in ct: return ".bmp"
    if "tiff" in ct or "tif" in ct: return ".tif"
    return ""

def download_one(session: requests.Session, url: str, out_dir: Path, base_name: str, idx: int) -> bool:
    try:
        # Optional HEAD to weed out huge or non-image responses
        try:
            h = session.head(url, allow_redirects=True, timeout=REQUEST_TIMEOUT)
            ct = h.headers.get("Content-Type", "")
            if ct and not ct.lower().startswith("image/"):
                return False
            if "Content-Length" in h.headers:
                try:
                    if int(h.headers["Content-Length"]) > MAX_BYTES:
                        return False
                except Exception:
                    pass
        except Exception:
            pass

        r = session.get(url, stream=True, timeout=REQUEST_TIMEOUT, headers={"Connection": "close"})
        r.raise_for_status()
        ct = r.headers.get("Content-Type", "")

        buf = BytesIO()
        for chunk in r.iter_content(1024 * 64):
            if not chunk:
                break
            buf.write(chunk)
            if buf.tell() > MAX_BYTES:
                return False

        data = buf.getvalue()
        if len(data) < 1024:
            return False

        # quick hash dedupe inside this run
        digest = hashlib.md5(data).hexdigest()
        hash_dir = out_dir / ".hashes"
        hash_dir.mkdir(parents=True, exist_ok=True)
        hash_file = hash_dir / f"{digest[:2]}.txt"
        if hash_file.exists():
            if digest in hash_file.read_text(encoding="utf-8", errors="ignore").splitlines():
                return False

        try:
            im = Image.open(BytesIO(data))
            im.load()
        except Exception:
            return False

        w, h = im.size
        if w < MIN_DIM or h < MIN_DIM:
            return False

        ext = sniff_extension_from_ct(ct)
        if not ext:
            path = urlparse(url).path.lower()
            for e in IMG_EXTS:
                if path.endswith(e):
                    ext = e
                    break
        if not ext:
            fmt = (im.format or "").lower()
            ext = ".jpg" if fmt in ("", "jpeg") else f".{fmt}"

        safe = sanitize_filename(base_name)
        out_path = out_dir / f"{safe}_{idx:04d}{ext}"

        if ext in (".jpg", ".jpeg") and im.mode in ("RGBA", "P"):
            im = im.convert("RGB")
        with open(out_path, "wb") as f:
            f.write(data)

        with open(hash_file, "a", encoding="utf-8") as hf:
            hf.write(digest + "\n")

        return True
    except Exception:
        return False

def process_query(session: requests.Session, query: str, out_root: Path, images_per_keyword: int) -> int:
    # Flat output: no per-keyword subfolders
    out_root.mkdir(parents=True, exist_ok=True)

    # gather candidates from pages
    collected: List[str] = []
    for html_text in google_images_pages(session, query):
        candidates = extract_image_urls(html_text)
        for u in candidates:
            if u not in collected:
                collected.append(u)
            if len(collected) >= images_per_keyword:
                break
        if len(collected) >= images_per_keyword:
            break

    if not collected:
        LOG.warning("No URLs found for '%s'", query)
        return 0

    LOG.info("Found %d candidate URLs for '%s'", len(collected), query)

    downloaded = 0
    for i, u in enumerate(collected):
        # save directly in out_root; filenames remain like "<keyword>_0000.jpg"
        if download_one(session, u, out_root, query, i):
            downloaded += 1
        time.sleep(random.uniform(*SLEEP_DL))
    return downloaded

# ---------------- CLI (matches your pipeline) ----------------
def main():
    parser = argparse.ArgumentParser(
        description="Google Images scraper (requests-only, no APIs, headless).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--keywords", type=str, required=True, help="Path to keywords file (one query per line)")
    parser.add_argument("--images_per_keyword", type=int, required=True, help="Number of images per keyword")
    parser.add_argument("--save_dir", type=str, required=True, help="Output directory for images")
    args = parser.parse_args()

    kw_path = Path(args.keywords)
    if not kw_path.exists():
        LOG.error("Keywords file not found: %s", kw_path)
        sys.exit(1)

    with open(kw_path, "r", encoding="utf-8") as f:
        queries = [ln.strip() for ln in f if ln.strip()]
    LOG.info("Total queries: %d", len(queries))

    out_root = Path(args.save_dir)
    out_root.mkdir(parents=True, exist_ok=True)

    session = build_session()

    total = 0
    for i, q in enumerate(queries, 1):
        LOG.info("(%d/%d) Query: %s", i, len(queries), q)
        try:
            n = process_query(session, q, out_root, args.images_per_keyword)
            LOG.info("Downloaded %d images for: %s", n, q)
            total += n
            time.sleep(random.uniform(1.0, 2.0))
        except KeyboardInterrupt:
            LOG.warning("Interrupted by user.")
            break
        except Exception as e:
            LOG.error("Query failed '%s': %s", q, e)

    LOG.info("All done. Total images: %d", total)

if __name__ == "__main__":
    main()