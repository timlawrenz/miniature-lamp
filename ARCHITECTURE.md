# DINO Upscale Architecture

## Overview

DINO Upscale is a semantic-aware image upscaler that uses DINOv2 vision features to guide diffusion models. As of **v2.0.0**, it is **fully model-agnostic** and works with ANY ComfyUI-compatible diffusion model.

## Architecture (v2.0.0)

### Model-Agnostic Design

The node **requires** external MODEL and VAE inputs from ComfyUI workflows. It no longer includes any internal diffusion models.

**Key Principle:** Use the models you already have loaded in your workflow - no duplicate loading, maximum flexibility.

### Component Structure

```
nodes.py (ComfyUI Node Interface)
    ├── DINOUpscale class
    │   ├── REQUIRES: MODEL + VAE inputs
    │   └── _initialize_models()
    │       └── Creates ComfyUISamplerWrapper
    │
    ├── upscaler.py (Upscaling Logic)
    │   ├── upscale() - main entry point
    │   ├── _upscale_with_comfyui() - ComfyUI native sampling
    │   └── _upscale_bicubic() - simple fallback
    │
    ├── comfyui_sampler.py
    │   └── ComfyUISamplerWrapper
    │       ├── Uses comfy.sample.sample()
    │       ├── Works with any MODEL/VAE
    │       └── Encodes → Upscales latent → Samples → Decodes
    │
    └── dino_extractor.py
        └── DINOFeatureExtractor (DINOv2)
            └── Extracts semantic features for guidance
```

### Workflow (REQUIRED)

```
[Load Checkpoint] → MODEL → [DINO Upscale] → [Preview Image]
                  → VAE   ↗
[Load Image] ---------------↗

Benefits:
- ✅ Works with ANY model (SD 1.5, SDXL, FLUX, custom models)
- ✅ No duplicate model loading
- ✅ Memory efficient
- ✅ Uses ComfyUI's native samplers
- ✅ Fast installation (no FLUX dependencies)
```

### Key Features

- **Semantic Guidance**: DINOv2 features preserve object identity
- **Tiled Processing**: Handles large images via seamless tiling
- **Model-Agnostic**: Works with any ComfyUI diffusion model
- **Configurable**: Scale, denoise, steps, sampler, scheduler

## Dependencies

### Required
- torch, torchvision
- transformers (for DINOv2)
- numpy, PIL, opencv
- **ComfyUI** (provides MODEL/VAE/samplers)

### NOT Required
- ❌ diffusers
- ❌ accelerate  
- ❌ safetensors (for FLUX)
- ❌ sentencepiece
- ❌ protobuf

## Changes from v1.x

### v1.1.0 (Dual Backend)
- Supported both ComfyUI sampler AND FLUX fallback
- FLUX loaded if no external model provided
- Larger package size

### v2.0.0 (Model-Agnostic)
- **REMOVED** FLUX fallback completely
- **REQUIRES** external MODEL + VAE
- Smaller, faster, more flexible
- Breaking change: Old workflows need MODEL/VAE connections

## Future Enhancements

- [ ] DINO conditioning integration with ComfyUI sampler
- [ ] ControlNet integration
- [ ] Attention-based feature injection
- [ ] Multi-model ensemble
- [ ] Advanced tiling strategies

## Migration from v1.x

**Old (v1.x):** Could run without external model (used FLUX)
**New (v2.0):** MUST provide external MODEL + VAE

Simply add a "Load Checkpoint" node and connect MODEL + VAE!
