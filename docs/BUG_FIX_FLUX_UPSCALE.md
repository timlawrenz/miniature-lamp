# Critical Bug Fix: FLUX Upscaling Logic

## Issue Identified

The FLUX img2img upscaling was implemented backwards, causing:
- **Stage 2**: Aspect ratio changed to 1:1, image stretched
- **Stage 3**: Tiles showing disconnected details, unrecognizable output

## Root Cause

**Original (Incorrect) Logic:**
```python
# Process at original size
result = flux_pipe(image=original_image)
# Then resize to 2x
result = result.resize((w*2, h*2))
```

This approach:
1. FLUX sees small input (256x256)
2. FLUX refines at that small size
3. Then we enlarge with simple interpolation
4. Result: Loss of aspect ratio, poor quality

## Fix Applied

**Corrected Logic:**
```python
# First upscale to target size with interpolation
upscaled_input = image.resize((w*2, h*2), LANCZOS)
# Then FLUX refines at that size
result = flux_pipe(image=upscaled_input)
```

This approach:
1. Start with high-quality interpolation to target size
2. FLUX refines/enhances at full resolution
3. Maintains aspect ratio
4. Proper img2img workflow

## Files Modified

- `src/flux_pipeline.py`: Fixed `upscale_tile()` method (lines 168-216)
- `debug_upscale.sh`: Improved output naming (`${BASENAME}_stage*.png`)

## Testing Recommendation

Run the debug script again:
```bash
./debug_upscale.sh 46723.png
```

**Expected improvements:**
- **Stage 2**: Should maintain aspect ratio, look like input
- **Stage 3**: Should be fully recognizable with subtle enhancements
- **Stage 4**: Should be recognizable with more noticeable enhancements

## Technical Details

FLUX img2img expects:
- Input image at TARGET resolution
- `strength` parameter controls how much to denoise/modify
- Lower strength (0.01-0.1) = subtle changes
- Higher strength (0.3+) = significant regeneration

Our previous approach was treating it like:
- Process at source resolution
- Then enlarge

Which is fundamentally wrong for img2img workflows.
