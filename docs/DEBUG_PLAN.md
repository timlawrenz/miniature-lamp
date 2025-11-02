# FLUX Upscaling Debug Plan

## Problem
FLUX upscaling with DINO conditioning produces unrecognizable results. Need to systematically identify the cause.

## Variables Affecting Output

### 1. Tiling & Stitching
- Tile size (256x256)
- Overlap amount (32 pixels)
- Blend mask calculation
- Coordinate mapping
- Tile generation logic

### 2. FLUX Parameters
- `strength` (denoising strength, 0.0-1.0)
- `guidance_scale` (CFG scale)
- `num_steps` (inference steps)
- `prompt` (text guidance)
- Model variant (schnell vs dev)

### 3. DINO Conditioning
- `dino_conditioning_strength` (0.0-1.0)
- Feature extraction
- Feature projection
- Spatial alignment

### 4. Image Processing
- Image preprocessing (PIL → array conversions)
- Upscaling method (FLUX vs bicubic)
- Final resize operation
- Color space handling

## Debugging Strategy (Bottom-Up Approach)

### Stage 0: Baseline Bicubic (NO tiling)
**Goal**: Verify basic image I/O and simple upscaling works

**Test**:
```bash
python examples/simple_poc.py <image>
```

**What it tests**: Basic bicubic upscaling without tiling
**Expected**: Recognizable 2x upscaled image

---

### Stage 1: Bicubic with Tiling (NO FLUX, NO DINO)
**Goal**: Verify tiling and stitching logic works correctly

**Parameters**:
- `use_flux=False`
- No DINO features
- Bicubic interpolation per tile

**Test command**:
```bash
python examples/flux_poc.py <image> --no-dino
# (uses bicubic fallback)
```

**What it tests**: Tile generation, stitching, blend masks
**Expected**: Recognizable 2x upscaled image (same as Stage 0)

---

### Stage 2: FLUX Only (NO DINO, NO tiling)
**Goal**: Test FLUX img2img on small image (single tile)

**Parameters**:
- Small image (≤512x512) to avoid tiling
- `use_flux=True`
- `--no-dino`
- `strength=0.0` (minimal denoising, almost passthrough)
- `guidance_scale=1.0` (minimal guidance)
- `prompt=""` (empty prompt)

**Test command**:
```bash
# First resize image to 256x256 for single-tile processing
python -c "from PIL import Image; img=Image.open('<image>'); img.resize((256,256)).save('small.jpg')"

python examples/flux_poc.py small.jpg --flux --no-dino \
  --strength 0.0 \
  --prompt "" \
  --seed 42
```

**What it tests**: FLUX img2img pipeline in isolation
**Expected**: Image very similar to input (minimal changes due to strength=0.0)

---

### Stage 3: FLUX with Minimal Denoising (NO DINO, with tiling)
**Goal**: Test FLUX with tiling but minimal modification

**Parameters**:
- Original image size (triggers tiling)
- `use_flux=True`
- `--no-dino`
- `strength=0.1` (very light denoising)
- `guidance_scale=1.0`
- `prompt=""` (empty)

**Test command**:
```bash
python examples/flux_poc.py <image> --flux --no-dino \
  --strength 0.1 \
  --prompt "" \
  --seed 42
```

**What it tests**: FLUX tiled processing with minimal changes
**Expected**: Recognizable image with slight modifications

---

### Stage 4: FLUX with Standard Parameters (NO DINO)
**Goal**: Test FLUX at normal settings without DINO

**Parameters**:
- `use_flux=True`
- `--no-dino`
- `strength=0.3` (default)
- `guidance_scale=3.5` (default)
- `prompt="high quality, detailed, sharp"` (default)

**Test command**:
```bash
python examples/flux_poc.py <image> --flux --no-dino \
  --strength 0.3 \
  --seed 42
```

**What it tests**: FLUX img2img at normal settings
**Expected**: Upscaled image with enhanced details (may look different but should be recognizable)

---

### Stage 5: FLUX + DINO with Zero Conditioning
**Goal**: Test DINO pipeline but with no influence

**Parameters**:
- `use_flux=True`
- DINO features extracted
- `--dino-strength 0.0` (no conditioning)
- `strength=0.1`
- `guidance_scale=1.0`
- `prompt=""`

**Test command**:
```bash
python examples/flux_poc.py <image> --flux \
  --dino-strength 0.0 \
  --strength 0.1 \
  --prompt "" \
  --seed 42
```

**What it tests**: DINO extraction pipeline without affecting output
**Expected**: Same as Stage 3 (DINO extracted but not used)

---

### Stage 6: FLUX + DINO with Light Conditioning
**Goal**: Test DINO conditioning at minimal strength

**Parameters**:
- `use_flux=True`
- `--dino-strength 0.1` (very light conditioning)
- `strength=0.1`
- `guidance_scale=1.0`
- `prompt=""`

**Test command**:
```bash
python examples/flux_poc.py <image> --flux \
  --dino-strength 0.1 \
  --strength 0.1 \
  --prompt "" \
  --seed 42
```

