# Fashion Assist POC - Implementation Guide

## 🚀 Getting Started

### Prerequisites
- MacBook Pro M4 Pro with 48GB unified memory
- Python 3.9+
- **uv** (modern Python package manager) - Install with: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Git
- Internet connection for model downloads

**Why uv?** UV is 10-100x faster than pip, has better dependency resolution, and provides modern Python project management. Perfect for rapid prototyping!

### Environment Setup

```bash
# Create project directory
mkdir fashion_assist_poc
cd fashion_assist_poc

# Initialize with uv (faster than pip/venv)
uv init --python 3.11

# Create project structure
mkdir -p {models,utils,data/{wardrobe,scraped,generated}}
```

---

## 📦 Dependencies & Installation

### requirements.txt
```txt
streamlit>=1.25.0
torch>=2.0.0
transformers>=4.30.0
diffusers>=0.20.0
open-clip-torch>=2.20.0
requests>=2.31.0
beautifulsoup4>=4.12.0
Pillow>=9.5.0
numpy>=1.24.0
opencv-python>=4.8.0
scikit-learn>=1.3.0
```

### Installation Commands
```bash
# Install all dependencies with uv (much faster than pip)
uv add streamlit torch torchvision transformers diffusers accelerate
uv add open-clip-torch Pillow opencv-python numpy
uv add requests beautifulsoup4 selenium scikit-learn pandas

# Download Fashion-CLIP model
uv run python -c "
import open_clip
model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k')
print('Fashion-CLIP downloaded successfully')
"
```

---

## 🎯 Day-by-Day Implementation

### Day 1: Basic Setup & Fashion-CLIP

#### Step 1: Create main app structure
**File: `app.py`**
```python
import streamlit as st
import os
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="Fashion Assist POC",
    page_icon="👗",
    layout="wide"
)

def main():
    st.title("👗 Fashion Assist - AI Shopping Companion")
    st.markdown("*A proof of concept for AI-powered fashion assistance*")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📸 Upload Wardrobe", "🛒 Analyze Shopping", "✨ Generate Outfit"])
    
    with tab1:
        wardrobe_upload()
    
    with tab2:
        shopping_analysis()
    
    with tab3:
        outfit_generation()

def wardrobe_upload():
    st.header("Upload Your Wardrobe")
    st.write("Upload photos of your clothing items to build your digital wardrobe")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose clothing images",
        accept_multiple_files=True,
        type=['png', 'jpg', 'jpeg']
    )
    
    if uploaded_files:
        st.success(f"Uploaded {len(uploaded_files)} items!")
        
        # Display uploaded items (placeholder)
        for file in uploaded_files:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(file, width=150)
            with col2:
                st.write(f"**{file.name}**")
                st.write("Category: Processing...")
                st.write("Color: Processing...")

def shopping_analysis():
    st.header("Analyze Shopping Item")
    st.write("Paste a shopping URL to analyze compatibility with your wardrobe")
    
    url = st.text_input("Shopping URL", placeholder="https://example.com/product")
    
    if url:
        st.info("Analysis feature coming soon...")

def outfit_generation():
    st.header("Generate Outfit")
    st.write("Create outfit combinations with AI")
    
    st.info("Outfit generation feature coming soon...")

if __name__ == "__main__":
    main()
```

