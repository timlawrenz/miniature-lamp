# DINO FLUX Upscale Node - Architecture Draft

## Based on Research: 2024-11-02

## Node Design Decision: Monolithic Approach

After analyzing Ultimate SD Upscale, recommend **single node** approach:
- Easier for users (fewer nodes to connect)
- Similar to Ultimate SD Upscale pattern
- Optional DINO can be controlled via parameter
- Can always split later if needed

## Proposed Node Inputs

```python
class DINOFLUXUpscale:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # Image
                "image": ("IMAGE",),  # ComfyUI image tensor [B,H,W,C], 0-1 range
                
                # FLUX Model (from ComfyUI loader node)
                "model": ("MODEL",),
                "positive": ("CONDITIONING",),
                "negative": ("CONDITIONING",),
                "vae": ("VAE",),
                
                # Upscaling Parameters
                "scale_factor": ("FLOAT", {
                    "default": 2.0, 
                    "min": 1.0, 
                    "max": 4.0, 
                    "step": 0.1
                }),
                
                # FLUX Parameters
                "flux_variant": (["schnell", "dev"], {"default": "schnell"}),
                "steps": ("INT", {
                    "default": 4, 
                    "min": 1, 
                    "max": 100
                }),
                "cfg": ("FLOAT", {
                    "default": 3.5, 
                    "min": 0.0, 
                    "max": 20.0, 
                    "step": 0.1
                }),
                "strength": ("FLOAT", {
                    "default": 0.2,  # Conservative default
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.01
                }),
                
                # DINO Parameters
                "dino_enabled": ("BOOLEAN", {"default": True}),
                "dino_strength": ("FLOAT", {
                    "default": 0.5, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.01
                }),
                
                # Tiling Parameters
                "tile_width": ("INT", {
                    "default": 512, 
                    "min": 256, 
                    "max": 2048, 
                    "step": 64
                }),
                "tile_height": ("INT", {
                    "default": 512, 
                    "min": 256, 
                    "max": 2048, 
                    "step": 64
                }),
                "tile_overlap": ("INT", {
                    "default": 64, 
                    "min": 0, 
                    "max": 256, 
                    "step": 8
                }),
                
                # Misc
                "seed": ("INT", {
                    "default": 0, 
                    "min": 0, 
                    "max": 0xffffffffffffffff
                }),
            },
            "optional": {
                "prompt_override": ("STRING", {
                    "default": "",
                    "multiline": True
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("upscaled_image",)
    FUNCTION = "upscale"
    CATEGORY = "image/upscaling"
```

## Implementation Strategy

### Phase 1: Tensor Conversion Layer

```python
def comfyui_to_pil(tensor, batch_index=0):
    """Convert ComfyUI tensor [B,H,W,C] 0-1 to PIL"""
    img_np = (tensor[batch_index].cpu().numpy() * 255).astype(np.uint8)
    return Image.fromarray(img_np)

def pil_to_comfyui(pil_image):
    """Convert PIL to ComfyUI tensor [1,H,W,C] 0-1"""
    img_np = np.array(pil_image).astype(np.float32) / 255.0
    return torch.from_numpy(img_np).unsqueeze(0)
```

### Phase 2: Integrate Existing Code

Our existing code from `src/`:
- `dino_extractor.py` - Can use as-is with PIL images
- `flux_pipeline.py` - Can use as-is
- `upscaler.py` - Can use as-is
- `dino_conditioning.py` - Can use as-is

Just need wrapper to:
1. Convert ComfyUI tensor → PIL
2. Call our existing upscaler
3. Convert result back to ComfyUI tensor

### Phase 3: Model Integration

**Challenge**: Our code loads FLUX directly, but ComfyUI pattern is different.

**Options**:

**Option A**: Accept ComfyUI MODEL and adapt
- Pro: Standard ComfyUI pattern
- Con: Need to understand ComfyUI's MODEL wrapper
- Con: May need significant refactoring

**Option B**: Load FLUX ourselves (ignore MODEL input)
- Pro: Can use our existing code as-is
- Con: Not standard ComfyUI pattern
- Con: Users can't leverage ComfyUI's model management

**Option C**: Hybrid approach
- Accept optional MODEL input
- If not provided, load FLUX ourselves
- If provided, try to use it

**Recommendation**: Start with Option B for POC, move to Option A for production

### Phase 4: DINO Integration

DINO is custom to our node, so we handle it:
1. Load DINOv2 model in node's `__init__` or first run
2. Extract features from PIL image
3. Pass to our existing conditioning adapter
4. Use in FLUX upscaling

### Phase 5: Tiling

