# ComfyUI Node Deployment Guide

## Quick Start

### Installing to ComfyUI

The recommended way to install is to clone the entire repository into ComfyUI's custom_nodes directory:

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/timlawrenz/miniature-lamp.git
cd miniature-lamp
pip install -r requirements.txt
```

**Important**: Restart ComfyUI after installation.

### How It Works

ComfyUI automatically discovers custom nodes in subdirectories. When you install the `miniature-lamp` repository, ComfyUI will find the node in the `ComfyUI_DINO_FLUX_Upscale/` subfolder.

Directory structure after installation:
```
ComfyUI/
└── custom_nodes/
    └── miniature-lamp/                    # Repository root
        ├── src/                           # Core upscaler code
        ├── ComfyUI_DINO_FLUX_Upscale/    # ← ComfyUI finds this
        │   ├── __init__.py
        │   ├── nodes.py
        │   ├── utils.py
        │   └── README.md
        ├── requirements.txt
        └── README.md
```

## Verification

After restarting ComfyUI, verify the node is loaded:

1. Check the ComfyUI console/terminal for:
   ```
   Loading custom nodes...
   Loaded: miniature-lamp (contains: DINOFLUXUpscale)
   ```

2. In the ComfyUI interface:
   - Right-click → `Add Node`
   - Navigate to: `image` → `upscaling`
   - You should see: `DINO FLUX Upscale`

## First Run

The first time you use the node:

1. **FLUX Model Download** (~10GB)
   - Downloads from HuggingFace automatically
   - Cached in `~/.cache/huggingface/hub/`
   - Shows progress in ComfyUI console

2. **DINOv2 Model Download** (~350MB)
   - Also downloads automatically
   - Also cached locally
   - One-time download

**Expected console output:**
```
[DINO FLUX Upscale] Loading FLUX schnell model...
Loading checkpoint shards: 100%|████| 2/2 [00:13<00:00]
✓ FLUX model loaded

[DINO FLUX Upscale] Loading DINOv2 model...
(Downloads ~350MB from HuggingFace on first use)
✓ DINOv2 model loaded
```

## Basic Workflow

Minimal workflow to test the node:

```
[Load Image] → [DINO FLUX Upscale] → [Save Image]
```

### Parameters for First Test

Use these conservative settings:
- **scale_factor**: 2.0
- **strength**: 0.1 (minimal changes)
- **flux_variant**: schnell (fast)
- **steps**: 4
- **dino_enabled**: True
- **dino_strength**: 0.5

Queue the prompt and watch the console for progress.

## Troubleshooting

### Node Not Found

If the node doesn't appear in ComfyUI:

1. **Check Installation Path**:
   ```bash
   ls ComfyUI/custom_nodes/miniature-lamp/ComfyUI_DINO_FLUX_Upscale/
   # Should show: __init__.py, nodes.py, utils.py, README.md
   ```

2. **Check Console for Errors**:
   Look for import errors or Python exceptions

3. **Verify Python Environment**:
   ```bash
   # Make sure you're using ComfyUI's Python environment
   which python
   pip list | grep -E "torch|transformers|diffusers"
   ```

4. **Reinstall Requirements**:
   ```bash
   cd ComfyUI/custom_nodes/miniature-lamp
   pip install -r requirements.txt --force-reinstall
   ```

### Import Errors

If you see errors like `ModuleNotFoundError`:

```bash
cd ComfyUI/custom_nodes/miniature-lamp
pip install -r requirements.txt
```

Required packages:
- torch >= 2.0.0
- transformers >= 4.30.0
- diffusers >= 0.28.0
- Pillow
- numpy

### Out of Memory

If you get CUDA OOM errors:

1. Use `flux_variant: schnell` (lighter)
2. Reduce `scale_factor` (try 1.5)
3. Process smaller images
4. Close other applications
5. Disable DINO if needed (`dino_enabled: False`)

### Slow Performance

First run is always slower (model loading). Subsequent runs should be:
- ~1.8s per tile with schnell
- ~4-5s per tile with dev

If consistently slow:
- Check GPU is being used (console shows `cuda`)
- Close other GPU applications
- Use schnell variant
- Reduce steps to 4

## Alternative Installation Methods

### Method 2: Symlink (Development)

If you're developing/modifying the node:

```bash
cd ~/miniature-lamp  # Your dev location
ln -s $(pwd) ~/ComfyUI/custom_nodes/miniature-lamp
```

Changes are immediately reflected (after restarting ComfyUI).

### Method 3: Copy Only Node (Not Recommended)

You can copy just the node folder, but you'll need to manually copy dependencies:

```bash
cp -r miniature-lamp/ComfyUI_DINO_FLUX_Upscale ~/ComfyUI/custom_nodes/
cp -r miniature-lamp/src ~/ComfyUI/custom_nodes/ComfyUI_DINO_FLUX_Upscale/
```

**Note**: This breaks the clean structure. Use Method 1 instead.

## Updating

To update to the latest version:

```bash
cd ComfyUI/custom_nodes/miniature-lamp
git pull
pip install -r requirements.txt --upgrade
```

Restart ComfyUI after updating.

## Uninstalling

```bash
cd ComfyUI/custom_nodes/
rm -rf miniature-lamp
```

Restart ComfyUI.

Models remain cached in `~/.cache/huggingface/` and can be reused by other applications.

## Advanced: Hot Reload

ComfyUI supports hot reloading custom nodes during development:

1. Make changes to node code
2. In ComfyUI: Right-click → `Reload Custom Nodes`
3. Node updates without full restart

**Note**: Not all changes work with hot reload. For major changes, restart ComfyUI.

## Getting Help

- **Issues**: https://github.com/timlawrenz/miniature-lamp/issues
- **Discussions**: https://github.com/timlawrenz/miniature-lamp/discussions
- **Documentation**: See `docs/` folder in repository

## Testing Without ComfyUI

You can test the node locally before deploying:

```bash
cd miniature-lamp
python test_node_local.py          # Quick tests
python test_node_local.py --full   # Full upscale test
```

This verifies the node works without needing ComfyUI.
