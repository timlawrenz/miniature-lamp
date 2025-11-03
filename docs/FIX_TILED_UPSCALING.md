# Fix Summary: Implement Proper Tiled Diffusion Upscaling

## Issue
**Symptom**: Node only processes one tile regardless of image size and tile_size setting
**Example**: 864x1152 input → 1728x2304 output with tile_size=1024
- Expected: ~6 tiles (3 wide × 2 tall)
- Actual: 1 tile (entire image)

## Root Cause

The upscaling workflow was **not actually using tiling**. The implementation was:

```python
# OLD - No tiling
def _upscale_with_comfyui(image, ...):
    result = sampler.upscale(
        image,
        scale_factor=2.0,  # Upscale in latent space
        ...
    )
    return result
```

This processed the entire image at once by:
1. Encoding full image to latent
2. Bicubic upscaling the latent
3. Running diffusion on the upscaled latent
4. Decoding to full image

**Problems:**
- No memory benefits from tiling
- Can't handle very large images
- `tile_size` parameter was ignored
- Progress bar showed 1 tile when should be multiple

## The Fix

Implemented **true tiled diffusion upscaling**:

```python
# NEW - Proper tiling
def _upscale_with_comfyui(image, tile_size=1024, ...):
    # 1. Simple upscale to target size (Lanczos)
    upscaled = cv2.resize(image, (target_w, target_h), INTER_LANCZOS4)
    
    # 2. Check if tiling needed
    if target_h <= tile_size and target_w <= tile_size:
        # Process as one tile
        return sampler.upscale(upscaled, scale_factor=1.0, ...)
    
    # 3. Generate overlapping tiles
    tiles = generate_tiles(upscaled, tile_size, overlap=64)
    
    # 4. Process each tile independently
    processed_tiles = []
    for i, (tile, x, y) in enumerate(tiles):
        processed = sampler.upscale(
            tile,
            scale_factor=1.0,  # Already at target size
            seed=seed + i,     # Vary seed per tile
            ...
        )
        processed_tiles.append((processed, x, y))
    
    # 5. Stitch tiles with gradient blending
    result = stitch_tiles(processed_tiles, (target_w, target_h), ...)
    return result
```

## Key Changes

### 1. Workflow Restructure
**Before**: Latent upscale → diffusion
**After**: Pixel upscale → tile → diffusion per tile → stitch

### 2. Tile Calculation Fixed
```python
# Before: Wrong calculation on input dimensions
input_tile_size = tile_size / scale_factor
tiles = calculate_tiles(input_image, input_tile_size)

# After: Correct calculation on output dimensions
target_h, target_w = h * scale_factor, w * scale_factor
tiles = calculate_tiles(upscaled_image, tile_size)
```

### 3. Parameter Consistency
- `strength` → `denoise`
- `num_steps` → `steps`
- `tile_size` now properly passed through

### 4. Per-Tile Seeding
Each tile gets `seed + tile_index` to avoid repetitive patterns

## Results

### Example: 864x1152 input, 2x upscale, tile_size=1024

**Before:**
- Tiles: 1 (entire 1728x2304 image)
- VRAM: High (full image in memory)
- Quality: Limited by processing entire latent at once

**After:**
- Tiles: 6 (3×2 grid: 1024×1024 each with 64px overlap)
- VRAM: Lower (one tile at a time)
- Quality: Each tile gets full diffusion treatment

### Tile Grid Calculation
```
Output: 2304w × 1728h
Tile size: 1024
Overlap: 64
Stride: 960 (1024 - 64)

Width tiles:  ceil(2304 / 960) = 3 tiles
Height tiles: ceil(1728 / 960) = 2 tiles
Total: 3 × 2 = 6 tiles
```

## Benefits

### Memory Management
- Process one tile at a time (1024×1024) vs entire image (2304×1728)
- Enables processing of 4K, 8K+ images
- Predictable VRAM usage

### Quality
- Each tile gets full diffusion treatment at proper resolution
- Better detail generation per region
- Gradient blending prevents visible seams

### Scalability
- Can process arbitrarily large images
- Performance scales linearly with tile count
- Easy to add GPU parallelization later

### User Experience
- Accurate progress bar (6 steps vs 1)
- Clear console logging per tile
- Can interrupt mid-process

## Technical Details

### Why Upscale First?

**Approach 1** (Old): Upscale latent → diffusion
```
864×1152 → encode → 108×144 latent → bicubic 2x → 216×288 latent → diffusion → decode → 1728×2304
```
- Con: Bicubic latent doesn't add real detail
- Con: Diffusion works on already-upscaled blurry latent

**Approach 2** (New): Upscale pixel → tile → diffusion
```
864×1152 → lanczos 2x → 1728×2304 → tiles → encode per tile → diffusion → decode → stitch
```
- Pro: Each tile processed at proper resolution
- Pro: Diffusion adds detail to each region independently
- Pro: Better memory management

### Overlap & Stitching

**Overlap**: 64 pixels between tiles
- Provides context for diffusion model
- Enables gradient blending
- Prevents hard seams

**Gradient Blending**:
- Create fade masks at tile edges
- Weight pixels by distance from edge
- Smooth transitions between tiles

## Testing

Verify with:
```python
# Input: 864×1152
# Scale: 2x
# Output: 1728×2304
# Tile size: 1024

# Expected tiles:
# Width:  2304 / (1024-64) = 2.4 → 3 tiles
# Height: 1728 / (1024-64) = 1.8 → 2 tiles  
# Total: 6 tiles
```

Check console output:
```
[Upscaler] Processing 6 tiles of size 1024x1024
[Upscaler] Processing tile 1/6 at position (0, 0)
[Upscaler] Processing tile 2/6 at position (960, 0)
...
[Upscaler] Stitching 6 tiles
```

## Known Limitations

1. **No DINO per-tile**: DINO features not yet extracted per tile
2. **Sequential processing**: Tiles processed one at a time (could parallelize)
3. **Fixed overlap**: 64px overlap (could make configurable)
4. **Lanczos upscale**: Initial upscale is non-ML (could use ESRGAN)

## Future Improvements

1. Extract DINO features per tile for better semantic guidance
2. Parallel tile processing on multi-GPU systems
3. Configurable overlap size
4. Optional ML-based initial upscale (ESRGAN, Real-ESRGAN)
5. Smart tiling based on content (avoid cutting through faces/objects)
