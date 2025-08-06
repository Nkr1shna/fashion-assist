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
        """Scrape basic product info from URL with enhanced context extraction"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic info
            title = self._extract_title(soup)
            price = self._extract_price(soup)
            images = self._extract_images(soup, url)
            description = self._extract_description(soup)
            
            # Extract additional context from URL and page
            context = self._extract_context(url, soup, title, description)
            
            return {
                "url": url,
                "title": title,
                "price": price,
                "images": images,
                "description": description,
                "context": context
            }
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def _extract_context(self, url, soup, title, description):
        """Extract additional context from URL and page content"""
        context = {
            "brand": "Unknown",
            "category_hints": [],
            "color_hints": [],
            "material_hints": [],
            "style_hints": []
        }
        
        # Extract brand from URL
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc.lower()
            if 'akindofguise' in domain:
                context["brand"] = "A Kind of Guise"
            elif 'zara' in domain:
                context["brand"] = "Zara"
            elif 'hm' in domain or 'h&m' in domain:
                context["brand"] = "H&M"
            elif 'uniqlo' in domain:
                context["brand"] = "Uniqlo"
            else:
                # Try to extract brand from title or page
                brand_element = soup.select_one('[class*="brand"], [data-brand], .designer, .brand-name')
                if brand_element:
                    context["brand"] = brand_element.get_text(strip=True)
        except:
            pass
        
        # Extract category hints from URL path
        url_lower = url.lower()
        category_keywords = {
            'shirt': ['shirt', 'blouse', 'top'],
            'pants': ['pants', 'trousers', 'jeans', 'denim'],
            'dress': ['dress', 'gown'],
            'jacket': ['jacket', 'blazer', 'coat', 'outerwear'],
            'shoes': ['shoes', 'sneakers', 'boots', 'sandals'],
            'skirt': ['skirt'],
            'sweater': ['sweater', 'jumper', 'pullover', 'knit'],
            'accessories': ['bag', 'belt', 'hat', 'scarf', 'jewelry']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in url_lower for keyword in keywords):
                context["category_hints"].append(category)
        
        # Extract hints from title and description
        combined_text = f"{title} {description}".lower()
        
        # Color hints
        color_keywords = [
            'black', 'white', 'red', 'blue', 'green', 'yellow', 'orange', 
            'purple', 'pink', 'brown', 'gray', 'grey', 'navy', 'beige',
            'cream', 'ivory', 'tan', 'burgundy', 'maroon', 'turquoise',
            'rose', 'florale', 'floral'
        ]
        
        for color in color_keywords:
            if color in combined_text:
                context["color_hints"].append(color)
        
        # Material hints
        material_keywords = [
            'cotton', 'linen', 'silk', 'wool', 'cashmere', 'polyester',
            'denim', 'leather', 'suede', 'velvet', 'satin', 'chiffon',
            'jacquard', 'jersey', 'fleece', 'corduroy'
        ]
        
        for material in material_keywords:
            if material in combined_text:
                context["material_hints"].append(material)
        
        # Style hints
        style_keywords = [
            'casual', 'formal', 'business', 'elegant', 'sporty', 'vintage',
            'modern', 'classic', 'bohemian', 'minimalist', 'oversized',
            'fitted', 'relaxed', 'tailored', 'loose'
        ]
        
        for style in style_keywords:
            if style in combined_text:
                context["style_hints"].append(style)
        
        return context
    
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
        """Extract product images with smart filtering"""
        images = []
        product_title = self._extract_title(soup).lower()
        
        # Enhanced product image selectors (priority order)
        priority_selectors = [
            # High priority - specific product selectors
            'img[data-testid*="product"]',
            'img[alt*="product"]',
            '.product-image img',
            '.product-gallery img',
            '.gallery img',
            '[class*="product"] img',
            '[id*="product"] img',
            
            # Medium priority - common e-commerce patterns
            '.hero img',
            '.main-image img',
            '.primary-image img',
            'picture img',
            '.carousel img',
            '.slider img',
            
            # Shopify/common platform specific
            '[data-zoom] img',
            '.featured-image img',
            '[class*="media"] img'
        ]
        
        # Try priority selectors first
        for selector in priority_selectors:
            img_elements = soup.select(selector)
            for img in img_elements:
                src = self._get_image_src(img, base_url)
                if src and self._is_product_image(img, src, product_title):
                    images.append(src)
                    if len(images) >= 5:  # Get more candidates for validation
                        break
            if len(images) >= 5:
                break
        
        # If still no images, try broader search with stricter filtering
        if len(images) < 2:
            all_imgs = soup.find_all('img')
            for img in all_imgs:
                src = self._get_image_src(img, base_url)
                if src and self._is_product_image(img, src, product_title, strict=True):
                    images.append(src)
                    if len(images) >= 5:
                        break
        
        # Remove duplicates while preserving order
        unique_images = []
        seen_urls = set()
        for img_url in images:
            # Normalize URL for comparison (remove query params for deduplication)
            clean_url = img_url.split('?')[0]
            if clean_url not in seen_urls:
                seen_urls.add(clean_url)
                unique_images.append(img_url)
        
        return unique_images[:3]  # Return top 3 candidates
    
    def _get_image_src(self, img, base_url):
        """Extract and normalize image source URL"""
        src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original')
        
        if not src:
            return None
            
        # Convert relative URLs to absolute
        if src.startswith('//'):
            src = 'https:' + src
        elif src.startswith('/'):
            src = urljoin(base_url, src)
        elif not src.startswith('http'):
            src = urljoin(base_url, src)
            
        return src if self._is_valid_image_url(src) else None
    
    def _is_product_image(self, img, src, product_title, strict=False):
        """Determine if an image is likely a product image"""
        if not src or not self._is_valid_image_url(src):
            return False
        
        # Get image attributes
        alt_text = (img.get('alt') or '').lower()
        class_name = (img.get('class') or [])
        if isinstance(class_name, list):
            class_name = ' '.join(class_name).lower()
        else:
            class_name = str(class_name).lower()
        
        # Size filtering - product images are usually larger
        width = img.get('width')
        height = img.get('height')
        if width and height:
            try:
                w, h = int(width), int(height)
                if w < 150 or h < 150:  # Too small for product image
                    return False
                if w > 2000 or h > 2000:  # Probably too large/banner
                    return False
            except:
                pass
        
        # Exclude obvious non-product images
        exclude_patterns = [
            'logo', 'icon', 'badge', 'banner', 'header', 'footer',
            'social', 'facebook', 'instagram', 'twitter', 'nav',
            'menu', 'search', 'cart', 'checkout', 'payment',
            'shipping', 'return', 'warranty', 'care', 'size-guide'
        ]
        
        exclude_in_url = [
            'logo', 'icon', 'badge', 'banner', 'social', 'nav',
            'menu', 'header', 'footer', 'thumb', 'avatar'
        ]
        
        # Check for exclusion patterns
        text_to_check = f"{alt_text} {class_name}".lower()
        url_to_check = src.lower()
        
        for pattern in exclude_patterns:
            if pattern in text_to_check:
                return False
                
        for pattern in exclude_in_url:
            if pattern in url_to_check:
                return False
        
        # In strict mode, be more selective
        if strict:
            # Must have some product-related indicators
            product_indicators = [
                'product', 'item', 'main', 'primary', 'hero',
                'gallery', 'zoom', 'large', 'detail'
            ]
            
            has_product_indicator = any(
                indicator in text_to_check or indicator in url_to_check
                for indicator in product_indicators
            )
            
            if not has_product_indicator:
                return False
        
        # Positive signals for product images
        positive_signals = [
            'product' in text_to_check,
            'main' in text_to_check,
            'hero' in text_to_check,
            'primary' in text_to_check,
            'gallery' in text_to_check,
            any(word in alt_text for word in product_title.split() if len(word) > 3),
            'zoom' in class_name,
            'featured' in class_name
        ]
        
        # Boost score if we have positive signals
        score = sum(positive_signals)
        
        return score > 0 or not strict
    
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
    
    def download_and_validate_images(self, product_data, fashion_clip=None, llm_validator=None):
        """Download images and validate them using Fashion-CLIP + LLM semantic validation"""
        validated_images = []
        
        if not product_data.get("images"):
            return []
        
        # Create directory for this product
        import hashlib
        url_hash = hashlib.md5(product_data["url"].encode()).hexdigest()[:8]
        base_path = f"data/scraped/{url_hash}"
        os.makedirs(base_path, exist_ok=True)
        
        # First pass: Download images and get Fashion-CLIP analysis
        images_with_analysis = []
        
        for i, img_url in enumerate(product_data["images"]):
            img_path = os.path.join(base_path, f"image_{i}.jpg")
            
            # Download image
            downloaded_path = self.download_image(img_url, img_path)
            if not downloaded_path:
                continue
            
            # Get Fashion-CLIP analysis
            analysis = {}
            if fashion_clip:
                analysis = fashion_clip.categorize_item(downloaded_path)
            
            images_with_analysis.append({
                "path": downloaded_path,
                "url": img_url,
                "analysis": analysis
            })
        
        # Second pass: Use LLM to validate semantic consistency
        if llm_validator and images_with_analysis:
            print("🧠 Running LLM semantic validation...")
            validated_images = llm_validator.validate_image_batch(images_with_analysis, product_data)
        else:
            # Fallback to basic Fashion-CLIP validation
            for img_data in images_with_analysis:
                analysis = img_data.get("analysis", {})
                validation_score = analysis.get("confidence", 0.5)
                
                validated_images.append({
                    **img_data,
                    "validation_score": validation_score,
                    "is_valid": validation_score > 0.3,
                    "llm_validation": {"reason": "LLM not available", "overall_match": True}
                })
            
            # Sort by validation score
            validated_images.sort(key=lambda x: x.get("validation_score", 0), reverse=True)
        
        return validated_images
    
    def _validate_image_with_fashionclip(self, image_path, product_data, fashion_clip):
        """Validate if image matches product description using Fashion-CLIP"""
        try:
            # Get Fashion-CLIP analysis of the image
            analysis = fashion_clip.categorize_item(image_path)
            
            # Extract expected attributes from product data
            context = product_data.get("context", {})
            title = product_data.get("title", "").lower()
            description = product_data.get("description", "").lower()
            
            validation_score = 0.0
            
            # Check category match
            predicted_category = analysis.get("category", "").lower()
            category_hints = context.get("category_hints", [])
            
            if category_hints:
                if predicted_category in category_hints:
                    validation_score += 0.4
                elif any(hint in predicted_category for hint in category_hints):
                    validation_score += 0.2
            
            # Check if category appears in title/description
            category_keywords = ['shirt', 'pants', 'dress', 'jacket', 'shoes', 'skirt', 'sweater']
            title_categories = [cat for cat in category_keywords if cat in title]
            
            if title_categories:
                if predicted_category in title_categories:
                    validation_score += 0.3
                elif any(cat in predicted_category for cat in title_categories):
                    validation_score += 0.15
            
            # Check color match
            predicted_color = analysis.get("color", "").lower()
            color_hints = context.get("color_hints", [])
            
            if color_hints:
                if predicted_color in color_hints:
                    validation_score += 0.2
                elif any(hint in predicted_color for hint in color_hints):
                    validation_score += 0.1
            
            # Check style consistency
            predicted_style = analysis.get("style", "").lower()
            style_hints = context.get("style_hints", [])
            
            if style_hints:
                if predicted_style in style_hints:
                    validation_score += 0.1
                elif any(hint in predicted_style for hint in style_hints):
                    validation_score += 0.05
            
            # Bonus for high confidence
            confidence = analysis.get("confidence", 0.0)
            if confidence > 0.8:
                validation_score += 0.1
            elif confidence > 0.6:
                validation_score += 0.05
            
            return min(validation_score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            print(f"Error validating image with Fashion-CLIP: {e}")
            return 0.5  # Default score on error