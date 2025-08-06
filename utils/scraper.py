import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from pathlib import Path
import os

class SimpleWebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def scrape_product(self, url):
        """Scrape basic product info from URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic info
            title = self._extract_title(soup)
            price = self._extract_price(soup)
            images = self._extract_images(soup, url)
            description = self._extract_description(soup)
            
            return {
                "url": url,
                "title": title,
                "price": price,
                "images": images[:3],  # Limit to 3 images
                "description": description
            }
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def _extract_title(self, soup):
        """Extract product title"""
        # Try multiple selectors
        selectors = [
            'h1',
            '[data-testid="product-title"]',
            '.product-title',
            '.pdp-product-name',
            'title',
            '[class*="title"]',
            '[class*="name"]',
            'h2'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                title = element.get_text(strip=True)
                # Clean up title (remove extra whitespace, limit length)
                title = re.sub(r'\s+', ' ', title)
                return title[:100] if len(title) > 100 else title
        
        return "Unknown Product"
    
    def _extract_price(self, soup):
        """Extract product price"""
        # Look for price patterns
        price_selectors = [
            '[data-testid="price"]',
            '.price',
            '.current-price',
            '.sale-price',
            '.product-price',
            '[class*="price"]',
            '[id*="price"]'
        ]
        
        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                # Extract price with regex
                price_match = re.search(r'[\$€£¥][\d,]+\.?\d*', price_text)
                if price_match:
                    return price_match.group()
        
        # Fallback: search for price patterns in all text
        all_text = soup.get_text()
        price_pattern = re.search(r'[\$€£¥][\d,]+\.?\d*', all_text)
        if price_pattern:
            return price_pattern.group()
        
        return "Price not found"
    
    def _extract_images(self, soup, base_url):
        """Extract product images"""
        images = []
        
        # Common image selectors
        img_selectors = [
            'img[data-testid*="product"]',
            'img[alt*="product"]',
            '.product-image img',
            '.gallery img',
            'img[src*="product"]',
            'img[class*="product"]',
            'picture img',
            '.hero img'
        ]
        
        for selector in img_selectors:
            img_elements = soup.select(selector)
            for img in img_elements:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src:
                    # Convert relative URLs to absolute
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = urljoin(base_url, src)
                    
                    if self._is_valid_image_url(src):
                        images.append(src)
                        if len(images) >= 3:  # Limit to 3 images
                            break
            if len(images) >= 3:
                break
        
        # If no images found with specific selectors, try general img tags
        if not images:
            all_imgs = soup.find_all('img')
            for img in all_imgs:
                src = img.get('src') or img.get('data-src')
                if src and self._is_valid_image_url(src):
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = urljoin(base_url, src)
                    
                    # Filter out small images (likely icons)
                    width = img.get('width')
                    height = img.get('height')
                    if width and height:
                        try:
                            if int(width) > 100 and int(height) > 100:
                                images.append(src)
                                if len(images) >= 3:
                                    break
                        except:
                            images.append(src)
                            if len(images) >= 3:
                                break
                    else:
                        images.append(src)
                        if len(images) >= 3:
                            break
        
        return images
    
    def _extract_description(self, soup):
        """Extract product description"""
        desc_selectors = [
            '[data-testid="product-description"]',
            '.product-description',
            '.description',
            '.product-details',
            '[class*="description"]',
            '[class*="detail"]'
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                desc = element.get_text(strip=True)
                # Clean up description
                desc = re.sub(r'\s+', ' ', desc)
                return desc[:300] + "..." if len(desc) > 300 else desc
        
        # Fallback: try to find any paragraph with meaningful content
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 50:  # Likely to be a description
                text = re.sub(r'\s+', ' ', text)
                return text[:300] + "..." if len(text) > 300 else text
        
        return "No description available"
    
    def _is_valid_image_url(self, url):
        """Check if URL points to a valid image"""
        if not url:
            return False
        
        # Check for image extensions
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        url_lower = url.lower()
        
        # Direct extension check
        if any(ext in url_lower for ext in image_extensions):
            return True
        
        # Check for image-related keywords in URL
        image_keywords = ['image', 'img', 'photo', 'picture', 'product']
        if any(keyword in url_lower for keyword in image_keywords):
            return True
        
        return False
    
    def download_image(self, image_url, save_path):
        """Download image from URL"""
        try:
            response = requests.get(image_url, headers=self.headers, timeout=10, stream=True)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return save_path
            
        except Exception as e:
            print(f"Error downloading image {image_url}: {e}")
            return None