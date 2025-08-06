#!/usr/bin/env python3
"""
Simple CLI wrapper for the Fashion Analysis Pipeline
Usage: python run_pipeline.py <URL>
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from pipeline import FashionAnalysisPipeline

def main():
    """Main CLI function"""
    
    if len(sys.argv) < 2:
        print("👗 Fashion Analysis Pipeline")
        print("=" * 40)
        print("Usage: python run_pipeline.py <URL>")
        print("\nExample:")
        print("  python run_pipeline.py https://www.zara.com/us/en/product.html")
        print("\nThis will:")
        print("  1. 📥 Scrape the URL for product info and images")
        print("  2. 🧠 Generate categories using LLM")
        print("  3. 👁️ Analyze images with Fashion-CLIP")
        print("  4. 🔍 Validate with LLM")
        print("  5. 🏆 Save all validated images to gallery")
        print("  6. 💾 Save results to data/pipeline_output/")
        sys.exit(1)
    
    url = sys.argv[1]
    
    print(f"🚀 Running Fashion Analysis Pipeline")
    print(f"🔗 URL: {url}")
    print("=" * 60)
    
    try:
        # Initialize and run pipeline
        pipeline = FashionAnalysisPipeline()
        results = pipeline.run_pipeline(url)
        
        if results.get('pipeline_success'):
            print("\n" + "=" * 60)
            print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print(f"📁 Output Directory: {results['output_directory']}")
            print(f"🖼️ Gallery Images: {len(results.get('all_images', []))}")
            print(f"🏷️ Generated Categories: {', '.join(results['generated_categories'])}")
            
            # Show analysis details for top image
            all_images = results.get('all_images', [])
            if all_images:
                top_analysis = all_images[0]
                print(f"📊 Top Score: {top_analysis['final_score']:.1%}")
                
                fashion_clip_analysis = top_analysis.get('analysis', {})
                print(f"👁️ Fashion-CLIP: {fashion_clip_analysis.get('category', '?')} | {fashion_clip_analysis.get('color', '?')} | {fashion_clip_analysis.get('style', '?')}")
                
                llm_validation = top_analysis.get('llm_validation', {})
                if llm_validation.get('overall_match'):
                    print(f"🧠 LLM Validation: ✅ MATCH ({llm_validation.get('confidence', 0):.1%})")
                else:
                    print(f"🧠 LLM Validation: ❌ NO MATCH ({llm_validation.get('confidence', 0):.1%})")
                
                print(f"💡 Reason: {llm_validation.get('reason', 'No reason provided')}")
            
            # Show file structure
            output_dir = Path(results['output_directory'])
            print(f"\n📂 Files created:")
            for file in output_dir.iterdir():
                if file.is_file():
                    print(f"   📄 {file.name}")
            
        else:
            print("\n" + "=" * 60)
            print("❌ PIPELINE FAILED")
            print("=" * 60)
            print(f"💥 Error: {results.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()