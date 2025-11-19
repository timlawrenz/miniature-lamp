# Session Summary: DINO Upscale Node Fixes

## Issues Fixed

### 1. Double Tensor Permutation Bug
**Error**: `RuntimeError: expected input[1, 870, 0, 1160] to have 3 channels, but got 870 channels`

**Cause**: Code was manually permuting tensors from `[B, H, W, C]` to `[B, C, H, W]` before passing to VAE, but ComfyUI's VAE already does this conversion internally using `movedim(-1, 1)`.

**Fix**: Removed manual permutation in both `encode_image()` and `decode_latent()`. Now passes tensors in ComfyUI format directly.

**Files**: `src/comfyui_sampler.py`

---

### 2. Missing CLIP for FLUX pooled_output
**Error**: `KeyError: 'pooled_output'`

**Cause**: FLUX models require `pooled_output` in the conditioning dictionary, which comes from CLIP text encoding. Node was creating empty conditioning without this field.

**Fix**: 
- Added optional CLIP input to node
- Use CLIP to encode prompts when available
- Properly format conditioning with pooled_output

**Files**: `nodes.py`, `src/comfyui_sampler.py`, `src/upscaler.py`

---

### 3. Bicubic-Looking Output (Low Denoise)
**Issue**: Upscaled images looked like bicubic interpolation, not diffusion-enhanced

**Cause**: Default denoise=0.2 was too conservative (80% preserved + 20% diffusion)

**Fix**: 
- Initially increased to 0.4
- Based on user feedback, adjusted to 0.25 (balanced)

**Files**: `nodes.py`

---

### 4. No Actual Tiling
**Issue**: Node processed entire image as one tile regardless of size or tile_size parameter

**Example**: 1728×2304 output with tile_size=1024
- Expected: 6 tiles (3×2 grid)
- Actual: 1 tile (entire image)

**Cause**: Implementation was upscaling in latent space without using tile generation/stitching code.

**Fix**: Implemented proper tiled diffusion upscaling:
1. Simple upscale to target size (Lanczos)
2. Split into overlapping tiles (1024×1024 with 64px overlap)
3. Process each tile through diffusion independently
4. Stitch tiles with gradient blending

**Files**: `src/upscaler.py`, `nodes.py`

---

## Current Workflow

### Node Inputs
- **Required**: image, scale_factor, denoise, tile_size, sampler_name, scheduler, steps, dino_enabled, dino_strength, seed
- **Optional**: model (REQUIRED for FLUX), vae (REQUIRED for FLUX), clip (REQUIRED for FLUX), prompt

### Upscaling Process
```
1. Load image [B, H, W, C]
2. Extract DINO features (if enabled)
3. Simple upscale to target size (Lanczos)
4. Split into tiles (if needed)
5. For each tile:
   - Encode to latent [B, C, H//8, W//8]
   - Run diffusion with denoise strength
   - Decode back to pixels
6. Stitch tiles with gradient blending
7. Return upscaled image
```

### FLUX Model Setup
```
[Load Checkpoint] → MODEL → [DINO Upscale] → [Preview Image]
                   → VAE   ↗
                   → CLIP ↗
```

---

## Parameter Recommendations

### Denoise (Default: 0.25)
- **0.15-0.20**: Very subtle, mostly bicubic
- **0.25-0.30**: Balanced enhancement (recommended)
- **0.35-0.45**: Strong detail generation
- **0.50+**: Heavy modification

### Tile Size (Default: 1024)
- **512**: SD 1.5 optimal, more tiles, slower
- **1024**: FLUX/SDXL optimal, balanced (recommended)
- **2048**: Fewer tiles, higher VRAM, faster

### Scale Factor (Default: 2.0)
- **1.5-2.0**: Standard upscaling
- **2.5-4.0**: Aggressive upscaling (may need higher denoise)

---

## Key Improvements

### Memory Efficiency
- Process one tile at a time instead of entire image
- Enables 4K, 8K+ image processing
- Predictable VRAM usage

### Quality
- Each tile gets full diffusion treatment
- Gradient blending prevents seams
- Per-tile seeding avoids repetitive patterns

### User Experience
- Accurate progress tracking (shows all tiles)
- Clear logging: "Processing tile 1/6 at position (0, 0)"
- Can interrupt mid-process

---

## Testing Verified

### Test Case: 864×1152 input, 2x scale
- Output: 1728×2304
- Tile size: 1024
- Expected tiles: 6 (3 wide × 2 tall) ✓
- Denoise: 0.25 ✓
- Quality: Noticeable diffusion enhancement ✓

### Supported Models
- ✅ FLUX (with CLIP)
- ✅ SDXL (with CLIP)
- ✅ SD 1.5 (CLIP optional)

---

## Documentation Created
- `docs/FIX_DOUBLE_PERMUTATION.md` - Tensor permutation bug details
- `docs/FIX_CLIP_POOLED_OUTPUT.md` - CLIP requirement for FLUX
- `docs/INVESTIGATION_BICUBIC_QUALITY.md` - Denoise parameter analysis
- `docs/FIX_TILED_UPSCALING.md` - Tiled upscaling implementation

---

## Commits
1. `c93fff5` - Fix: Remove double tensor permutation in VAE encode/decode
2. `b2f47ec` - docs: Add detailed fix documentation for double permutation bug
3. `0810223` - Fix: Add CLIP support for FLUX pooled_output requirement
4. `bbeebe9` - docs: Add detailed fix documentation for CLIP pooled_output requirement
5. `317d040` - Improve: Increase default denoise from 0.2 to 0.4 for better diffusion effect
6. `25641fd` - Fix: Implement proper tiled diffusion upscaling
7. `c2fafdb` - docs: Add detailed documentation for tiled upscaling implementation
8. `5e9969e` - Adjust: Set default denoise to 0.25 for balanced quality

---

## Summary

All major issues fixed! The node now:
- ✅ Works with FLUX models (proper CLIP conditioning)
- ✅ Uses proper tensor formats (no double permutation)
- ✅ Implements true tiled diffusion upscaling
- ✅ Has balanced default parameters (denoise=0.25)
- ✅ Provides clear progress feedback
- ✅ Handles large images efficiently
- ✅ Produces visibly diffusion-enhanced results
