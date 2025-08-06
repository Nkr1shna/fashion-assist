import torch
import open_clip
from PIL import Image
import numpy as np
from pathlib import Path

class FashionCLIP:
    def __init__(self):
        if torch.cuda.is_available():
            self.device = "cuda"
        elif torch.backends.mps.is_available():
            self.device = "mps"
        else:
            self.device = "cpu"
        print(f"Using device: {self.device}")
        
        # Load Fashion-CLIP model
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            'ViT-B-32', 
            pretrained='laion2b_s34b_b79k'
        )
        self.model = self.model.to(self.device)
        self.tokenizer = open_clip.get_tokenizer('ViT-B-32')
        
        # Fashion categories for classification
        self.categories = [
            "a photo of a shirt",
            "a photo of a t-shirt", 
            "a photo of pants",
            "a photo of jeans",
            "a photo of a dress",
            "a photo of a skirt",
            "a photo of a jacket",
            "a photo of a sweater",
            "a photo of shoes",
            "a photo of sneakers",
            "a photo of boots",
            "a photo of accessories",
            "a photo of shorts",
            "a photo of hoodie",
            "a photo of blazer"
        ]
        
        self.colors = [
            "black", "white", "red", "blue", "green", 
            "yellow", "orange", "purple", "pink", "brown", 
            "gray", "navy", "beige", "cream", "maroon"
        ]
        
        self.styles = [
            "casual", "formal", "business", "sporty", 
            "elegant", "vintage", "modern", "bohemian",
            "streetwear", "minimalist"
        ]
    
    def categorize_item(self, image_path):
        """Categorize clothing item using Fashion-CLIP"""
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)
            
            # Encode image
            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                image_features /= image_features.norm(dim=-1, keepdim=True)
            
            # Get category with confidence
            category, category_confidence = self._classify_with_labels_and_confidence(image_features, self.categories)
            
            # Get color with confidence
            color_prompts = [f"a photo of {color} clothing" for color in self.colors]
            color, color_confidence = self._classify_with_labels_and_confidence(image_features, color_prompts)
            
            # Get style with confidence
            style_prompts = [f"a photo of {style} clothing" for style in self.styles]
            style, style_confidence = self._classify_with_labels_and_confidence(image_features, style_prompts)
            
            # Calculate overall confidence as average of individual confidences
            overall_confidence = (category_confidence + color_confidence + style_confidence) / 3.0
            
            return {
                "category": category.replace("a photo of a ", "").replace("a photo of ", ""),
                "color": color,
                "style": style,
                "confidence": float(overall_confidence),  # Real confidence based on similarity scores
                "category_confidence": float(category_confidence),
                "color_confidence": float(color_confidence),
                "style_confidence": float(style_confidence)
            }
            
        except Exception as e:
            print(f"Error categorizing item: {e}")
            return {
                "category": "unknown",
                "color": "unknown", 
                "style": "unknown",
                "confidence": 0.0,
                "category_confidence": 0.0,
                "color_confidence": 0.0,
                "style_confidence": 0.0
            }
    
    def _classify_with_labels(self, image_features, labels):
        """Helper function for zero-shot classification"""
        text_tokens = self.tokenizer(labels).to(self.device)
        
        with torch.no_grad():
            text_features = self.model.encode_text(text_tokens)
            text_features /= text_features.norm(dim=-1, keepdim=True)
            
            # Calculate similarities
            similarities = (image_features @ text_features.T).squeeze(0)
            best_idx = similarities.argmax().item()
            
            if "clothing" in labels[best_idx]:
                return labels[best_idx].split()[-2]  # Extract color/style word
            else:
                return labels[best_idx].replace("a photo of a ", "").replace("a photo of ", "")
    
    def _classify_with_labels_and_confidence(self, image_features, labels):
        """Helper function for zero-shot classification with confidence scores"""
        text_tokens = self.tokenizer(labels).to(self.device)
        
        with torch.no_grad():
            text_features = self.model.encode_text(text_tokens)
            text_features /= text_features.norm(dim=-1, keepdim=True)
            
            # Calculate similarities
            similarities = (image_features @ text_features.T).squeeze(0)
            best_idx = similarities.argmax().item()
            
            # Get the confidence as the maximum similarity score
            # Convert from cosine similarity (-1 to 1) to confidence (0 to 1)
            confidence = (similarities[best_idx].item() + 1.0) / 2.0
            
            # Apply softmax to get more realistic confidence scores
            softmax_similarities = torch.softmax(similarities * 10, dim=0)  # Scale for sharper probabilities
            confidence = softmax_similarities[best_idx].item()
            
            if "clothing" in labels[best_idx]:
                label = labels[best_idx].split()[-2]  # Extract color/style word
            else:
                label = labels[best_idx].replace("a photo of a ", "").replace("a photo of ", "")
                
            return label, confidence
    
    def get_image_embedding(self, image_path):
        """Get image embedding for similarity comparisons"""
        try:
            image = Image.open(image_path).convert('RGB')
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                image_features /= image_features.norm(dim=-1, keepdim=True)
            
            return image_features.cpu().numpy()
            
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return None
    
    def compatibility_score(self, image1_path, image2_path):
        """Calculate compatibility score between two items"""
        emb1 = self.get_image_embedding(image1_path)
        emb2 = self.get_image_embedding(image2_path)
        
        if emb1 is None or emb2 is None:
            return 0.0
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2.T).item()
        return max(0.0, min(1.0, similarity))  # Clamp between 0 and 1