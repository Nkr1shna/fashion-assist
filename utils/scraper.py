import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from pathlib import Path
import os

class SimpleWebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
    
    def scrape_product(self, url):
        """Scrape basic product info from URL with enhanced context extraction"""
        # Try multiple approaches for better compatibility
        approaches = [
            ("enhanced", self.headers),
            ("simple", {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        ]
        
        for approach_name, headers in approaches:
            try:
                import requests
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                
                # Handle encoding properly
                if response.encoding is None:
                    response.encoding = 'utf-8'
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract basic info
                title = self._extract_title(soup)
                price = self._extract_price(soup)
                images = self._extract_images(soup, url)
                description = self._extract_description(soup)
                
                # Check if we got good data
                if title != "Unknown Product" or len(images) > 0:
                    # Extract additional context from URL and page
                    context = self._extract_context(url, soup, title, description)
                    
                    print(f"DEBUG: Successfully scraped {url} using {approach_name} approach")
                    print(f"  Title: {title}")
                    print(f"  Images found: {len(images)}")
                    
                    return {
                        "url": url,
                        "title": title,
                        "price": price,
                        "images": images,
                        "description": description,
                        "context": context
                    }
                else:
                    print(f"DEBUG: {approach_name} approach failed for {url} - trying next")
                    continue
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    print(f"Access denied with {approach_name} approach for {url}: {e}")
                    continue
                else:
                    print(f"HTTP error with {approach_name} approach for {url}: {e}")
                    continue
            except Exception as e:
                print(f"Error with {approach_name} approach for {url}: {e}")
                continue
        
        print(f"ERROR: All approaches failed for {url}")
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
            
            # Shopify specific selectors (used by A Kind of Guise, Aime Leon Dore)
            '.product__media img',
            '.product-media img', 
            '.product-gallery-wrapper img',
            '.product__photo img',
            '[data-media-id] img',
            '.slideshow img',
            '.product-single__photo img',
            
            # A Kind of Guise specific selectors
            '[class*="media"] img',  # Their media gallery
            '[class*="gallery"] img',  # Gallery images
            '[class*="image"] img',   # Image containers
            
            # COS and other modern sites
            '.pdp-image img',
            '.product-details-image img',
            '.product-hero img',
            '[data-testid*="image"] img',
            '[data-cy*="image"] img',
            
            # Medium priority - common e-commerce patterns
            '.hero img',
            '.main-image img',
            '.primary-image img',
            'picture img',
            '.carousel img',
            '.slider img',
            'main img',  # More permissive for modern layouts
            'article img',  # More permissive for modern layouts
            
            # Shopify/common platform specific
            '[data-zoom] img',
            '.featured-image img',
            
            # Next.js and React common patterns
            '[class*="Image"] img',
            '[class*="photo"] img',
            '[data-src] img',
            'img[loading="lazy"]'
        ]
        
        # Try priority selectors first
        for selector in priority_selectors:
            img_elements = soup.select(selector)
            for img in img_elements:
                src = self._get_image_src(img, base_url)
                if src and self._is_product_image(img, src, product_title):
                    images.append(src)
                    if len(images) >= 10:  # Get more candidates for validation
                        break
            if len(images) >= 10:
                break
        
        # If still no images, try broader search with relaxed filtering
        if len(images) < 3:
            all_imgs = soup.find_all('img')
            for img in all_imgs:
                src = self._get_image_src(img, base_url)
                if src and self._is_product_image(img, src, product_title, strict=False):
                    images.append(src)
                    if len(images) >= 10:
                        break
        
        # Remove duplicates while preserving order
        unique_images = []
        seen_urls = set()
        for img_url in images:
            # Normalize URL for comparison (remove query params for deduplication)
            # But keep the highest quality version (with width parameter)
            clean_url = img_url.split('?')[0]
            if clean_url not in seen_urls:
                seen_urls.add(clean_url)
                # Prefer URLs with width parameter for better quality
                if 'width=' in img_url:
                    # Replace any existing entry with this higher quality version
                    unique_images = [url for url in unique_images if not url.split('?')[0] == clean_url]
                    unique_images.append(img_url)
                else:
                    unique_images.append(img_url)
        
        return unique_images[:8]  # Return up to 8 candidates instead of 3
    
    def _get_image_src(self, img, base_url):
        """Extract and normalize image source URL"""
        # Try multiple possible source attributes
        src_attrs = [
            'src', 'data-src', 'data-lazy-src', 'data-original', 
            'data-srcset', 'data-zoom-image', 'data-large', 'data-full',
            'data-image', 'data-lazy', 'srcset'
        ]
        
        src = None
        for attr in src_attrs:
            src = img.get(attr)
            if src:
                # Handle srcset format (take the first/largest image)
                if 'srcset' in attr and ',' in src:
                    src = src.split(',')[0].strip().split(' ')[0]
                break
        
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
        
        # More relaxed size filtering - product images are usually larger
        width = img.get('width')
        height = img.get('height')
        if width and height:
            try:
                w, h = int(width), int(height)
                if w < 100 or h < 100:  # More relaxed than 150
                    return False
                if w > 3000 or h > 3000:  # More relaxed than 2000
                    return False
            except:
                pass
        
        # Exclude only the most obvious non-product images
        exclude_patterns = [
            'logo', 'icon', 'facebook', 'instagram', 'twitter', 
            'nav', 'menu', 'cart', 'checkout'
        ]
        
        exclude_in_url = [
            'logo', 'icon', 'nav', 'menu', 'thumb', 'avatar'
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
                'gallery', 'zoom', 'large', 'detail', 'media'
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
            'media' in text_to_check,
            any(word in alt_text for word in product_title.split() if len(word) > 3),
            'zoom' in class_name,
            'featured' in class_name
        ]
        
        # Boost score if we have positive signals
        score = sum(positive_signals)
        
        # Be more permissive in non-strict mode
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
        
        # Create downloads directory
        downloads_path = "downloads"
        os.makedirs(downloads_path, exist_ok=True)
        
        # Create a unique identifier for this product's images
        import hashlib
        url_hash = hashlib.md5(product_data["url"].encode()).hexdigest()[:8]
        
        # First pass: Download images and get Fashion-CLIP analysis
        images_with_analysis = []
        
        for i, img_url in enumerate(product_data["images"]):
            # Save to downloads folder with product identifier
            img_filename = f"{url_hash}_image_{i}.jpg"
            img_path = os.path.join(downloads_path, img_filename)
            
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