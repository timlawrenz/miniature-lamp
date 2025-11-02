"""
Quick diagnostic tool to check upscaler parameters and flow
Run this to understand what parameters are being used
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from flux_pipeline import FLUXUpscalePipeline
from upscaler import BasicUpscaler
from config import FLUXConfig

print("=" * 60)
print("FLUX Upscaling Parameter Audit")
print("=" * 60)
print()

# Check default config
config = FLUXConfig()
print("Default FLUXConfig:")
print(f"  variant: {config.variant}")
print(f"  strength: {config.strength}")
print(f"  guidance_scale: {config.guidance_scale}")
print(f"  dino_conditioning_strength: {config.dino_conditioning_strength}")
print(f"  prompt: '{config.prompt}'")
print(f"  num_steps: {config.num_steps} (None = use default)")
print(f"  tile_size: {config.tile_size}")
print(f"  tile_overlap: {config.tile_overlap}")
print()

# Check pipeline defaults
print("FLUXUpscalePipeline defaults:")
pipe = FLUXUpscalePipeline(variant="schnell")
print(f"  default_steps[schnell]: {pipe.default_steps['schnell']}")
print(f"  default_steps[dev]: {pipe.default_steps['dev']}")
print()

# Check upscaler defaults
print("BasicUpscaler defaults:")
upscaler = BasicUpscaler()
print(f"  scale_factor: {upscaler.scale_factor}")
print()

print("=" * 60)
print("Key Parameters for 'Neutral' Upscaling:")
print("=" * 60)
print()
print("To get output closest to simple bicubic:")
print()
print("Option 1: Use bicubic (no FLUX)")
print("  python examples/flux_poc.py image.jpg --no-dino")
print()
print("Option 2: FLUX with minimal modification")
print("  python examples/flux_poc.py image.jpg --flux \\")
print("    --no-dino \\              # Disable DINO")
print("    --strength 0.0 \\         # No denoising (passthrough)")
print("    --prompt \"\" \\            # No text guidance")
print("    --seed 42")
print()
print("Option 3: FLUX with very light modification")
print("  python examples/flux_poc.py image.jpg --flux \\")
print("    --no-dino \\              # Disable DINO")
print("    --strength 0.1 \\         # Minimal denoising")
print("    --prompt \"\" \\            # No text guidance")
print("    --seed 42")
print()
print("=" * 60)
print("Current Default Command Behavior:")
print("=" * 60)
print()
print("python examples/flux_poc.py image.jpg --flux")
print()
print("This uses:")
print(f"  - DINO extraction: YES (strength=0.5)")
print(f"  - FLUX denoising strength: 0.3")
print(f"  - Text prompt: 'high quality, detailed, sharp, 8k'")
print(f"  - Guidance scale: 3.5")
print(f"  - Steps: 4 (schnell)")
print()
print("These settings allow significant modification!")
print()
