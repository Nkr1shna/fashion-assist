# Fashion Assist: AI-Powered Shopping Companion
## Proof of Concept Specification (1-Week School Project)

**Version:** 1.0 POC  
**Date:** January 2025  
**Timeline:** 1 Week  
**Scope:** Basic Demonstration of Core AI Concepts

---

## 🎯 Project Overview

### Vision Statement
Create a **simple proof of concept** that demonstrates how AI models can help users visualize clothing combinations by analyzing their wardrobe and generating outfit images with new shopping items.

### Core Objectives (POC)
1. **Wardrobe Upload**: Users can upload photos of their clothes
2. **Auto-Tagging**: AI automatically categorizes uploaded items
3. **Shopping Analysis**: Paste a shopping URL and extract item info
4. **Outfit Generation**: Create a visual showing new item + existing clothes

### Success Criteria
- ✅ Demo works end-to-end in 1 week
- ✅ Shows AI models working together
- ✅ Generates at least one realistic outfit combination
- ✅ Simple but functional user interface

---

## 💻 Simplified Technical Stack

```yaml
Core Technology:
  - Python 3.9+
  - uv (fast package manager)
  - Streamlit (entire UI)
  - PyTorch + Transformers
  - Local file storage (no database)

AI Models (3 only):
  - Fashion-CLIP: Auto-tagging and compatibility
  - FLUX Outfit Generator: Basic outfit generation
  - Basic web scraping: Shopping item extraction

Dependencies (installed via uv):
  - streamlit
  - torch
  - transformers
  - requests
  - beautifulsoup4
  - Pillow
  - numpy
```

---

## 🏗 Simplified Architecture

```
fashion_assist_poc/
├── app.py                 # Main Streamlit app
├── models/
│   ├── fashion_clip.py    # Fashion-CLIP wrapper
│   └── outfit_gen.py      # FLUX outfit generation
├── utils/
│   ├── scraper.py         # Simple web scraping
│   └── file_manager.py    # Local file operations
├── data/
│   ├── wardrobe/          # User uploaded images
│   ├── scraped/           # Shopping item images
│   └── generated/         # AI generated outfits
└── requirements.txt
```

---

## 🎨 Core Features (Week 1 Only)

### Feature 1: Wardrobe Upload & Auto-Tagging
**Time**: Day 1-2

```python
# Simple Streamlit interface
def wardrobe_upload():
    st.header("📸 Upload Your Wardrobe")
    
    uploaded_files = st.file_uploader(
        "Choose clothing images", 
        accept_multiple_files=True,
        type=['png', 'jpg', 'jpeg']
    )
    
    for file in uploaded_files:
        # Save file locally
        # Use Fashion-CLIP to auto-tag
        # Display results
```

**Deliverable**: Users can upload 3-5 clothing items and see auto-generated tags

### Feature 2: Shopping Item Analysis  
**Time**: Day 2-3

```python
# Simple URL input and scraping
def shopping_analysis():
    st.header("🛒 Analyze Shopping Item")
    
    url = st.text_input("Paste shopping URL here")
    
    if url:
        # Simple scraping for product images
        # Extract basic info (title, price)
        # Use Fashion-CLIP for categorization
        # Show compatibility with wardrobe
```

**Deliverable**: Paste a URL, see extracted item info and basic compatibility scores

### Feature 3: Basic Outfit Generation
**Time**: Day 3-5

```python
# Generate outfit combination
def generate_outfit():
    st.header("✨ Generate Outfit")
    
    # Select new shopping item
    # Select 1-2 wardrobe items
    # Generate text prompt
    # Use FLUX to create outfit image
    # Display result
```

**Deliverable**: Generate 1 outfit image showing new item + existing clothes

---

## 🤖 Simplified Model Usage

### Fashion-CLIP Integration
```python
class SimpleFashionCLIP:
    def __init__(self):
        # Load model from HuggingFace
        pass
    
    def categorize_item(self, image_path):
        """Return: category, color, style"""
        categories = ["shirt", "pants", "dress", "shoes", "jacket"]
        # Return highest scoring category
        return {"category": "shirt", "color": "blue", "style": "casual"}
    
    def compatibility_score(self, item1_path, item2_path):
        """Return 0-1 compatibility score"""
        return 0.85  # Simple cosine similarity
```

### FLUX Outfit Generator
```python
class SimpleOutfitGenerator:
    def __init__(self):
        # Load FLUX model
        pass
    
    def generate_outfit(self, items_description, style="casual"):
        """Generate outfit image from text description"""
        prompt = f"A {style} outfit with {items_description}"
        # Use FLUX to generate image
        return "generated_outfit.jpg"
```

