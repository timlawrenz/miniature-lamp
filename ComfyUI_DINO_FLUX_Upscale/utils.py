"""
Tensor conversion utilities for ComfyUI integration
"""
import torch
import numpy as np
from PIL import Image


def comfyui_to_pil(tensor, batch_index=0):
    """
    Convert ComfyUI image tensor to PIL Image
    
    ComfyUI format: [Batch, Height, Width, Channels], float32, 0.0-1.0, RGB
    
    Args:
        tensor: ComfyUI image tensor [B, H, W, C]
        batch_index: Which image in batch to convert
        
    Returns:
        PIL Image in RGB mode
    """
    # Handle NaN values
    safe_tensor = torch.nan_to_num(tensor[batch_index])
    
    # Convert to numpy: 0.0-1.0 -> 0-255, float32 -> uint8
    img_np = (safe_tensor.cpu().numpy() * 255.0).astype(np.uint8)
    
    return Image.fromarray(img_np, mode='RGB')


def pil_to_comfyui(pil_image):
    """
    Convert PIL Image to ComfyUI tensor format
    
    Args:
        pil_image: PIL Image (any mode, will convert to RGB)
        
    Returns:
        Tensor of shape [1, H, W, 3], float32, 0.0-1.0
    """
    # Ensure RGB mode
    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')
    
    # Convert to numpy: 0-255 uint8 -> 0.0-1.0 float32
    img_np = np.array(pil_image).astype(np.float32) / 255.0
    
    # Convert to tensor and add batch dimension: [H, W, 3] -> [1, H, W, 3]
    tensor = torch.from_numpy(img_np).unsqueeze(0)
    
    return tensor


def batch_comfyui_to_pil(tensor):
    """
    Convert entire batch of ComfyUI tensors to list of PIL Images
    
    Args:
        tensor: ComfyUI image tensor [B, H, W, C]
        
    Returns:
        List of PIL Images
    """
    return [comfyui_to_pil(tensor, i) for i in range(tensor.shape[0])]


def batch_pil_to_comfyui(pil_images):
    """
    Convert list of PIL Images to ComfyUI batch tensor
    
    Args:
        pil_images: List of PIL Images
        
    Returns:
        Tensor of shape [B, H, W, 3], float32, 0.0-1.0
    """
    tensors = [pil_to_comfyui(img) for img in pil_images]
    return torch.cat(tensors, dim=0)
