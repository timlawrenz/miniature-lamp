# Phase 1: ComfyUI Fundamentals Research

## Date: 2024-11-02

## Task 1.1: Study ComfyUI Custom Node Documentation

### Key Findings from https://docs.comfy.org/custom-nodes/walkthrough

#### Basic Node Structure

A ComfyUI custom node is a Python class that defines:

1. **Class Attributes**:
   - `INPUT_TYPES` - classmethod that returns input definitions
   - `RETURN_TYPES` - tuple of output type names
   - `RETURN_NAMES` - (optional) tuple of output labels
   - `FUNCTION` - name of the method to execute
   - `CATEGORY` - where node appears in UI menu
   - `OUTPUT_NODE` - (optional) boolean if this is a final output node

2. **Required Methods**:
   - The function named in `FUNCTION` attribute
   - Takes inputs as parameters
   - Returns tuple matching `RETURN_TYPES`

#### Minimal Example Structure

```python
class MyNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "param": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0}),
            },
            "optional": {
                "mask": ("MASK",),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "process"
    CATEGORY = "image/upscaling"
    
    def process(self, image, param, mask=None):
        # Implementation here
        return (result_image,)
```

### Questions to Investigate Next:
- [ ] What are the standard type names (IMAGE, MASK, MODEL, etc.)?
- [ ] How are tensors formatted (shape, dtype, range)?
- [ ] How to handle batches?
- [ ] How to report progress?
- [ ] How to handle errors?

---

## Task 1.2: Examine Existing Node Examples

### Looking at ComfyUI Repository

Need to examine:
- `comfy/nodes.py` - core nodes
- Look for upscaling nodes
- Look for nodes with multiple parameters
- Look for nodes that use models

---

## Task 1.3: Node Class Structure

### Required Class Methods/Attributes

**INPUT_TYPES classmethod**:
- Returns dict with "required" and "optional" keys
- Each input is `"name": (TYPE, options_dict)`
- Options can include: default, min, max, step, multiline, etc.

**RETURN_TYPES tuple**:
- Type names for each output
- Must match the return tuple length

**FUNCTION string**:
- Name of the method to call
- Method signature must match INPUT_TYPES

**CATEGORY string**:
- Menu path like "image/upscaling"
- Uses forward slashes for hierarchy

---

## Task 1.4: INPUT_TYPES and RETURN_TYPES System

### Input Type Syntax

```python
"required": {
    "type_name": (TYPE_STRING,),  # Simple type
    "with_default": (TYPE, {"default": value}),
    "with_range": (TYPE, {"min": 0, "max": 1, "step": 0.01}),
    "with_widget": (TYPE, {"multiline": True}),
}
```

### Common Type Names:
- `IMAGE` - image tensors
- `MASK` - mask tensors  
- `LATENT` - latent space tensors
- `MODEL` - model objects
- `VAE` - VAE objects
- `CLIP` - CLIP models
- `CONDITIONING` - conditioning data
- `STRING` - text input
- `INT` - integer
- `FLOAT` - floating point
- `BOOLEAN` - true/false

### Widget Types Based on Input Type:
- STRING with multiline: text area
- FLOAT/INT with min/max: slider
- List of strings: dropdown
- BOOLEAN: checkbox

---

## Task 1.5: Widget Types for Parameters

### Automatic Widget Selection

ComfyUI automatically creates appropriate widgets based on type and options:

**Sliders**:
```python
"strength": ("FLOAT", {
    "default": 0.3,
    "min": 0.0,
    "max": 1.0,
    "step": 0.01,
    "display": "slider"  # optional
}),
```

**Dropdowns**:
```python
"variant": (["schnell", "dev"], {"default": "schnell"}),
```

**Text Input**:
```python
"prompt": ("STRING", {
    "default": "",
    "multiline": True
}),
```

**Integer Input**:
```python
"seed": ("INT", {
    "default": 0,
    "min": 0,
    "max": 0xffffffffffffffff
}),
```

---

## Next Steps for Phase 1

- [x] Basic understanding of node structure
- [ ] Need to see actual example from ComfyUI repo
- [ ] Need to understand IMAGE tensor format
- [ ] Need to understand model handling
- [ ] Need to understand progress reporting

## Questions for Next Phase

1. How are IMAGE tensors formatted exactly? (BHWC? RGB? 0-1 or 0-255?)
2. Can we access existing FLUX model loaders?
3. How to report progress during tiling?
4. Where do we access ComfyUI's API locally?
5. How to test a node without packaging?

---

## Task 1.2: Examine Ultimate SD Upscale Implementation

### Date: 2024-11-02

### Key Findings from Ultimate SD Upscale

#### Image Tensor Format in ComfyUI

From `utils.py`:

**ComfyUI IMAGE Tensor Format**:
- Shape: `[batch_size, height, width, channels]`
- Dtype: `float32`
- Range: `0.0 to 1.0` (not 0-255!)
- Color order: RGB (not BGR)
- Note: BHWC format, NOT BCHW!

