# ComfyUI Node Improvements

## Issues Identified

### 1. Scale Factor Ignored ✗

**Problem**: Scale factor parameter is ignored, always uses 2x

**Root Cause**: 
- `scale_factor` set during `BasicUpscaler.__init__()`
- Not updated when user changes parameter
- Each upscale call uses the initial value

**Current Flow**:
```python
# First call with scale_factor=2
_initialize_models(flux_variant, scale_factor=2, ...)
  → BasicUpscaler(scale_factor=2)  # Stored in self.upscaler

# Second call with scale_factor=1
_initialize_models(flux_variant, scale_factor=1, ...)
  → self.upscaler already exists, skips init
  → Still uses scale_factor=2 ✗
```

**Fix**: Update scale_factor before each upscale call
```python
# In nodes.py upscale():
if self.upscaler is not None:
    self.upscaler.scale_factor = scale_factor
```

---

### 2. Not Using ComfyUI's Model System ✗

**Problem**: Loads FLUX internally instead of accepting models from ComfyUI

**Why This Matters**:
- Users can't share models between nodes (memory waste)
- Can't use custom checkpoints
- Can't leverage ComfyUI's model management
- Doesn't follow ComfyUI conventions

**Standard ComfyUI Pattern**:
```python
INPUT_TYPES = {
    "required": {
        "model": ("MODEL",),           # UNET/Transformer
        "vae": ("VAE",),                # VAE encoder/decoder
        "conditioning": ("CONDITIONING",), # Text embeddings
        ...
    }
}
```

**Benefits**:
- ✓ Model reuse across workflow
- ✓ Memory efficient
- ✓ User can load custom models
- ✓ Works with model loaders, LoRAs, etc.
- ✓ Follows ecosystem standards

**Required Changes**:
1. Change inputs to accept MODEL, VAE, CONDITIONING
2. Extract FLUX components from ComfyUI's model format
3. Remove internal model loading
4. Pass components to our upscaler

**Challenge**: Our code uses `diffusers` pipeline, ComfyUI uses native format
- Need adapter layer to convert between formats
- Or refactor to use ComfyUI's model calling convention

---

### 3. Ignores Stop Signal ✗

**Problem**: Node doesn't respond to ComfyUI's stop button

**Why**: Long-running operations don't check for interrupts

**ComfyUI's Interrupt System**:
```python
from comfy.utils import ProgressBar

# Create progress bar (also handles interrupts)
pbar = ProgressBar(total_steps)

for i in range(total_steps):
    # This raises exception if user clicks Stop
    pbar.update(1)
    
    # Do work...
```

**Where to Add Checks**:
1. **Tile loop** - Most important
   ```python
   for tile_idx, tile in enumerate(tiles):
       pbar.update(1)  # Check for stop
       process_tile(tile)
   ```

2. **FLUX inference** - Secondary
   ```python
   # In flux_pipeline.py, during diffusion steps
   ```

3. **DINO extraction** - Optional
   ```python
   # Less critical, usually fast
   ```

**Implementation**:
```python
class DINOFLUXUpscale:
    def upscale(self, image, ...):
        from comfy.utils import ProgressBar
        
        # Estimate total work
        num_tiles = estimate_tiles(image, scale_factor)
        pbar = ProgressBar(num_tiles)
        
        # Pass progress callback to upscaler
        result = self.upscaler.upscale(
            ...,
            progress_callback=lambda: pbar.update(1)
        )
```

---

## Proposed Solutions

### Priority 1: Fix Scale Factor (Quick Win)

**Complexity**: Low
**Impact**: High
**Time**: 10 minutes

```python
# In nodes.py, upscale() method:
def upscale(self, image, scale_factor, ...):
    self._initialize_models(flux_variant, scale_factor, dino_enabled)
    
    # FIX: Update scale factor each time
    if self.upscaler is not None:
        self.upscaler.scale_factor = scale_factor
    
    result_pil = self.upscaler.upscale(...)
```

**Test**:
- Scale by 1.0 → should output same size ✓
- Scale by 1.5 → should output 1.5x ✓
- Scale by 2.0 → should output 2.0x ✓

---

### Priority 2: Add Stop Signal Support (Medium Win)

