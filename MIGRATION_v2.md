# Migration Guide: v1.x → v2.0

## What Changed

**v2.0.0 removes FLUX completely.** The node is now fully model-agnostic and requires external MODEL + VAE inputs.

## Breaking Changes

### 1. External Model Required

**Before (v1.x):**
```
[Load Image] → [DINO Upscale]
# Could work without external model (used internal FLUX)
```

**After (v2.0):**
```
[Load Checkpoint] → MODEL → [DINO Upscale]
                  → VAE   ↗
[Load Image] ---------------↗
# MUST provide MODEL + VAE
```

### 2. Removed Parameter

- ❌ `flux_variant` - No longer exists (was "schnell" or "dev")

### 3. Changed Defaults

- `steps`: 4 → 20 (FLUX-schnell default was 4, general models need more)

### 4. Dependencies Removed

- diffusers
- accelerate
- safetensors (FLUX-specific)
- sentencepiece
- protobuf

## Why This Change?

### Problems with v1.x FLUX Fallback

1. **Heavy**: diffusers + FLUX dependencies = large package
2. **Redundant**: Users had FLUX loaded anyway in ComfyUI
3. **Inflexible**: Hard-coded to FLUX.1-schnell or FLUX.1-dev
4. **VRAM hungry**: Loaded second copy of model if user had FLUX in workflow

### Benefits of v2.0

1. **✅ Lightweight**: No FLUX dependencies, faster install
2. **✅ Flexible**: Works with ANY model you choose
3. **✅ Efficient**: Uses models already in your workflow
4. **✅ Future-proof**: Automatically supports new ComfyUI models

## How to Upgrade

### Step 1: Update the Node

```bash
cd ComfyUI/custom_nodes/comfyui-dino-upscale
git pull
pip install -r requirements.txt --upgrade
```

### Step 2: Update Your Workflows

Add a Load Checkpoint node and connect MODEL + VAE:

```
[Load Checkpoint (e.g., SDXL)]
    ├─ MODEL ──→ [DINO Upscale]
    └─ VAE ────→ [DINO Upscale]
    
[Load Image] ──→ [DINO Upscale]
```

### Step 3: Adjust Steps (Optional)

If you were using FLUX-schnell (default 4 steps), you may want to increase to 20+ steps for other models.

## Model Recommendations

Works with any ComfyUI model:

- **SD 1.5**: 20-30 steps, tile_size=512
- **SDXL**: 20-40 steps, tile_size=1024  
- **FLUX**: 4-20 steps (schnell=4, dev=20), tile_size=1024
- **Custom models**: Experiment with your model's sweet spot

## Troubleshooting

### Error: "MODEL and VAE are required"

**Cause:** No MODEL/VAE connected to the node.

**Fix:** Add a "Load Checkpoint" node and connect MODEL + VAE outputs to DINO Upscale inputs.

### Slow upscaling

**Cause:** Too many steps for your model.

**Fix:** 
- FLUX schnell: 4-8 steps
- SD/SDXL: 20-30 steps
- Lower denoise value (try 0.2-0.4)

### Out of memory

**Cause:** Model + upscaling uses too much VRAM.

**Fix:**
- Lower tile_size (try 512)
- Use smaller model (SD 1.5 instead of SDXL)
- Enable CPU offloading in your checkpoint loader

## Questions?

Open an issue on GitHub: https://github.com/timlawrenz/miniature-lamp/issues
