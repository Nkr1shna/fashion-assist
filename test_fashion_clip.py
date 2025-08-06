import os
import glob
from models.fashion_clip import FashionCLIP
from pathlib import Path

def test_fashion_clip():
    """Test Fashion-CLIP on downloaded images"""
    
    print("🚀 Testing Fashion-CLIP Auto-Tagging Feature...")
    print("=" * 50)
    
    # Initialize Fashion-CLIP
    print("Loading Fashion-CLIP model...")
    try:
        fashion_clip = FashionCLIP()
        print("✅ Fashion-CLIP loaded successfully!")
    except Exception as e:
        print(f"❌ Failed to load Fashion-CLIP: {e}")
        return
    
    print()
    
    # Get test images
    test_images = glob.glob("data/test_images/*.jpg")
    
    if not test_images:
        print("❌ No test images found. Please run download_test_images.py first.")
        return
    
    print(f"📸 Found {len(test_images)} test images")
    print()
    
    # Test each image
    results = []
    
    for i, image_path in enumerate(test_images, 1):
        filename = Path(image_path).name
        print(f"[{i}/{len(test_images)}] Testing: {filename}")
        
        try:
            # Categorize the image
            analysis = fashion_clip.categorize_item(image_path)
            
            # Display results
            print(f"   Category: {analysis['category']}")
            print(f"   Color: {analysis['color']}")
            print(f"   Style: {analysis['style']}")
            print(f"   Confidence: {analysis['confidence']:.1%}")
            
            results.append({
                'filename': filename,
                'analysis': analysis,
                'success': True
            })
            
            print("   ✅ Success!")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                'filename': filename,
                'analysis': None,
                'success': False,
                'error': str(e)
            })
        
        print()
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    successful_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]
    
    print(f"✅ Successful: {len(successful_tests)}/{len(results)}")
    print(f"❌ Failed: {len(failed_tests)}/{len(results)}")
    
    if successful_tests:
        print("\n🎯 TAGGING RESULTS:")
        print("-" * 30)
        
        categories = {}
        colors = {}
        styles = {}
        
        for result in successful_tests:
            analysis = result['analysis']
            filename = result['filename']
            
            # Count categories
            cat = analysis['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(filename)
            
            # Count colors
            color = analysis['color']
            if color not in colors:
                colors[color] = []
            colors[color].append(filename)
            
            # Count styles
            style = analysis['style']
            if style not in styles:
                styles[style] = []
            styles[style].append(filename)
        
        print(f"Categories detected: {list(categories.keys())}")
        print(f"Colors detected: {list(colors.keys())}")
        print(f"Styles detected: {list(styles.keys())}")
        
        print("\n📋 DETAILED RESULTS:")
        print("-" * 30)
        for result in successful_tests:
            analysis = result['analysis']
            print(f"{result['filename']:20} → {analysis['color']} {analysis['category']} ({analysis['style']})")
    
    if failed_tests:
        print(f"\n❌ FAILED TESTS:")
        print("-" * 30)
        for result in failed_tests:
            print(f"{result['filename']} - {result.get('error', 'Unknown error')}")
    
    # Test completion
    if len(successful_tests) >= 5:
        print(f"\n🎉 FEATURE 1 TEST PASSED!")
        print(f"Fashion-CLIP successfully tagged {len(successful_tests)} clothing items!")
        print("✅ Auto-tagging functionality is working correctly.")
    else:
        print(f"\n⚠️  FEATURE 1 TEST WARNING:")
        print(f"Only {len(successful_tests)} items were successfully tagged.")
        print("Consider checking the model or image quality.")
    
    return results

if __name__ == "__main__":
    test_fashion_clip()