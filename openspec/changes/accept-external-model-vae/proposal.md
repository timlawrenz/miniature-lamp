# Proposal: Accept External Model and VAE Inputs

## Why
Currently, the DINOFLUXUpscale node loads FLUX models internally, which prevents users from reusing models already loaded in their ComfyUI workflow. This creates unnecessary memory overhead, longer initialization times, and limits flexibility in model selection. Users should be able to pass in pre-loaded models and VAE from other nodes, similar to how standard ComfyUI upscaling nodes work.

## What Changes
- Add optional `model` and `vae` inputs to accept external MODEL and VAE objects from ComfyUI workflow
- Add `tile_size` parameter to allow configuring output tile dimensions (different models work best at different sizes: SD at 512x512, FLUX at 1024x1024)
- Add `sampler_name` and `scheduler` parameters for full sampling control
- Rename `strength` parameter to `denoise` to match ComfyUI conventions (keep `dino_strength` as-is for DINO conditioning)
- Modify pipeline initialization to use external model/VAE when provided instead of loading internally
- Maintain backward compatibility: when model/VAE not provided, fall back to current behavior (loading based on `flux_variant`)
- Update the pipeline to accept and use pre-loaded model components
- **BREAKING**: Users who want to use custom models must now pass them via inputs instead of relying on internal loading

## Impact
- Affected specs: `comfyui-node` (new spec)
- Affected code: 
  - `nodes.py`: Add optional model/vae inputs, tile_size/sampler_name/scheduler parameters, rename strength→denoise
  - `src/flux_pipeline.py`: Accept external pipeline, support sampler/scheduler selection, rename strength→denoise
  - `src/upscaler.py`: Use configurable tile_size instead of hardcoded 512, pass sampler/scheduler
- Benefits:
  - Reduced memory usage (reuse loaded models)
  - Faster node execution (no redundant loading)
  - Greater flexibility (use any model loaded in workflow)
  - Full control over sampling process (sampler, scheduler, denoise)
  - Better integration with standard ComfyUI patterns and conventions
