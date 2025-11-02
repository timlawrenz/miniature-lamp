## Why

The POC successfully extracts DINO semantic features but uses simple bicubic upscaling. To achieve semantic-aware upscaling, we need a diffusion model that can be conditioned on DINO embeddings. FLUX is a modern, high-quality diffusion model that can be adapted for img2img upscaling with custom conditioning.

## What Changes

- Integrate FLUX diffusion model for img2img upscaling pipeline
- Implement DINO feature injection as additional conditioning signal
- Create tiled upscaling workflow that processes tiles with DINO guidance
- Add feature mapping to align DINO patches with upscaled tile coordinates
- Replace bicubic upscaling in BasicUpscaler with FLUX-based generation
- Add configuration for FLUX model variants and sampling parameters

## Impact

- Affected specs: `flux-integration` (new), `dino-guided-conditioning` (new), `image-upscaling` (modified)
- Affected code: 
  - `src/upscaler.py` - Replace bicubic with FLUX pipeline
  - `src/flux_pipeline.py` - New FLUX integration
  - `src/dino_conditioning.py` - New DINO conditioning adapter
  - `examples/simple_poc.py` - Update to use FLUX
- Dependencies: Add `diffusers`, `accelerate`, FLUX model weights
- Performance: Significantly slower than bicubic but higher quality with semantic consistency
