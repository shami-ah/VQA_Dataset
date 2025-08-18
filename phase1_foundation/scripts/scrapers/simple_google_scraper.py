#!/usr/bin/env python3
"""
Simple, robust Google Images scraper using requests + BeautifulSoup.

This is a fallback scraper that doesn't require Selenium and works by parsing
Google Images search results directly. It's more reliable but may get fewer images.
"""

import os
import re
import time
import random
import requests
from urllib.parse import quote_plus, urljoin
from typing import List, Optional
from bs4 import BeautifulSoup
import json

# Configure logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SimpleGoogleImageScraper:
    """Simple Google Images scraper using requests and BeautifulSoup."""
    
    def __init__(self):
        """Initialize the scraper."""
        self.session = requests.Session()
        
        # Set up session with good headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def search_images(self, query: str, max_images: int = 20) -> List[str]:
        """Search for images using Google Images.
        
        Args:
            query: Search query
            max_images: Maximum number of images to find
            
        Returns:
            List of image URLs
        """
        logger.info(f"Searching for: '{query}'")
        
        try:
            # Construct search URL
            encoded_query = quote_plus(query)
            search_url = f"https://www.google.com/search?q={encoded_query}&tbm=isch&hl=en&safe=off"
            
            # Make request
            logger.debug(f"Requesting: {search_url}")
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            # Add delay to be respectful
            time.sleep(random.uniform(1, 3))
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract image URLs using multiple methods
            image_urls = []
            
            # Method 1: Look for JSON data in script tags
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string and 'AF_initDataCallback' in script.string:
                    try:
                        # Extract JSON data
                        script_content = script.string
                        
                        # Look for image URLs in the JSON
                        url_pattern = r'https?://[^\s",\]]+\.(?:jpg|jpeg|png|webp|gif)'
                        urls = re.findall(url_pattern, script_content, re.IGNORECASE)
                        
                        for url in urls:
                            if self._is_valid_image_url(url):
                                clean_url = self._clean_url(url)
                                if clean_url and clean_url not in image_urls:
                                    image_urls.append(clean_url)
                                    if len(image_urls) >= max_images:
                                        break
                    except Exception as e:
                        logger.debug(f"Error parsing script tag: {e}")
                        continue
            
            # Method 2: Look for img tags (backup method)
            if len(image_urls) < max_images:
                img_tags = soup.find_all('img')
                for img in img_tags:
                    if len(image_urls) >= max_images:
                        break
                    
                    # Try different src attributes
                    src = img.get('data-src') or img.get('src') or img.get('data-iurl')
                    if src and self._is_valid_image_url(src):
                        clean_url = self._clean_url(src)
                        if clean_url and clean_url not in image_urls:
                            image_urls.append(clean_url)
            
            logger.info(f"Found {len(image_urls)} image URLs for '{query}'")
            return image_urls[:max_images]
            
        except Exception as e:
            logger.error(f"Error searching for images: {e}")
            return []
    
    def _is_valid_image_url(self, url: str) -> bool:
        """Check if URL looks like a valid image URL."""
        if not url or len(url) < 20:
            return False
        
        # Skip data URLs, google's own assets, etc.
        skip_patterns = [
            'data:', 'blob:', 'javascript:',
            'gstatic.com', 'googleusercontent.com/gadgets',
            'google.com/images/branding',
            'encrypted-tbn0'
        ]
        
        for pattern in skip_patterns:
            if pattern in url.lower():
                return False
        
        # Must be HTTP(S)
        if not url.startswith(('http://', 'https://')):
            return False
        
        # Should look like an image URL
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        url_lower = url.lower()
        
        # Either has image extension or is from a known image hosting service
        has_extension = any(ext in url_lower for ext in image_extensions)
        is_image_host = any(host in url_lower for host in [
            'imgur.com', 'wikimedia.org', 'unsplash.com', 'pexels.com',
            'flickr.com', 'shutterstock.com', 'istockphoto.com'
        ])
        
        return has_extension or is_image_host
    
    def _clean_url(self, url: str) -> Optional[str]:
        """Clean and validate URL."""
        if not url:
            return None
        
        # Handle relative URLs
        if url.startswith('//'):
            url = 'https:' + url
        elif url.startswith('/'):
            return None  # Skip relative URLs
        
        # Remove some URL parameters that might cause issues
        if '&amp;' in url:
            url = url.replace('&amp;', '&')
        
        # Decode HTML entities
        url = url.replace('%3A', ':').replace('%2F', '/')
        
        return url if len(url) < 2048 else None  # Skip very long URLs


def test_simple_scraper():
    """Test the simple scraper."""
    scraper = SimpleGoogleImageScraper()
    
    test_queries = ["cat", "dog", "education poster"]
    
    for query in test_queries:
        print(f"\n🔎 Testing query: '{query}'")
        urls = scraper.search_images(query, max_images=5)
        
        print(f"✅ Found {len(urls)} URLs")
        for i, url in enumerate(urls[:3], 1):
            print(f"   {i}. {url[:80]}...")
        
        if not urls:
            print("⚠️  No URLs found")
        
        # Small delay between queries
        time.sleep(2)


if __name__ == "__main__":
    test_simple_scraper()