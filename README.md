# Fashion Assist: AI-Powered Shopping Companion

> **Status: Feature 2 (Shopping Analysis) ✅ IMPLEMENTED**

A proof of concept that demonstrates how AI models can help users visualize clothing combinations by analyzing their wardrobe and shopping items.

## 🚀 Quick Start

**⚠️ Important: Always use `uv` instead of `pip`**

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# Install dependencies
uv add streamlit torch transformers requests beautifulsoup4

# Run the application
uv run streamlit run app.py
```

## ✨ Features Implemented

### ✅ Feature 1: Wardrobe Upload & Auto-Tagging
- Upload multiple clothing images
- AI-powered automatic categorization (category, color, style)
- Confidence scoring for AI predictions
- Save wardrobe items with metadata
- Visual wardrobe summary dashboard

### ✅ Feature 2: Shopping Analysis ⭐ **NEW**
- **Paste any shopping URL** to analyze products
- **Automatic product extraction** (title, price, description, images)
- **AI-powered categorization** using Fashion-CLIP
- **Wardrobe compatibility scoring** - see how well new items match your existing clothes
- **Color-coded compatibility ratings** (Excellent >70%, Good >50%)
- **Shopping history** - review previously analyzed items
- **Smart image downloading** - automatically save product images
- **Error handling** - robust fallback for different site structures

### 🔜 Feature 3: Outfit Generation (Coming Soon)
- Generate outfit combinations with AI
- Visual outfit mockups
- Style recommendations

## 🛒 How to Use Feature 2: Shopping Analysis

1. **Run the app**: `uv run streamlit run app.py`
2. **Go to "Analyze Shopping" tab**
3. **Paste any product URL** (e.g., from Zara, H&M, Amazon, etc.)
4. **Click "🔍 Analyze Item"**
5. **View results**:
   - Product information (title, price, description)
   - AI analysis (category, color, style)
   - Compatibility scores with your wardrobe items
   - Overall compatibility assessment

### Supported Shopping Sites
- **Any e-commerce site** with standard HTML structure
- Automatically adapts to different layouts
- Robust extraction for title, price, images, and descriptions

## 🤖 AI Models Used

### Fashion-CLIP
- **Purpose**: Auto-categorization and compatibility scoring
- **Capabilities**: 
  - Categorizes clothing items (shirt, pants, dress, shoes, etc.)
  - Identifies colors (black, white, blue, red, etc.)
  - Determines style (casual, formal, business, sporty, etc.)
  - Calculates compatibility between items

### Web Scraping Engine
- **Purpose**: Extract product information from shopping URLs
- **Capabilities**:
  - Multi-site support with adaptive selectors
  - Image downloading and processing
  - Price and description extraction
  - Error handling for blocked requests

## 📊 Data Storage

### Local JSON Files
```
data/
├── wardrobe_items.json    # Your uploaded wardrobe items
├── shopping_items.json    # Analyzed shopping items  
├── wardrobe/             # Uploaded clothing images
└── scraped/              # Downloaded product images
```

## 🔧 Development Rules

### ⚠️ IMPORTANT: Use `uv` Instead of `pip`

**🚫 DON'T USE:**
```bash
pip install package_name
pip3 install package_name  
```

**✅ USE INSTEAD:**
```bash
uv add package_name
uv run python script.py
uv run streamlit run app.py
```

**Why?** 
- 10-100x faster than pip
- Better dependency resolution
- Modern Python project management
- See `docs/development_rules.md` for complete guidelines

## 🏗 Architecture

```
fashion_assist/
├── app.py                 # Main Streamlit application
├── models/
│   └── fashion_clip.py    # Fashion-CLIP wrapper for AI analysis
├── utils/
│   └── scraper.py         # Web scraping utility ⭐ NEW
├── data/                  # Local file storage
└── docs/
    └── development_rules.md # Development guidelines
```

## 🧪 Testing

Feature 2 has been thoroughly tested:
- ✅ Web scraper initialization
- ✅ HTML parsing and extraction 
- ✅ JSON storage operations
- ✅ Directory structure validation
- ✅ Integration with Fashion-CLIP
- ✅ Streamlit UI functionality

## 🎯 Next Steps

1. **Try Feature 2**: Upload some wardrobe items, then analyze shopping URLs
2. **Test compatibility**: See how well new items match your style
3. **Build wardrobe**: Use compatibility scores to make informed purchases
4. **Wait for Feature 3**: Outfit generation coming soon!

## 📝 Project Status

- [x] **Day 1-2**: ✅ Wardrobe Upload & Auto-Tagging  
- [x] **Day 2-3**: ✅ Shopping Item Analysis ⭐ **COMPLETED**
- [ ] **Day 3-5**: 🔜 Basic Outfit Generation
- [ ] **Day 4**: 🔜 Integration & Polish
- [ ] **Day 5**: 🔜 Demo Preparation

---

**🎉 Feature 2 is live! Start analyzing your shopping finds with AI-powered compatibility scoring!**