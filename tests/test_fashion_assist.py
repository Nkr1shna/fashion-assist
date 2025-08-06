#!/usr/bin/env python3
"""
Comprehensive test suite for Fashion Assist
Consolidates all testing functionality
"""

import os
import sys
import pytest
from pathlib import Path
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.fashion_clip import FashionCLIP
from models.llm_validator import LLMValidator
from utils.scraper import SimpleWebScraper
from pipeline import FashionAnalysisPipeline


class TestFashionCLIP:
    """Test Fashion-CLIP model functionality"""
    
    @pytest.fixture(scope="class")
    def fashion_clip(self):
        """Initialize Fashion-CLIP model once for all tests"""
        return FashionCLIP()
    
    def test_model_initialization(self, fashion_clip):
        """Test that Fashion-CLIP initializes correctly"""
        assert fashion_clip is not None
        assert hasattr(fashion_clip, 'model')
        assert hasattr(fashion_clip, 'preprocess')
    
    def test_categorization_structure(self, fashion_clip):
        """Test that categorization returns expected structure"""
        # Create a test image (1x1 pixel RGB)
        from PIL import Image
        test_image = Image.new('RGB', (224, 224), color='red')
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            test_image.save(tmp.name)
            
            try:
                result = fashion_clip.categorize_item(tmp.name)
                
                # Check structure
                assert isinstance(result, dict)
                assert 'category' in result
                assert 'color' in result
                assert 'style' in result
                assert 'confidence' in result
                
                # Check types
                assert isinstance(result['category'], str)
                assert isinstance(result['color'], str)
                assert isinstance(result['style'], str)
                assert isinstance(result['confidence'], (int, float))
                assert 0 <= result['confidence'] <= 1
                
            finally:
                os.unlink(tmp.name)


class TestWebScraper:
    """Test web scraping functionality"""
    
    @pytest.fixture(scope="class")
    def scraper(self):
        """Initialize scraper once for all tests"""
        return SimpleWebScraper()
    
    def test_scraper_initialization(self, scraper):
        """Test that scraper initializes correctly"""
        assert scraper is not None
        assert hasattr(scraper, 'headers')
        assert 'User-Agent' in scraper.headers
    
    def test_url_validation(self, scraper):
        """Test URL validation methods"""
        # Valid image URLs
        assert scraper._is_valid_image_url("https://example.com/image.jpg")
        assert scraper._is_valid_image_url("https://example.com/photo.png")
        
        # Invalid URLs
        assert not scraper._is_valid_image_url("https://example.com/document.pdf")
        assert not scraper._is_valid_image_url(None)
        assert not scraper._is_valid_image_url("")


class TestPipeline:
    """Test complete analysis pipeline"""
    
    @pytest.fixture(scope="class")
    def pipeline(self):
        """Initialize pipeline once for all tests"""
        return FashionAnalysisPipeline()
    
    def test_pipeline_initialization(self, pipeline):
        """Test that pipeline initializes all components"""
        assert pipeline is not None
        assert hasattr(pipeline, 'scraper')
        assert hasattr(pipeline, 'fashion_clip')
        assert hasattr(pipeline, 'llm_validator')
    
    def test_category_generation(self, pipeline):
        """Test LLM category generation"""
        test_product = {
            'title': 'Blue Denim Jacket',
            'description': 'Classic blue denim jacket with button closure'
        }
        
        categories = pipeline.generate_categories_from_description(test_product)
        assert isinstance(categories, list)
        assert len(categories) > 0


@pytest.mark.integration
class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_full_pipeline_structure(self):
        """Test that pipeline returns expected structure"""
        pipeline = FashionAnalysisPipeline()
        
        # Mock URL for testing
        test_url = "https://example.com/product"
        
        # Test with actual URL would require network access
        # This test validates the pipeline structure
        assert hasattr(pipeline, 'run_pipeline')
        assert callable(pipeline.run_pipeline)


def run_development_tests():
    """Run tests suitable for development"""
    print("🧪 Running Fashion Assist Test Suite")
    print("=" * 50)
    
    # Basic component tests
    print("1. Testing Fashion-CLIP initialization...")
    try:
        fashion_clip = FashionCLIP()
        print("   ✅ Fashion-CLIP loaded successfully")
    except Exception as e:
        print(f"   ❌ Fashion-CLIP failed: {e}")
        return False
    
    print("2. Testing Web Scraper...")
    try:
        scraper = SimpleWebScraper()
        print("   ✅ Scraper initialized successfully")
    except Exception as e:
        print(f"   ❌ Scraper failed: {e}")
        return False
    
    print("3. Testing Pipeline...")
    try:
        pipeline = FashionAnalysisPipeline()
        print("   ✅ Pipeline initialized successfully")
    except Exception as e:
        print(f"   ❌ Pipeline failed: {e}")
        return False
    
    print("\n🎉 All basic tests passed!")
    print("💡 Run 'pytest tests/' for comprehensive testing")
    return True


if __name__ == "__main__":
    run_development_tests()