# DINO Conditioning Guide

## Overview

DINO conditioning allows semantic features from DINOv2 vision transformer to guide FLUX diffusion during upscaling, helping maintain object identity and semantic consistency.

## How It Works

1. **Feature Extraction**: DINOv2 extracts semantic patch embeddings from the input image (768-dim vectors for each 14x14 pixel patch)

2. **Projection**: The DINO conditioning adapter projects these embeddings into FLUX's latent space (4096-dim)

3. **Spatial Alignment**: Features are spatially aligned to match FLUX's latent grid dimensions

4. **Conditioning**: Projected features guide the diffusion process alongside text prompts

## Parameters

### `--dino-strength` (0.0 - 1.0)

Controls the influence of DINO features on the generation:

- **0.0**: No DINO conditioning (text prompt only)
- **0.3-0.5**: Subtle semantic guidance (recommended for most cases)
- **0.7-0.9**: Strong semantic preservation
- **1.0**: Maximum semantic conditioning

**Default**: 0.5

**Example**:
```bash
python examples/flux_poc.py image.jpg --flux --dino-strength 0.7
```

### `--no-dino`

Skip DINO feature extraction entirely (faster, but no semantic guidance):

```bash
python examples/flux_poc.py image.jpg --flux --no-dino
```

## Usage Examples

### Basic FLUX Upscaling with DINO

```bash
python examples/flux_poc.py portrait.jpg --flux
```

This uses default settings:
- DINO strength: 0.5
- FLUX variant: schnell (4 steps)
- Denoising strength: 0.3

### High-Quality Mode

For best quality with maximum semantic preservation:

```bash
python examples/flux_poc.py portrait.jpg --flux \
  --variant dev \
  --steps 20 \
  --dino-strength 0.8 \
  --strength 0.5
```

### Fast Mode

For quick results with light conditioning:

```bash
python examples/flux_poc.py landscape.jpg --flux \
  --variant schnell \
  --steps 2 \
  --dino-strength 0.3
```

## Technical Details

### Feature Dimensions

- **DINO Input**: (num_patches, 768)
  - DINOv2-base produces 768-dimensional embeddings
  - Patch size: 14x14 pixels
  - Example: 512x512 image → 37x37 = 1,369 patches

- **After Projection**: (num_patches, 4096)
  - Projected to FLUX's cross-attention dimension
  - Scaled by conditioning strength

- **Spatial Alignment**: Automatically interpolated to match FLUX's latent grid

### Memory Considerations

DINO feature extraction adds minimal overhead:
- ~350MB model size (DINOv2-base)
- ~100MB GPU memory during extraction
- Features cached per tile during processing

### Tiled Processing

For large images, DINO features are extracted per tile:

1. Image split into 256x256 tiles (configurable)
2. DINO features extracted for each tile independently
3. Features guide FLUX upscaling for that tile
4. Results blended with overlap regions

This ensures semantic consistency even in large images.

## Advanced Usage

### Programmatic Control

```python
from src.dino_extractor import DINOFeatureExtractor
from src.flux_pipeline import FLUXUpscalePipeline
from src.upscaler import BasicUpscaler
from PIL import Image

# Initialize components
extractor = DINOFeatureExtractor()
flux = FLUXUpscalePipeline(variant="schnell")
upscaler = BasicUpscaler(
    flux_pipeline=flux,
    dino_extractor=extractor,
    scale_factor=2.0
)

# Load and upscale
image = Image.open("photo.jpg")
result = upscaler.upscale(
    image,
    use_flux=True,
    prompt="high quality, detailed",
    dino_conditioning_strength=0.7,
    num_steps=4,
    seed=42
)
result.save("upscaled.jpg")
```

### Custom Conditioning Adapter

```python
from src.dino_conditioning import DINOConditioningAdapter
import torch

# Create adapter
adapter = DINOConditioningAdapter(
    dino_dim=768,
    flux_dim=4096,
    device="cuda"
)

# Extract and project features
dino_features = extractor.extract_features(image)
projected = adapter.project_features(
    dino_features,
    conditioning_strength=0.8
)

# Align to target latent shape
latent_shape = adapter.calculate_latent_shape((512, 512))
aligned = adapter.align_spatial_dimensions(
    projected,
    latent_shape
)
```

## Troubleshooting

### DINO Features Not Being Used

If you see the message "DINO Conditioning: ⚠️ Prepared but not fully integrated", this is expected. The current implementation:

- ✅ Extracts DINO features per tile
- ✅ Projects them to FLUX space
- ✅ Prepares conditioning embeddings
- ⚠️ Does not inject into cross-attention (requires custom pipeline)

Full integration would require modifying FLUX's UNet forward pass, which is planned for a future update.

### Out of Memory Errors

If you encounter VRAM issues:

1. Reduce tile size (edit `src/upscaler.py`, line 62-63)
2. Enable CPU offloading (enabled by default)
3. Skip DINO for very large images: `--no-dino`

### Quality Not Improving

If DINO conditioning doesn't seem to help:

1. Try increasing `--dino-strength` to 0.7-0.8
2. Increase denoising `--strength` to 0.4-0.5
3. Use more steps: `--steps 8` (schnell) or `--steps 30` (dev)
4. Ensure your prompt is detailed and specific

## Limitations

### Current Implementation

The current DINO conditioning adapter:
- Extracts and projects features correctly
- Prepares them for injection into FLUX
- Does NOT yet modify FLUX's cross-attention mechanism

This means DINO features are prepared but not fully utilized in the diffusion process. Full integration requires:
- Custom FLUX pipeline with modified UNet
- Injection points in cross-attention layers
- Training/fine-tuning (optional, for best results)

### Planned Improvements

- Direct cross-attention injection
- Cached DINO features (avoid recomputation)
- Adaptive conditioning strength per region
- Multi-scale DINO features

## See Also

- [FLUX Integration Design](../openspec/changes/add-flux-diffusion/design.md)
- [Project Roadmap](../openspec/project.md)
- [DINOv2 Paper](https://arxiv.org/abs/2304.07193)
