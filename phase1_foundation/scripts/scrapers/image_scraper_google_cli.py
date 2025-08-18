import os
import re
import time
import random
import argparse
import requests
import logging
from urllib.parse import quote_plus, urljoin
from typing import List, Dict, Any, Optional, Set
from PIL import Image
from io import BytesIO
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Try to import webdriver-manager for automatic driver management
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False
    logger.warning("webdriver-manager not available. You may need to manually install ChromeDriver.")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GoogleImageScraper:
    """Advanced Google Images scraper using Selenium with anti-detection measures."""
    
    def __init__(self, headless: bool = True, implicit_wait: int = 10):
        """Initialize the Google Images scraper.
        
        Args:
            headless: Run browser in headless mode
            implicit_wait: Implicit wait time for elements
        """
        self.headless = headless
        self.implicit_wait = implicit_wait
        self.driver = None
        self.scraped_urls: Set[str] = set()
        
        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36'
        ]
    
    def _setup_driver(self) -> webdriver.Chrome:
        """Set up Chrome WebDriver with anti-detection options."""
        options = Options()
        
        if self.headless:
            options.add_argument('--headless=new')
        
        # Anti-detection and performance options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')  # Don't load images in browser for speed
        options.add_argument('--window-size=1920,1080')
        
        # Random user agent
        user_agent = random.choice(self.user_agents)
        options.add_argument(f'--user-agent={user_agent}')
        
        # Disable automation indicators
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Additional preferences
        prefs = {
            "profile.managed_default_content_settings.images": 2,  # Block images
            "profile.default_content_setting_values.notifications": 2,  # Block notifications
        }
        options.add_experimental_option("prefs", prefs)
        
        try:
            # Try to use webdriver-manager for automatic driver management
            if WEBDRIVER_MANAGER_AVAILABLE:
                try:
                    driver = webdriver.Chrome(
                        service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                        options=options
                    )
                except Exception as e:
                    logger.warning(f"webdriver-manager failed: {e}. Trying system ChromeDriver...")
                    driver = webdriver.Chrome(options=options)
            else:
                driver = webdriver.Chrome(options=options)
            
            # Execute script to remove webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set implicit wait
            driver.implicitly_wait(self.implicit_wait)
            
            return driver
            
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            logger.error("Make sure Chrome browser and ChromeDriver are installed")
            logger.error("Install with: pip install webdriver-manager")
            raise
    
    def _human_like_delay(self, min_delay: float = 1.0, max_delay: float = 3.0) -> None:
        """Add human-like random delays."""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _scroll_to_load_images(self, target_count: int) -> None:
        """Scroll page to load more images dynamically."""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        images_found = 0
        scroll_attempts = 0
        max_scroll_attempts = 8
        
        while images_found < target_count and scroll_attempts < max_scroll_attempts:
            # Scroll down in smaller increments
            self.driver.execute_script("window.scrollBy(0, 1000);")
            self._human_like_delay(1, 2)
            
            # Try multiple scroll positions
            for i in range(3):
                self.driver.execute_script("window.scrollBy(0, 800);")
                self._human_like_delay(0.5, 1)
            
            # Wait for new content to load
            self._human_like_delay(2, 3)
            
            # Try to find and click "Show more results" or "See more" button
            try:
                # Multiple possible selectors for the "Show more" button
                button_selectors = [
                    "//input[@value='Show more results']",
                    "//input[@type='button' and contains(@value, 'more')]",
                    "//*[contains(text(), 'Show more')]",
                    "//*[contains(text(), 'See more')]",
                    "//div[@role='button' and contains(text(), 'more')]"
                ]
                
                for selector in button_selectors:
                    try:
                        button = self.driver.find_element(By.XPATH, selector)
                        if button.is_displayed() and button.is_enabled():
                            self.driver.execute_script("arguments[0].click();", button)
                            logger.debug("Clicked 'Show more' button")
                            self._human_like_delay(3, 5)
                            break
                    except (NoSuchElementException, WebDriverException):
                        continue
                        
            except Exception as e:
                logger.debug(f"Could not find/click show more button: {e}")
            
            # Check for new images with multiple selectors
            image_selectors = [
                "img[data-src]",
                "img[src]",
                "img[data-iurl]",
                "div[data-id] img",
                ".rg_i img"
            ]
            
            all_images = []
            for selector in image_selectors:
                try:
                    images = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    all_images.extend(images)
                except Exception:
                    continue
            
            # Remove duplicates and filter valid images
            unique_images = []
            seen_srcs = set()
            for img in all_images:
                try:
                    src = img.get_attribute('data-src') or img.get_attribute('src') or img.get_attribute('data-iurl')
                    if src and src not in seen_srcs and self._is_valid_image_element(img):
                        unique_images.append(img)
                        seen_srcs.add(src)
                except Exception:
                    continue
            
            images_found = len(unique_images)
            
            # Check if page height changed
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
            else:
                scroll_attempts = 0
                last_height = new_height
            
            logger.debug(f"Found {images_found} unique images after scrolling, attempt {scroll_attempts}")
            
            if images_found >= target_count:
                break
    
    def _is_valid_image_element(self, img_element) -> bool:
        """Check if image element is valid for scraping."""
        try:
            # Get image source - try multiple attributes
            src = (img_element.get_attribute('data-src') or 
                  img_element.get_attribute('src') or 
                  img_element.get_attribute('data-iurl') or
                  img_element.get_attribute('data-original'))
            
            if not src:
                return False
            
            # Skip base64 images, icons, and very small images
            if (src.startswith('data:') or 
                'icon' in src.lower() or 
                'logo' in src.lower() or 
                'avatar' in src.lower() or
                'favicon' in src.lower() or
                src.startswith('blob:') or
                len(src) < 10):
                return False
            
            # Skip Google's own UI elements
            if any(pattern in src.lower() for pattern in [
                'gstatic.com',
                'googleusercontent.com/gadgets',
                'google.com/images/branding',
                'encrypted-tbn0',  # Google's thumbnail URLs
            ]):
                return False
            
            # Check image dimensions if available
            width = img_element.get_attribute('width')
            height = img_element.get_attribute('height')
            
            if width and height:
                try:
                    w, h = int(width), int(height)
                    if w < 50 or h < 50:  # Skip very small images
                        return False
                except ValueError:
                    pass
            
            # Check natural dimensions if possible
            try:
                natural_width = img_element.get_attribute('naturalWidth')
                natural_height = img_element.get_attribute('naturalHeight')
                if natural_width and natural_height:
                    nw, nh = int(natural_width), int(natural_height)
                    if nw < 100 or nh < 100:
                        return False
            except (ValueError, TypeError):
                pass
            
            return True
            
        except Exception:
            return False
    
    def _extract_image_urls(self, max_images: int) -> List[str]:
        """Extract image URLs from the current page."""
        # First, scroll to load more images
        self._scroll_to_load_images(max_images * 2)  # Load extra to have options
        
        # Find all image elements with multiple selectors
        image_selectors = [
            "img[data-src]",
            "img[src]", 
            "img[data-iurl]",
            "div[data-id] img",
            ".rg_i img",
            "img[data-original]",
            ".isv-r img"
        ]
        
        all_img_elements = []
        for selector in image_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                all_img_elements.extend(elements)
                logger.debug(f"Found {len(elements)} images with selector: {selector}")
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
        
        # Remove duplicates based on element reference
        unique_elements = list(set(all_img_elements))
        logger.debug(f"Total unique image elements found: {len(unique_elements)}")
        
        image_urls = []
        processed_count = 0
        
        for img_element in unique_elements:
            if len(image_urls) >= max_images:
                break
                
            try:
                if not self._is_valid_image_element(img_element):
                    continue
                
                # Get the image URL - try multiple attributes
                img_url = (img_element.get_attribute('data-src') or 
                          img_element.get_attribute('src') or 
                          img_element.get_attribute('data-iurl') or
                          img_element.get_attribute('data-original'))
                
                if img_url and img_url not in self.scraped_urls:
                    # Clean and validate URL
                    cleaned_url = self._clean_image_url(img_url)
                    if cleaned_url:
                        image_urls.append(cleaned_url)
                        self.scraped_urls.add(cleaned_url)
                        logger.debug(f"Added URL: {cleaned_url[:80]}...")
                        
                processed_count += 1
                
                # Add small delay every few images
                if processed_count % 10 == 0:
                    self._human_like_delay(0.3, 0.7)
                    
            except Exception as e:
                logger.debug(f"Error processing image element: {e}")
                continue
        
        logger.info(f"Extracted {len(image_urls)} valid image URLs from {len(unique_elements)} elements")
        return image_urls
    
    def _clean_image_url(self, url: str) -> Optional[str]:
        """Clean and validate image URL."""
        if not url or url.startswith(('data:', 'blob:')):
            return None
        
        # Handle relative URLs
        if url.startswith('//'):
            url = 'https:' + url
        elif url.startswith('/'):
            url = 'https://www.google.com' + url
        
        # Handle Google's encoded URLs
        if 'imgurl=' in url:
            try:
                # Extract the actual image URL from Google's wrapper
                import urllib.parse
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                if 'imgurl' in parsed:
                    url = parsed['imgurl'][0]
            except Exception:
                pass
        
        # Remove URL parameters that might cause issues (but keep some that are needed)
        if '?' in url and not any(keep in url.lower() for keep in ['imgur.com', 'wikimedia', 'wikipedia']):
            url = url.split('?')[0]
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            return None
        
        # Skip certain domains/file types that are usually not useful
        skip_patterns = [
            'googleusercontent.com/gadgets',
            'gstatic.com',
            'doubleclick.net',
            'google.com/images/branding',
            'encrypted-tbn0.gstatic.com',  # Google thumbnails
        ]
        
        for pattern in skip_patterns:
            if pattern in url.lower():
                return None
        
        # Skip very short URLs or suspicious patterns
        if len(url) < 20:
            return None
        
        return url
    
    def search_images(self, query: str, max_images: int = 20, debug: bool = False) -> List[str]:
        """Search for images on Google Images.
        
        Args:
            query: Search query
            max_images: Maximum number of image URLs to return
            debug: Enable debug mode with extra logging
            
        Returns:
            List of image URLs
        """
        if not self.driver:
            self.driver = self._setup_driver()
        
        try:
            # Construct Google Images search URL
            encoded_query = quote_plus(query)
            search_url = f"https://www.google.com/search?q={encoded_query}&tbm=isch&hl=en"
            
            logger.info(f"Searching Google Images for: '{query}'")
            if debug:
                logger.info(f"Search URL: {search_url}")
            
            # Navigate to search page
            self.driver.get(search_url)
            self._human_like_delay(2, 4)
            
            if debug:
                logger.info(f"Page title: {self.driver.title}")
                logger.info(f"Current URL: {self.driver.current_url}")
                
                # Take screenshot for debugging
                try:
                    screenshot_path = f"debug_screenshot_{query.replace(' ', '_')}.png"
                    self.driver.save_screenshot(screenshot_path)
                    logger.info(f"Debug screenshot saved: {screenshot_path}")
                except Exception as e:
                    logger.debug(f"Could not save screenshot: {e}")
            
            # Handle cookie consent if present
            try:
                consent_selectors = [
                    "//button[contains(text(), 'Accept')]",
                    "//button[contains(text(), 'I agree')]",
                    "//button[contains(text(), 'Accept all')]",
                    "//div[contains(text(), 'Accept')]",
                    "//form//button[@type='submit']"
                ]
                
                for selector in consent_selectors:
                    try:
                        consent_button = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        consent_button.click()
                        logger.debug("Clicked consent button")
                        self._human_like_delay(1, 2)
                        break
                    except TimeoutException:
                        continue
                        
            except Exception as e:
                logger.debug(f"No consent dialog or error handling it: {e}")
            
            # Wait a bit more for the page to fully load
            self._human_like_delay(3, 5)
            
            # Extract image URLs
            image_urls = self._extract_image_urls(max_images)
            
            if debug and not image_urls:
                # Debug information when no images found
                logger.warning("No images found. Debugging information:")
                
                # Check if we're on the right page
                page_source_snippet = self.driver.page_source[:1000]
                logger.debug(f"Page source snippet: {page_source_snippet}")
                
                # Check for various error indicators
                if "blocked" in self.driver.page_source.lower():
                    logger.warning("Page content suggests request may be blocked")
                
                # Try to find any img elements at all
                all_imgs = self.driver.find_elements(By.TAG_NAME, "img")
                logger.debug(f"Total img elements found on page: {len(all_imgs)}")
                
                if all_imgs:
                    sample_src = all_imgs[0].get_attribute('src') if all_imgs else "None"
                    logger.debug(f"Sample img src: {sample_src}")
            
            logger.info(f"Successfully found {len(image_urls)} images for query: '{query}'")
            return image_urls
            
        except Exception as e:
            logger.error(f"Error searching for images with query '{query}': {e}")
            if debug:
                logger.error(f"Debug: Current URL when error occurred: {self.driver.current_url if self.driver else 'No driver'}")
            return []
    
    def close(self):
        """Close the browser driver."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.debug(f"Error closing driver: {e}")
            finally:
                self.driver = None

# Import shared utilities
try:
    from phase1_foundation.scripts.utils.common import (
        sanitize_filename, download_image, load_keywords, 
        validate_directory, ProgressTracker
    )
except ImportError:
    logger.warning("Could not import shared utilities. Using fallback functions.")
    
    def sanitize_filename(filename: str) -> str:
        """Fallback sanitize function."""
        import re
        return re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    def download_image(img_url: str, save_path: str, **kwargs) -> bool:
        """Fallback download function."""
        try:
            response = requests.get(img_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (VQA Dataset Scraper)'
            })
            response.raise_for_status()
            
            img = Image.open(BytesIO(response.content))
            if img.width < 100 or img.height < 100:
                return False
                
            img = img.convert("RGB")
            img.save(save_path, "JPEG", quality=90)
            return True
        except Exception:
            return False

def scrape_images(keywords: List[str], save_dir: str, images_per_keyword: int, 
                 headless: bool = True) -> int:
    """Scrape images from Google Images for given keywords using Selenium.
    
    Args:
        keywords: List of search keywords
        save_dir: Directory to save images
        images_per_keyword: Number of images per keyword
        headless: Run browser in headless mode
        
    Returns:
        Total number of images successfully downloaded
    """
    # Validate and create save directory
    save_path = validate_directory(save_dir, create=True) if 'validate_directory' in globals() else Path(save_dir)
    if not isinstance(save_path, Path):
        save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)
    
    total_downloaded = 0
    scraper = None
    
    try:
        # Initialize the scraper
        scraper = GoogleImageScraper(headless=headless)
        
        # Track progress
        progress = ProgressTracker(len(keywords), "🔎 Scraping Google Images") if 'ProgressTracker' in globals() else None
        
        for i, keyword in enumerate(keywords):
            keyword_downloaded = 0
            
            try:
                logger.info(f"Processing keyword {i+1}/{len(keywords)}: '{keyword}'")
                
                # Search for images
                image_urls = scraper.search_images(keyword, images_per_keyword)
                
                if not image_urls:
                    logger.warning(f"No image URLs found for keyword: {keyword}")
                    continue
                
                # Download images
                safe_keyword = sanitize_filename(keyword)
                
                for j, img_url in enumerate(image_urls):
                    filename = f"{safe_keyword}_{total_downloaded:04d}.jpg"
                    save_file_path = save_path / filename
                    
                    if download_image(img_url, str(save_file_path)):
                        total_downloaded += 1
                        keyword_downloaded += 1
                        
                        # Add small delay between downloads
                        time.sleep(random.uniform(0.5, 1.5))
                    
                    # Respect rate limiting
                    if j > 0 and j % 5 == 0:
                        time.sleep(random.uniform(2, 4))
                
                logger.info(f"Keyword '{keyword}': {keyword_downloaded}/{len(image_urls)} images downloaded")
                
                # Update progress
                if progress:
                    progress.update()
                
                # Add delay between keywords to be respectful
                if i < len(keywords) - 1:  # Don't delay after the last keyword
                    time.sleep(random.uniform(3, 7))
                
            except Exception as e:
                logger.error(f"Error processing keyword '{keyword}': {e}")
                continue
        
        if progress:
            progress.finish()
        
        logger.info(f"✅ Scraping completed. Total images downloaded: {total_downloaded}")
        return total_downloaded
        
    except Exception as e:
        logger.error(f"Fatal error during scraping: {e}")
        return total_downloaded
        
    finally:
        # Always clean up the scraper
        if scraper:
            scraper.close()

def main():
    """Main entry point for the Google image scraper."""
    parser = argparse.ArgumentParser(
        description="🔎 Google Image Scraper for VQA Dataset (API-Free)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--keywords", type=str, required=True, 
                       help="Path to keywords.txt file")
    parser.add_argument("--images_per_keyword", type=int, default=10,
                       help="Number of images to download per keyword")
    parser.add_argument("--save_dir", type=str, default="data/raw_google_test",
                       help="Directory to save downloaded images")
    parser.add_argument("--headless", action="store_true", default=True,
                       help="Run browser in headless mode (default: True)")
    parser.add_argument("--visible", action="store_true",
                       help="Run browser in visible mode (opposite of headless)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Determine headless mode
    headless_mode = args.headless and not args.visible
    
    try:
        # Load keywords using shared utility if available, otherwise fallback
        if 'load_keywords' in globals() and callable(globals()['load_keywords']):
            keywords = load_keywords(args.keywords)
        else:
            # Fallback keyword loading
            if not os.path.exists(args.keywords):
                raise FileNotFoundError(f"Keywords file not found: {args.keywords}")
            
            with open(args.keywords, "r", encoding="utf-8") as f:
                keywords = [line.strip() for line in f if line.strip()]
            
            if not keywords:
                raise ValueError("No valid keywords found in file")
            
            logger.info(f"Loaded {len(keywords)} keywords from {args.keywords}")
        
        # Start scraping
        print(f"\n🚀 Starting Google Images scraping...")
        print(f"📝 Keywords file: {args.keywords}")
        print(f"🎯 Target images per keyword: {args.images_per_keyword}")
        print(f"📁 Save directory: {args.save_dir}")
        print(f"🤖 Headless mode: {'Yes' if headless_mode else 'No'}")
        print(f"📊 Total keywords to process: {len(keywords)}")
        print("="*60)
        
        total_images = scrape_images(
            keywords=keywords, 
            save_dir=args.save_dir, 
            images_per_keyword=args.images_per_keyword,
            headless=headless_mode
        )
        
        print("\n" + "="*60)
        print("🎉 SCRAPING COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"📊 Total images downloaded: {total_images}")
        print(f"📁 Images saved to: {os.path.abspath(args.save_dir)}")
        print(f"⚡ Average images per keyword: {total_images / len(keywords):.1f}")
        
        if total_images == 0:
            print("\n⚠️  No images were downloaded. This could be due to:")
            print("   - Network connectivity issues")
            print("   - Google blocking the scraper")
            print("   - Invalid keywords")
            print("   - Chrome driver issues")
            print("\n💡 Try running with --visible flag to see what's happening")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Scraping interrupted by user")
        print("✅ Partial results have been saved")
        
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        print(f"\n❌ Error: {e}")
        
        if "selenium" in str(e).lower() or "driver" in str(e).lower():
            print("\n🔧 Chrome/ChromeDriver Issues:")
            print("   1. Make sure Chrome browser is installed")
            print("   2. Install ChromeDriver: pip install webdriver-manager")
            print("   3. Or download ChromeDriver manually from https://chromedriver.chromium.org/")
        
        print("\n💡 Troubleshooting tips:")
        print("   - Try running with --visible flag to see browser actions")
        print("   - Check your internet connection")
        print("   - Verify keywords file exists and contains valid keywords")
        print("   - Try with fewer keywords first to test")
        
        exit(1)


if __name__ == "__main__":
    main()