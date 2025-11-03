# DINO Upscale Architecture

## Overview

DINO Upscale is a semantic-aware image upscaler that uses DINOv2 vision features to guide diffusion models. As of v1.1.0, it supports **any diffusion model** via ComfyUI's native sampling system.

## Architecture (v1.1.0)

### Dual Backend Support

The node now supports two diffusion backends:

1. **ComfyUI Native Sampler** (Model-Agnostic) ✨ NEW
   - Used when external MODEL + VAE are provided
   - Works with ANY ComfyUI-compatible diffusion model
   - Uses `comfyui_sampler.py` wrapper
   - Supports: SD 1.5, SDXL, FLUX, and any future models

2. **FLUX Pipeline** (Legacy Fallback)
   - Used when NO external model is provided  
   - Loads FLUX.1-schnell or FLUX.1-dev internally
   - Uses `flux_pipeline.py` wrapper
   - Requires ~8-12GB VRAM

### Component Structure

```
nodes.py (ComfyUI Node Interface)
    ├── DINOUpscale class
    │   ├── Accepts: image, MODEL, VAE, sampler settings
    │   └── _initialize_models()
    │       ├── If MODEL+VAE provided → ComfyUISamplerWrapper
    │       └── Else → FLUXUpscalePipeline
    │
    ├── upscaler.py (Backend Router)
    │   ├── upscale() - routes to appropriate backend
    │   ├── _upscale_with_comfyui() - ComfyUI native
    │   ├── _upscale_with_flux() - FLUX fallback
    │   └── _upscale_bicubic() - simple fallback
    │
    ├── comfyui_sampler.py (NEW) 
    │   └── ComfyUISamplerWrapper
    │       ├── Uses comfy.sample.sample()
    │       ├── Works with any MODEL/VAE
    │       └── Model-agnostic
    │
    ├── flux_pipeline.py (Legacy)
    │   └── FLUXUpscalePipeline
    │       ├── Uses diffusers.FluxImg2ImgPipeline
    │       └── FLUX-specific
    │
    └── dino_extractor.py
        └── DINOFeatureExtractor (DINOv2)
```

### Workflow Modes

#### Mode 1: Model-Agnostic (Recommended)

```
[Load Checkpoint] → MODEL → [DINO Upscale]
                  → VAE   ↗

Benefits:
- ✅ Works with any model (SD, SDXL, FLUX, etc.)
- ✅ No additional model loading
- ✅ Memory efficient
- ✅ Uses ComfyUI's native samplers
```

#### Mode 2: FLUX Fallback (No External Model)

```
[Load Image] → [DINO Upscale]

Behavior:
- Loads FLUX.1 internally
- ~8-12GB VRAM required
- Slower initialization
```

### Key Features

- **Semantic Guidance**: DINOv2 features preserve object identity
- **Tiled Processing**: Handles large images via seamless tiling
- **Flexible Backend**: ComfyUI native or FLUX
- **Configurable**: Scale, denoise, steps, sampler, scheduler

## Dependencies

### Required (Core)
- torch
- transformers (for DINOv2)
- numpy, PIL, opencv

### Optional (Backends)
- **diffusers** - Required ONLY if using FLUX fallback (no external model)
- **ComfyUI** - Always required (provides MODEL/VAE/samplers)

## Future Enhancements

- [ ] DINO conditioning integration with ComfyUI sampler
- [ ] ControlNet integration
- [ ] Attention-based feature injection
- [ ] Multi-model ensemble

## Migration from v1.0.x

v1.0.x: Always used FLUX (external models ignored)
v1.1.0: Uses external models when provided, FLUX only as fallback

**No workflow changes needed** - but now MODEL/VAE inputs are actually used!
