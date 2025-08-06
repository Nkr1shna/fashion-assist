#!/usr/bin/env python3
"""
Test script for the Fashion Analysis Pipeline
"""

import sys
from pathlib import Path
from pipeline import FashionAnalysisPipeline

def test_pipeline_with_sample_url():
    """Test the pipeline with a sample fashion URL"""
    
    # Sample fashion URLs (you can modify these)
    test_urls = [
        "https://www.zara.com/us/en/textured-knit-sweater-p05755160.html",
        "https://www.uniqlo.com/us/en/products/E460582-000?colorCode=COL09",
        # Add more URLs here for testing
    ]
    
    print("🧪 Testing Fashion Analysis Pipeline")
    print("=" * 50)
    
    # Initialize pipeline
    try:
        pipeline = FashionAnalysisPipeline()
    except Exception as e:
        print(f"❌ Failed to initialize pipeline: {e}")
        return False
    
    # Test with each URL
    for i, url in enumerate(test_urls, 1):
        print(f"\n📋 Test {i}/{len(test_urls)}: {url}")
        print("-" * 80)
        
        try:
            results = pipeline.run_pipeline(url)
            
            if results.get('pipeline_success'):
                print(f"✅ Test {i} PASSED")
                print(f"   📁 Output: {results['output_directory']}")
                print(f"   🖼️ Gallery images: {len(results.get('all_images', []))}")
                print(f"   🏷️ Categories: {', '.join(results['generated_categories'])}")
                print(f"   📊 Top score: {results['all_images'][0]['final_score']:.1%}")
            else:
                print(f"❌ Test {i} FAILED: {results.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Test {i} CRASHED: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🏁 Testing completed!")
    return True

def demo_pipeline_features():
    """Demonstrate pipeline features"""
    
    print("\n🎯 Pipeline Features Demo")
    print("=" * 50)
    
    pipeline = FashionAnalysisPipeline()
    
    print("📦 Pipeline Components:")
    print(f"   🕷️ Scraper: {type(pipeline.scraper).__name__}")
    print(f"   👁️ Fashion-CLIP: {type(pipeline.fashion_clip).__name__}")
    print(f"   🧠 LLM Validator: {type(pipeline.llm_validator).__name__}")
    
    print("\n🔧 Pipeline Steps:")
    print("   1. 📥 Scrape product URL for description and images")
    print("   2. 🧠 Generate categories from description using LLM")  
    print("   3. 🖼️ Download all product images")
    print("   4. 👁️ Analyze images with Fashion-CLIP using generated categories")
    print("   5. 🔍 Validate with LLM for semantic consistency")
    print("   6. 🏆 Save all validated images to gallery")
    print("   7. 💾 Save results and analysis")

if __name__ == "__main__":
    print("👗 Fashion Analysis Pipeline Test Suite")
    print("=" * 60)
    
    # Show demo features
    demo_pipeline_features()
    
    # Ask user for URL to test
    print("\n" + "=" * 60)
    test_url = input("🔗 Enter a fashion product URL to test (or press Enter for sample): ").strip()
    
    if not test_url:
        print("📋 Using sample URLs for testing...")
        test_pipeline_with_sample_url()
    else:
        print(f"🧪 Testing with your URL: {test_url}")
        pipeline = FashionAnalysisPipeline()
        results = pipeline.run_pipeline(test_url)
        
        if results.get('pipeline_success'):
            print(f"\n🎉 SUCCESS! Check results at: {results['output_directory']}")
            print(f"📄 Gallery with {len(results.get('all_images', []))} images ready")
        else:
            print(f"\n💥 FAILED: {results.get('error', 'Unknown error')}")