**What it tests**: DINO conditioning at minimal level
**Expected**: Very similar to Stage 3

---

## Parameter Reference Table

| Stage | Tiling | FLUX | DINO | Strength | Guidance | Prompt | Purpose |
|-------|--------|------|------|----------|----------|--------|---------|
| 0 | No | No | No | - | - | - | Baseline |
| 1 | Yes | No | No | - | - | - | Test tiling |
| 2 | No | Yes | No | 0.0 | 1.0 | "" | Test FLUX (passthrough) |
| 3 | Yes | Yes | No | 0.1 | 1.0 | "" | Test FLUX tiling |
| 4 | Yes | Yes | No | 0.3 | 3.5 | default | Test FLUX normal |
| 5 | Yes | Yes | Yes (0.0) | 0.1 | 1.0 | "" | Test DINO pipeline |
| 6 | Yes | Yes | Yes (0.1) | 0.1 | 1.0 | "" | Test DINO minimal |

## Quick Test Script

Save this as `debug_upscale.sh`:

```bash
#!/bin/bash
IMAGE=$1

if [ -z "$IMAGE" ]; then
    echo "Usage: $0 <image_path>"
    exit 1
fi

echo "=== Stage 0: Baseline Bicubic ==="
python examples/simple_poc.py $IMAGE
mv ${IMAGE%.*}_upscaled_2x.${IMAGE##*.} stage0_baseline.png

echo ""
echo "=== Stage 1: Bicubic with Tiling ==="
python examples/flux_poc.py $IMAGE --no-dino
mv ${IMAGE%.*}_upscaled_2x.${IMAGE##*.} stage1_tiling.png

echo ""
echo "=== Stage 2: FLUX Single Tile (needs 256x256 image) ==="
python -c "from PIL import Image; img=Image.open('$IMAGE'); img.resize((256,256)).save('small_test.jpg')"
python examples/flux_poc.py small_test.jpg --flux --no-dino --strength 0.0 --prompt "" --seed 42
mv small_test_flux_2x.jpg stage2_flux_single.png

echo ""
echo "=== Stage 3: FLUX Tiling Minimal ==="
python examples/flux_poc.py $IMAGE --flux --no-dino --strength 0.1 --prompt "" --seed 42
mv ${IMAGE%.*}_flux_2x.${IMAGE##*.} stage3_flux_tiling_minimal.png

echo ""
echo "=== Stage 4: FLUX Normal ==="
python examples/flux_poc.py $IMAGE --flux --no-dino --strength 0.3 --seed 42
mv ${IMAGE%.*}_flux_2x.${IMAGE##*.} stage4_flux_normal.png

echo ""
echo "=== Results saved as stage*.png ==="
ls -lh stage*.png
```

## Diagnostic Checklist

For each stage, check:

- [ ] Output file created successfully
- [ ] Output dimensions correct (2x input)
- [ ] Image recognizable / similar to input
- [ ] No obvious artifacts (seams, discontinuities)
- [ ] Colors preserved correctly
- [ ] No extreme distortions

## Known Issue Hypotheses

### Hypothesis 1: Strength Too High
**Symptom**: Unrecognizable output
**Cause**: `strength=0.3` allows too much modification
**Fix**: Reduce to 0.1 or lower

### Hypothesis 2: Tile Coordinate Mismatch
**Symptom**: Scrambled/misaligned image
**Cause**: Bug in tile position calculation or stitching
**Fix**: Debug `generate_tiles()` and `stitch_tiles()`

### Hypothesis 3: FLUX Upscaling Wrong Direction
**Symptom**: Image looks compressed/weird
**Cause**: FLUX processes at input size then resizes, might be backwards
**Fix**: Check `scale_factor` usage in `upscale_tile()`

### Hypothesis 4: Color Space Issue
**Symptom**: Wrong colors or grayscale
**Cause**: RGB/BGR mismatch or normalization issue
**Fix**: Check PIL/cv2 conversions

### Hypothesis 5: DINO Feature Size Mismatch
**Symptom**: Crashes or weird output with DINO
**Cause**: Feature dimensions don't match tile size
**Fix**: Verify DINO patch extraction per tile

## Next Steps After Testing

1. **Run stages 0-3** to isolate tiling vs FLUX issues
2. **Compare outputs** to identify where degradation occurs
3. **Add debug logging** to problematic stage
4. **Fix identified issue**
5. **Continue to next stage**

## Debug Logging Points

Add these to help diagnose:

```python
# In upscaler.py _upscale_with_flux()
print(f"DEBUG: Input image shape: {image.shape}")
print(f"DEBUG: Target dimensions: {target_w}x{target_h}")
print(f"DEBUG: Generated {len(tiles)} tiles")

# In each tile processing
print(f"DEBUG: Tile {i}: pos ({x},{y}), shape {tile.shape}")
print(f"DEBUG: Upscaled tile shape: {upscaled_tile.shape}")

# In stitch_tiles()
print(f"DEBUG: Output canvas: {result.shape}")
print(f"DEBUG: Stitching tile at ({x},{y}), size {tile.shape}")
```
