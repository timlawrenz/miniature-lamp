"""
Simple POC: Load image, extract DINO features, and upscale
"""
import sys
from pathlib import Path
from PIL import Image
import torch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dino_extractor import DINOFeatureExtractor
from upscaler import BasicUpscaler


def main():
    print("=" * 60)
    print("DINO-Guided Image Upscaler - Proof of Concept")
    print("=" * 60)
    
    # Get input image path
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = input("\nEnter path to image: ")
    
    image_path = Path(image_path)
    if not image_path.exists():
        print(f"Error: Image not found at {image_path}")
        return
    
    # Load image
    print(f"\nLoading image: {image_path}")
    image = Image.open(image_path).convert("RGB")
    print(f"Image size: {image.size[0]}x{image.size[1]}")
    
    # Initialize DINO extractor
    print("\n" + "-" * 60)
    print("Stage 1: DINO Feature Extraction")
    print("-" * 60)
    print("Loading DINOv2 model...")
    extractor = DINOFeatureExtractor()
    print(f"Device: {extractor.device}")
    
    # Extract features
    print("Extracting semantic patch embeddings...")
    features = extractor.extract_features(image)
    grid_size = extractor.get_patch_grid_size(image.size[::-1])
    
    print(f"✓ Feature shape: {features.shape}")
    print(f"✓ Patch grid: {grid_size[0]}x{grid_size[1]} patches")
    print(f"✓ Feature dimension: {features.shape[1]}")
    
    # Initialize upscaler
    print("\n" + "-" * 60)
    print("Stage 2: Image Upscaling (2x)")
    print("-" * 60)
    upscaler = BasicUpscaler()
    
    print("Upscaling image...")
    upscaled = upscaler.upscale(image, dino_features=features)
    print(f"✓ Output size: {upscaled.size[0]}x{upscaled.size[1]}")
    
    # Save result
    output_path = image_path.parent / f"{image_path.stem}_upscaled_2x{image_path.suffix}"
    upscaled.save(output_path)
    print(f"✓ Saved to: {output_path}")
    
    # Summary
    print("\n" + "=" * 60)
    print("POC Complete!")
    print("=" * 60)
    print(f"Original: {image.size[0]}x{image.size[1]}")
    print(f"Upscaled: {upscaled.size[0]}x{upscaled.size[1]}")
    print(f"DINO patches: {features.shape[0]}")
    
    print("\n" + "-" * 60)
    print("TODO: Next Steps for Full Implementation")
    print("-" * 60)
    print("1. Integrate Stable Diffusion img2img pipeline")
    print("2. Train/adapt ControlNet for DINO embeddings")
    print("3. Implement proper tiled processing with DINO guidance")
    print("4. Map DINO features to upscaled tile coordinates")
    print("5. Add semantic consistency enforcement during generation")
    print("6. Create ComfyUI custom node interface")
    print("7. Test with various image types and compare vs standard upscaling")
    print("=" * 60)


if __name__ == "__main__":
    main()
