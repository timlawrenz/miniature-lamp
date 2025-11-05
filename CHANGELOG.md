## [2.1.0] - 2024-11-05

### Added
- **Tile Preview During Sampling**: Real-time visual feedback showing progressive refinement
  - Preview updates after each sampling step (e.g., 20 previews for 20 steps)
  - Shows individual tiles being processed, not merged result
  - Integrates with ComfyUI's native preview system (same as KSampler)
  - Works alongside existing progress bar
  - Graceful degradation if preview system unavailable
  
### Technical Details
- Integrated with `comfy.sample.sample()` callback mechanism
- Callback decodes latent (x0) to image after each denoising step
- Preview sent via `ProgressBar.update_absolute()` to ComfyUI UI
- Zero breaking changes - fully backward compatible
- Performance: Adds ~10-20% overhead due to VAE decode per step (acceptable for user feedback)

### Implementation
- `src/comfyui_sampler.py`: Added preview_callback parameter and sampler callback wrapper
- `src/upscaler.py`: Passes preview_callback through pipeline
- `nodes.py`: Creates preview callback and integrates with ProgressBar

### Benefits
- ✅ Users see what's being processed in real-time
- ✅ Better feedback for long-running upscaling operations
- ✅ Consistent with other ComfyUI sampling nodes (KSampler, etc.)
- ✅ No workflow changes needed - works automatically
# Changelog

## [2.1.0] - 2024-11-05

### Added
- **Tile Preview During Sampling**: Real-time visual feedback showing progressive refinement
  - Preview updates after each sampling step (e.g., 20 previews for 20 steps)
  - Shows individual tiles being processed, not merged result
  - Integrates with ComfyUI's native preview system (same as KSampler)
  - Works alongside existing progress bar
  - Graceful degradation if preview system unavailable
  
### Technical Details
- Integrated with `comfy.sample.sample()` callback mechanism
- Callback decodes latent (x0) to image after each denoising step
- Preview sent via `ProgressBar.update_absolute()` to ComfyUI UI
- Zero breaking changes - fully backward compatible
- Performance: Adds ~10-20% overhead due to VAE decode per step (acceptable for user feedback)

### Implementation
- `src/comfyui_sampler.py`: Added preview_callback parameter and sampler callback wrapper
- `src/upscaler.py`: Passes preview_callback through pipeline
- `nodes.py`: Creates preview callback and integrates with ProgressBar

### Benefits
- ✅ Users see what's being processed in real-time
- ✅ Better feedback for long-running upscaling operations
- ✅ Consistent with other ComfyUI sampling nodes (KSampler, etc.)
- ✅ No workflow changes needed - works automatically

## [2.0.1] - 2024-11-03

### Fixed
- **Critical**: Fixed double tensor permutation bug causing "expected 3 channels, but got 870 channels" error
  - ComfyUI VAE internally converts tensor format with `movedim(-1, 1)`
  - Removed manual permutation in `encode_image()` and `decode_latent()`
  - Now correctly passes tensors in ComfyUI format `[B, H, W, C]`
  
- **Critical**: Added CLIP support for FLUX models to provide required `pooled_output`
  - FLUX models require `pooled_output` in conditioning dictionary
  - Added optional CLIP input to node
  - Properly encode prompts using CLIP when available
  - Fixes `KeyError: 'pooled_output'` with FLUX models

- **Major**: Implemented proper tiled diffusion upscaling
  - Previous version processed entire image as one tile regardless of `tile_size` parameter
  - Now correctly splits large images into overlapping tiles
  - Each tile processed through diffusion independently
  - Gradient blending prevents visible seams
  - Example: 1728×2304 output with tile_size=1024 now processes 6 tiles (3×2 grid) instead of 1

### Changed
- **Improved**: Default denoise value adjusted from 0.2 to 0.25
  - Previous default looked too similar to bicubic upscale
  - New default provides better balance between preservation and enhancement
  - 0.25 = 75% preserved + 25% diffusion enhancement

- **Improved**: Tile estimation now calculates based on output dimensions
  - Progress bar now shows accurate tile count
  - Better memory usage prediction

### Added
- Comprehensive documentation for all fixes in `/docs`:
  - `FIX_DOUBLE_PERMUTATION.md` - Tensor format bug details
  - `FIX_CLIP_POOLED_OUTPUT.md` - CLIP requirement explanation
  - `INVESTIGATION_BICUBIC_QUALITY.md` - Denoise parameter analysis
  - `FIX_TILED_UPSCALING.md` - Tiled upscaling implementation
  - `SESSION_SUMMARY.md` - Complete overview of all changes

### Technical Details
- Fixed parameter name mismatches (`strength` → `denoise`, `num_steps` → `steps`)
- Upscaling workflow now: Lanczos upscale → tile → encode → diffusion → decode → stitch
- Per-tile seeding (seed + tile_index) prevents repetitive patterns
- Fixed tile calculation: uses output dimensions, not input dimensions

### Benefits
- ✅ Works with FLUX, SDXL, and SD 1.5 models
- ✅ Properly tiles large images for memory efficiency
- ✅ Visible diffusion enhancement (not just bicubic)
- ✅ Accurate progress tracking
- ✅ Clear console logging per tile