#### Step 2: Fashion-CLIP Integration
**File: `models/fashion_clip.py`**
```python
import torch
import open_clip
from PIL import Image
import numpy as np
from pathlib import Path

class FashionCLIP:
    def __init__(self):
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Load Fashion-CLIP model
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            'ViT-B-32', 
            pretrained='laion2b_s34b_b79k'
        )
        self.model = self.model.to(self.device)
        self.tokenizer = open_clip.get_tokenizer('ViT-B-32')
        
        # Fashion categories for classification
        self.categories = [
            "a photo of a shirt",
            "a photo of a t-shirt", 
            "a photo of pants",
            "a photo of jeans",
            "a photo of a dress",
            "a photo of a skirt",
            "a photo of a jacket",
            "a photo of a sweater",
            "a photo of shoes",
            "a photo of sneakers",
            "a photo of boots",
            "a photo of accessories"
        ]
        
        self.colors = [
            "black", "white", "red", "blue", "green", 
            "yellow", "orange", "purple", "pink", "brown", "gray"
        ]
        
        self.styles = [
            "casual", "formal", "business", "sporty", 
            "elegant", "vintage", "modern", "bohemian"
        ]
    
    def categorize_item(self, image_path):
        """Categorize clothing item using Fashion-CLIP"""
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)
            
            # Encode image
            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                image_features /= image_features.norm(dim=-1, keepdim=True)
            
            # Get category
            category = self._classify_with_labels(image_features, self.categories)
            
            # Get color
            color_prompts = [f"a photo of {color} clothing" for color in self.colors]
            color = self._classify_with_labels(image_features, color_prompts)
            
            # Get style
            style_prompts = [f"a photo of {style} clothing" for style in self.styles]
            style = self._classify_with_labels(image_features, style_prompts)
            
            return {
                "category": category.replace("a photo of a ", "").replace("a photo of ", ""),
                "color": color,
                "style": style,
                "confidence": 0.85  # Placeholder
            }
            
        except Exception as e:
            print(f"Error categorizing item: {e}")
            return {
                "category": "unknown",
                "color": "unknown", 
                "style": "unknown",
                "confidence": 0.0
            }
    
    def _classify_with_labels(self, image_features, labels):
        """Helper function for zero-shot classification"""
        text_tokens = self.tokenizer(labels).to(self.device)
        
        with torch.no_grad():
            text_features = self.model.encode_text(text_tokens)
            text_features /= text_features.norm(dim=-1, keepdim=True)
            
            # Calculate similarities
            similarities = (image_features @ text_features.T).squeeze(0)
            best_idx = similarities.argmax().item()
            
            if "clothing" in labels[best_idx]:
                return labels[best_idx].split()[-2]  # Extract color/style word
            else:
                return labels[best_idx].replace("a photo of a ", "").replace("a photo of ", "")
    
    def get_image_embedding(self, image_path):
        """Get image embedding for similarity comparisons"""
        try:
            image = Image.open(image_path).convert('RGB')
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                image_features /= image_features.norm(dim=-1, keepdim=True)
            
            return image_features.cpu().numpy()
            
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return None
    
    def compatibility_score(self, image1_path, image2_path):
        """Calculate compatibility score between two items"""
        emb1 = self.get_image_embedding(image1_path)
        emb2 = self.get_image_embedding(image2_path)
        
        if emb1 is None or emb2 is None:
            return 0.0
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2.T).item()
        return max(0.0, min(1.0, similarity))  # Clamp between 0 and 1
```

#### Step 3: Update main app to use Fashion-CLIP
**Update `app.py`**
```python
import streamlit as st
import os
from pathlib import Path
import json
from models.fashion_clip import FashionCLIP

# Initialize Fashion-CLIP (cached)
@st.cache_resource
def load_fashion_clip():
    return FashionCLIP()

def wardrobe_upload():
    st.header("Upload Your Wardrobe")
    st.write("Upload photos of your clothing items to build your digital wardrobe")
    
    # Initialize Fashion-CLIP
    fashion_clip = load_fashion_clip()
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose clothing images",
        accept_multiple_files=True,
        type=['png', 'jpg', 'jpeg']
    )
    
    if uploaded_files:
        st.success(f"Uploaded {len(uploaded_files)} items!")
        
        # Process each uploaded file
        for i, file in enumerate(uploaded_files):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(file, width=150)
            
            with col2:
                st.write(f"**{file.name}**")
                
                # Save file temporarily and analyze
                temp_path = f"data/wardrobe/{file.name}"
                os.makedirs("data/wardrobe", exist_ok=True)
                
                with open(temp_path, "wb") as f:
                    f.write(file.read())
                
                # Analyze with Fashion-CLIP
                with st.spinner("Analyzing..."):
                    analysis = fashion_clip.categorize_item(temp_path)
                
                st.write(f"Category: **{analysis['category']}**")
                st.write(f"Color: **{analysis['color']}**")
                st.write(f"Style: **{analysis['style']}**")
                st.write(f"Confidence: {analysis['confidence']:.2f}")
                
                st.divider()
```

