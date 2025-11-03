# FLUX Dependencies Status

## Current State (v1.0.3)

The DINO Upscale node **currently uses FLUX.1 as its diffusion backend**. While the branding has been generalized to "DINO Upscale", the implementation still depends on FLUX.

### Core Dependencies

1. **flux_pipeline.py** - Wraps `diffusers.FluxImg2ImgPipeline`
   - Supports FLUX.1-schnell (fast, 4 steps)
   - Supports FLUX.1-dev (quality, 20 steps)

2. **upscaler.py** - Uses FLUX pipeline for img2img upscaling
   - Falls back to bicubic if FLUX not available

3. **nodes.py** - Node interface
   - Accepts external MODEL/VAE but doesn't use them yet (TODO)
   - Uses internal FLUX pipeline

### External Model Support Status

**Status:** ⚠️ Not Yet Implemented

The node accepts `model` and `vae` inputs from ComfyUI workflows, but currently:
- Always falls back to internal FLUX.1 models
- Does not use ComfyUI's native sampler system
- External models are ignored

### To Remove FLUX Dependencies

Would require:

1. **Create ComfyUI Sampler Wrapper**
   - Integrate with ComfyUI's `comfy.samplers` 
   - Support external MODEL and VAE properly
   - Use provided sampler_name and scheduler

2. **Refactor Pipeline Architecture**
   - Make diffusion backend pluggable
   - Support both FLUX (via diffusers) and ComfyUI native (via samplers)

3. **Update Upscaler**
   - Abstract the diffusion interface
   - Support multiple backends

### Recommendation

**For v1.0.3:** Keep FLUX as documented dependency
- Update README to clearly state FLUX.1 is used
- Mark as a FLUX-based upscaler with DINO guidance
- External model support can be future enhancement

**For v2.0.0:** Implement true model-agnostic architecture
- Proper ComfyUI sampler integration
- Support any diffusion model
- FLUX becomes optional