**Complexity**: Medium
**Impact**: High (UX)
**Time**: 30 minutes

**Changes**:

1. **Add progress callback parameter** to `BasicUpscaler.upscale()`:
   ```python
   def upscale(self, image, ..., progress_callback=None):
       # In tile loop:
       for tile in tiles:
           if progress_callback:
               progress_callback()  # Raises interrupt if stopped
           process_tile(tile)
   ```

2. **Use ComfyUI's ProgressBar** in node:
   ```python
   from comfy.utils import ProgressBar
   
   def upscale(self, image, scale_factor, ...):
       h, w = image.shape[1:3]
       num_tiles = self._estimate_tiles(h, w, scale_factor)
       pbar = ProgressBar(num_tiles)
       
       result = self.upscaler.upscale(
           ...,
           progress_callback=lambda: pbar.update(1)
       )
   ```

**Benefits**:
- ✓ User can stop long upscales
- ✓ Shows progress bar in UI
- ✓ Proper cleanup on stop

---

### Priority 3: Use ComfyUI Models (Major Refactor)

**Complexity**: High
**Impact**: High (ecosystem compatibility)
**Time**: 4-8 hours

**Approach Options**:

#### Option A: Adapter Pattern (Recommended)

Keep our diffusers code, add adapter:

```python
INPUT_TYPES = {
    "required": {
        "image": ("IMAGE",),
        "model": ("MODEL",),      # ComfyUI's FLUX model
        "vae": ("VAE",),          # ComfyUI's VAE
        "clip": ("CLIP",),        # For prompt encoding
        "positive": ("CONDITIONING",),
        ...
    }
}

def upscale(self, image, model, vae, clip, positive, ...):
    # Convert ComfyUI model to diffusers format
    flux_pipeline = comfyui_to_diffusers(model, vae, clip)
    
    # Use our existing code
    upscaler = BasicUpscaler(flux_pipeline, ...)
    result = upscaler.upscale(...)
```

**Pros**: Minimal code changes
**Cons**: Conversion overhead, may be tricky

#### Option B: Native ComfyUI Format

Refactor to use ComfyUI's model format directly:

```python
def upscale(self, image, model, vae, positive, ...):
    # Process tiles
    for tile in tiles:
        # Encode with VAE
        latent = vae.encode(tile)
        
        # Denoise with model
        latent = model.sample(latent, positive, ...)
        
        # Decode with VAE
        result = vae.decode(latent)
```

**Pros**: True ComfyUI integration, more efficient
**Cons**: Major refactor, need to understand ComfyUI's API

#### Option C: Hybrid (Phase 1 + Phase 2)

**Phase 1**: Keep internal loading, add optional model inputs:
```python
"optional": {
    "model": ("MODEL",),
    "vae": ("VAE",),
}

# If provided, use them; else load internally
if model is not None:
    use_comfyui_model(model, vae)
else:
    load_flux_internal()
```

**Phase 2**: Deprecate internal loading after testing

**Pros**: Gradual migration, backwards compatible
**Cons**: More complex code temporarily

---

## Recommended Implementation Order

### Sprint 1: Quick Fixes (Today)

1. **Fix scale_factor** (10 min)
   - Update scale_factor before each upscale
   - Test with various scales
   - Commit

2. **Add progress bar + stop support** (30 min)
   - Import ComfyUI ProgressBar
   - Add progress callback to upscaler
   - Handle interrupts gracefully
   - Test stop functionality
   - Commit

**Result**: Node is now usable and responsive ✓

### Sprint 2: Major Refactor (Future)

3. **Add ComfyUI model support** (4-8 hours)
   - Research ComfyUI model format
   - Implement Option A (adapter) or Option C (hybrid)
   - Test with various models
   - Update documentation
   - Commit

**Result**: Node follows ComfyUI conventions ✓

---

## Testing Checklist

### Scale Factor Fix
- [ ] Scale 1.0 → output same size as input
- [ ] Scale 1.5 → output 1.5x size
- [ ] Scale 2.0 → output 2.0x size
- [ ] Scale 4.0 → output 4.0x size
- [ ] Change scale between runs → uses new value