### Basic Web Scraping
```python
def simple_scrape(url):
    """Extract basic info from shopping URL"""
    # Handle 2-3 major sites (Amazon, Zara, H&M)
    return {
        "title": "Blue Cotton Shirt",
        "price": "$29.99",
        "images": ["shirt1.jpg"],
        "description": "Casual blue cotton shirt"
    }
```

---

## 📱 Streamlit UI Flow

### Page 1: Wardrobe Upload
```python
st.title("👗 Fashion Assist POC")

tab1, tab2, tab3 = st.tabs(["Upload Wardrobe", "Analyze Shopping", "Generate Outfit"])

with tab1:
    # File uploader
    # Display uploaded items with auto-tags
    # Simple edit functionality
```

### Page 2: Shopping Analysis  
```python
with tab2:
    # URL input
    # Display scraped item info
    # Show compatibility scores with wardrobe
    # Simple recommendation
```

### Page 3: Outfit Generation
```python
with tab3:
    # Select shopping item (dropdown)
    # Select wardrobe items (checkboxes)
    # Style selection (radio buttons)
    # Generate button
    # Display result image
```

---

## 📊 Data Structure (Local Files)

### Simple JSON Storage
```json
// wardrobe_items.json
{
    "items": [
        {
            "id": 1,
            "filename": "shirt1.jpg",
            "category": "shirt",
            "color": "blue",
            "style": "casual",
            "uploaded_at": "2025-01-15"
        }
    ]
}

// shopping_items.json
{
    "items": [
        {
            "url": "https://example.com/product",
            "title": "Blue Shirt",
            "price": "$29.99",
            "compatibility_scores": [0.85, 0.72, 0.91]
        }
    ]
}
```

---

## 📅 1-Week Implementation Plan

### Day 1: Setup & Fashion-CLIP
```yaml
Morning:
  - [x] Environment setup
  - [x] Install dependencies
  - [x] Download Fashion-CLIP model

Afternoon:
  - [x] Basic Streamlit app structure
  - [x] File upload functionality
  - [x] Fashion-CLIP integration for auto-tagging

Deliverable: Upload image → see auto-generated tags
```

### Day 2: Web Scraping
```yaml
Morning:
  - [x] Simple web scraping for 2-3 sites
  - [x] Image extraction from URLs
  - [x] Basic metadata parsing

Afternoon:
  - [x] Streamlit page for URL input
  - [x] Display scraped results
  - [x] Compatibility scoring

Deliverable: Paste URL → see item info + compatibility
```

### Day 3: FLUX Setup
```yaml
Morning:
  - [x] Download FLUX outfit generator
  - [x] Test basic image generation
  - [x] Prompt engineering

Afternoon:
  - [x] Integration with wardrobe data
  - [x] Simple text prompt creation
  - [x] Basic error handling

Deliverable: Generate first outfit image
```

### Day 4: Integration
```yaml
Morning:
  - [x] Connect all components
  - [x] End-to-end workflow testing
  - [x] Basic error handling

Afternoon:
  - [x] UI improvements
  - [x] Result display optimization
  - [x] Simple validation

Deliverable: Complete workflow working
```

### Day 5: Polish & Demo
```yaml
Morning:
  - [x] Bug fixes
  - [x] UI polish
  - [x] Add sample data

Afternoon:
  - [x] Demo preparation
  - [x] Documentation
  - [x] Final testing

Deliverable: Functional demo ready
```

---

## 🛠 Quick Start Commands

```bash
# Setup (Day 1 morning)
git clone <your-repo>
cd fashion_assist_poc

# Initialize with uv (much faster than pip)
uv init --python 3.11
uv add streamlit torch transformers diffusers open-clip-torch

# Run app
uv run streamlit run app.py

# Demo data (if available)
uv run python load_sample_data.py
```

---

## 📋 Success Checklist

- [ ] ✅ Fashion-CLIP auto-categorizes uploaded clothes
- [ ] ✅ Web scraper extracts shopping item info
- [ ] ✅ FLUX generates at least one outfit image
- [ ] ✅ Streamlit app has clean, working interface
- [ ] ✅ End-to-end demo completes without errors
- [ ] ✅ Code is documented and runnable by others
- [ ] ✅ Demo presentation prepared (5 minutes)

**Target**: Functional proof of concept demonstrating AI-powered fashion assistance in 1 week.