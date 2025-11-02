# Contributing to DINO-Guided Image Upscaler

## Development Setup

```bash
# Clone repository
git clone <repository-url>
cd miniature-lamp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_dino_extractor.py
```

## Code Style

We follow PEP 8 guidelines. Format code with Black:

```bash
black src/ tests/ examples/
```

## Project Structure

```
src/
  dino_extractor.py      # DINO feature extraction
  dino_conditioning.py   # DINO→FLUX adapter
  flux_pipeline.py       # FLUX diffusion integration
  upscaler.py            # Upscaling pipeline with tiling
  config.py              # Configuration dataclasses
tests/
  test_dino_extractor.py
  test_dino_conditioning.py
  test_flux_pipeline.py
  test_upscaler.py
examples/
  simple_poc.py          # Basic POC (bicubic)
  flux_poc.py            # FLUX upscaling demo
docs/
  DINO_CONDITIONING.md   # DINO conditioning guide
```

## Making Changes

1. Check `openspec/` for active proposals
2. Create a new change proposal if needed (see `openspec/AGENTS.md`)
3. Implement according to specs
4. Write tests
5. Update documentation
6. Submit PR

## Current Status (Phase 2)

**✅ Completed:**
- DINO feature extraction
- FLUX diffusion model integration
- DINO conditioning adapter (projection + spatial alignment)
- Tiled processing with per-tile DINO guidance
- Configuration system for FLUX parameters
- Memory optimization (offloading, tiling)

**⚠️ Partial:**
- DINO conditioning prepared but not injected into cross-attention
  (requires custom FLUX pipeline modification)

**📋 Planned:**
- Full cross-attention integration
- ComfyUI custom node
- Performance optimizations

## FLUX Development Notes

### Working with FLUX Models

The project supports two FLUX variants:
- `flux-schnell`: Fast (4 steps), good quality
- `flux-dev`: High quality (20 steps)

```python
from src.flux_pipeline import FLUXUpscalePipeline

# Load from HuggingFace (downloads ~10GB)
flux = FLUXUpscalePipeline(variant="schnell")

# Or use local model
flux = FLUXUpscalePipeline(
    model_path="/path/to/flux_schnell.safetensors"
)
```

### VRAM Requirements

- FLUX schnell fp16: ~12GB
- With CPU offloading: ~8GB minimum
- Per-tile processing reduces baseline needs

Tips for low VRAM:
1. Use schnell variant (lighter)
2. Enable offloading (enabled by default)
3. Reduce tile size in `upscaler.py`
4. Process smaller images

### Testing DINO Conditioning

Run the test suite:
```bash
# All DINO conditioning tests
pytest tests/test_dino_conditioning.py -v

# Specific feature
pytest tests/test_dino_conditioning.py::test_spatial_alignment -v
```

Tests run on CPU to avoid VRAM conflicts.

### Adding DINO Conditioning Features

The `DINOConditioningAdapter` class handles:
1. Feature projection (768→4096 dims)
2. Spatial alignment (interpolation to match FLUX latents)
3. Conditioning strength scaling
4. Text+DINO embedding concatenation

To extend:
```python
from src.dino_conditioning import DINOConditioningAdapter

adapter = DINOConditioningAdapter()

# Project features
projected = adapter.project_features(
    dino_features,
    conditioning_strength=0.7
)

# Align to target spatial dimensions
aligned = adapter.align_spatial_dimensions(
    projected,
    target_shape=(32, 32)
)
```

### Debugging Tips

1. **Check DINO feature extraction:**
   ```python
   features = extractor.extract_features(image)
   print(f"Features: {features.shape}")  # Should be (N, 768)
   ```

2. **Verify conditioning adapter:**
   ```python
   projected = adapter.project_features(features)
   print(f"Projected: {projected.shape}")  # Should be (N, 4096)
   ```

3. **Monitor VRAM usage:**
   ```python
   import torch
   print(f"VRAM: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
   flux.clear_memory()
   ```

4. **Test with small images first:**
   Start with 512x512 or smaller to verify pipeline works before scaling up.