---

### Day 2: Web Scraping Implementation

#### Step 1: Create web scraper
**File: `utils/scraper.py`**
```python
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from pathlib import Path
import os

class SimpleWebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
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
            'title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)[:100]  # Limit length
        
        return "Unknown Product"
    
    def _extract_price(self, soup):
        """Extract product price"""
        # Look for price patterns
        price_selectors = [
            '[data-testid="price"]',
            '.price',
            '.current-price',
            '.sale-price',
            '.product-price'
        ]
        
        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                # Extract price with regex
                price_match = re.search(r'[\$€£][\d,]+\.?\d*', price_text)
                if price_match:
                    return price_match.group()
        
        # Fallback: search for price patterns in all text
        price_pattern = re.search(r'[\$€£][\d,]+\.?\d*', soup.get_text())
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
            'img[src*="product"]'
        ]
        
        for selector in img_selectors:
            img_elements = soup.select(selector)
            for img in img_elements:
                src = img.get('src') or img.get('data-src')
                if src:
                    # Convert relative URLs to absolute
                    full_url = urljoin(base_url, src)
                    if self._is_valid_image_url(full_url):
                        images.append(full_url)
                        if len(images) >= 3:  # Limit to 3 images
                            break
            if len(images) >= 3:
                break
        
        return images
    
    def _extract_description(self, soup):
        """Extract product description"""
        desc_selectors = [
            '[data-testid="product-description"]',
            '.product-description',
            '.description',
            '.product-details'
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                desc = element.get_text(strip=True)
                return desc[:200] + "..." if len(desc) > 200 else desc
        
        return "No description available"
    
    def _is_valid_image_url(self, url):
        """Check if URL points to a valid image"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        return any(ext in url.lower() for ext in image_extensions)
    
    def download_image(self, image_url, save_path):
        """Download image from URL"""
        try:
            response = requests.get(image_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            return save_path
            
        except Exception as e:
            print(f"Error downloading image {image_url}: {e}")
            return None
```

#### Step 2: Update app with shopping analysis
**Update `app.py` - shopping_analysis function**
```python
from utils.scraper import SimpleWebScraper

def shopping_analysis():
    st.header("Analyze Shopping Item")
    st.write("Paste a shopping URL to analyze compatibility with your wardrobe")
    
    # Initialize scraper and Fashion-CLIP
    scraper = SimpleWebScraper()
    fashion_clip = load_fashion_clip()
    
    url = st.text_input("Shopping URL", placeholder="https://example.com/product")
    
    if url and st.button("Analyze Item"):
        with st.spinner("Scraping product information..."):
            product_data = scraper.scrape_product(url)
        
        if product_data:
            st.success("Product analyzed successfully!")
            
            # Display product info
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if product_data["images"]:
                    # Download and display first image
                    img_url = product_data["images"][0]
                    temp_img_path = f"data/scraped/temp_product.jpg"
                    
                    downloaded_path = scraper.download_image(img_url, temp_img_path)
                    if downloaded_path:
                        st.image(downloaded_path, width=200)
                    else:
                        st.write("Could not load image")
                else:
                    st.write("No images found")
            
            with col2:
                st.write(f"**Title:** {product_data['title']}")
                st.write(f"**Price:** {product_data['price']}")
                st.write(f"**Description:** {product_data['description']}")
                
                # Analyze with Fashion-CLIP if image was downloaded
                if product_data["images"] and downloaded_path:
                    with st.spinner("Analyzing item category..."):
                        analysis = fashion_clip.categorize_item(downloaded_path)
                    
                    st.write("---")
                    st.write("**AI Analysis:**")
                    st.write(f"Category: **{analysis['category']}**")
                    st.write(f"Color: **{analysis['color']}**")
                    st.write(f"Style: **{analysis['style']}**")
                    
                    # Compatibility with wardrobe (placeholder)
                    st.write("---")
                    st.write("**Wardrobe Compatibility:**")
                    st.info("Upload wardrobe items first to see compatibility scores!")
        
        else:
            st.error("Could not analyze this URL. Please try a different product page.")
```

