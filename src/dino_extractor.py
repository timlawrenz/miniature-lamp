"""
DINO feature extractor for semantic embeddings
"""
import torch
from transformers import AutoImageProcessor, AutoModel
from PIL import Image
import numpy as np


class DINOFeatureExtractor:
    def __init__(self, model_name="facebook/dinov2-base"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.model.eval()
    
    @torch.no_grad()
    def extract_features(self, image):
        """
        Extract patch-level DINO features from an image
        
        Args:
            image: PIL Image or numpy array
            
        Returns:
            Tensor of shape (num_patches, feature_dim)
        """
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        
        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        outputs = self.model(**inputs)
        # Get patch embeddings (excluding CLS token)
        features = outputs.last_hidden_state[:, 1:, :]
        
        return features.squeeze(0)
    
    def get_patch_grid_size(self, image_size):
        """Calculate the patch grid dimensions for an image size"""
        # DINOv2 uses 14x14 patches by default
        patch_size = 14
        h, w = image_size if isinstance(image_size, tuple) else (image_size, image_size)
        return (h // patch_size, w // patch_size)
