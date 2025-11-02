# ComfyUI Test Workflows

Example workflows for testing the DINO FLUX Upscale node in ComfyUI.

## Quick Start

### Installation

1. **Copy the node to ComfyUI:**
   ```bash
   # From the miniature-lamp directory
   cp -r . ~/ComfyUI/custom_nodes/DINO_FLUX_Upscale/
   
   # Or create a symlink (recommended for development)
   ln -s $(pwd) ~/ComfyUI/custom_nodes/DINO_FLUX_Upscale
   ```

2. **Install dependencies:**
   ```bash
   cd ~/ComfyUI/custom_nodes/DINO_FLUX_Upscale
   pip install -r requirements.txt
   ```

3. **Restart ComfyUI**

4. **Verify:** Right-click in ComfyUI → Add Node → image → upscaling → "DINO FLUX Upscale"

## Test Workflows

### 1. Basic Test (`basic_test.json`)

**Simplest test - just load an image and upscale it.**

```
Load Image → DINO FLUX Upscale → Save Image
```

**How to use:**
1. Drag `basic_test.json` into ComfyUI window (or File → Load)
2. In "Load Image" node, select an image
3. Click "Queue Prompt"
4. First run downloads FLUX model (~10GB, takes 5-10 minutes)

**What to test:**
- Does the node appear and connect properly?
- Does it process without errors?
- Is the output actually upscaled (2x size)?
- Try changing `denoise` value (0.1 vs 0.3 vs 0.5)
- Try changing `tile_size` (512 vs 1024)
- Toggle `dino_enabled` on/off

### 2. External Model Test (`with_external_model.json`)

**Tests the new MODEL and VAE inputs for memory efficiency.**

```
Load Image ───────────────┐
                          ├──→ DINO FLUX Upscale → Save Image
Load Checkpoint → MODEL ──┘
                → VAE ────┘
```

**How to use:**
1. Load `with_external_model.json`
2. In "Load Checkpoint", select a FLUX model from your ComfyUI models folder
   (e.g., `models/checkpoints/flux1-schnell.safetensors`)
3. Select an input image
4. Queue Prompt

**What to test:**
- Do the MODEL and VAE connections work?
- Currently shows a warning (expected - full integration coming)
- Does it still process successfully?

## Testing Checklist

### Basic Functionality
- [ ] Node loads in ComfyUI without errors
- [ ] All parameters show up correctly
- [ ] Can process an image end-to-end
- [ ] Output is upscaled to correct size
- [ ] Progress bar shows during processing

### New Parameters
- [ ] `denoise` slider (0.0-1.0) replaces old `strength`
- [ ] `tile_size` dropdown (512-2048, default 1024)
- [ ] `sampler_name` dropdown shows 15 samplers
- [ ] `scheduler` dropdown shows 6 schedulers
- [ ] MODEL input socket appears
- [ ] VAE input socket appears

### Parameter Effects
- [ ] Lower `denoise` (0.1) = more conservative
- [ ] Higher `denoise` (0.5) = more creative
- [ ] Higher `dino_strength` = better semantic preservation
- [ ] Larger `tile_size` (1024) = better quality but slower
- [ ] Smaller `tile_size` (512) = faster but more seams

## Quick Parameter Guide

### Conservative Upscaling (preserve original)
```
denoise: 0.1-0.2
dino_strength: 0.7-0.9
tile_size: 1024
```

### Balanced (recommended)
```
denoise: 0.2-0.3
dino_strength: 0.5
tile_size: 1024
```

### Creative Enhancement
```
denoise: 0.4-0.5
dino_strength: 0.3
tile_size: 1024
flux_variant: dev
steps: 20
```

## Common Issues

**"Node not found"**
- Restart ComfyUI completely
- Check `custom_nodes/` directory contains the files
- Check ComfyUI console for import errors

**"Out of memory"**
- Reduce `tile_size` to 512
- Use smaller input images
- Close other GPU applications

**"Takes forever to load"**
- First run downloads FLUX model (~10GB)
- Check ComfyUI console for download progress
- Subsequent runs much faster (model cached)

**"Output looks strange"**
- Try reducing `denoise` (start with 0.2)
- Increase `dino_strength` for better preservation
- Use `tile_size: 1024` for FLUX models

## Next Steps

After basic testing works:

1. **Test different images:**
   - Portraits
   - Landscapes  
   - Product photos
   - Low-res screenshots

2. **Compare parameters:**
   - Create multiple upscale nodes with different settings
   - Save outputs side-by-side
   - Find best settings for your use case

3. **Test external models:**
   - Once full integration added
   - Compare memory usage with/without external models

4. **Report issues:**
   - https://github.com/timlawrenz/miniature-lamp/issues
   - Include: GPU model, VRAM, input size, error messages