Use our existing tiling from `upscaler.py`:
- Already handles tile generation
- Already handles overlap blending
- Just need to expose tile_size parameters

## Simplified Implementation Plan

### MVP Node (Simplest Possible)

```python
import sys
import os
import torch
import numpy as np
from PIL import Image

# Import our existing code
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'miniature-lamp', 'src'))
from dino_extractor import DINOFeatureExtractor
from flux_pipeline import FLUXUpscalePipeline
from upscaler import BasicUpscaler

class DINOFLUXUpscale:
    def __init__(self):
        self.dino_extractor = None
        self.flux_pipeline = None
        self.upscaler = None
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "scale_factor": ("FLOAT", {"default": 2.0, "min": 1.0, "max": 4.0}),
                "strength": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0}),
                "dino_enabled": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "upscale"
    CATEGORY = "image/upscaling"
    
    def upscale(self, image, scale_factor, strength, dino_enabled):
        # Initialize on first run
        if self.flux_pipeline is None:
            self.flux_pipeline = FLUXUpscalePipeline(variant="schnell")
            self.upscaler = BasicUpscaler(
                flux_pipeline=self.flux_pipeline,
                scale_factor=scale_factor
            )
            if dino_enabled:
                self.dino_extractor = DINOFeatureExtractor()
                self.upscaler.dino_extractor = self.dino_extractor
        
        # Convert ComfyUI tensor to PIL
        pil_image = self.comfyui_to_pil(image)
        
        # Extract DINO features if enabled
        dino_features = None
        if dino_enabled and self.dino_extractor:
            dino_features = self.dino_extractor.extract_features(pil_image)
        
        # Upscale using our existing code
        result_pil = self.upscaler.upscale(
            pil_image,
            dino_features=dino_features,
            use_flux=True,
            strength=strength
        )
        
        # Convert back to ComfyUI tensor
        result_tensor = self.pil_to_comfyui(result_pil)
        
        return (result_tensor,)
    
    def comfyui_to_pil(self, tensor, batch_index=0):
        img_np = (tensor[batch_index].cpu().numpy() * 255).astype(np.uint8)
        return Image.fromarray(img_np)
    
    def pil_to_comfyui(self, pil_image):
        img_np = np.array(pil_image).astype(np.float32) / 255.0
        return torch.from_numpy(img_np).unsqueeze(0)
```

## Testing Strategy

### Phase 1: Local Testing Without ComfyUI
```python
# Create fake ComfyUI tensor
image = Image.open("test.jpg")
fake_tensor = pil_to_comfyui(image)

# Test node
node = DINOFLUXUpscale()
result = node.upscale(fake_tensor, 2.0, 0.2, True)

# Check result
result_pil = comfyui_to_pil(result[0])
result_pil.save("result.jpg")
```

### Phase 2: Test in ComfyUI
1. Copy node to ComfyUI's `custom_nodes/` directory
2. Restart ComfyUI
3. Node should appear in "image/upscaling" category
4. Connect to image input and run

### Phase 3: API Testing
- Use ComfyUI's API to queue workflows
- Automate testing different parameters
- Compare results

## Open Questions

1. **Model Loading**: How to best integrate with ComfyUI's FLUX loaders?
2. **Progress Reporting**: How to show progress during tiling?
3. **Error Handling**: What happens if VRAM runs out?
4. **Batch Processing**: Should we handle batches > 1?
5. **DINO Model**: Bundle or require separate download?

## Next Steps

1. Create MVP node with simplified implementation
2. Test locally with fake ComfyUI tensors
3. Test in ComfyUI
4. Iterate based on results
5. Add full parameter support
6. Package for distribution

## Directory Structure

```
ComfyUI/custom_nodes/ComfyUI_DINO_FLUX_Upscale/
├── __init__.py              # Node registration
├── nodes.py                 # Node implementation
├── utils.py                 # Tensor conversion helpers
├── README.md                # Usage documentation
├── requirements.txt         # Dependencies
└── miniature-lamp/          # Our existing code (git submodule or copy)
    └── src/
        ├── dino_extractor.py
        ├── flux_pipeline.py
        ├── upscaler.py
        └── dino_conditioning.py
```

## Dependencies

Will need to add to ComfyUI environment:
- diffusers
- transformers
- Our exact torch/transformers versions may conflict
- Need to test compatibility

## Timeline Estimate

- MVP Implementation: 2-3 hours
- Testing & Debugging: 2-4 hours
- Full Feature Set: 4-6 hours
- Documentation & Packaging: 2-3 hours

**Total**: 10-16 hours spread across 3-4 sessions
