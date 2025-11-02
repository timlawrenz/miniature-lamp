"""
Enhanced POC: DINO extraction with optional FLUX upscaling
"""
import sys
import argparse
from pathlib import Path
from PIL import Image
import torch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dino_extractor import DINOFeatureExtractor
from upscaler import BasicUpscaler
from flux_pipeline import FLUXUpscalePipeline
from config import FLUXConfig


def main():
    parser = argparse.ArgumentParser(description="DINO-Guided Image Upscaler")
    parser.add_argument("image", help="Path to input image")
    parser.add_argument("--flux", action="store_true", help="Use FLUX diffusion (slow, requires GPU)")
    parser.add_argument("--variant", choices=["schnell", "dev"], default="schnell",
                       help="FLUX variant: schnell (fast) or dev (quality)")
    parser.add_argument("--model-path", help="Path to local FLUX model file (.safetensors) or directory")
    parser.add_argument("--prompt", default="high quality, detailed, sharp, 8k",
                       help="Text prompt for FLUX guidance")
    parser.add_argument("--steps", type=int, help="Inference steps (default: 4 for schnell, 20 for dev)")
    parser.add_argument("--strength", type=float, default=0.3,
                       help="Denoising strength (0.0-1.0)")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--no-dino", action="store_true", help="Skip DINO feature extraction")
    parser.add_argument("--scale", type=float, default=2.0, help="Upscale factor (default: 2.0, e.g., 1.1 for 10%% larger)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("DINO-Guided Image Upscaler")
    print("=" * 60)
    
    # Load image
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: Image not found at {image_path}")
        return
    
    print(f"\nLoading image: {image_path}")
    image = Image.open(image_path).convert("RGB")
    print(f"Image size: {image.size[0]}x{image.size[1]}")
    
    # Extract DINO features
    features = None
    if not args.no_dino:
        print("\n" + "-" * 60)
        print("Stage 1: DINO Feature Extraction")
        print("-" * 60)
        print("Loading DINOv2 model...")
        extractor = DINOFeatureExtractor()
        print(f"Device: {extractor.device}")
        
        print("Extracting semantic patch embeddings...")
        features = extractor.extract_features(image)
        grid_size = extractor.get_patch_grid_size(image.size[::-1])
        
        print(f"✓ Feature shape: {features.shape}")
        print(f"✓ Patch grid: {grid_size[0]}x{grid_size[1]} patches")
        print(f"✓ Feature dimension: {features.shape[1]}")
    
    # Initialize upscaler
    print("\n" + "-" * 60)
    if args.flux:
        print(f"Stage 2: FLUX {args.variant.upper()} Upscaling (2x)")
        print("-" * 60)
        
        if args.model_path:
            print(f"Using local model: {args.model_path}")
        else:
            print("⚠️  This will download ~10GB of models on first run")
            print("⚠️  Requires GPU with ~12GB VRAM (8GB with offloading)")
        
        flux_pipeline = FLUXUpscalePipeline(
            variant=args.variant,
            model_path=args.model_path,
            enable_offloading=True
        )
        upscaler = BasicUpscaler(flux_pipeline=flux_pipeline, scale_factor=args.scale)
        
        print("Upscaling with FLUX diffusion...")
        upscaled = upscaler.upscale(
            image,
            dino_features=features,
            use_flux=True,
            prompt=args.prompt,
            num_steps=args.steps,
            strength=args.strength,
            seed=args.seed
        )
    else:
        print("Stage 2: Bicubic Upscaling (2x)")
        print("-" * 60)
        upscaler = BasicUpscaler()
        
        print("Upscaling with bicubic interpolation...")
        upscaled = upscaler.upscale(image, dino_features=features, use_flux=False)
    
    print(f"✓ Output size: {upscaled.size[0]}x{upscaled.size[1]}")
    
    # Save result
    suffix = "_flux_2x" if args.flux else "_upscaled_2x"
    output_path = image_path.parent / f"{image_path.stem}{suffix}{image_path.suffix}"
    upscaled.save(output_path)
    print(f"✓ Saved to: {output_path}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Complete!")
    print("=" * 60)
    print(f"Original: {image.size[0]}x{image.size[1]}")
    print(f"Upscaled: {upscaled.size[0]}x{upscaled.size[1]}")
    if features is not None:
        print(f"DINO patches: {features.shape[0]}")
    print(f"Method: {'FLUX ' + args.variant if args.flux else 'Bicubic'}")
    
    if args.flux:
        print("\n" + "-" * 60)
        print("FLUX Status: ✓ Working")
        print("DINO Conditioning: 🚧 Not yet integrated (Phase 2, Stage 2)")
        print("\nNext: Implement DINO conditioning adapter")
    else:
        print("\n" + "-" * 60)
        print("To try FLUX diffusion upscaling:")
        print(f"  python {Path(__file__).name} {args.image} --flux")
        print("\nOr use a local model:")
        print(f"  python {Path(__file__).name} {args.image} --flux \\")
        print(f"    --model-path /path/to/flux_schnell.safetensors")
    print("=" * 60)


if __name__ == "__main__":
    main()
