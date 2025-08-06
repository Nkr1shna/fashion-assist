import requests
import os
from pathlib import Path

def download_test_images():
    """Download test clothing images from the internet"""
    
    # Create test images directory
    test_dir = "data/test_images"
    os.makedirs(test_dir, exist_ok=True)
    
    # List of test clothing images (using placeholder and public domain images)
    test_images = {
        "blue_jeans.jpg": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=400&h=400&fit=crop",
        "red_dress.jpg": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400&h=400&fit=crop",
        "white_shirt.jpg": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop",
        "black_jacket.jpg": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400&h=400&fit=crop",
        "brown_shoes.jpg": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400&h=400&fit=crop",
        "green_hoodie.jpg": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400&h=400&fit=crop",
        "gray_sweater.jpg": "https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=400&h=400&fit=crop",
        "yellow_tshirt.jpg": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop&sat=-100&hue=60",
        "navy_blazer.jpg": "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=400&h=400&fit=crop",
        "pink_skirt.jpg": "https://images.unsplash.com/photo-1583496661160-fb5886a13d75?w=400&h=400&fit=crop"
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    downloaded_count = 0
    
    for filename, url in test_images.items():
        try:
            print(f"Downloading {filename}...")
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            file_path = os.path.join(test_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Downloaded {filename}")
            downloaded_count += 1
            
        except Exception as e:
            print(f"❌ Failed to download {filename}: {e}")
    
    print(f"\n🎉 Downloaded {downloaded_count}/{len(test_images)} test images!")
    print(f"Images saved to: {test_dir}")
    
    return downloaded_count

if __name__ == "__main__":
    download_test_images()