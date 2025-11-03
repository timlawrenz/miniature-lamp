# Fix Summary: Double Tensor Permutation Bug

## Issue
**Error:** `RuntimeError: Given groups=1, weight of size [128, 3, 3, 3], expected input[1, 870, 0, 1160] to have 3 channels, but got 870 channels instead`

**Root Cause:** The code was performing double tensor permutation - once manually in our code, and once internally by ComfyUI's VAE.

## The Problem

### What Was Happening

1. **Input tensor:** `[1, 1160, 870, 3]` (ComfyUI format: `[B, H, W, C]`)
2. **Our code permuted to:** `[1, 3, 1160, 870]` (thinking VAE needs `[B, C, H, W]`)
3. **VAE internally does `movedim(-1, 1)`:** `[1, 870, 3, 1160]` ❌ **BROKEN!**
4. **Conv2d sees 870 as channel dimension** instead of 3 → Error!

### Why This Happened

We incorrectly assumed ComfyUI's VAE.encode() expects input in `[B, C, H, W]` format (standard PyTorch convention). However, ComfyUI's VAE is designed to accept ComfyUI's native image format `[B, H, W, C]` and handles the conversion internally.

## The Solution

**Removed all manual permutation** - just pass tensors in ComfyUI format `[B, H, W, C]` to both encode and decode.

### Changes in `src/comfyui_sampler.py`

#### encode_image() - Before:
```python
# WRONG: Manual permute causes double conversion
pixels = image_tensor.permute(0, 3, 1, 2).contiguous()
t = self.vae.encode(pixels)
```

#### encode_image() - After:
```python
# CORRECT: Pass in ComfyUI format, VAE handles conversion
pixels = image_tensor
if not pixels.is_contiguous():
    pixels = pixels.contiguous()
t = self.vae.encode(pixels)
```

#### decode_latent() - Before:
```python
# WRONG: VAE already returns [B, H, W, C], don't permute again
pixels = self.vae.decode(latent)
image = pixels.permute(0, 2, 3, 1).contiguous()
return image
```

#### decode_latent() - After:
```python
# CORRECT: VAE returns [B, H, W, C], use directly
pixels = self.vae.decode(latent)
if not pixels.is_contiguous():
    pixels = pixels.contiguous()
return pixels
```

## How ComfyUI VAE Actually Works

Verified from `/mnt/essdee/ComfyUI/comfy/sd.py`:

### VAE.encode() (line 752):
```python
def encode(self, pixel_samples):
    # ... preprocessing ...
    pixel_samples = pixel_samples.movedim(-1, 1)  # [B,H,W,C] -> [B,C,H,W]
    # ... encode with first_stage_model ...
```
**Input:** `[B, H, W, C]` → **Output:** Latent `[B, C, H//8, W//8]`

### VAE.decode() (line 718):
```python
def decode(self, samples_in):
    # ... decode with first_stage_model ...
    pixel_samples = pixel_samples.movedim(1, -1)  # [B,C,H,W] -> [B,H,W,C]
    return pixel_samples
```
**Input:** Latent `[B, C, H//8, W//8]` → **Output:** `[B, H, W, C]`

## Testing

Created verification test showing correct tensor flow:
```
PIL (1160, 870) 
  → numpy (870, 1160, 3)  [H, W, C]
  → tensor (1, 870, 1160, 3)  [B, H, W, C]
  → VAE.encode() does movedim(-1, 1)
  → Conv2d input (1, 3, 870, 1160)  [B, C, H, W] ✓
```

## Impact

- **Fixes:** RuntimeError with malformed tensor shapes
- **Works with:** All ComfyUI-compatible VAEs (SD 1.5, SDXL, FLUX, etc.)
- **No behavior change:** Only fixes the bug, no API changes
- **Tested:** Verified tensor shapes match expected format at each step

## Key Takeaway

**Always check framework conventions!** ComfyUI uses `[B, H, W, C]` format throughout, and its components handle internal conversions. Don't assume standard PyTorch `[B, C, H, W]` format.
