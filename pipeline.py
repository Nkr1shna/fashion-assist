#!/usr/bin/env python3
"""
Complete Fashion Analysis Pipeline
Scrapes product URL, analyzes images with Fashion-CLIP + LLM, displays all images in gallery
"""

import os
import sys
import shutil
from pathlib import Path
import json
import hashlib
from typing import Dict, List, Optional
import torch

# Add project root to Python path
sys.path.append(str(Path(__file__).parent))

from models.fashion_clip import FashionCLIP
from models.llm_validator import LLMValidator
from utils.scraper import SimpleWebScraper


class FashionAnalysisPipeline:
    """Complete pipeline for analyzing fashion items from URLs"""
    
    def __init__(self):
        """Initialize all components"""
        print("🔧 Initializing Fashion Analysis Pipeline...")
        
        # Initialize components
        self.scraper = SimpleWebScraper()
        self.fashion_clip = FashionCLIP()
        self.llm_validator = LLMValidator()
        
        print("✅ Pipeline ready!")
    
    def run_pipeline(self, url: str, output_dir: str = "data/pipeline_output") -> Dict:
        """
        Complete pipeline:
        1. Scrape URL description and generate LLM categories
        2. Download all images from URL
        3. Run images through Fashion-CLIP with generated categories
        4. Save all validated images to gallery
        
        Args:
            url: Product URL to analyze
            output_dir: Directory to save results
            
        Returns:
            Dict with analysis results and paths
        """
        print(f"\n🚀 Starting pipeline for: {url}")
        
        try:
            # Step 1: Scrape product info and generate categories
            print("\n📥 Step 1: Scraping product information...")
            product_data = self.scraper.scrape_product(url)
            
            if not product_data:
                raise Exception("Failed to scrape product data")
            
            print(f"   ✅ Scraped: {product_data['title']}")
            print(f"   📝 Description: {product_data['description'][:100]}...")
            
            # Generate categories using LLM
            print("\n🧠 Step 1.5: Generating categories with LLM...")
            generated_categories = self.generate_categories_from_description(product_data)
            product_data['generated_categories'] = generated_categories
            print(f"   ✅ Generated categories: {', '.join(generated_categories)}")
            
            # Step 2: Download and analyze images
            print(f"\n🖼️ Step 2: Downloading {len(product_data.get('images', []))} images...")
            if not product_data.get('images'):
                raise Exception("No images found in the product page")
            
            # Create unique output directory for this URL
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            work_dir = Path(output_dir) / f"analysis_{url_hash}"
            work_dir.mkdir(parents=True, exist_ok=True)
            
            # Step 3: Enhanced image validation with generated categories
            print("\n🔍 Step 3: Running enhanced Fashion-CLIP analysis...")
            validated_images = self.enhanced_image_validation(
                product_data, 
                str(work_dir),
                generated_categories
            )
            
            if not validated_images:
                raise Exception("No valid images found after analysis")
            
            # Step 4: Save all images to work directory and keep paths
            print(f"\n💾 Step 4: Saving all validated images... (count: {len(validated_images)})")
            all_image_paths = self.save_all_images(validated_images, str(work_dir))
            
            # Prepare final results - focus on gallery, not single best image
            results = {
                "url": url,
                "product_data": product_data,
                "generated_categories": generated_categories,
                "all_images": validated_images,  # Include all validated images
                "all_image_paths": all_image_paths,  # Include all saved paths
                "output_directory": str(work_dir),
                "pipeline_success": True
            }
            
            # Save results
            results_file = work_dir / "pipeline_results.json"
            with open(results_file, 'w') as f:
                # Create a JSON-serializable version
                json_results = {
                    "url": results["url"],
                    "product_title": results["product_data"]["title"],
                    "product_description": results["product_data"]["description"],
                    "generated_categories": results["generated_categories"],
                    "all_images_analysis": [
                        {
                            "path": img.get("saved_path", img.get("path")),
                            "fashion_clip_analysis": img.get("analysis", {}),
                            "llm_validation": img.get("llm_validation", {}),
                            "final_score": img.get("final_score", 0),
                            "enhanced_analysis": img.get("enhanced_analysis", {})
                        }
                        for img in results["all_images"]
                    ],
                    "total_images": len(results["all_images"]),
                    "output_directory": results["output_directory"]
                }
                json.dump(json_results, f, indent=2)
            
            print(f"\n🎉 Pipeline completed successfully!")
            print(f"   📁 Output directory: {work_dir}")
            print(f"   🖼️ Total images saved: {len(validated_images)}")
            print(f"   🏆 Gallery ready with {len(validated_images)} images")
            print(f"   💾 Results saved: {results_file}")
            
            return results
            
        except Exception as e:
            print(f"\n❌ Pipeline failed: {e}")
            return {
                "url": url,
                "error": str(e),
                "pipeline_success": False
            }
    
    def generate_categories_from_description(self, product_data: Dict) -> List[str]:
        """Generate fashion categories from product description using LLM"""
        
        title = product_data.get('title', '')
        description = product_data.get('description', '')
        context = product_data.get('context', {})
        
        # Combine all text context
        combined_text = f"{title} {description}"
        category_hints = context.get('category_hints', [])
        color_hints = context.get('color_hints', [])
        
        # Use LLM to generate categories if available
        if self.llm_validator.model:
            try:
                categories = self._llm_generate_categories(combined_text, category_hints, color_hints)
                if categories:
                    return categories
            except Exception as e:
                print(f"   ⚠️ LLM category generation failed: {e}")
        
        # Fallback to rule-based category extraction
        print("   📋 Using rule-based category extraction...")
        return self._rule_based_categories(combined_text, category_hints, color_hints)
    
    def _llm_generate_categories(self, text: str, category_hints: List[str], color_hints: List[str]) -> List[str]:
        """Use LLM to generate categories from text description"""
        
        prompt = f"""Analyze this fashion product description and generate relevant categories for image analysis.

PRODUCT DESCRIPTION:
{text[:500]}

URL HINTS:
- Categories: {', '.join(category_hints) if category_hints else 'none'}
- Colors: {', '.join(color_hints) if color_hints else 'none'}

TASK: Generate 3-5 specific fashion categories that would help identify this item in images.

Categories should be specific like:
- "black leather jacket"
- "blue denim jeans" 
- "white cotton t-shirt"
- "red summer dress"
- "brown leather boots"

Format your response as a simple list, one category per line, starting with a dash.

Categories:"""

        try:
            # Prepare messages
            messages = [
                {"role": "system", "content": "You are a fashion expert who generates precise categories for image recognition."},
                {"role": "user", "content": prompt}
            ]
            
            # Apply chat template
            if hasattr(self.llm_validator.tokenizer, 'apply_chat_template'):
                text = self.llm_validator.tokenizer.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
            else:
                text = f"<|im_start|>system\nYou are a fashion expert who generates precise categories for image recognition.<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
            
            # Generate
            model_inputs = self.llm_validator.tokenizer([text], return_tensors="pt").to(self.llm_validator.device)
            
            with torch.no_grad():
                generated_ids = self.llm_validator.model.generate(
                    model_inputs.input_ids,
                    max_new_tokens=100,
                    do_sample=True,
                    temperature=0.3,
                    pad_token_id=self.llm_validator.tokenizer.eos_token_id
                )
            
            # Decode
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            response = self.llm_validator.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            # Parse categories from response
            categories = []
            for line in response.split('\n'):
                line = line.strip()
                if line.startswith('-'):
                    category = line[1:].strip()
                    if category and len(category) > 3:
                        categories.append(category)
            
            return categories[:5]  # Limit to 5 categories
            
        except Exception as e:
            print(f"   ⚠️ LLM generation error: {e}")
            return []
    
    def _rule_based_categories(self, text: str, category_hints: List[str], color_hints: List[str]) -> List[str]:
        """Fallback rule-based category generation"""
        
        text_lower = text.lower()
        categories = []
        
        # Start with URL category hints
        if category_hints:
            categories.extend(category_hints)
        
        # Add color + category combinations
        if color_hints and category_hints:
            for color in color_hints[:2]:  # Limit colors
                for category in category_hints[:2]:  # Limit categories
                    categories.append(f"{color} {category}")
        
        # Fallback to basic categories if nothing found
        if not categories:
            basic_categories = {
                'shirt': ['shirt', 'blouse', 'top'],
                'pants': ['pants', 'trousers', 'jeans'],
                'dress': ['dress', 'gown'],
                'jacket': ['jacket', 'blazer', 'coat'],
                'shoes': ['shoes', 'sneakers', 'boots']
            }
            
            for category, keywords in basic_categories.items():
                if any(keyword in text_lower for keyword in keywords):
                    categories.append(category)
        
        return categories[:5]  # Limit to 5
    
    def enhanced_image_validation(self, product_data: Dict, work_dir: str, generated_categories: List[str]) -> List[Dict]:
        """Enhanced image validation using generated categories"""
        
        # Download and validate images using existing scraper method
        print("   🔍 Running Fashion-CLIP + LLM validation...")
        validated_images = self.scraper.download_and_validate_images(
            product_data, 
            self.fashion_clip, 
            self.llm_validator
        )
        
        if not validated_images:
            return []
        
        # Enhance analysis with generated categories
        print("   🎯 Enhancing analysis with generated categories...")
        for img_data in validated_images:
            # Get additional Fashion-CLIP analysis with generated categories
            if generated_categories:
                enhanced_analysis = self._analyze_with_custom_categories(
                    img_data['path'], 
                    generated_categories
                )
                img_data['enhanced_analysis'] = enhanced_analysis
                
                # Update final score considering category match
                category_boost = self._calculate_category_boost(
                    enhanced_analysis, 
                    generated_categories
                )
                img_data['final_score'] = min(1.0, img_data.get('final_score', 0.5) + category_boost)
        
        # Re-sort by enhanced final score
        validated_images.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        
        print(f"   ✅ Validated {len(validated_images)} images")
        for i, img in enumerate(validated_images[:3]):  # Show top 3
            score = img.get('final_score', 0)
            analysis = img.get('analysis', {})
            print(f"      #{i+1}: {score:.1%} - {analysis.get('category', '?')} {analysis.get('color', '?')}")
        
        return validated_images
    
    def _analyze_with_custom_categories(self, image_path: str, categories: List[str]) -> Dict:
        """Analyze image with custom generated categories"""
        
        try:
            # Load and preprocess image
            from PIL import Image
            import torch
            
            image = Image.open(image_path).convert('RGB')
            image_input = self.fashion_clip.preprocess(image).unsqueeze(0).to(self.fashion_clip.device)
            
            # Encode image
            with torch.no_grad():
                image_features = self.fashion_clip.model.encode_image(image_input)
                image_features /= image_features.norm(dim=-1, keepdim=True)
            
            # Test against generated categories
            category_prompts = [f"a photo of {cat}" for cat in categories]
            
            if category_prompts:
                best_match = self.fashion_clip._classify_with_labels(image_features, category_prompts)
                
                # Calculate similarity scores for all categories
                text_tokens = self.fashion_clip.tokenizer(category_prompts).to(self.fashion_clip.device)
                
                with torch.no_grad():
                    text_features = self.fashion_clip.model.encode_text(text_tokens)
                    text_features /= text_features.norm(dim=-1, keepdim=True)
                    similarities = (image_features @ text_features.T).squeeze(0)
                
                # Get top matches
                top_indices = similarities.argsort(descending=True)[:3]
                top_matches = [(categories[i], similarities[i].item()) for i in top_indices]
                
                return {
                    "best_category_match": best_match.replace("a photo of ", ""),
                    "top_matches": top_matches,
                    "max_similarity": similarities.max().item()
                }
        
        except Exception as e:
            print(f"   ⚠️ Custom category analysis failed: {e}")
        
        return {"best_category_match": "unknown", "top_matches": [], "max_similarity": 0.0}
    
    def _calculate_category_boost(self, enhanced_analysis: Dict, generated_categories: List[str]) -> float:
        """Calculate boost to final score based on category match"""
        
        max_similarity = enhanced_analysis.get('max_similarity', 0.0)
        
        # Boost score if we have a good match with generated categories
        if max_similarity > 0.8:
            return 0.2  # Strong boost
        elif max_similarity > 0.6:
            return 0.1  # Moderate boost
        elif max_similarity > 0.4:
            return 0.05  # Small boost
        
        return 0.0  # No boost
    
    def save_all_images(self, validated_images: List[Dict], work_dir: str) -> List[str]:
        """Save all validated images to the work directory and return their paths"""
        
        if not validated_images:
            raise Exception("No images to save")
        
        saved_paths = []
        work_dir_path = Path(work_dir)
        
        print(f"   💾 Saving {len(validated_images)} validated images...")
        
        for i, img_data in enumerate(validated_images):
            src_path = img_data['path']
            score = img_data.get('final_score', 0)
            
            # Create descriptive filename with score
            filename = f"image_{i+1}_score_{score:.0%}.jpg"
            dest_path = work_dir_path / filename
            
            try:
                # Copy image to work directory
                shutil.copy2(src_path, dest_path)
                saved_paths.append(str(dest_path))
                
                # Update the image data with the new path
                img_data['saved_path'] = str(dest_path)
                
                print(f"   📁 #{i+1}: {filename} (score: {score:.1%})")
                
            except Exception as e:
                print(f"   ⚠️ Could not save {src_path}: {e}")
        
        print(f"   ✅ Saved {len(saved_paths)} images to gallery")
        
        return saved_paths


def main():
    """Command line interface for the pipeline"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fashion Analysis Pipeline")
    parser.add_argument("url", help="Product URL to analyze")
    parser.add_argument("--output", "-o", default="data/pipeline_output", 
                       help="Output directory (default: data/pipeline_output)")
    
    args = parser.parse_args()
    
    # Run pipeline
    pipeline = FashionAnalysisPipeline()
    results = pipeline.run_pipeline(args.url, args.output)
    
    if results.get('pipeline_success'):
        print(f"\n✅ Success! Results saved to: {results['output_directory']}")
        print(f"📄 Gallery with {len(results.get('all_images', []))} images ready")
    else:
        print(f"\n❌ Failed: {results.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()