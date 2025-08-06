import streamlit as st
import os
from pathlib import Path
import json
from models.fashion_clip import FashionCLIP
from models.llm_validator import LLMValidator
from utils.scraper import SimpleWebScraper

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

# Initialize LLM Validator (cached)
@st.cache_resource
def load_llm_validator():
    return LLMValidator()

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
    
    # Initialize scraper, Fashion-CLIP, and LLM validator
    scraper = SimpleWebScraper()
    fashion_clip = load_fashion_clip()
    llm_validator = load_llm_validator()
    
    url = st.text_input("Shopping URL", placeholder="https://example.com/product", help="Paste a link to any product from popular shopping sites")
    
    if url and st.button("🔍 Analyze Item", type="primary"):
        with st.spinner("Scraping product information..."):
            product_data = scraper.scrape_product(url)
        
        if product_data:
            st.success("Product analyzed successfully!")
            
            # Display product info
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if product_data["images"]:
                    # Download and validate images using Fashion-CLIP + LLM
                    with st.spinner("Downloading images and running AI validation..."):
                        validated_images = scraper.download_and_validate_images(product_data, fashion_clip, llm_validator)
                    
                    if validated_images:
                        # Show the best validated image
                        best_image = validated_images[0]
                        downloaded_path = best_image["path"]
                        final_score = best_image.get("final_score", 0.5)
                        llm_validation = best_image.get("llm_validation", {})
                        
                        st.image(downloaded_path, width=250, caption="Best Match Product Image")
                        
                        # Show LLM validation results
                        if llm_validation.get("overall_match", False):
                            st.success(f"✅ LLM Verified Match ({final_score:.1%} confidence)")
                        else:
                            st.error(f"❌ LLM Detected Mismatch ({final_score:.1%} confidence)")
                        
                        # Show detailed validation info
                        with st.expander("🔍 Validation Details"):
                            st.write(f"**LLM Reasoning:** {llm_validation.get('reason', 'No reason provided')}")
                            st.write(f"**Category Match:** {'✅' if llm_validation.get('category_match', False) else '❌'}")
                            st.write(f"**Color Match:** {'✅' if llm_validation.get('color_match', False) else '❌'}")
                            st.write(f"**LLM Confidence:** {llm_validation.get('confidence', 0):.1%}")
                            
                            # Show Fashion-CLIP analysis
                            analysis = best_image.get("analysis", {})
                            if analysis:
                                st.write("**Fashion-CLIP Detected:**")
                                st.write(f"- Category: {analysis.get('category', 'unknown')}")
                                st.write(f"- Color: {analysis.get('color', 'unknown')}")
                                st.write(f"- Style: {analysis.get('style', 'unknown')}")
                        
                        # Show other candidates if available
                        valid_alternatives = [img for img in validated_images[1:] if img.get("is_valid", False)]
                        if valid_alternatives:
                            with st.expander(f"View {len(valid_alternatives)} other valid images"):
                                for i, img_data in enumerate(valid_alternatives, 1):
                                    col_img, col_info, col_action = st.columns([1, 2, 1])
                                    with col_img:
                                        st.image(img_data["path"], width=100)
                                    with col_info:
                                        score = img_data.get("final_score", 0)
                                        llm_val = img_data.get("llm_validation", {})
                                        st.write(f"**Image {i+1}** - Score: {score:.1%}")
                                        st.write(f"Reason: {llm_val.get('reason', 'No reason')[:50]}...")
                                    with col_action:
                                        if st.button(f"Use This", key=f"use_img_{i}"):
                                            downloaded_path = img_data["path"]
                                            st.rerun()
                        
                        # Show rejected images
                        rejected_images = [img for img in validated_images if not img.get("is_valid", True)]
                        if rejected_images:
                            with st.expander(f"⚠️ {len(rejected_images)} images rejected by LLM"):
                                for i, img_data in enumerate(rejected_images, 1):
                                    col_img, col_info = st.columns([1, 3])
                                    with col_img:
                                        st.image(img_data["path"], width=80)
                                    with col_info:
                                        llm_val = img_data.get("llm_validation", {})
                                        st.write(f"**Rejected Image {i}**")
                                        st.write(f"Reason: {llm_val.get('reason', 'Unknown reason')}")
                                        analysis = img_data.get("analysis", {})
                                        if analysis:
                                            st.write(f"Detected: {analysis.get('category', '?')} - {analysis.get('color', '?')}")
                    else:
                        st.error("Could not download or validate any product images")
                        downloaded_path = None
                else:
                    st.warning("No product images found in webpage")
                    downloaded_path = None
            
            with col2:
                st.subheader("Product Information")
                st.write(f"**Title:** {product_data['title']}")
                st.write(f"**Price:** {product_data['price']}")
                st.write(f"**Description:** {product_data['description']}")
                
                # Show extracted context
                if product_data.get("context"):
                    context = product_data["context"]
                    st.write(f"**Brand:** {context['brand']}")
                    
                    if context.get("category_hints"):
                        st.write(f"**URL Category Hints:** {', '.join(context['category_hints'])}")
                    if context.get("color_hints"):
                        st.write(f"**Color Hints:** {', '.join(context['color_hints'])}")
                    if context.get("material_hints"):
                        st.write(f"**Materials:** {', '.join(context['material_hints'])}")
                
                # Analyze with Fashion-CLIP if image was downloaded
                if downloaded_path:
                    with st.spinner("Analyzing item category with AI..."):
                        analysis = fashion_clip.categorize_item(downloaded_path)
                    
                    st.divider()
                    st.subheader("AI Analysis vs Context")
                    
                    # Display analysis in a nice format
                    col2a, col2b, col2c = st.columns(3)
                    
                    with col2a:
                        ai_category = analysis['category'].title()
                        st.metric("AI Category", ai_category)
                        # Show if it matches context
                        context_cats = product_data.get("context", {}).get("category_hints", [])
                        if context_cats and analysis['category'].lower() in context_cats:
                            st.success("✅ Matches context")
                        elif context_cats:
                            st.warning("⚠️ Different from context")
                    
                    with col2b:
                        ai_color = analysis['color'].title()
                        st.metric("AI Color", ai_color)
                        # Show if it matches context
                        context_colors = product_data.get("context", {}).get("color_hints", [])
                        if context_colors and analysis['color'].lower() in context_colors:
                            st.success("✅ Matches context")
                        elif context_colors:
                            st.warning("⚠️ Different from context")
                    
                    with col2c:
                        ai_style = analysis['style'].title()
                        st.metric("AI Style", ai_style)
                        # Show if it matches context
                        context_styles = product_data.get("context", {}).get("style_hints", [])
                        if context_styles and analysis['style'].lower() in context_styles:
                            st.success("✅ Matches context")
                        elif context_styles:
                            st.info("ℹ️ No style context")
                    
                    # Confidence score
                    st.write("**AI Confidence:**")
                    st.progress(analysis['confidence'])
                    st.write(f"{analysis['confidence']:.1%}")
                    
                    # Save shopping item analysis
                    save_shopping_analysis(url, product_data, analysis, downloaded_path)
            
            # Compatibility with wardrobe
            st.divider()
            st.subheader("🤝 Wardrobe Compatibility")
            
            # Load wardrobe items
            wardrobe_summary = get_wardrobe_summary()
            
            if wardrobe_summary and wardrobe_summary['items'] and downloaded_path:
                st.write("Compatibility with your existing wardrobe items:")
                
                compatibility_scores = []
                
                # Calculate compatibility with each wardrobe item
                for item in wardrobe_summary['items']:
                    if os.path.exists(item['image_path']):
                        score = fashion_clip.compatibility_score(downloaded_path, item['image_path'])
                        compatibility_scores.append({
                            'item': item,
                            'score': score
                        })
                
                # Sort by compatibility score
                compatibility_scores.sort(key=lambda x: x['score'], reverse=True)
                
                # Display top 5 compatible items
                st.write("**Most Compatible Items:**")
                for i, comp in enumerate(compatibility_scores[:5]):
                    item = comp['item']
                    score = comp['score']
                    
                    col1, col2, col3 = st.columns([1, 2, 1])
                    
                    with col1:
                        if os.path.exists(item['image_path']):
                            st.image(item['image_path'], width=80)
                    
                    with col2:
                        st.write(f"**{item['color'].title()} {item['category'].title()}**")
                        st.write(f"Style: {item['style'].title()}")
                    
                    with col3:
                        # Color code the compatibility score
                        if score > 0.7:
                            st.success(f"{score:.1%}")
                        elif score > 0.5:
                            st.warning(f"{score:.1%}")
                        else:
                            st.error(f"{score:.1%}")
                
                # Overall compatibility summary
                avg_score = sum(comp['score'] for comp in compatibility_scores) / len(compatibility_scores)
                
                st.write("---")
                st.write("**Overall Compatibility Assessment:**")
                
                if avg_score > 0.7:
                    st.success(f"Excellent match! This item scores {avg_score:.1%} compatibility with your wardrobe.")
                    st.balloons()
                elif avg_score > 0.5:
                    st.warning(f"Good match. This item scores {avg_score:.1%} compatibility with your wardrobe.")
                else:
                    st.info(f"This item scores {avg_score:.1%} compatibility. Consider if it fits your style!")
                
            elif not wardrobe_summary or not wardrobe_summary['items']:
                st.info("Upload some wardrobe items first to see compatibility scores!")
            else:
                st.warning("Could not analyze compatibility - product image not available.")
        
        else:
            st.error("Could not analyze this URL. Please try a different product page or check that the URL is valid.")
    
    # Show recent shopping analysis if any
    if st.checkbox("Show Recent Analyses"):
        show_recent_shopping_analyses()

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