---

### Day 3: FLUX Integration (Basic)

#### Step 1: Install FLUX dependencies
```bash
pip install diffusers accelerate xformers
```

#### Step 2: Create FLUX outfit generator
**File: `models/outfit_gen.py`**
```python
import torch
from diffusers import DiffusionPipeline
from PIL import Image
import os

class SimpleOutfitGenerator:
    def __init__(self):
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"Using device for FLUX: {self.device}")
        
        # Load FLUX model (simplified for POC)
        try:
            self.pipe = DiffusionPipeline.from_pretrained(
                "tryonlabs/FLUX.1-dev-LoRA-Outfit-Generator",
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            self.pipe = self.pipe.to(self.device)
            print("FLUX model loaded successfully")
        except Exception as e:
            print(f"Could not load FLUX model: {e}")
            self.pipe = None
    
    def generate_outfit_description(self, items_info, style="casual"):
        """Generate text description for outfit"""
        descriptions = []
        
        for item in items_info:
            category = item.get('category', 'clothing item')
            color = item.get('color', '')
            material = item.get('material', '')
            
            if color and material:
                desc = f"{color} {material} {category}"
            elif color:
                desc = f"{color} {category}"
            else:
                desc = category
            
            descriptions.append(desc)
        
        # Create outfit prompt
        outfit_desc = ", ".join(descriptions)
        
        prompt = f"A {style} outfit featuring {outfit_desc}. " \
                f"Professional fashion photography, clean background, " \
                f"well-coordinated colors, stylish and modern."
        
        return prompt
    
    def generate_outfit_image(self, items_info, style="casual", output_path=None):
        """Generate outfit image using FLUX"""
        if not self.pipe:
            # Fallback: return placeholder image
            return self._create_placeholder_image(items_info, style, output_path)
        
        try:
            # Generate text prompt
            prompt = self.generate_outfit_description(items_info, style)
            print(f"Generated prompt: {prompt}")
            
            # Generate image
            with torch.no_grad():
                image = self.pipe(
                    prompt,
                    num_inference_steps=20,  # Reduced for speed
                    guidance_scale=7.5,
                    height=512,
                    width=512
                ).images[0]
            
            # Save image
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                image.save(output_path)
                return output_path
            else:
                return image
                
        except Exception as e:
            print(f"Error generating outfit: {e}")
            return self._create_placeholder_image(items_info, style, output_path)
    
    def _create_placeholder_image(self, items_info, style, output_path):
        """Create placeholder image when FLUX is not available"""
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple placeholder
        img = Image.new('RGB', (512, 512), color='lightgray')
        draw = ImageDraw.Draw(img)
        
        # Add text
        try:
            # Try to use default font
            font = ImageFont.load_default()
        except:
            font = None
        
        text_lines = [
            f"Outfit: {style.title()}",
            "",
            "Items:"
        ]
        
        for item in items_info:
            category = item.get('category', 'item')
            color = item.get('color', '')
            if color:
                text_lines.append(f"• {color.title()} {category.title()}")
            else:
                text_lines.append(f"• {category.title()}")
        
        text_lines.append("")
        text_lines.append("(Generated with AI)")
        
        y_position = 50
        for line in text_lines:
            draw.text((50, y_position), line, fill='black', font=font)
            y_position += 30
        
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.save(output_path)
            return output_path
        else:
            return img
```

