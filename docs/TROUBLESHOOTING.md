# Troubleshooting Unrecognizable FLUX Upscale Results

## Problem
Running `python examples/flux_poc.py image.jpg --flux --dino-strength 0.7` produces unrecognizable output.

## Root Cause Analysis

The default parameters allow **significant modification** of the image:

| Parameter | Default Value | Effect |
|-----------|--------------|--------|
| `strength` | 0.3 | Allows 30% denoising (heavy modification) |
| `guidance_scale` | 3.5 | Strong CFG guidance |
| `prompt` | "high quality, detailed, sharp, 8k" | Adds text-guided features |
| `dino_conditioning_strength` | 0.5 | Moderate semantic guidance |
| `num_steps` | 4 | Few steps but FLUX is powerful even at 4 |

**Combined effect**: These parameters give FLUX creative freedom to heavily modify the image while upscaling.

## Debugging Tools Created

### 1. `DEBUG_PLAN.md`
Complete systematic debugging guide with 6 stages:
- Stage 0: Baseline bicubic
- Stage 1: Bicubic with tiling  
- Stage 2: FLUX single tile (minimal)
- Stage 3: FLUX tiled (minimal)
- Stage 4: FLUX normal
- Stage 5-6: DINO conditioning tests

### 2. `debug_upscale.sh`
Automated script to run all 6 stages:
```bash
./debug_upscale.sh image.jpg
```
Creates `debug_output/stage*.png` files for comparison.

### 3. `quick_test.sh`
Fast test with neutral parameters:
```bash
./quick_test.sh image.jpg
```
Uses minimal modification settings.

### 4. `check_params.py`
Shows all default parameters:
```bash
python check_params.py
```

## Quick Fix: Neutral Parameters

To get output **closest to simple bicubic upscaling**, use these parameters:

### Option 1: Pure Bicubic (No FLUX)
```bash
python examples/simple_poc.py image.jpg
```
or
```bash
python examples/flux_poc.py image.jpg --no-dino
```

### Option 2: FLUX Passthrough Mode
```bash
python examples/flux_poc.py image.jpg --flux \
    --no-dino \
    --strength 0.01 \
    --prompt "" \
    --seed 42
```
**Effect**: FLUX processes with absolute minimal changes (1% denoising)

### Option 3: FLUX Minimal Modification
```bash
python examples/flux_poc.py image.jpg --flux \
    --no-dino \
    --strength 0.05 \
    --prompt "" \
    --steps 4 \
    --seed 42
```
**Effect**: Very light enhancement while preserving original

## Recommended Testing Sequence

### Step 1: Verify baseline works
```bash
python examples/simple_poc.py image.jpg
```
Check that `image_upscaled_2x.jpg` looks correct.

### Step 2: Test FLUX with neutral settings
```bash
./quick_test.sh image.jpg
```
Compare output to Step 1. Should be very similar.

### Step 3: If Step 2 looks good, gradually increase strength
```bash
# Very light
python examples/flux_poc.py image.jpg --flux --no-dino --strength 0.1 --prompt ""

# Light
python examples/flux_poc.py image.jpg --flux --no-dino --strength 0.2 --prompt ""

# Normal (default)
python examples/flux_poc.py image.jpg --flux --no-dino --strength 0.3
```

### Step 4: Once good strength found, add DINO gradually
```bash
# DINO with minimal influence
python examples/flux_poc.py image.jpg --flux \
    --strength 0.1 \
    --dino-strength 0.1

# DINO with light influence  
python examples/flux_poc.py image.jpg --flux \
    --strength 0.1 \
    --dino-strength 0.3

# DINO with moderate influence
python examples/flux_poc.py image.jpg --flux \
    --strength 0.2 \
    --dino-strength 0.5
```

## Parameter Recommendations by Use Case

### For Minimal Changes (close to bicubic):
```bash
--flux --no-dino --strength 0.05 --prompt ""
```

### For Subtle Enhancement:
```bash
--flux --no-dino --strength 0.15 --prompt "sharp, detailed"
```

### For Noticeable Enhancement:
```bash
--flux --no-dino --strength 0.25 --prompt "high quality, detailed"
```

### For Creative Upscaling:
```bash
--flux --strength 0.4 --dino-strength 0.6 --prompt "high quality, 8k, sharp"
```

## Most Likely Issues

### Issue 1: Strength Too High (MOST LIKELY)
**Symptom**: Unrecognizable output, looks like different image
**Cause**: `strength=0.3` allows too much denoising
**Fix**: Use `--strength 0.05` to 0.15

### Issue 2: Prompt Adding Unwanted Features
**Symptom**: Extra details that weren't in original
**Cause**: Text prompt "high quality, detailed, sharp, 8k" guides generation
**Fix**: Use `--prompt ""` for neutral upscaling

### Issue 3: Tiling Artifacts
**Symptom**: Visible seams or misaligned tiles
**Cause**: Bug in tile stitching
**Fix**: Test with small image (≤512x512) to avoid tiling

### Issue 4: DINO Features Misaligned
**Symptom**: Only appears when DINO enabled
**Cause**: DINO feature extraction or projection issue
**Fix**: Use `--no-dino` to verify FLUX works, then debug DINO separately

## Expected Behavior

### With `strength=0.0`:
Output should be **almost identical** to input, just upscaled.

### With `strength=0.1`:
Output should be **recognizable** with subtle enhancement.

### With `strength=0.3` (default):
Output may look **noticeably different** but should still be recognizable. This is by design - FLUX has creative freedom to add detail.

### With `strength=0.5+`:
Output will look **significantly different**. FLUX essentially generates new content guided by input.

## Next Steps

1. **Run**: `./debug_upscale.sh your_image.jpg`
2. **Check** which stage output becomes unrecognizable
3. **Review** `DEBUG_PLAN.md` for that stage's analysis
4. **Adjust** parameters based on findings

If all stages produce recognizable output but the default command doesn't, the issue is specifically with the default parameter combination (strength + prompt + DINO).