### Stop Signal
- [ ] Click stop during tile processing → stops immediately
- [ ] No errors in console after stop
- [ ] Can run new upscale after stopping
- [ ] Progress bar shows in UI
- [ ] Progress bar updates per tile

### Model Support (Future)
- [ ] Load FLUX via ComfyUI loader → works
- [ ] Share model between nodes → memory saved
- [ ] Use custom checkpoint → works
- [ ] Use with LoRA → works
- [ ] Compare results with internal loading → identical

---

## Code Examples

### Fix 1: Scale Factor

```python
# In nodes.py
def upscale(self, image, scale_factor, strength, flux_variant, steps,
            dino_enabled, dino_strength, seed, prompt="high quality, detailed, sharp"):
    try:
        # Initialize models if needed
        self._initialize_models(flux_variant, scale_factor, dino_enabled)
        
        # FIX: Always update scale_factor
        if self.upscaler is not None:
            self.upscaler.scale_factor = scale_factor
        
        # ... rest of code
```

### Fix 2: Progress Bar

```python
# In nodes.py
def upscale(self, image, scale_factor, ...):
    try:
        from comfy.utils import ProgressBar
        
        # Initialize models
        self._initialize_models(...)
        
        # Estimate work
        h, w = image.shape[1:3]
        num_tiles = self._estimate_tiles(h, w, scale_factor)
        pbar = ProgressBar(num_tiles)
        
        # Convert to PIL
        pil_image = comfyui_to_pil(image)
        
        # Upscale with progress
        result_pil = self.upscaler.upscale(
            pil_image,
            ...,
            progress_callback=lambda: pbar.update(1)
        )
        
        return (pil_to_comfyui(result_pil),)
    except Exception as e:
        # Will catch KeyboardInterrupt from progress bar
        print(f"[DINO FLUX Upscale] Stopped or error: {e}")
        raise

def _estimate_tiles(self, h, w, scale_factor):
    """Estimate number of tiles for progress bar"""
    target_h = int(h * scale_factor)
    target_w = int(w * scale_factor)
    
    # Tile size from config (256x256 with 32px overlap)
    tile_size = 256
    overlap = 32
    stride = tile_size - overlap
    
    tiles_y = (target_h + stride - 1) // stride
    tiles_x = (target_w + stride - 1) // stride
    
    return tiles_y * tiles_x
```

```python
# In src/upscaler.py
def upscale(self, image, dino_features=None, use_flux=True, prompt="", 
            num_steps=4, strength=0.1, seed=None, 
            dino_conditioning_strength=0.5,
            progress_callback=None):  # NEW PARAMETER
    
    # ... existing code ...
    
    # In tiled processing loop:
    for i, (tile, x, y) in enumerate(tiles):
        # Check for stop signal
        if progress_callback:
            try:
                progress_callback()
            except KeyboardInterrupt:
                print("Upscaling stopped by user")
                raise
        
        # Process tile...
```

---

## Impact Assessment

### Scale Factor Fix
- **Users impacted**: All users trying to use scale != 2
- **Severity**: High (broken feature)
- **Urgency**: Immediate

### Stop Signal
- **Users impacted**: Anyone upscaling large images
- **Severity**: Medium (UX issue)
- **Urgency**: High (frustrating without it)

### Model Support
- **Users impacted**: Advanced users, model collectors
- **Severity**: Low (workaround exists - use internal loading)
- **Urgency**: Low (nice to have)

---

## Questions to Resolve

1. **Model Support**: Which option (A/B/C)?
   - Need to research ComfyUI's model API
   - Check diffusers ↔ ComfyUI conversion difficulty
   - Consider maintenance burden

2. **Progress Bar**: Where to show?
   - Per tile? (current proposal)
   - Per step within tile?
   - Overall percentage?

3. **Backwards Compatibility**: 
   - Keep internal model loading as fallback?
   - Or require ComfyUI models only?

4. **DINO Model**: Should it also come from ComfyUI?
   - Probably not - no standard "feature extractor" type
   - Keep internal loading for DINO

---

## Documentation Updates Needed

After fixes:
- [ ] Update INSTALLATION.md with stop button note
- [ ] Update COMFYUI_NODE_README.md with scale factor usage
- [ ] Add example showing 1x detailing
- [ ] Document model input system (after implementing)
- [ ] Update parameter reference