**Conversion Functions**:
```python
def tensor_to_pil(img_tensor, batch_index=0):
    # Converts ComfyUI tensor to PIL
    return Image.fromarray((255 * safe_tensor.cpu().numpy()).astype(np.uint8))

def pil_to_tensor(image):
    # Converts PIL to ComfyUI tensor
    image = np.array(image).astype(np.float32) / 255.0
    image = torch.from_numpy(image).unsqueeze(0)  # Add batch dimension
    return image  # Shape: [1, H, W, C]
```

#### Node Input Structure from Ultimate SD Upscale

Ultimate SD Upscale uses:

1. **Image Input**: `("IMAGE",)` - the ComfyUI image tensor
2. **Model Inputs**: 
   - `("MODEL",)` - the diffusion model
   - `("VAE",)` - VAE for encoding/decoding
   - `("UPSCALE_MODEL",)` - upscaling model (e.g., RealESRGAN)
3. **Conditioning**:
   - `("CONDITIONING",)` - positive conditioning (prompt embeddings)
   - `("CONDITIONING",)` - negative conditioning
4. **Sampler Params**:
   - `(comfy.samplers.KSampler.SAMPLERS,)` - list of available samplers
   - `(comfy.samplers.KSampler.SCHEDULERS,)` - list of schedulers
5. **Numeric Params** with widgets:
   - Sliders: `("FLOAT", {"default": value, "min": 0, "max": 1})`
   - Integer inputs: `("INT", {"default": value, "min": 0, "max": max})`

#### Tiling Strategy

Ultimate SD Upscale implements:

**Tile Parameters**:
- `tile_width`, `tile_height`: Size of each tile (default: 512x512)
- `tile_padding`: Overlap/padding between tiles (default: 32)
- `mask_blur`: Gaussian blur for tile blending (default: 8)

**Seam Fixing**:
- Multiple modes: None, Band Pass, Half Tile, Half Tile + Intersections
- Additional pass over tile boundaries to fix seams
- `seam_fix_denoise`: Separate denoising strength for seam fixing

**Processing Flow**:
1. Initial upscale with upscale model (RealESRGAN, etc.)
2. Tile the upscaled image
3. Run SD img2img on each tile
4. Apply seam fixing if enabled
5. Blend tiles back together

#### Model Integration Pattern

Ultimate SD Upscale:
- Accepts MODEL, VAE, CONDITIONING inputs from other nodes
- Does NOT load models itself
- Relies on ComfyUI's model loader nodes
- This is the standard ComfyUI pattern!

**Important**: Users connect model loader nodes → Ultimate SD Upscale node

#### Helper Functions for Tiling

From `utils.py`, useful functions:

```python
# Crop a region from tensor
crop_tensor(tensor, region)  # region = (x1, y1, x2, y2)

# Resize tensor
resize_tensor(tensor, size, mode="nearest-exact")

# Pad tensor with edge data
pad_tensor(tensor, left, right, top, bottom, fill=True, blur=True)

# Expand crop region to target size
expand_crop(region, width, height, target_width, target_height)
```

---

## Answers to Questions

### Q1: IMAGE Tensor Format
✅ **Answered**: 
- Shape: `[B, H, W, C]` (NOT BCHW!)
- Range: `0.0-1.0` (float32)
- RGB color order

### Q2: Can we access existing model loaders?
✅ **Answered**: 
- Yes! Standard pattern is to accept MODEL/VAE/CONDITIONING as inputs
- User connects model loader nodes to our node
- We don't load models ourselves

### Q3: How to report progress?
⏸️ **Deferred**: Need to investigate ComfyUI's progress callback system

### Q4: How does tiling work?
✅ **Answered**:
- Split image into overlapping tiles
- Process each tile independently
- Blend with gaussian blur at boundaries
- Optional seam fixing pass

### Q5: Parameter exposure strategy
✅ **Answered**:
- Use helper function to build INPUT_TYPES dict
- Separate "required" and "optional" inputs
- Provide sensible defaults
- Use dropdowns for mode selection

---

## Key Insights for Our Node

### 1. Don't Load Models Directly
- Accept MODEL input from ComfyUI model loader
- Accept VAE if needed
- Let users manage model loading

### 2. Image Format is Critical
- ComfyUI uses BHWC, not BCHW!
- Must convert to PIL for our existing code
- Remember 0-1 range, not 0-255

### 3. Tiling Pattern is Well-Established
- Use tile_width, tile_height, padding params
- Apply gaussian blur at boundaries
- Consider seam fixing mode

### 4. Input Organization
- Group related parameters
- Use helper functions for cleaner code
- Provide good defaults

### 5. Integration with Existing Code
```python
# Our node will need to:
1. Convert ComfyUI tensor → PIL image
2. Run our existing upscaler code
3. Convert PIL image → ComfyUI tensor
4. Handle batches properly
```

---

## Next Phase Questions

1. How does ComfyUI handle FLUX models specifically?
2. Where can we test the node locally?
3. What's the hot reload workflow?
4. How to package for distribution?
5. Does ComfyUI have DINO model support?

