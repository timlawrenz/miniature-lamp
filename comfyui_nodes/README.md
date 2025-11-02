# DINO FLUX Upscale - ComfyUI Custom Node

Semantic-aware image upscaling using DINOv2 vision features and FLUX diffusion models.

## Features

- **Semantic Preservation**: Uses DINOv2 to maintain object identity and characteristics
- **FLUX Diffusion**: High-quality upscaling with FLUX schnell/dev models
- **Tiled Processing**: Automatically handles large images with seamless tile blending
- **Configurable**: Adjust strength, DINO conditioning, and other parameters
- **Memory Efficient**: Automatic model offloading and optimizations

## Installation

### Option 1: Install in ComfyUI (Recommended)

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/your-username/miniature-lamp.git ComfyUI_DINO_FLUX_Upscale
cd ComfyUI_DINO_FLUX_Upscale
pip install -r requirements.txt
```

### Option 2: Development Installation

```bash
# In this repository
cd comfyui_nodes/
# ComfyUI will auto-discover nodes in this directory
```

## Usage

1. Start ComfyUI
2. Find "DINO FLUX Upscale" in the node menu under `image/upscaling`
3. Connect an image input
4. Adjust parameters as needed
5. Queue prompt

### Parameters

#### Core Parameters
- **scale_factor** (1.0-4.0): Upscaling factor, default 2.0
- **strength** (0.0-1.0): FLUX denoising strength, default 0.2
  - Lower = more conservative (preserve original)
  - Higher = more creative (add details)

#### FLUX Parameters  
- **flux_variant**: Choose "schnell" (fast) or "dev" (quality)
- **steps**: Inference steps (4 for schnell, 20+ for dev)
- **prompt**: Text guidance for FLUX (optional)
- **seed**: Random seed for reproducibility

#### DINO Parameters
- **dino_enabled**: Toggle DINO semantic conditioning
- **dino_strength** (0.0-1.0): How much to use DINO features, default 0.5

## First Run

On first use, the node will download:
- **FLUX model** (~10GB) from HuggingFace
- **DINOv2 model** (~350MB) from HuggingFace

Models are cached in `~/.cache/huggingface/` for subsequent runs.

## Requirements

- CUDA-capable GPU (8-12GB VRAM recommended)
- Python 3.8+
- ComfyUI
- See `requirements.txt` for Python dependencies

## Examples

### Conservative Upscaling (Preserve Original)
- scale_factor: 2.0
- strength: 0.1
- dino_enabled: True
- dino_strength: 0.3

### Balanced (Recommended)
- scale_factor: 2.0
- strength: 0.2
- dino_enabled: True
- dino_strength: 0.5

### Creative Enhancement
- scale_factor: 2.0
- strength: 0.4
- flux_variant: dev
- steps: 20
- dino_strength: 0.7

## Troubleshooting

### Out of Memory
- Use "schnell" variant instead of "dev"
- Reduce image size before upscaling
- Close other applications

### Slow Processing
- Use "schnell" variant (4 steps)
- Disable DINO if not needed
- Smaller scale_factor

### Poor Quality
- Increase strength (0.3-0.4)
- Use "dev" variant with more steps
- Adjust DINO strength
- Try different prompts

## Development

### Local Testing

```bash
# Quick tests (structure, tensor conversion)
python test_node_local.py

# Full test with actual upscaling
python test_node_local.py --full
```

### Structure

```
comfyui_nodes/
├── __init__.py       # Node registration
├── nodes.py          # Main node implementation
└── utils.py          # Tensor conversion utilities
```

## Technical Details

- **ComfyUI Image Format**: [B, H, W, C], float32, 0-1 range, RGB
- **Tiling**: Automatic for images > 512px, with gaussian blur blending
- **Model Loading**: Lazy initialization on first use
- **Memory**: Aggressive offloading, attention slicing, VAE slicing

## Credits

- DINOv2 by Meta AI Research
- FLUX by Black Forest Labs
- ComfyUI by comfyanonymous

## License

[Your license here]

## Links

- [Main Repository](https://github.com/your-username/miniature-lamp)
- [Documentation](../docs/)
- [Issues](https://github.com/your-username/miniature-lamp/issues)
