## Context

The POC validates DINO feature extraction and basic upscaling pipeline. Moving to FLUX diffusion requires careful integration of DINO embeddings as conditioning signals. FLUX is a modern transformer-based diffusion model with different architecture than Stable Diffusion.

## Goals / Non-Goals

**Goals:**
- Integrate FLUX for high-quality img2img upscaling
- Inject DINO features as semantic conditioning
- Maintain tile-based processing for large images
- Preserve semantic consistency during generation

**Non-Goals:**
- Training custom FLUX models (use pretrained)
- ComfyUI node implementation (separate phase)
- Real-time performance (quality over speed)
- Multi-model support (FLUX only for now)

## Decisions

### Decision: Use FLUX over Stable Diffusion
**Why:** FLUX provides higher quality generation and has cleaner architecture for custom conditioning. It's also more actively maintained.

**Alternatives considered:**
- Stable Diffusion XL + ControlNet Tile: More established but requires ControlNet training
- Stable Diffusion 1.5: Lower quality output
- Custom trained model: Too time-intensive for POC validation

### Decision: Inject DINO as cross-attention conditioning
**Why:** FLUX uses transformer architecture where DINO embeddings can be concatenated with text embeddings in cross-attention layers, similar to how text conditioning works.

**Alternatives considered:**
- Adapter layers: Requires training
- Latent concatenation: Less effective for semantic guidance
- ControlNet-style architecture: Requires full model training

### Decision: Process tiles independently with overlap blending
**Why:** Large images exceed VRAM. Independent tiles with DINO guidance per tile maintains semantic coherence.

**Alternatives considered:**
- Full-image processing: VRAM prohibitive
- Sliding window: More complex, similar results
- Multi-GPU split: Overengineered for POC

## Architecture

```
Image → Tiles → For each tile:
                  ├─ Extract DINO features
                  ├─ Project to FLUX latent space
                  ├─ FLUX img2img with DINO conditioning
                  └─ Output tile
              → Stitch tiles → Final upscaled image
```

### DINO Conditioning Flow

```
DINO Patches (Nx768) 
    ↓
Feature Projection Layer (768→4096) 
    ↓
Spatial Reshape to match tile latents
    ↓
Concatenate with text embeddings
    ↓
FLUX Cross-Attention (semantic guidance)
    ↓
Denoised Latents → Upscaled Tile
```

## Implementation Notes

**FLUX Model Variants:**
- `flux-schnell`: 4-step model, faster, good quality
- `flux-dev`: More steps, highest quality

**VRAM Requirements:**
- FLUX schnell fp16: ~12GB
- With offloading: ~8GB minimum
- Per tile processing reduces baseline needs

**DINO Feature Mapping:**
- DINOv2 patch size: 14x14 pixels
- FLUX latent space: 8x downsampled
- Need interpolation to align DINO patches with FLUX latents

## Risks / Trade-offs

**Risk:** DINO conditioning may not significantly improve quality
- **Mitigation:** Implement A/B comparison, make conditioning strength tunable

**Risk:** FLUX inference too slow for practical use
- **Mitigation:** Use schnell variant, optimize with fp16, attention slicing

**Risk:** Tile seams visible despite blending
- **Mitigation:** Increase overlap region, use gradient blending

**Trade-off:** Quality vs Speed
- Decision: Prioritize quality for validation, optimize later if needed

## Migration Plan

1. Keep bicubic upscaling as fallback option
2. Add `--use-flux` flag to POC script
3. Default to bicubic, require explicit FLUX enable
4. Once validated, make FLUX the default in future versions

## Open Questions

- [ ] What DINO conditioning strength works best? (Need experimentation: 0.3-0.8 range)
- [ ] Should we support text prompts alongside DINO? (Likely yes for flexibility)
- [ ] How many inference steps optimal for quality/speed? (Start with 4 for schnell, 20 for dev)
- [ ] Can we cache DINO features to avoid recomputation? (Yes, implement in Phase 3)
