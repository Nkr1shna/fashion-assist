import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import json
import re

class LLMValidator:
    """Lightweight LLM validator using Qwen2-0.5B for semantic verification"""
    
    def __init__(self):
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"LLM Validator using device: {self.device}")
        
        try:
            # Load Qwen3-0.6B - lightweight base model that we can use for instruction following
            model_name = "Qwen/Qwen3-0.6B"
            print(f"Loading {model_name}...")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )
            
            if self.device != "cuda":
                self.model = self.model.to(self.device)
            
            print("✅ Qwen3-0.6B loaded successfully!")
            
        except Exception as e:
            print(f"⚠️ Could not load Qwen3-0.6B: {e}")
            print("Falling back to rule-based validation...")
            self.model = None
            self.tokenizer = None
    
    def validate_match(self, fashion_clip_analysis, product_data):
        """
        Validate if Fashion-CLIP analysis matches the product description using LLM
        Returns: dict with validation results and confidence score
        """
        if not self.model:
            return self._fallback_validation(fashion_clip_analysis, product_data)
        
        try:
            # Prepare the validation prompt
            prompt = self._create_validation_prompt(fashion_clip_analysis, product_data)
            
            # Get LLM response
            response = self._query_llm(prompt)
            
            # Parse the response
            validation_result = self._parse_llm_response(response)
            
            return validation_result
            
        except Exception as e:
            print(f"LLM validation error: {e}")
            return self._fallback_validation(fashion_clip_analysis, product_data)
    
    def _create_validation_prompt(self, fashion_clip_analysis, product_data):
        """Create a structured prompt for the LLM to validate the match"""
        
        title = product_data.get('title', 'Unknown')
        description = product_data.get('description', 'No description')
        url = product_data.get('url', '')
        context = product_data.get('context', {})
        
        # Extract context hints
        category_hints = ', '.join(context.get('category_hints', []))
        color_hints = ', '.join(context.get('color_hints', []))
        brand = context.get('brand', 'Unknown')
        
        # Fashion-CLIP predictions
        predicted_category = fashion_clip_analysis.get('category', 'unknown')
        predicted_color = fashion_clip_analysis.get('color', 'unknown')
        predicted_style = fashion_clip_analysis.get('style', 'unknown')
        confidence = fashion_clip_analysis.get('confidence', 0.0)
        
        prompt = f"""You are a fashion expert validating product image analysis. Compare what an AI vision model detected in an image versus what the product actually is.

PRODUCT INFORMATION:
- Title: "{title}"
- Brand: {brand}
- Description: "{description[:200]}..."
- URL categories: {category_hints or 'none'}
- URL colors: {color_hints or 'none'}

IMAGE ANALYSIS (by Fashion-CLIP):
- Detected category: {predicted_category}
- Detected color: {predicted_color}
- Detected style: {predicted_style}
- AI confidence: {confidence:.2f}

TASK: Determine if the image analysis matches the product description.

Validation rules:
1. Category must match exactly (shirt vs shirt ✓, shirt vs pants ✗)
2. Color should be compatible (rose/pink are similar ✓, black/white are different ✗)
3. Minor style differences are acceptable
4. Brand context matters (luxury vs casual brands)

Respond in this EXACT format:
MATCH: [YES/NO]
CONFIDENCE: [0.0-1.0]
CATEGORY_MATCH: [YES/NO] 
COLOR_MATCH: [YES/NO]
REASON: [brief explanation]

Response:"""

        return prompt
    
    def _query_llm(self, prompt):
        """Query the LLM with the validation prompt"""
        
        # Prepare the messages for chat format
        messages = [
            {"role": "system", "content": "You are a precise fashion validation expert. Follow the exact response format requested."},
            {"role": "user", "content": prompt}
        ]
        
        # Apply chat template (Qwen3 format)
        try:
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
        except Exception as e:
            print(f"Chat template error: {e}, using simple format")
            # Fallback for Qwen3 if chat template not available
            text = f"<|im_start|>system\nYou are a precise fashion validation expert. Follow the exact response format requested.<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
        
        # Tokenize
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.device)
        
        # Generate response
        with torch.no_grad():
            generated_ids = self.model.generate(
                model_inputs.input_ids,
                max_new_tokens=150,
                do_sample=True,
                temperature=0.3,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode response
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return response
    
    def _parse_llm_response(self, response):
        """Parse the structured LLM response"""
        
        result = {
            'overall_match': False,
            'confidence': 0.5,
            'category_match': False,
            'color_match': False,
            'reason': 'Could not parse LLM response',
            'llm_response': response
        }
        
        try:
            # Extract structured information using regex with more flexible patterns
            match_pattern = r'MATCH:\s*(YES|NO|True|False|yes|no)'
            confidence_pattern = r'CONFIDENCE:\s*([0-9.]+)'
            category_pattern = r'CATEGORY_MATCH:\s*(YES|NO|True|False|yes|no)'
            color_pattern = r'COLOR_MATCH:\s*(YES|NO|True|False|yes|no)'
            reason_pattern = r'REASON:\s*(.+?)(?:\n\n|$)'
            
            # Parse each field with better handling
            if match := re.search(match_pattern, response, re.IGNORECASE):
                match_text = match.group(1).upper()
                result['overall_match'] = match_text in ['YES', 'TRUE']
            
            if confidence := re.search(confidence_pattern, response):
                try:
                    conf_val = float(confidence.group(1))
                    # Handle if confidence is given as percentage (>1)
                    if conf_val > 1.0:
                        conf_val = conf_val / 100.0
                    result['confidence'] = min(max(conf_val, 0.0), 1.0)  # Clamp 0-1
                except:
                    result['confidence'] = 0.5
                
            if category := re.search(category_pattern, response, re.IGNORECASE):
                cat_text = category.group(1).upper()
                result['category_match'] = cat_text in ['YES', 'TRUE']
                
            if color := re.search(color_pattern, response, re.IGNORECASE):
                color_text = color.group(1).upper()
                result['color_match'] = color_text in ['YES', 'TRUE']
                
            if reason := re.search(reason_pattern, response, re.IGNORECASE | re.DOTALL):
                result['reason'] = reason.group(1).strip()
            
            # Fallback parsing if structured format not found
            if not any([result['overall_match'], result['category_match'], result['color_match']]):
                # Try to infer from general content
                response_lower = response.lower()
                if 'match' in response_lower or 'correct' in response_lower or 'yes' in response_lower:
                    result['overall_match'] = True
                    result['category_match'] = True
                    result['color_match'] = True
                    result['confidence'] = 0.7
                    result['reason'] = "Inferred positive match from response content"
            
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            result['reason'] = f"Parsing error: {e}"
        
        return result
    
    def _fallback_validation(self, fashion_clip_analysis, product_data):
        """Rule-based fallback validation when LLM is not available"""
        
        title = product_data.get('title', '').lower()
        description = product_data.get('description', '').lower()
        context = product_data.get('context', {})
        
        predicted_category = fashion_clip_analysis.get('category', '').lower()
        predicted_color = fashion_clip_analysis.get('color', '').lower()
        
        # Category validation
        category_hints = [cat.lower() for cat in context.get('category_hints', [])]
        title_categories = []
        
        category_keywords = ['shirt', 'pants', 'dress', 'jacket', 'shoes', 'skirt', 'sweater', 'top', 'bottom']
        for keyword in category_keywords:
            if keyword in title or keyword in description:
                title_categories.append(keyword)
        
        # Check category match
        category_match = False
        if category_hints:
            category_match = predicted_category in category_hints
        elif title_categories:
            category_match = predicted_category in title_categories or any(cat in predicted_category for cat in title_categories)
        else:
            category_match = True  # No strong category signal, assume OK
        
        # Color validation
        color_hints = [color.lower() for color in context.get('color_hints', [])]
        color_match = True  # Default to True for colors
        
        if color_hints:
            # Check if predicted color is compatible with hints
            color_match = predicted_color in color_hints or any(hint in predicted_color for hint in color_hints)
        
        # Overall validation
        overall_match = category_match and color_match
        confidence = 0.8 if overall_match else 0.3
        
        reason = f"Rule-based: Category {'✓' if category_match else '✗'}, Color {'✓' if color_match else '✗'}"
        
        return {
            'overall_match': overall_match,
            'confidence': confidence,
            'category_match': category_match,
            'color_match': color_match,
            'reason': reason,
            'llm_response': 'Rule-based fallback'
        }
    
    def validate_image_batch(self, images_with_analysis, product_data):
        """Validate a batch of images and return them ranked by validation score"""
        
        validated_images = []
        
        for img_data in images_with_analysis:
            # Get Fashion-CLIP analysis for this image
            fashion_clip_analysis = img_data.get('analysis', {})
            
            # Get LLM validation
            llm_validation = self.validate_match(fashion_clip_analysis, product_data)
            
            # Combine scores
            fashion_clip_confidence = fashion_clip_analysis.get('confidence', 0.5)
            llm_confidence = llm_validation.get('confidence', 0.5)
            
            # Weighted final score (LLM validation is more important)
            final_score = (llm_confidence * 0.7) + (fashion_clip_confidence * 0.3)
            
            validated_images.append({
                **img_data,
                'llm_validation': llm_validation,
                'final_score': final_score,
                'is_valid': llm_validation['overall_match'] and final_score > 0.4
            })
        
        # Sort by final score (best first)
        validated_images.sort(key=lambda x: x['final_score'], reverse=True)
        
        return validated_images