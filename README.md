# Fashion Assist: AI-Powered Shopping Companion

An AI-powered fashion analysis tool that helps users analyze their wardrobe and make informed shopping decisions using computer vision and natural language processing.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run the application
uv run streamlit run app.py
```

## ✨ Features

### 📸 Wardrobe Management
- Upload and organize clothing images
- AI-powered automatic categorization (category, color, style)
- Confidence scoring for predictions
- Digital wardrobe dashboard

### 🛍️ Shopping Analysis
- Analyze products from any shopping URL
- Automatic product information extraction
- AI-powered categorization using Fashion-CLIP
- Compatibility scoring with existing wardrobe items
- LLM-enhanced category generation

### 🔄 Analysis Pipeline
- Complete automated analysis workflow
- Command-line interface for batch processing
- Enhanced Fashion-CLIP analysis with custom categories
- Semantic validation with reasoning
- Automatic image optimization and cleanup

## 📋 Usage

### Web Interface
```bash
uv run streamlit run app.py
```

1. Open the Streamlit app
2. Go to "Upload Wardrobe" to add clothing items
3. Use "Shopping Analysis" to analyze product URLs
4. View compatibility scores and AI analysis

### Command Line Pipeline
```bash
# Analyze a fashion product URL
python run_pipeline.py "https://example.com/product-url"

# Test the pipeline
python test_pipeline.py
```

### Python API
```python
from pipeline import FashionAnalysisPipeline

pipeline = FashionAnalysisPipeline()
results = pipeline.run_pipeline("https://fashion-url.com/product")

if results['pipeline_success']:
    print(f"Best image: {results['best_image_path']}")
    print(f"Categories: {results['generated_categories']}")
    print(f"Confidence: {results['best_image_analysis']['final_score']:.1%}")
```

### Example URLs for Testing
- Zara: `https://www.zara.com/us/en/textured-knit-sweater-p05755160.html`
- Uniqlo: `https://www.uniqlo.com/us/en/products/E460582-000`

## 🏗️ Architecture

```
fashion_assist/
├── app.py                 # Streamlit web interface
├── pipeline.py            # Complete analysis pipeline
├── run_pipeline.py        # CLI interface
├── models/
│   ├── fashion_clip.py    # Fashion-CLIP model wrapper
│   └── llm_validator.py   # LLM validation component
├── utils/
│   └── scraper.py         # Web scraping utilities
└── data/                  # Local storage
    ├── wardrobe/          # User wardrobe images
    ├── scraped/           # Downloaded product images
    └── pipeline_output/   # Analysis results
```

### Pipeline Steps

1. **Scrape**: Extract product title, description, price, and images
2. **Generate**: Create specific categories using LLM analysis
3. **Download**: Retrieve all product images
4. **Analyze**: Process images with Fashion-CLIP using generated categories
5. **Validate**: Use LLM to verify analysis accuracy
6. **Optimize**: Keep only the best image, delete others
7. **Save**: Store results in JSON format

### Output Structure

```
data/pipeline_output/analysis_<hash>/
├── best_image.jpg           # Highest confidence product image
├── pipeline_results.json    # Complete analysis results
└── (temporary files cleaned up automatically)
```

### Supported Sites

The pipeline adapts to most e-commerce sites including:
- Zara, H&M, Uniqlo
- Amazon Fashion
- Most standard e-commerce platforms

## 🤖 AI Models

- **Fashion-CLIP**: Product categorization and style analysis
- **LLM Validator**: Semantic validation and category generation
- **Web Scraper**: Multi-site product information extraction

## 🧪 Testing

```bash
# Run tests
python tests/test_fashion_assist.py

# Test specific URL
python run_pipeline.py "https://fashion-url.com/product"
```

## 🔧 Troubleshooting

**Model loading issues**: Ensure you have sufficient RAM (4GB+) and stable internet for model downloads.

**Scraping failures**: Some sites may block requests. Try different products or use the provided test URLs.

**Image errors**: Ensure uploaded images are valid JPG/PNG files under 10MB.

**Pipeline failures**: The pipeline includes robust error handling for network failures, invalid URLs, missing images, and model failures. Failed analyses return detailed error information for debugging.

## 📝 Development

### Package Management
**⚠️ Important**: Always use `uv` instead of `pip` for this project:

```bash
# ✅ Correct way
uv add package_name
uv run python script.py

# ❌ Don't use
pip install package_name
python script.py
```

This ensures 10-100x faster installations and consistent dependency resolution.

### Code Style
This project uses Black for code formatting and follows PEP 8 guidelines.

### Dependencies
- Streamlit: Web interface
- PyTorch + Transformers: AI model inference
- OpenCLIP: Fashion-CLIP implementation
- BeautifulSoup: Web scraping
- Pillow: Image processing

## 📄 License

MIT License - see LICENSE file for details.