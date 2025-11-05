# Testing Checklist for v2.1.0

**Release**: v2.1.0 - Tile Preview Support  
**Type**: Minor (Feature + Regression Testing)  
**Estimated Time**: 1-2 hours  
**Date**: ___________

## Installation

```bash
# Navigate to ComfyUI custom_nodes
cd /mnt/essdee/ComfyUI/custom_nodes/

# Backup existing installation (if present)
if [ -d "comfyui-dino-upscale" ]; then
  mv comfyui-dino-upscale comfyui-dino-upscale.backup-$(date +%Y%m%d-%H%M)
fi

# Copy development version
cp -r /home/tim/source/activity/miniature-lamp comfyui-dino-upscale

# Verify files copied
ls -la comfyui-dino-upscale/
```

Restart ComfyUI after installation.

---

## ✅ Installation Verification

- [x] Node appears in menu: Image → Upscaling → DINO Upscale
- [x] No Python errors in console during startup
- [x] Dependencies loaded correctly

---

## 🆕 New Feature Tests: Tile Preview

### Test 1: Small Image (Single Tile)
**Setup**: 512x512 image, scale=2.0, steps=10

- [x] Preview shows during processing
- [x] Preview updates ~10 times (once per step)
- [x] Preview shows progressive refinement
- [ ] Final result matches expected quality

**Result**: ___________

### Test 2: Large Image (Multi-Tile)
**Setup**: 1024x1024 image, scale=2.0, steps=10

- [ ] Preview updates for each tile
- [ ] Each preview shows individual tile (not merged)
- [ ] Preview changes when switching to next tile
- [ ] All tiles complete successfully

**Result**: ___________

### Test 3: Progress Bar + Preview Together
- [x] Progress bar increments correctly
- [x] Progress bar and preview update together
- [x] Progress shows tile count (e.g., 2/4)

**Result**: ___________

### Test 4: Stop Button Works
- [ ] Start upscaling large image
- [ ] Click Stop during processing
- [ ] Processing stops cleanly
- [ ] No Python errors

**Result**: ___________

---

## 🔄 Regression Tests: Existing Features

### Test 5: Model Compatibility
Test with different model types:

- [ ] **SD 1.5**: Works correctly
- [ ] **SDXL**: Works correctly
- [ ] **FLUX**: Works correctly (with CLIP connected)

**Result**: ___________

### Test 6: DINO Feature Extraction
- [x] Set dino_enabled = True
- [x] Console shows "Extracting DINO features..."
- [x] Console shows "Extracted N patch features"
- [x] Upscaling completes successfully

**Result**: ___________

### Test 7: DINO Disabled
- [x] Set dino_enabled = False
- [x] No DINO messages in console
- [x] Upscaling still works (faster)

**Result**: ___________

---

## 📐 Scenario Tests

### Test 8: Different Image Sizes
- [ ] Small (256x256): ___________
- [ ] Medium (768x768): ___________
- [ ] Large (1536x1536): ___________

### Test 9: Different Scale Factors
- [ ] 1.5x: ___________
- [ ] 2.0x: ___________
- [ ] 3.0x: ___________

### Test 10: Different Denoise Values
- [ ] 0.1 (subtle): ___________
- [ ] 0.25 (default): ___________
- [ ] 0.5 (strong): ___________

### Test 11: Different Samplers
- [ ] euler: ___________
- [ ] dpmpp_2m: ___________
- [ ] ddim: ___________

---

## ⚠️ Error Handling

### Test 12: Missing MODEL/VAE
- [ ] Don't connect MODEL input
- [ ] Run node
- [ ] **Expected**: Clear error message

**Result**: ___________

### Test 13: Memory Pressure
- [ ] Try large image (2000x2000+)
- [ ] Monitor memory usage
- [ ] **Expected**: Tiling prevents OOM
- [ ] **Expected**: Preview doesn't cause issues

**Result**: ___________

---

## ⚡ Performance

### Test 14: Preview Overhead
Test same image with preview enabled:

- [ ] Time with preview: _____ seconds
- [ ] Visual quality check: Good / Acceptable / Poor
- [ ] **Expected**: ~10-20% slower is acceptable

**Result**: ___________

---

## 📊 Test Summary

**Date Tested**: ___________  
**ComfyUI Version**: ___________  
**Python Version**: ___________  
**GPU**: ___________  

**Tests Passed**: ___ / 14  
**Tests Failed**: ___  
**Critical Issues**: ___  

---

## ✅ Sign-off

**Decision**: APPROVE / NEEDS WORK / REJECT

**Tester**: ___________  
**Date**: ___________  

**Notes**:
