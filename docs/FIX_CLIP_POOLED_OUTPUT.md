# Fix Summary: Missing CLIP for FLUX pooled_output

## Issue
**Error:** `KeyError: 'pooled_output'`

**Root Cause:** FLUX models require `pooled_output` in the conditioning dictionary, which comes from CLIP text encoding. The node was creating empty conditioning without this required field.

## The Problem

### Error Location
The error occurred during sampling in ComfyUI's model_base.py:
```python
def encode_adm(self, **kwargs):
    return kwargs["pooled_output"]  # <- KeyError here
```

### Why It Happened
1. FLUX models override `encode_adm()` to extract `pooled_output` from conditioning
2. Our code created empty conditioning: `[[torch.zeros((1, 77, 768)), {}]]`
3. The empty dict `{}` doesn't contain `pooled_output` → KeyError
4. CLIP text encoding provides `pooled_output` in the conditioning dict

### Model Requirements
Different diffusion models have different conditioning requirements:

| Model Type | Requires CLIP | Requires pooled_output |
|------------|---------------|------------------------|
| SD 1.5 | Optional | No |
| SDXL | Yes | Yes |
| FLUX | Yes | Yes |
| Other | Varies | Varies |

## The Solution

**Added optional CLIP input** to the node and use it to properly encode text prompts.

### Changes

#### 1. Added CLIP as optional input (nodes.py)
```python
"optional": {
    "model": ("MODEL",),
    "vae": ("VAE",),
    "clip": ("CLIP",),  # NEW
    "prompt": ("STRING", {...}),
}
```

#### 2. Updated sampler to use CLIP (comfyui_sampler.py)
```python
# NEW: Accept CLIP and prompt text
def upscale(self, ..., positive_prompt=None, negative_prompt=None, ...):
    
    # NEW: Encode prompts if CLIP available
    if positive_conditioning is None:
        if self.clip is not None and positive_prompt is not None:
            tokens = self.clip.tokenize(positive_prompt)
            positive_conditioning = self.clip.encode_from_tokens_scheduled(tokens)
        else:
            # Fallback to empty conditioning (may not work with FLUX)
            positive_conditioning = [[torch.zeros((1, 77, 768)), {}]]
```

#### 3. Updated initialization to pass CLIP
```python
def _initialize_models(self, ..., clip=None):
    self.comfyui_sampler = ComfyUISamplerWrapper(
        model=model,
        vae=vae,
        clip=clip  # Pass CLIP to sampler
    )
```

#### 4. Updated upscaler to pass prompt text
```python
def _upscale_with_comfyui(self, ..., prompt=None, ...):
    result = self.comfyui_sampler.upscale(
        ...
        positive_prompt=prompt,  # Pass prompt for encoding
        negative_prompt="",
        ...
    )
```

## Usage

### With FLUX Models (CLIP Required)
```
[Load Checkpoint] → MODEL → [DINO Upscale]
                   → VAE   ↗
                   → CLIP ↗
```

### With SD 1.5 Models (CLIP Optional)
```
[Load Checkpoint] → MODEL → [DINO Upscale]
                   → VAE   ↗
```

## What This Fixes

- ✅ FLUX models now work (CLIP provides pooled_output)
- ✅ SDXL models now work (CLIP provides pooled_output)
- ✅ SD 1.5 models still work (CLIP optional)
- ✅ Text prompts are properly encoded when CLIP available
- ✅ Graceful fallback for models that don't need CLIP

## Technical Details

### CLIP Encoding Output Format
ComfyUI's CLIP.encode_from_tokens_scheduled() returns:
```python
[
    [
        conditioning_tensor,  # Shape: [1, seq_len, hidden_dim]
        {
            "pooled_output": pooled_tensor,  # Shape: [1, pooled_dim]
            # ... other keys ...
        }
    ],
    # ... more conditioning entries if using scheduling ...
]
```

### Why pooled_output?
- **Pooled output** = Single vector summarizing the entire text prompt
- Used by FLUX/SDXL for global conditioning (ADM = Adaptive Model)
- Different from per-token conditioning used in cross-attention

## Testing

Verified that:
1. FLUX models work with CLIP connected
2. Prompts are properly encoded
3. Conditioning dict contains required pooled_output
4. No errors during sampling

## Key Takeaway

**FLUX and SDXL models require CLIP for text conditioning.** Always connect CLIP output from Load Checkpoint node when using these models. SD 1.5 can work without CLIP but benefits from it for prompt guidance.