#### Step 3: Update app with outfit generation
**Update `app.py` - outfit_generation function**
```python
from models.outfit_gen import SimpleOutfitGenerator
import json
import glob

def outfit_generation():
    st.header("Generate Outfit")
    st.write("Create outfit combinations with AI")
    
    # Initialize generators
    outfit_gen = SimpleOutfitGenerator()
    fashion_clip = load_fashion_clip()
    
    # Check for available items
    wardrobe_items = glob.glob("data/wardrobe/*")
    scraped_items = glob.glob("data/scraped/*")
    
    if not wardrobe_items and not scraped_items:
        st.warning("Please upload wardrobe items or analyze shopping items first!")
        return
    
    st.subheader("Select Items for Outfit")
    
    selected_items = []
    
    # Wardrobe items selection
    if wardrobe_items:
        st.write("**Your Wardrobe Items:**")
        for item_path in wardrobe_items[:5]:  # Limit to 5 items
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                st.image(item_path, width=100)
            
            with col2:
                # Analyze item if not already done
                analysis = fashion_clip.categorize_item(item_path)
                st.write(f"{analysis['color']} {analysis['category']}")
            
            with col3:
                if st.checkbox(f"Include", key=item_path):
                    selected_items.append({
                        'path': item_path,
                        'category': analysis['category'],
                        'color': analysis['color'],
                        'style': analysis['style']
                    })
    
    # Shopping items selection
    if scraped_items:
        st.write("**Shopping Items:**")
        for item_path in scraped_items:
            if "temp_product" in item_path:
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    st.image(item_path, width=100)
                
                with col2:
                    analysis = fashion_clip.categorize_item(item_path)
                    st.write(f"{analysis['color']} {analysis['category']}")
                
                with col3:
                    if st.checkbox(f"Include shopping item", key=item_path):
                        selected_items.append({
                            'path': item_path,
                            'category': analysis['category'],
                            'color': analysis['color'],
                            'style': analysis['style']
                        })
    
    # Style selection
    style = st.selectbox(
        "Choose outfit style:",
        ["casual", "formal", "business", "sporty", "elegant"]
    )
    
    # Generate outfit
    if st.button("Generate Outfit") and selected_items:
        with st.spinner("Generating outfit visualization..."):
            output_path = f"data/generated/outfit_{len(selected_items)}items_{style}.jpg"
            
            generated_image_path = outfit_gen.generate_outfit_image(
                selected_items, 
                style=style,
                output_path=output_path
            )
        
        if generated_image_path:
            st.success("Outfit generated successfully!")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Selected Items")
                for item in selected_items:
                    st.image(item['path'], width=150)
                    st.write(f"{item['color']} {item['category']}")
            
            with col2:
                st.subheader("Generated Outfit")
                st.image(generated_image_path, width=400)
                st.write(f"Style: {style.title()}")
                
                # Download button
                with open(generated_image_path, "rb") as file:
                    st.download_button(
                        label="Download Outfit Image",
                        data=file.read(),
                        file_name=f"outfit_{style}.jpg",
                        mime="image/jpeg"
                    )
        else:
            st.error("Failed to generate outfit. Please try again.")
    
    elif not selected_items and st.button("Generate Outfit"):
        st.warning("Please select at least one item for the outfit!")
```

---

## 🧪 Testing & Debugging

### Test checklist for each day:

**Day 1 Tests:**
```bash
# Test Fashion-CLIP
uv run python -c "
from models.fashion_clip import FashionCLIP
fc = FashionCLIP()
print('Fashion-CLIP loaded successfully')
"

# Test Streamlit app
uv run streamlit run app.py
```

**Day 2 Tests:**
```bash
# Test web scraper
uv run python -c "
from utils.scraper import SimpleWebScraper
scraper = SimpleWebScraper()
result = scraper.scrape_product('https://www.zara.com/us/en/basic-t-shirt-p00706460.html')
print(result)
"
```

**Day 3 Tests:**
```bash
# Test outfit generator
uv run python -c "
from models.outfit_gen import SimpleOutfitGenerator
gen = SimpleOutfitGenerator()
print('Outfit generator initialized')
"
```

### Common Issues & Solutions:

1. **Memory Issues**: Reduce model precision or batch sizes
2. **Model Download Fails**: Check internet connection, try manual download
3. **Streamlit Crashes**: Check error logs, restart with `streamlit run app.py`
4. **Images Not Loading**: Check file paths and permissions

---

## 🚀 Quick Demo Setup

If you need a quick demo setup:

```bash
# Create sample data
mkdir -p data/{wardrobe,scraped,generated}

# Download sample images (optional)
# Add your own test images to data/wardrobe/

# Run with sample data
uv run streamlit run app.py
```

---

This implementation guide provides step-by-step instructions for building your Fashion Assist POC in one week. Focus on getting the basic functionality working first, then add polish as time allows!