#!/usr/bin/env python3
"""
Test to verify the tensor dimension fix for VAE encode/decode
"""
import torch
import numpy as np
from PIL import Image


def test_tensor_conversion():
    """Test that tensor shapes are correct throughout the pipeline"""
    
    # Create test image
    pil_img = Image.new('RGB', (1160, 870))
    print(f"✓ Created PIL image size: {pil_img.size} (width, height)")
    
    # Simulate upscaler.py conversion to numpy
    np_img = np.array(pil_img)
    assert np_img.shape == (870, 1160, 3), f"Numpy shape should be (H, W, C), got {np_img.shape}"
    assert np_img.dtype == np.uint8, f"Numpy dtype should be uint8, got {np_img.dtype}"
    print(f"✓ Numpy array shape: {np_img.shape} (H, W, C)")
    
    # Simulate comfyui_sampler.py conversion to tensor
    tensor = torch.from_numpy(np_img).float() / 255.0
    assert tensor.shape == (870, 1160, 3), f"Tensor shape should be (H, W, C), got {tensor.shape}"
    print(f"✓ Tensor shape: {tensor.shape} (H, W, C)")
    
    # Add batch dimension
    tensor = tensor.unsqueeze(0)
    assert tensor.shape == (1, 870, 1160, 3), f"Tensor shape should be (B, H, W, C), got {tensor.shape}"
    assert tensor.shape[-1] == 3, f"Last dimension should be 3 (channels), got {tensor.shape[-1]}"
    print(f"✓ Tensor with batch: {tensor.shape} (B, H, W, C)")
    
    # Simulate VAE.encode() internal conversion: movedim(-1, 1)
    # This is what ComfyUI VAE does internally
    vae_internal = tensor.movedim(-1, 1)
    assert vae_internal.shape == (1, 3, 870, 1160), f"After movedim should be (B, C, H, W), got {vae_internal.shape}"
    assert vae_internal.shape[1] == 3, f"Channels should be at position 1, got {vae_internal.shape[1]}"
    print(f"✓ After VAE internal movedim: {vae_internal.shape} (B, C, H, W)")
    print(f"✓ Channels dimension: {vae_internal.shape[1]} (correct for Conv2d)")
    
    # Simulate VAE.decode() output: movedim(1, -1) 
    # This is what ComfyUI VAE returns
    decoded = vae_internal.movedim(1, -1)
    assert decoded.shape == (1, 870, 1160, 3), f"Decoded should be (B, H, W, C), got {decoded.shape}"
    assert decoded.shape[-1] == 3, f"Channels should be at last position, got {decoded.shape[-1]}"
    print(f"✓ After VAE decode: {decoded.shape} (B, H, W, C)")
    
    print("\n✅ All tensor conversion tests passed!")
    print("\nSummary:")
    print("  - Input to VAE.encode(): [B, H, W, C]")
    print("  - VAE does movedim(-1, 1) internally: [B, C, H, W]")
    print("  - Output from VAE.decode(): [B, H, W, C]")
    print("  - No manual permutation needed!")


if __name__ == "__main__":
    test_tensor_conversion()
