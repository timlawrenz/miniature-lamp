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
