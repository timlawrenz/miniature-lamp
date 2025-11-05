# Add Tile Preview Support

## Why

Most ComfyUI samplers (KSampler, SamplerCustomAdvanced) show real-time previews of what they are working on during generation. This provides valuable feedback to users during long upscaling operations. Currently, the DINO Upscale node only shows a progress bar without visual feedback of the tile currently being refined.

## What Changes

- Add preview image callback support using ComfyUI sampler's built-in callback mechanism
- Display preview updates during each sampling step (denoising process)
- Show each individual tile as it's progressively refined (not the merged/stitched result)
- Maintain existing progress bar functionality while adding visual feedback

## Impact

- **Affected specs**: tiled-upscaling (new capability)
- **Affected code**: 
  - `nodes.py` - DINOUpscale node to pass preview callbacks
  - `src/upscaler.py` - BasicUpscaler to pass callbacks through
  - `src/comfyui_sampler.py` - ComfyUISamplerWrapper to integrate with sampler callback and decode latents

**Performance**: Moderate impact - adds VAE decoding per sampling step (can be optimized to decode every N steps if needed)
**UX**: Significant improvement - users see progressive refinement of each tile during sampling
