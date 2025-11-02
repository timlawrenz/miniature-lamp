#!/usr/bin/env python3
"""
Test the DINO FLUX Upscale node locally without ComfyUI

This creates fake ComfyUI tensors to test the node implementation.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import torch
from PIL import Image
from comfyui_nodes.nodes import DINOFLUXUpscale
from comfyui_nodes.utils import pil_to_comfyui, comfyui_to_pil


def test_tensor_conversion():
    """Test tensor conversion utilities"""
    print("Testing tensor conversion...")
    
    # Load test image
    test_image_path = "46723.png"
    if not Path(test_image_path).exists():
        test_image_path = "test_small.jpg"
    
    if not Path(test_image_path).exists():
        print("Creating test image...")
        img = Image.new('RGB', (256, 256), color=(100, 150, 200))
        img.save("test_image.jpg")
        test_image_path = "test_image.jpg"
    
    # Load image
    print(f"Loading {test_image_path}...")
    pil_img = Image.open(test_image_path).convert('RGB')
    print(f"  PIL image: {pil_img.size}, mode={pil_img.mode}")
    
    # Convert to ComfyUI tensor
    tensor = pil_to_comfyui(pil_img)
    print(f"  ComfyUI tensor: {tensor.shape}, dtype={tensor.dtype}")
    print(f"  Range: {tensor.min():.3f} to {tensor.max():.3f}")
    
    # Convert back to PIL
    pil_img_back = comfyui_to_pil(tensor)
    print(f"  Back to PIL: {pil_img_back.size}, mode={pil_img_back.mode}")
    
    # Check if images match
    import numpy as np
    orig_arr = np.array(pil_img)
    back_arr = np.array(pil_img_back)
    diff = np.abs(orig_arr.astype(float) - back_arr.astype(float)).mean()
    print(f"  Mean difference: {diff:.2f} (should be < 1.0)")
    
    assert tensor.shape == (1, pil_img.height, pil_img.width, 3), "Wrong tensor shape!"
    assert tensor.dtype == torch.float32, "Wrong dtype!"
    assert 0.0 <= tensor.min() <= 1.0 and 0.0 <= tensor.max() <= 1.0, "Wrong range!"
    assert diff < 1.0, "Conversion not reversible!"
    
    print("✓ Tensor conversion test passed!\n")
    return tensor, test_image_path


def test_node_minimal():
    """Test node with minimal parameters (no FLUX, just structure)"""
    print("Testing node structure...")
    
    # Create node
    node = DINOFLUXUpscale()
    
    # Check INPUT_TYPES
    input_types = node.INPUT_TYPES()
    print("  Required inputs:", list(input_types['required'].keys()))
    print("  Optional inputs:", list(input_types.get('optional', {}).keys()))
    
    # Check attributes
    assert hasattr(node, 'RETURN_TYPES'), "Missing RETURN_TYPES"
    assert hasattr(node, 'FUNCTION'), "Missing FUNCTION"
    assert hasattr(node, 'CATEGORY'), "Missing CATEGORY"
    
    print(f"  Return types: {node.RETURN_TYPES}")
    print(f"  Function: {node.FUNCTION}")
    print(f"  Category: {node.CATEGORY}")
    
    print("✓ Node structure test passed!\n")


def test_node_upscale(test_tensor, test_image_path):
    """Test actual upscaling (this will be slow)"""
    print("Testing upscaling...")
    print("WARNING: This will download FLUX (~10GB) and DINOv2 (~350MB) on first run")
    print("Press Ctrl+C within 5 seconds to skip...")
    
    import time
    time.sleep(5)
    
    # Create node
    node = DINOFLUXUpscale()
    
    # Test with minimal settings
    print("\nRunning upscale with minimal settings...")
    print("  scale_factor: 2.0")
    print("  strength: 0.1 (minimal changes)")
    print("  flux_variant: schnell (fast)")
    print("  steps: 4")
    print("  dino_enabled: True")
    
    result = node.upscale(
        image=test_tensor,
        scale_factor=2.0,
        strength=0.1,
        flux_variant="schnell",
        steps=4,
        dino_enabled=True,
        dino_strength=0.5,
        seed=42,
        prompt="high quality"
    )
    
    # Check result
    assert isinstance(result, tuple), "Result should be tuple"
    assert len(result) == 1, "Should return 1 output"
    
    result_tensor = result[0]
    print(f"\n✓ Upscale complete!")
    print(f"  Input shape: {test_tensor.shape}")
    print(f"  Output shape: {result_tensor.shape}")
    print(f"  Expected: ~{test_tensor.shape[1]*2}x{test_tensor.shape[2]*2}")
    
    # Save result
    result_pil = comfyui_to_pil(result_tensor)
    output_path = test_image_path.replace('.', '_upscaled_test.')
    result_pil.save(output_path)
    print(f"  Saved to: {output_path}")
    
    print("\n✓ Full upscale test passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("DINO FLUX Upscale Node - Local Test")
    print("=" * 60)
    print()
    
    # Test 1: Tensor conversion
    test_tensor, test_image_path = test_tensor_conversion()
    
    # Test 2: Node structure
    test_node_minimal()
    
    # Test 3: Full upscale (optional, takes time)
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--full', action='store_true', help='Run full upscale test')
    args = parser.parse_args()
    
    if args.full:
        test_node_upscale(test_tensor, test_image_path)
    else:
        print("Skipping full upscale test (use --full to run)")
        print("\nAll quick tests passed! ✓")
        print("\nTo test upscaling, run:")
        print("  python test_node_local.py --full")
