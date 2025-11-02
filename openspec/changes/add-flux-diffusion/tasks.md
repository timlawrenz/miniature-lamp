## 1. FLUX Model Integration
- [x] 1.1 Add FLUX dependencies (diffusers, accelerate, safetensors)
- [x] 1.2 Create FLUXPipeline class for img2img
- [x] 1.3 Implement model loading with variant selection (schnell/dev)
- [x] 1.4 Add VRAM optimization (offloading, fp16, attention slicing)
- [x] 1.5 Test basic FLUX img2img upscaling

## 2. DINO Conditioning Adapter
- [ ] 2.1 Create DINOConditioningAdapter class
- [ ] 2.2 Implement feature projection from DINO embeddings to FLUX latent space
- [ ] 2.3 Add spatial mapping for patch-to-tile alignment
- [ ] 2.4 Integrate conditioning into FLUX UNet forward pass
- [ ] 2.5 Test conditioning injection points

## 3. Tiled DINO-Guided Upscaling
- [ ] 3.1 Update BasicUpscaler to use FLUX pipeline
- [ ] 3.2 Implement tile-level DINO feature extraction
- [ ] 3.3 Add DINO-guided denoising for each tile
- [ ] 3.4 Ensure semantic consistency across tile boundaries
- [ ] 3.5 Optimize memory usage for large images

## 4. Configuration and Parameters
- [ ] 4.1 Add FLUX model configuration (model path, variant)
- [ ] 4.2 Create upscaling parameters (steps, guidance, strength)
- [ ] 4.3 Add DINO conditioning strength parameter
- [ ] 4.4 Implement prompt support for additional guidance
- [ ] 4.5 Add seed control for reproducibility

## 5. Testing and Validation
- [ ] 5.1 Test FLUX upscaling quality vs bicubic
- [ ] 5.2 Validate DINO conditioning effect on semantic preservation
- [ ] 5.3 Compare with/without DINO guidance
- [ ] 5.4 Test on various image types (portraits, landscapes, textures)
- [ ] 5.5 Measure performance and memory usage

## 6. Documentation and Examples
- [ ] 6.1 Update README with FLUX usage
- [ ] 6.2 Document DINO conditioning parameters
- [ ] 6.3 Add example comparing POC vs FLUX results
- [ ] 6.4 Create troubleshooting guide for VRAM issues
- [ ] 6.5 Update CONTRIBUTING with FLUX development notes
