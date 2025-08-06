import streamlit as st
import os
from pathlib import Path
import json
from models.fashion_clip import FashionCLIP

# Configure page
st.set_page_config(
    page_title="Fashion Assist POC",
    page_icon="👗",
    layout="wide"
)

# Initialize Fashion-CLIP (cached)
@st.cache_resource
def load_fashion_clip():
    return FashionCLIP()

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
    
    # Initialize Fashion-CLIP
    fashion_clip = load_fashion_clip()
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose clothing images",
        accept_multiple_files=True,
        type=['png', 'jpg', 'jpeg'],
        help="Upload multiple images of your clothing items for AI analysis"
    )
    
    if uploaded_files:
        st.success(f"Uploaded {len(uploaded_files)} items!")
        
        # Process each uploaded file
        for i, file in enumerate(uploaded_files):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(file, width=200, caption=f"Item {i+1}")
            
            with col2:
                st.write(f"**{file.name}**")
                
                # Save file temporarily and analyze
                temp_path = f"data/wardrobe/{file.name}"
                os.makedirs("data/wardrobe", exist_ok=True)
                
                with open(temp_path, "wb") as f:
                    f.write(file.read())
                
                # Analyze with Fashion-CLIP
                with st.spinner("Analyzing with AI..."):
                    analysis = fashion_clip.categorize_item(temp_path)
                
                # Display results in a nice format
                col2a, col2b, col2c = st.columns(3)
                
                with col2a:
                    st.metric("Category", analysis['category'].title())
                
                with col2b:
                    st.metric("Color", analysis['color'].title())
                
                with col2c:
                    st.metric("Style", analysis['style'].title())
                
                # Confidence score with progress bar
                st.write("**Confidence Score:**")
                st.progress(analysis['confidence'])
                st.write(f"{analysis['confidence']:.1%}")
                
                # Save analysis to JSON file for later use
                save_analysis_to_file(file.name, analysis, temp_path)
                
                st.divider()
        
        # Show summary
        st.subheader("Wardrobe Summary")
        summary = get_wardrobe_summary()
        if summary:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Items", summary.get('total_items', 0))
            with col2:
                st.metric("Categories", len(summary.get('categories', [])))
            with col3:
                st.metric("Colors", len(summary.get('colors', [])))

def shopping_analysis():
    st.header("Analyze Shopping Item")
    st.write("Paste a shopping URL to analyze compatibility with your wardrobe")
    
    st.info("📋 This feature will be implemented in Feature 2!")
    st.write("For now, focus on uploading your wardrobe items in the first tab.")

def outfit_generation():
    st.header("Generate Outfit")
    st.write("Create outfit combinations with AI")
    
    st.info("✨ This feature will be implemented in Feature 3!")
    st.write("Upload wardrobe items first, then we'll generate amazing outfit combinations!")

def save_analysis_to_file(filename, analysis, image_path):
    """Save analysis results to a JSON file"""
    try:
        # Load existing data or create new
        data_file = "data/wardrobe_items.json"
        os.makedirs("data", exist_ok=True)
        
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                data = json.load(f)
        else:
            data = {"items": []}
        
        # Add new item
        item_data = {
            "filename": filename,
            "image_path": image_path,
            "category": analysis['category'],
            "color": analysis['color'],
            "style": analysis['style'],
            "confidence": analysis['confidence'],
            "uploaded_at": str(Path().cwd())
        }
        
        # Check if item already exists (avoid duplicates)
        existing = [item for item in data["items"] if item["filename"] == filename]
        if not existing:
            data["items"].append(item_data)
            
            with open(data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
    except Exception as e:
        st.error(f"Error saving analysis: {e}")

def get_wardrobe_summary():
    """Get summary statistics of wardrobe items"""
    try:
        data_file = "data/wardrobe_items.json"
        if not os.path.exists(data_file):
            return None
            
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        items = data.get("items", [])
        if not items:
            return None
        
        categories = set(item['category'] for item in items)
        colors = set(item['color'] for item in items)
        
        return {
            "total_items": len(items),
            "categories": list(categories),
            "colors": list(colors),
            "items": items
        }
        
    except Exception as e:
        st.error(f"Error getting summary: {e}")
        return None

if __name__ == "__main__":
    main()