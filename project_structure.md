# Fashion Assist POC - Project Structure

This document outlines the complete file structure for the Fashion Assist proof of concept project.

## 📁 Directory Structure

```
fashion_assist_poc/
├── 📄 README.md                      # Project overview and setup instructions
├── 📄 pyproject.toml                 # Modern Python project configuration (uv)
├── 📄 requirements.txt               # Legacy Python dependencies (fallback)
├── 📄 app.py                         # Main Streamlit application
├── 📄 .gitignore                     # Git ignore file
├── 📄 LICENSE                        # MIT license file
│
├── 📁 docs/                          # Documentation
│   ├── 📄 fashion_assist_poc_spec.md # Project specification
│   ├── 📄 implementation_guide.md    # Step-by-step implementation
│   ├── 📄 demo_script.md            # Demo presentation guide
│   └── 📄 project_structure.md      # This file
│
├── 📁 models/                        # AI model wrappers
│   ├── 📄 __init__.py               
│   ├── 📄 fashion_clip.py           # Fashion-CLIP integration
│   └── 📄 outfit_gen.py             # FLUX outfit generation
│
├── 📁 utils/                         # Utility functions
│   ├── 📄 __init__.py               
│   ├── 📄 scraper.py                # Web scraping functionality
│   └── 📄 file_manager.py           # File operations and storage
│
├── 📁 data/                          # Data storage (created at runtime)
│   ├── 📁 wardrobe/                 # User uploaded clothing images
│   ├── 📁 scraped/                  # Downloaded shopping item images
│   ├── 📁 generated/                # AI generated outfit images
│   └── 📁 temp/                     # Temporary files
│
├── 📁 config/                        # Configuration files (optional)
│   ├── 📄 model_config.yaml         # Model settings
│   └── 📄 app_config.yaml           # Application settings
│
└── 📁 tests/                         # Test files (optional)
    ├── 📄 test_fashion_clip.py       # Fashion-CLIP tests
    ├── 📄 test_scraper.py            # Web scraper tests
    └── 📄 test_app.py                # Application tests
```

---

## 🏗 Implementation Priority

### Core Files (Must Implement - Week 1)

#### Day 1: Basic Setup
1. **`app.py`** - Main Streamlit application with basic UI structure
2. **`requirements.txt`** - All necessary dependencies
3. **`models/fashion_clip.py`** - Fashion-CLIP wrapper for categorization
4. **Data directories** - Create folder structure

#### Day 2: Web Scraping
5. **`utils/scraper.py`** - Web scraping for shopping sites
6. **Update `app.py`** - Add shopping analysis functionality

#### Day 3: Outfit Generation
7. **`models/outfit_gen.py`** - FLUX outfit generation wrapper
8. **Update `app.py`** - Add outfit generation functionality

#### Day 4-5: Integration & Polish
9. **`utils/file_manager.py`** - File operations and management
10. **Testing and debugging** - End-to-end workflow validation

### Supporting Files (Nice to Have)

#### Documentation
- **`README.md`** - Project overview and setup instructions
- **`docs/`** - All documentation files (already created)

#### Configuration (Optional)
- **`.gitignore`** - Git ignore patterns
- **`config/`** - YAML configuration files for models and app settings

#### Testing (Optional)
- **`tests/`** - Unit tests for individual components

---

## 📝 File Templates

### Basic .gitignore
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# Data files
data/wardrobe/*
data/scraped/*
data/generated/*
!data/wardrobe/.gitkeep
!data/scraped/.gitkeep
!data/generated/.gitkeep

# Model files
*.safetensors
*.bin
*.pt
*.pth

# Streamlit
.streamlit/

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo
```

### Basic __init__.py files
```python
# models/__init__.py
"""AI model wrappers for Fashion Assist POC"""

# utils/__init__.py  
"""Utility functions for Fashion Assist POC"""
```

---

## 🚀 Quick Setup Commands

### Initial Project Setup
```bash
# Create main project directory
mkdir fashion_assist_poc && cd fashion_assist_poc

# Initialize with uv (modern Python project management)
uv init --python 3.11

# Create all directories
mkdir -p docs models utils data/{wardrobe,scraped,generated,temp} config tests

# Create empty __init__.py files
touch models/__init__.py utils/__init__.py

# Create data directory placeholders
touch data/wardrobe/.gitkeep data/scraped/.gitkeep data/generated/.gitkeep

# Initialize git repository
git init
```

### File Creation Order
```bash
# Day 1
touch app.py
touch models/fashion_clip.py
# Note: pyproject.toml is auto-created by uv init

# Day 2  
touch utils/scraper.py

# Day 3
touch models/outfit_gen.py

# Day 4-5
touch utils/file_manager.py
touch .gitignore
```

---

## 🎯 Minimum Viable Implementation

For a working demo in 1 week, focus on these essential files:

### Must Have (4 files)
1. **`requirements.txt`** - Dependencies
2. **`app.py`** - Main application (~200 lines)
3. **`models/fashion_clip.py`** - Fashion-CLIP wrapper (~150 lines)
4. **`utils/scraper.py`** - Basic web scraper (~100 lines)

### Nice to Have (2 files)
5. **`models/outfit_gen.py`** - FLUX integration (~100 lines)
6. **`utils/file_manager.py`** - File operations (~50 lines)

### Total Code: ~600 lines across 6 files

---

## 💡 Development Tips

### File Development Order
1. Start with `requirements.txt` and basic `app.py`
2. Implement `fashion_clip.py` and test integration
3. Add `scraper.py` and test with real URLs
4. Implement `outfit_gen.py` for AI generation
5. Polish UI and add error handling

### Code Organization
- Keep each file focused on single responsibility
- Use clear function/class names
- Add docstrings for main functions
- Handle errors gracefully with try/except blocks

### Testing Strategy
- Test each component individually before integration
- Use real data (images, URLs) for testing
- Have backup examples ready for demo

---

This structure provides a solid foundation for your 1-week Fashion Assist POC project while keeping complexity manageable for a school project demonstration.