## [2.0.0] - 2024-11-03

### 🚨 BREAKING CHANGES
- **FLUX completely removed** - External MODEL and VAE are now REQUIRED
- Removed `flux_variant` parameter (no longer needed)
- Removed flux_pipeline.py and config.py
- Default steps changed from 4 to 20 (more appropriate for general models)

### Removed
- FLUX.1 internal model loading
- diffusers, accelerate, safetensors, sentencepiece, protobuf dependencies
- All FLUX-specific code and parameters

### Benefits
- ✅ Smaller package size (no FLUX dependencies)
- ✅ Faster installation
- ✅ Lower VRAM usage (no internal model loading)
- ✅ Works with ANY ComfyUI-compatible model

### Migration Guide

**v1.x workflow:**
```
[Load Image] → [DINO Upscale]
```

**v2.0 workflow (REQUIRED):**
```
[Load Checkpoint] → MODEL → [DINO Upscale]
                  → VAE   ↗
[Load Image] ---------------↗
```

If you don't connect MODEL + VAE, the node will error with a clear message.

## [1.1.0] - 2024-11-03

### Added
- **ComfyUI Native Sampler Support** - Now works with any diffusion model via ComfyUI's sampling system
- `comfyui_sampler.py` - Model-agnostic upscaling using ComfyUI's native samplers
- FLUX_DEPENDENCIES.md documenting architecture

### Changed
- **FLUX is now optional** - When external MODEL/VAE are provided, uses ComfyUI's sampler
- Falls back to FLUX.1 only when no external model is provided
- Upscaler now supports both FLUX and ComfyUI backends
- Renamed `use_flux` parameter to `use_diffusion` for clarity
- Add .env to .gitignore for security

### Fixed
- External model/VAE inputs are now properly utilized
- Module import issues in ComfyUI installations

### Notes
- With external MODEL/VAE: Uses any ComfyUI-compatible diffusion model
- Without external model: Falls back to FLUX.1-schnell or FLUX.1-dev
- DINO conditioning integration with ComfyUI sampler is TODO

## [1.0.2] - 2024-11-03

### Changed
- Renamed project from "DINO FLUX Upscale" to "DINO Upscale" for broader compatibility
- Updated node class name from `DINOFLUXUpscale` to `DINOUpscale`
- Generalized messaging to support any diffusion model backend

### Fixed
- Module import issues in ComfyUI installations

## [1.0.1] - 2024-11-02

### Added
- ComfyUI Registry publishing support
- External model/VAE support for memory efficiency
- Configurable tile sizes, samplers, and schedulers

## [Unreleased] - 2024-11-02

### Added
- **DINO Conditioning Adapter** - Complete implementation for projecting DINO features to FLUX latent space
- **Comprehensive Parameter Documentation** - Full parameter reference in README with use cases
- **Debugging Tools** - `debug_upscale.sh` for systematic multi-stage testing
- **Parameter Inspection** - `check_params.py` for viewing default configurations
- **Quick Test Script** - `quick_test.sh` for fast neutral parameter testing
- **Documentation Suite** in `docs/`:
  - `TROUBLESHOOTING.md` - Parameter tuning and issue resolution
  - `DEBUG_PLAN.md` - Systematic debugging methodology
  - `DINO_CONDITIONING.md` - DINO parameter guide
  - `BUG_FIX_FLUX_UPSCALE.md` - Critical bug analysis
  - `IMPLEMENTATION_SUMMARY.md` - Technical details
- **Test Coverage** - 9 new tests for DINO conditioning adapter (36 total tests)

### Fixed
- **Critical: FLUX Upscaling Bug** - Added missing `width` and `height` parameters to FLUX pipeline
  - Without these, FLUX was auto-selecting sizes causing 4x upscaling instead of 2x
  - Fixed aspect ratio distortion in single-tile processing
- **Scale Factor Application** - Fixed `scale_factor` not being passed in single-tile path
- **Import Issues** - Added try/except for relative imports to support both module and script usage

### Changed
- **README.md** - Complete rewrite with:
  - Full parameter reference tables
  - Usage examples for different scenarios
  - Performance benchmarks
  - Troubleshooting section
  - Quick start guide
- **CONTRIBUTING.md** - Added FLUX development notes and debugging tips
- **Documentation Organization** - Moved all guides to `docs/` folder

### Technical Details
- FLUX img2img pipeline now receives explicit target dimensions
- DINO features extracted per tile for tiled processing
- Adapter supports feature projection (768→4096 dims), spatial alignment, and conditioning strength
- All tests passing with CPU fallback for CI/CD compatibility

## [0.1.0] - 2024-11-01

### Added
- Initial FLUX integration (schnell and dev variants)
- Basic DINO feature extraction
- Tiled processing with seamless blending
- Memory optimizations (CPU offloading, FP16, attention slicing)
- Configuration system with FLUXConfig
- Example scripts (simple_poc.py, flux_poc.py)

### Infrastructure
- OpenSpec-based development workflow
- Test suite foundation
- Project documentation structure
