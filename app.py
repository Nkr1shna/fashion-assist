import streamlit as st
import os
from pathlib import Path
import json
from models.fashion_clip import FashionCLIP
from models.llm_validator import LLMValidator
from utils.scraper import SimpleWebScraper
from pipeline import FashionAnalysisPipeline

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

# Initialize Pipeline (cached)
@st.cache_resource
def load_fashion_analyzer():
    return FashionAnalysisPipeline()

def main():
    st.title("👗 Fashion Assist - AI Shopping Companion")
    st.markdown("*A proof of concept for AI-powered fashion assistance*")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📸 Upload Wardrobe", "🛍️ Shopping Analysis", "✨ Generate Outfit"])
    
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
    st.header("🛍️ Shopping Analysis")
    st.write("Paste a shopping URL to analyze compatibility with your wardrobe")
    
    st.info("**✨ AI-Powered Analysis!** Automatically generates categories from descriptions, "
           "analyzes all images with AI, and displays them in an interactive gallery.")
    
    # Use form to capture enter key presses properly
    with st.form("url_analysis_form", clear_on_submit=False):
        url = st.text_input("Shopping URL", placeholder="https://example.com/product", help="Paste a link to any product from popular shopping sites")
        
        # Button is always enabled - we'll validate after submission
        form_submitted = st.form_submit_button("🔍 Analyze Item", type="primary")
    
    # Add clear results button if analysis exists
    if 'analysis_results' in st.session_state and st.session_state.analysis_results:
        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("🗑️ Clear", help="Clear current analysis results"):
                del st.session_state.analysis_results
                if 'gallery_index' in st.session_state:
                    del st.session_state.gallery_index
                st.rerun()
    
    # Check if we have existing results in session state (for navigation persistence)
    if 'analysis_results' in st.session_state and st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        if results.get('pipeline_success'):
            st.success("🎉 Analysis Completed Successfully!")
            
            # Display image gallery and product info
            display_image_gallery(results)
            
            # Gallery statistics and overview
            with st.expander("📊 Gallery Statistics & Details"):
                display_gallery_statistics(results)
            
            # Analysis features highlight
            st.info("**🔍 Analysis Features:**\n"
                   "✅ AI-generated categories from description\n"
                   "✅ Enhanced Fashion-CLIP analysis\n"
                   "✅ Semantic validation with reasoning\n"
                   "✅ Interactive image gallery with sorting\n"
                   "✅ All images saved with confidence scores\n"
                   "✅ Complete JSON results saved")
            
            # Show file locations
            with st.expander("📁 Generated Files"):
                st.write(f"**Output Directory:** `{results['output_directory']}`")
                st.write(f"**Total Images:** {len(results.get('all_images', []))}")
                st.write(f"**Results JSON:** `{results['output_directory']}/pipeline_results.json`")
            
            # Compatibility with wardrobe - use first image for compatibility analysis
            st.divider()
            st.subheader("🤝 Wardrobe Compatibility")
            st.info("💡 Use the gallery above to navigate through images. Compatibility is calculated for the currently selected image.")
            
            # Get the currently selected image from the gallery
            all_images = results.get('all_images', [])
            if all_images:
                # Get the currently selected image based on gallery navigation
                current_index = st.session_state.get('gallery_index', 0)
                if current_index < len(all_images):
                    current_image_path = all_images[current_index].get('saved_path') or all_images[current_index].get('path')
                    show_wardrobe_compatibility(current_image_path)
                else:
                    # Fallback to first image if index is invalid
                    first_image_path = all_images[0].get('saved_path') or all_images[0].get('path')
                    show_wardrobe_compatibility(first_image_path)
            else:
                st.warning("No images available for compatibility analysis.")
        else:
            st.error(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
            st.write("Please try a different URL or check the error details above.")
    
    # Handle form submission
    elif form_submitted:
        if not url.strip():
            st.error("⚠️ Please enter a valid URL before analyzing.")
            return
        
        # Clear any existing analysis results when starting new analysis
        if 'analysis_results' in st.session_state:
            del st.session_state.analysis_results
        
        # Analysis only starts with valid URL after form submission
        analyzer = load_fashion_analyzer()
        
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("🔧 Setting up analysis...")
            progress_bar.progress(10)
            
            status_text.text("📥 Scraping product information...")
            progress_bar.progress(20)
            
            # Run the analysis
            with st.spinner("Running complete fashion analysis..."):
                results = analyzer.run_pipeline(url, "data/streamlit_analysis")
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis completed!")
            
            # Store results in session state for navigation persistence
            st.session_state.analysis_results = results
            
            if results.get('pipeline_success'):
                st.success("🎉 Analysis Completed Successfully!")
                
                # Display image gallery and product info
                display_image_gallery(results)
                
                # Gallery statistics and overview
                with st.expander("📊 Gallery Statistics & Details"):
                    display_gallery_statistics(results)
                
                # Analysis features highlight
                st.info("**🔍 Analysis Features:**\n"
                       "✅ AI-generated categories from description\n"
                       "✅ Enhanced Fashion-CLIP analysis\n"
                       "✅ Semantic validation with reasoning\n"
                       "✅ Interactive image gallery with sorting\n"
                       "✅ All images saved with confidence scores\n"
                       "✅ Complete JSON results saved")
                
                # Show file locations
                with st.expander("📁 Generated Files"):
                    st.write(f"**Output Directory:** `{results['output_directory']}`")
                    st.write(f"**Total Images:** {len(results.get('all_images', []))}")
                    st.write(f"**Results JSON:** `{results['output_directory']}/pipeline_results.json`")
                
                # Compatibility with wardrobe - use first image for compatibility analysis
                st.divider()
                st.subheader("🤝 Wardrobe Compatibility")
                st.info("💡 Use the gallery above to navigate through images. Compatibility is calculated for the currently selected image.")
                
                # Get the currently selected image from the gallery
                all_images = results.get('all_images', [])
                if all_images:
                    # Get the currently selected image based on gallery navigation
                    current_index = st.session_state.get('gallery_index', 0)
                    if current_index < len(all_images):
                        current_image_path = all_images[current_index].get('saved_path') or all_images[current_index].get('path')
                        show_wardrobe_compatibility(current_image_path)
                    else:
                        # Fallback to first image if index is invalid
                        first_image_path = all_images[0].get('saved_path') or all_images[0].get('path')
                        show_wardrobe_compatibility(first_image_path)
                else:
                    st.warning("No images available for compatibility analysis.")
                
            else:
                st.error(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
                st.write("Please try a different URL or check the error details above.")
                
        except Exception as e:
            st.error(f"💥 Analysis error: {e}")
            import traceback
            with st.expander("🔍 Error Details"):
                st.code(traceback.format_exc())
        finally:
            progress_bar.empty()
            status_text.empty()
    
    # Show recent shopping analysis if any
    if st.checkbox("Show Recent Analyses"):
        show_recent_shopping_analyses()

def show_wardrobe_compatibility(image_path):
    """Show compatibility analysis with wardrobe items"""
    st.subheader("🤝 Wardrobe Compatibility")
    
    if not image_path or not os.path.exists(image_path):
        st.warning("Could not analyze compatibility - product image not available.")
        return
    
    # Load wardrobe items
    wardrobe_summary = get_wardrobe_summary()
    fashion_clip = load_fashion_clip()
    
    if wardrobe_summary and wardrobe_summary['items']:
        st.write("Compatibility with your existing wardrobe items:")
        
        compatibility_scores = []
        
        # Calculate compatibility with each wardrobe item
        for item in wardrobe_summary['items']:
            if os.path.exists(item['image_path']):
                score = fashion_clip.compatibility_score(image_path, item['image_path'])
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
        
    else:
        st.info("Upload some wardrobe items first to see compatibility scores!")

def outfit_generation():
    st.header("Generate Outfit")
    st.write("Create outfit combinations with AI")
    
    st.info("✨ This feature will be implemented in Feature 3!")
    st.write("Upload wardrobe items first, then we'll generate amazing outfit combinations!")

def display_image_gallery(results):
    """Display all scraped images in a gallery format with navigation and sorting"""
    
    all_images = results.get('all_images', [])
    
    if not all_images:
        st.warning("No images found in analysis results.")
        return
    
    st.subheader(f"🖼️ Image Gallery ({len(all_images)} images)")
    
    # Sort options
    sort_col1, sort_col2 = st.columns([1, 3])
    
    with sort_col1:
        sort_order = st.selectbox(
            "Sort by",
            ["Confidence Score ↓", "Confidence Score ↑"],
            key="gallery_sort"
        )
    
    # Sort images based on selection
    if sort_order == "Confidence Score ↑":
        sorted_images = sorted(all_images, key=lambda x: x.get('final_score', 0))
    else:  # Default: Confidence Score ↓
        sorted_images = sorted(all_images, key=lambda x: x.get('final_score', 0), reverse=True)
    
    # Initialize session state for gallery navigation
    if "gallery_index" not in st.session_state:
        st.session_state.gallery_index = 0
    
    # Reset index if it's out of bounds (e.g., after sorting)
    if st.session_state.gallery_index >= len(sorted_images):
        st.session_state.gallery_index = 0
    
    current_index = st.session_state.gallery_index
    
    # Display current image and its analysis
    current_image = sorted_images[current_index]
    
    # Main display area with navigation
    gallery_col1, gallery_col2 = st.columns([1, 1])
    
    with gallery_col1:
        # Image navigation with arrow buttons
        if len(sorted_images) > 1:
            nav_col1, nav_col2, nav_col3 = st.columns([1, 6, 1])
            
            with nav_col1:
                if st.button("◀", key="prev_image", help="Previous image") and current_index > 0:
                    st.session_state.gallery_index = current_index - 1
                    st.rerun()
            
            with nav_col3:
                if st.button("▶", key="next_image", help="Next image") and current_index < len(sorted_images) - 1:
                    st.session_state.gallery_index = current_index + 1
                    st.rerun()
            
            with nav_col2:
                # Display the current image
                image_path = current_image.get('saved_path') or current_image.get('path')
                if image_path and os.path.exists(image_path):
                    st.image(image_path, caption=f"Image {current_index + 1} of {len(sorted_images)}", use_column_width=True)
                else:
                    st.error("Image file not found")
        else:
            # Single image, no navigation needed
            image_path = current_image.get('saved_path') or current_image.get('path')
            if image_path and os.path.exists(image_path):
                st.image(image_path, caption=f"Image {current_index + 1} of {len(sorted_images)}", use_column_width=True)
            else:
                st.error("Image file not found")
        
        # Display confidence score with visual indicator
        final_score = current_image.get('final_score', 0)
        
        if final_score > 0.8:
            st.success(f"🏆 Excellent Match: {final_score:.1%}")
        elif final_score > 0.6:
            st.warning(f"✓ Good Match: {final_score:.1%}")
        else:
            st.info(f"⚠️ Uncertain Match: {final_score:.1%}")
        
        # Progress bar for confidence
        st.progress(final_score)
        
        # Image analysis details
        analysis = current_image.get('analysis', {})
        if analysis:
            st.write("**Fashion-CLIP Analysis:**")
            detail_col1, detail_col2 = st.columns(2)
            with detail_col1:
                st.metric("Category", analysis.get('category', 'Unknown').title())
                st.metric("Color", analysis.get('color', 'Unknown').title())
            with detail_col2:
                st.metric("Style", analysis.get('style', 'Unknown').title())
                st.metric("FC Confidence", f"{analysis.get('confidence', 0):.1%}")
    
    with gallery_col2:
        # Product information
        product_data = results['product_data']
        st.subheader("Product Information")
        st.write(f"**Title:** {product_data['title']}")
        st.write(f"**Price:** {product_data['price']}")
        st.write(f"**Description:** {product_data['description'][:200]}...")
        
        # Generated categories
        st.subheader("🧠 AI-Generated Categories")
        categories = results['generated_categories']
        if categories:
            for i, cat in enumerate(categories, 1):
                st.write(f"{i}. {cat}")
        else:
            st.write("No specific categories generated")
        
        # LLM validation for current image
        llm_validation = current_image.get('llm_validation', {})
        if llm_validation:
            st.subheader("🧠 LLM Validation")
            match_status = "✅ MATCH" if llm_validation.get('overall_match') else "❌ NO MATCH"
            st.write(f"**Result:** {match_status}")
            st.write(f"**Confidence:** {llm_validation.get('confidence', 0):.1%}")
            
            if llm_validation.get('reason'):
                st.write(f"**Reasoning:** {llm_validation['reason']}")
    



def display_gallery_statistics(results):
    """Display statistics and overview of all images in the gallery"""
    
    all_images = results.get('all_images', [])
    
    if not all_images:
        st.warning("No images to analyze.")
        return
    
    # Calculate statistics
    scores = [img.get('final_score', 0) for img in all_images]
    avg_score = sum(scores) / len(scores)
    max_score = max(scores)
    min_score = min(scores)
    
    # Score distribution
    excellent_count = len([s for s in scores if s > 0.8])
    good_count = len([s for s in scores if 0.6 < s <= 0.8])
    uncertain_count = len([s for s in scores if s <= 0.6])
    
    # Display overview metrics
    st.subheader("📈 Score Overview")
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.metric("Total Images", len(all_images))
    with stat_col2:
        st.metric("Avg Score", f"{avg_score:.1%}")
    with stat_col3:
        st.metric("Best Score", f"{max_score:.1%}")
    with stat_col4:
        st.metric("Worst Score", f"{min_score:.1%}")
    
    # Score distribution
    st.subheader("🎯 Score Distribution")
    dist_col1, dist_col2, dist_col3 = st.columns(3)
    
    with dist_col1:
        st.metric("🟢 Excellent (>80%)", excellent_count)
    with dist_col2:
        st.metric("🟡 Good (60-80%)", good_count)
    with dist_col3:
        st.metric("🔴 Uncertain (<60%)", uncertain_count)
    
    # Detailed breakdown
    st.subheader("🔍 Detailed Analysis Breakdown")
    
    for i, img in enumerate(all_images):
        with st.expander(f"Image #{i+1} - Score: {img.get('final_score', 0):.1%}"):
            detail_col1, detail_col2 = st.columns(2)
            
            with detail_col1:
                st.write("**👁️ Fashion-CLIP Analysis:**")
                fc_analysis = img.get('analysis', {})
                st.write(f"- **Category:** {fc_analysis.get('category', 'unknown')}")
                st.write(f"- **Color:** {fc_analysis.get('color', 'unknown')}")
                st.write(f"- **Style:** {fc_analysis.get('style', 'unknown')}")
                st.write(f"- **Confidence:** {fc_analysis.get('confidence', 0):.1%}")
                
                # Enhanced analysis if available
                enhanced = img.get('enhanced_analysis', {})
                if enhanced:
                    st.write("**🎯 Enhanced Analysis:**")
                    st.write(f"- **Best Match:** {enhanced.get('best_category_match', 'N/A')}")
                    st.write(f"- **Similarity:** {enhanced.get('max_similarity', 0):.1%}")
            
            with detail_col2:
                st.write("**🧠 LLM Validation:**")
                llm_val = img.get('llm_validation', {})
                if llm_val:
                    match_status = "✅ MATCH" if llm_val.get('overall_match') else "❌ NO MATCH"
                    st.write(f"- **Result:** {match_status}")
                    st.write(f"- **Confidence:** {llm_val.get('confidence', 0):.1%}")
                    st.write(f"- **Category Match:** {'✅' if llm_val.get('category_match') else '❌'}")
                    st.write(f"- **Color Match:** {'✅' if llm_val.get('color_match') else '❌'}")
                    st.write(f"- **Reasoning:** {llm_val.get('reason', 'No reason provided')}")
                else:
                    st.write("LLM validation not available")


def save_analysis_to_file(filename, analysis, image_path):
    """Save wardrobe analysis to JSON storage"""
    try:
        data_file = "data/wardrobe_items.json"
        os.makedirs("data", exist_ok=True)
        
        # Load existing data
        data = {"items": []}
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                data = json.load(f)
        
        # Create item data
        item_data = {
            "filename": filename,
            "image_path": image_path,
            "category": analysis['category'],
            "color": analysis['color'], 
            "style": analysis['style'],
            "confidence": analysis['confidence'],
            "uploaded_at": Path().cwd().as_posix()  # Better timestamp handling
        }
        
        # Avoid duplicates
        existing_files = {item.get("filename") for item in data["items"]}
        if filename not in existing_files:
            data["items"].append(item_data)
            
            with open(data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
    except Exception as e:
        st.error(f"Error saving analysis: {e}")
        import logging
        logging.error(f"Failed to save analysis for {filename}: {e}")

# Removed redundant save_shopping_analysis function - now handled by pipeline

def get_wardrobe_summary():
    """Get wardrobe statistics and items"""
    try:
        data_file = "data/wardrobe_items.json"
        if not os.path.exists(data_file):
            return None
            
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        items = data.get("items", [])
        if not items:
            return None
        
        # Calculate statistics
        categories = {item['category'] for item in items}
        colors = {item['color'] for item in items}
        
        return {
            "total_items": len(items),
            "categories": list(categories),
            "colors": list(colors),
            "items": items
        }
        
    except Exception as e:
        st.error(f"Error loading wardrobe data: {e}")
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