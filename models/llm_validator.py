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
        
        prompt = f"""Product: "{title}" 
Categories: {category_hints}
Colors: {color_hints}
Analysis: {predicted_category} {predicted_color}

STRICT VALIDATION:
1. Category must match exactly: {predicted_category} vs {category_hints}
2. Color must be compatible: {predicted_color} vs {color_hints}

EXAMPLES:
- shirt vs shirt = YES, shirt vs pants = NO, shirt vs dress = NO
- blue vs blue = YES, blue vs navy = YES, red vs blue = NO

If category OR color doesn't match: MATCH=NO, CONFIDENCE=0.1-0.3
Only if BOTH match: MATCH=YES, CONFIDENCE=0.7-0.9

MATCH: [YES/NO]
CONFIDENCE: [0.0-1.0]
CATEGORY_MATCH: [YES/NO] 
COLOR_MATCH: [YES/NO]
REASON: [brief explanation]"""

        return prompt
    
    def _query_llm(self, prompt):
        """Query the LLM with the validation prompt"""
        
        # Prepare the messages for chat format
        messages = [
            {"role": "system", "content": "You are a precise fashion validation expert. Respond directly in the exact format requested."},
            {"role": "user", "content": prompt}
        ]
        
        # Apply chat template (Qwen3 format) with thinking disabled
        try:
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False  # Disable thinking mode for direct responses
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
            
            # Debug: Print the response for analysis
            print(f"DEBUG - Full LLM Response: {response}")
            
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
                    result['confidence'] = 0.7  # Higher confidence for inferred matches
                    result['reason'] = "Inferred positive match from response content"
                elif 'no' in response_lower or 'not' in response_lower or 'mismatch' in response_lower:
                    result['overall_match'] = False
                    result['category_match'] = False  
                    result['color_match'] = False
                    result['confidence'] = 0.4  # Lower confidence for inferred non-matches
                    result['reason'] = "Inferred negative match from response content"
                else:
                    # Completely unclear response
                    result['confidence'] = 0.3  # Very low confidence for unclear responses
                    result['reason'] = "Unclear LLM response, defaulting to low confidence"
            
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
        
        # Check category match with confidence calculation
        category_match = False
        category_match_strength = 0.0
        
        if category_hints:
            if predicted_category in category_hints:
                category_match = True
                category_match_strength = 1.0  # Exact match
            elif any(hint in predicted_category for hint in category_hints):
                category_match = True
                category_match_strength = 0.8  # Partial match (increased from 0.7)
            elif any(predicted_category in hint for hint in category_hints):
                category_match = True
                category_match_strength = 0.7  # Reverse partial match
        elif title_categories:
            if predicted_category in title_categories:
                category_match = True
                category_match_strength = 0.95  # Strong match from title (increased from 0.9)
            elif any(cat in predicted_category for cat in title_categories):
                category_match = True
                category_match_strength = 0.7  # Partial match from title (increased from 0.6)
            elif any(predicted_category in cat for cat in title_categories):
                category_match = True
                category_match_strength = 0.65  # Reverse partial match
        else:
            category_match = True  # No strong category signal, assume OK
            category_match_strength = 0.6  # Neutral confidence (increased from 0.5)
        
        # Color validation with confidence
        color_hints = [color.lower() for color in context.get('color_hints', [])]
        color_match = False  # Default to False for colors - be more strict
        color_match_strength = 0.3  # Default low confidence
        
        if color_hints:
            if predicted_color in color_hints:
                color_match = True
                color_match_strength = 1.0  # Exact color match
            elif any(hint in predicted_color for hint in color_hints):
                color_match = True
                color_match_strength = 0.85  # Partial color match
            elif any(predicted_color in hint for hint in color_hints):
                color_match = True
                color_match_strength = 0.8  # Reverse partial match
            else:
                color_match = False
                color_match_strength = 0.2  # Color mismatch
        else:
            # No color hints available, be conservative
            color_match = False
            color_match_strength = 0.4
        
        # Calculate overall confidence based on match quality
        overall_match = category_match and color_match
        
        if overall_match:
            # High confidence if both category and color match well
            confidence = (category_match_strength + color_match_strength) / 2.0
            # Boost confidence for good matches - allow higher scores
            confidence = max(0.7, min(0.98, confidence))  # Clamp between 0.7-0.98
            
            # Additional boost for perfect matches
            if category_match_strength >= 0.9 and color_match_strength >= 0.8:
                confidence = min(0.98, confidence + 0.05)  # Small boost for near-perfect matches
        else:
            # Much lower confidence for mismatches - be more strict
            confidence = (category_match_strength + color_match_strength) / 6.0  # Reduced from 4.0
            confidence = max(0.05, min(0.25, confidence))  # Clamp between 0.05-0.25 (reduced from 0.1-0.4)
        
        reason = f"Rule-based: Category {'✓' if category_match else '✗'} ({category_match_strength:.1f}), Color {'✓' if color_match else '✗'} ({color_match_strength:.1f})"
        
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
            
            # Adaptive weighting based on confidence levels
            if fashion_clip_confidence > 0.8:
                # If Fashion-CLIP is very confident, give it more weight
                final_score = (llm_confidence * 0.6) + (fashion_clip_confidence * 0.4)
            elif llm_validation.get('overall_match', False):
                # If LLM validates as match, boost the score
                final_score = (llm_confidence * 0.7) + (fashion_clip_confidence * 0.3)
                # Additional boost for validated matches
                final_score = min(1.0, final_score + 0.1)
            else:
                # Standard weighting
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