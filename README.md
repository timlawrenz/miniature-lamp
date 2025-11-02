# DINO-Guided Image Upscaler

A ComfyUI custom node that uses DINOv2 vision transformer embeddings to guide semantic-aware tiled image upscaling.

## Overview

This project combines tiled upscaling with DINO semantic embeddings to maintain object identity and characteristics during the upscaling process, preventing common hallucination artifacts.

## Current Status

**✅ Phase 1 Complete:** Proof of concept with DINO feature extraction and basic upscaling

**🚧 Phase 2 In Progress:** FLUX diffusion integration with DINO conditioning (see `openspec/changes/add-flux-diffusion/`)

**Phase 3 (Planned):** Full ComfyUI custom node implementation

## How It Works

1. Extract DINO patch embeddings from source image (semantic map)
2. Tile the image for processing
3. Guide img2img denoising with DINO embeddings as ControlNet-style condition
4. Stitch tiles maintaining semantic consistency

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### POC Demo (Bicubic Upscaling)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the POC with your image (downloads DINOv2 model on first run ~350MB)
python examples/simple_poc.py path/to/your/image.jpg

# Or run interactively
python examples/simple_poc.py
```

**Note:** The POC uses bicubic upscaling. DINO features are extracted but not yet used for conditioning. FLUX diffusion integration is in progress (Phase 2).

### Example Usage

```python
from src.dino_extractor import DINOFeatureExtractor
from src.upscaler import BasicUpscaler
from PIL import Image

# Load image
image = Image.open("photo.jpg")

# Extract DINO features
extractor = DINOFeatureExtractor()
features = extractor.extract_features(image)
print(f"Extracted {features.shape[0]} patches with {features.shape[1]} features each")

# Upscale with DINO guidance
upscaler = BasicUpscaler()
upscaled = upscaler.upscale(image, dino_features=features)
upscaled.save("photo_upscaled_2x.jpg")
```

### DINO Feature Format

DINO features are returned as PyTorch tensors with shape `(num_patches, feature_dim)`:
- **num_patches**: Number of 14x14 patches in the image (e.g., 224x224 image = 16x16 = 256 patches)
- **feature_dim**: 768 for dinov2-base (semantic embedding dimension)

Each patch embedding captures the semantic meaning of that image region.

## Project Status

### ✅ Completed (Phase 1 - POC)
- DINO feature extraction from images
- Basic 2x upscaling pipeline
- Tiled processing with overlap blending
- Test suite with 9 passing tests
- Working demonstration script

### 🚧 In Progress (Phase 2 - FLUX Integration)
- FLUX diffusion model integration (see `openspec/changes/add-flux-diffusion/`)
- DINO conditioning adapter for semantic guidance
- Cross-attention injection architecture
- Memory-optimized tiled processing with diffusion

### 📋 Planned (Phase 3)
- ComfyUI custom node implementation
- Advanced conditioning controls
- Performance optimizations
- Batch processing support

## Development

See `openspec/project.md` for detailed project context and conventions.

## References

- [DINOv2 Paper](https://arxiv.org/abs/2304.07193)
- [ControlNet](https://arxiv.org/abs/2302.05543)
- [Ultimate SD Upscale](https://github.com/ssitu/ComfyUI_UltimateSDUpscale)
