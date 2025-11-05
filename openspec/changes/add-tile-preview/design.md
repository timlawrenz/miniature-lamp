# Tile Preview Design

## Context

ComfyUI's sampling infrastructure includes a preview system that allows nodes to display intermediate results during long-running operations. The KSampler and other sampling nodes use this to show generation progress. The DINO Upscale node processes images in tiles, and showing each tile as it's progressively refined during sampling would provide valuable user feedback.

**Stakeholders**: Users running long upscaling operations
**Constraints**: Must work with existing ComfyUI preview infrastructure; must not break when preview system is unavailable
**User Requirement**: 
- Show only the current tile being processed (e.g., 1024x1024), not the partially stitched result
- Show preview updates during sampling steps (progressive refinement), not just at completion

## Goals / Non-Goals

**Goals:**
- Display current tile in ComfyUI's preview area during each sampling step
- Show only the individual tile (e.g., 1024x1024), not merged result
- Leverage ComfyUI sampler's built-in callback mechanism
- Work seamlessly alongside existing progress bar
- Graceful degradation if preview unavailable

**Non-Goals:**
- Show stitched/merged result in preview (only individual tiles)
- Custom preview UI (use ComfyUI's built-in system)
- Preview during DINO feature extraction (only during tile refinement)
- Animated preview transitions between tiles
- Preview quality settings or tile position overlays

## Decisions

### Decision 1: Use ComfyUI's Sampler Callback

**What:** Use the existing `callback` parameter in `comfy.sample.sample()` to receive latent tensors during sampling.

**Why:** 
- Built into ComfyUI's sampling infrastructure (line 200 in comfyui_sampler.py)
- No need to modify ComfyUI internals
- Standard approach used by KSampler and other nodes
- Provides latent tensors at each denoising step
- User explicitly prefers this approach

**Alternatives considered:**
- Custom preview at tile completion only: Less responsive, doesn't show sampling progress
- Modify ComfyUI core: Not maintainable, breaks on updates

### Decision 2: Preview Individual Tiles Only

**What:** Show just the current tile (e.g., 1024x1024) being processed, not the merged result.

**Why:**
- User's explicit requirement - simpler and clearer
- No need to maintain canvas state or do partial stitching
- Minimal code complexity
- Natural match to processing pipeline (one tile at a time)

**Alternatives considered:**
- Show partial stitched result: More complex, not requested, adds state management
- Show tile in context of canvas: Requires rendering/compositing logic

### Decision 3: Preview During Sampling Steps

**What:** Use ComfyUI sampler's built-in `callback` parameter to show preview updates during each sampling step (denoising process).

**Why:**
- Provides much more granular feedback to users (every step, not just per tile)
- ComfyUI's `comfy.sample.sample()` already supports `callback` parameter
- Consistent with how KSampler and other ComfyUI nodes work
- Users explicitly prefer this approach
- Natural integration point - no additional infrastructure needed

**How it works:**
- ComfyUI sampler callback is invoked after each denoising step with latent tensor
- We decode the latent and display the preview
- Users see progressive refinement of each tile

**Alternatives considered:**
- Preview only at tile completion: Less responsive, doesn't show sampling progress
- Preview only at percentage milestones: Not aligned with natural callback points

### Decision 4: Decode Latents for Preview

**What:** Decode latent tensors to images for preview display using the VAE.

**Why:**
- ComfyUI sampler callbacks provide latent tensors, not decoded images
- Preview system needs pixel images to display
- VAE decode is relatively fast compared to full sampling
- Users expect to see actual image previews, not latent representations

**Trade-offs:**
- Additional VAE decoding per preview (every sampling step)
- Acceptable: Preview is optional, users want visual feedback
- Can optimize: Only decode every N steps if performance becomes issue

**Alternatives considered:**
- Show latent visualization: Not user-friendly, hard to interpret
- Decode only at tile completion: Less responsive, doesn't leverage sampler callback

### Decision 5: Callback-Based Architecture

**What:** Pass preview callback from node → upscaler → sampler wrapper, similar to progress_callback pattern.

**Why:**
- Consistent with existing progress_callback implementation
- Decouples preview logic from core upscaling logic
- Easy to disable or modify
- Testable without ComfyUI environment

**Alternatives considered:**
- Direct ComfyUI API calls from deep in call stack: Creates tight coupling
- Event emitter pattern: Overkill for single callback

### Decision 6: Optional Feature with Fallback

**What:** Import preview APIs with try/except, gracefully skip if unavailable.

**Why:**
- Maintains compatibility with different ComfyUI versions
- Allows testing outside ComfyUI environment
- Follows existing pattern for ProgressBar import

**Alternatives considered:**
- Require preview system: Would break in non-ComfyUI environments
- Verbose warnings: Would clutter logs unnecessarily

## Technical Approach

### Sampler Callback Signature (ComfyUI Native)
```python
def sampler_callback(step: int, x0: torch.Tensor, x: torch.Tensor, total_steps: int) -> None:
    """
    ComfyUI sampler callback invoked during denoising process.
    
    Args:
        step: Current step number
        x0: Predicted denoised latent (what we want to preview)
        x: Current noisy latent
        total_steps: Total number of steps
    """
```

### Integration Points

1. **DINOUpscale.upscale()** (nodes.py:~220)
   - Import preview API (likely comfy.utils.LatentPreviewMethod or similar)
   - Create preview callback that decodes latents and displays
   - Pass to upscaler

2. **BasicUpscaler._upscale_with_comfyui()** (src/upscaler.py:~110)
   - Accept preview_callback parameter
   - Pass to comfyui_sampler.upscale()

3. **ComfyUISamplerWrapper.upscale()** (src/comfyui_sampler.py:~184)
   - Accept preview_callback parameter
   - Create wrapper callback that:
     - Receives latent from sampler (x0 parameter)
     - Decodes to image using self.decode_latent()
     - Calls preview_callback with decoded image
   - Pass wrapper to `comfy.sample.sample(callback=...)`

### Preview API Discovery

Research needed to identify exact ComfyUI API:
- Check `comfy.utils` for preview utilities
- Look at KSampler implementation in ComfyUI codebase
- Likely involves `LatentPreviewMethod` or similar
- May use callback pattern similar to progress bar

## Risks / Trade-offs

**Risk: ComfyUI API Changes**
- **Impact**: Preview stops working in new ComfyUI versions
- **Mitigation**: Try/except imports, graceful degradation
- **Likelihood**: Low (preview API is stable and widely used)

**Risk: Preview Decoding Overhead**
- **Impact**: VAE decode per sampling step adds processing time
- **Mitigation**: Preview is optional; can optimize to decode every N steps if needed
- **Likelihood**: Medium (preview adds overhead, but acceptable for user feedback)

**Trade-off: Preview Shows Only Current Tile**
- Users see individual tiles, not overall progress on canvas
- Acceptable: User explicitly requested this behavior
- Benefit: Simpler implementation, no state management

**Trade-off: VAE Decoding Per Step**
- Preview requires decoding latent to image at each sampling step
- Adds processing time (VAE decode is ~50-100ms depending on size)
- Acceptable: Users want to see progress, can optimize later if needed

## Migration Plan

N/A - Pure additive feature, no breaking changes, no data migration needed.

## Open Questions

1. **Q: What is the exact ComfyUI preview API?**
   - Need to examine KSampler implementation
   - Likely in comfy.utils or passed via callback mechanism
   - Will determine in implementation phase (task 1.1-1.3)

2. **Q: Should we optimize to decode every N steps instead of every step?**
   - Start with every step for maximum feedback
   - Add optimization if users report performance issues
   - Could add parameter to control preview frequency