def save_shopping_analysis(url, product_data, analysis, image_path):
    """Save shopping analysis results to a JSON file"""
    try:
        # Load existing data or create new
        data_file = "data/shopping_items.json"
        os.makedirs("data", exist_ok=True)
        
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                data = json.load(f)
        else:
            data = {"items": []}
        
        # Add new item
        item_data = {
            "url": url,
            "title": product_data['title'],
            "price": product_data['price'],
            "description": product_data['description'],
            "image_path": image_path,
            "category": analysis['category'],
            "color": analysis['color'],
            "style": analysis['style'],
            "confidence": analysis['confidence'],
            "analyzed_at": str(Path().cwd())
        }
        
        # Check if item already exists (avoid duplicates)
        existing = [item for item in data["items"] if item["url"] == url]
        if not existing:
            data["items"].append(item_data)
            
            with open(data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
    except Exception as e:
        st.error(f"Error saving shopping analysis: {e}")

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

def show_recent_shopping_analyses():
    """Display recent shopping analyses"""
    try:
        data_file = "data/shopping_items.json"
        if not os.path.exists(data_file):
            st.info("No shopping analyses yet.")
            return
            
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        items = data.get("items", [])
        if not items:
            st.info("No shopping analyses yet.")
            return
        
        st.subheader("Recent Shopping Analyses")
        
        # Show last 5 analyses
        for item in reversed(items[-5:]):
            with st.expander(f"{item['title']} - {item['price']}"):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    if item.get('image_path') and os.path.exists(item['image_path']):
                        st.image(item['image_path'], width=150)
                
                with col2:
                    st.write(f"**Category:** {item['category'].title()}")
                    st.write(f"**Color:** {item['color'].title()}")
                    st.write(f"**Style:** {item['style'].title()}")
                    st.write(f"**Confidence:** {item['confidence']:.1%}")
                    st.write(f"**URL:** [View Product]({item['url']})")
                
    except Exception as e:
        st.error(f"Error showing recent analyses: {e}")

if __name__ == "__main__":
    main()