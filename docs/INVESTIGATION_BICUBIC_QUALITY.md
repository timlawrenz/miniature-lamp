# Investigation: Upscale Looks Like Bicubic Instead of Diffusion

## Issue Report
- **Symptom**: Upscaled image looks like bicubic upscale, not diffusion-enhanced
- **Parameters**: 2x upscale, denoise=0.2, 20 steps, one tile
- **Test image**: premium_photo-1761298779234-6f1f02431c7b.png (1160x870)

## Root Cause Analysis

### Current Implementation Flow
```
1. Encode original image → latent (145x109 at 8x downscale)
2. Bicubic upscale latent → 2x bigger (290x218)  
3. Run diffusion with denoise=0.2 (barely modifies it)
4. Decode → final image
```

### Why It Looks Like Bicubic

**The denoise=0.2 is too low!**

- `denoise=0.0` = No diffusion, pure latent upscale
- `denoise=0.2` = 80% of original, 20% new generation
- `denoise=0.4` = 60% of original, 40% new generation  
- `denoise=0.6` = 40% of original, 60% new generation
- `denoise=1.0` = 100% new generation

At denoise=0.2, the diffusion model is:
1. Taking the bicubic-upscaled latent
2. Adding only 20% noise
3. Denoising back (which mostly recovers the original)
4. Result: ~80% bicubic upscale + ~20% diffusion refinement

This is by design for **conservative upscaling** (preserving the original), but it won't look dramatically different from bicubic.

## Solutions

### Option 1: Increase Denoise (Quick Fix)

**For more dramatic diffusion effect:**
- Change denoise from `0.2` to `0.4-0.6`
- This allows the model to generate more detail
- Trade-off: Less faithful to original, more "hallucinated" details

**Example parameters:**
```python
denoise=0.4  # Balanced: noticeable diffusion enhancement
denoise=0.5  # Strong: significant new detail generation
denoise=0.6  # Very strong: almost like text2img
```

### Option 2: Implement Proper Tiled Diffusion (Correct Fix)

The current implementation doesn't use the `tile_size` parameter for actual tiled diffusion processing. It should:

```python
1. Simple upscale image to target size (bicubic/lanczos)
2. Split into overlapping tiles (e.g., 1024x1024)
3. Encode each tile → latent
4. Run diffusion on each tile independently
5. Decode each tile → image
6. Stitch tiles with gradient blending
```

**Benefits:**
- Process huge images (4K, 8K+)
- Each tile gets full diffusion treatment
- Better VRAM management
- Can use higher denoise per tile

**Current limitation:**
The `generate_tiles()` and `stitch_tiles()` methods exist but aren't being used in the diffusion path.

## Recommendations

### Immediate (User-facing)
1. **Update default denoise to 0.4** (currently 0.2)
2. **Add warning in docs** about denoise values:
   - 0.1-0.2: Subtle refinement (looks like bicubic)
   - 0.3-0.4: Moderate enhancement (recommended)
   - 0.5-0.6: Strong enhancement (adds detail)
   - 0.7+: Heavy modification (may look different)

### Long-term (Development)
1. **Implement true tiled diffusion upscaling:**
   ```python
   def _upscale_with_tiled_diffusion(self, image, tile_size=1024, overlap=64, ...):
       # 1. Upscale image to target size (simple)
       upscaled = simple_upscale(image, scale_factor)
       
       # 2. Generate tiles
       tiles = self.generate_tiles(upscaled, tile_size, overlap)
       
       # 3. Process each tile through diffusion
       processed_tiles = []
       for tile, x, y in tiles:
           # Encode tile → latent
           latent = encode(tile)
           # Run diffusion (no latent upscaling needed)
           denoised_latent = diffusion(latent, denoise=denoise)
           # Decode → processed tile
           processed_tile = decode(denoised_latent)
           processed_tiles.append((processed_tile, x, y))
       
       # 4. Stitch tiles
       result = self.stitch_tiles(processed_tiles, output_size, tile_size, overlap)
       return result
   ```

2. **Or use ComfyUI's tiled VAE encode/decode**
   - Available via `vae.encode_tiled()` and `vae.decode_tiled()`
   - Automatically handles large images
   - Still need to handle diffusion tiling separately

## Testing Suggestions

Try these denoise values with the same image:
- denoise=0.2 (current) - Should look mostly bicubic
- denoise=0.4 - Should show noticeable detail enhancement
- denoise=0.6 - Should look significantly different with generated details

Document which value gives the best quality/fidelity trade-off.

## Technical Notes

### Why Upscale Latent vs Image?

Current approach (upscale latent):
- **Pro**: Computationally cheaper (work in latent space)
- **Pro**: Can leverage latent structure
- **Con**: Bicubic latent upscale doesn't add real detail
- **Con**: Low denoise preserves the "blurry" upscaled latent

Alternative approach (upscale image, then process tiles):
- **Pro**: Each tile gets full diffusion treatment
- **Pro**: Works better with higher denoise
- **Pro**: True tiled processing for large images
- **Con**: More computationally expensive
- **Con**: Requires careful tile stitching

### Current vs Ideal Flow

**Current (Latent Upscale + Refinement):**
```
Image → Latent → Bicubic 2x → Denoise 20% → Decode → Output
         ↑                                              ↓
         └───────── Mostly preserved ──────────────────┘
```

**Ideal (Tiled Diffusion Upscaling):**
```
Image → Bicubic 2x → Tiles → Encode → Denoise 40-60% → Decode → Stitch
                                ↑                         ↓
                                └── Generate detail ──────┘
```

## Conclusion

The upscale looks like bicubic because:
1. **Denoise=0.2 is too conservative** (only 20% diffusion)
2. **No actual tiled diffusion processing** (just latent interpolation)

Quick fix: Increase default denoise to 0.4
Proper fix: Implement tiled diffusion upscaling workflow
