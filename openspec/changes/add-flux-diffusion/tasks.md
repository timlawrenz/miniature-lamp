## 1. FLUX Model Integration
- [x] 1.1 Add FLUX dependencies (diffusers, accelerate, safetensors)
- [x] 1.2 Create FLUXPipeline class for img2img
- [x] 1.3 Implement model loading with variant selection (schnell/dev)
- [x] 1.4 Add VRAM optimization (offloading, fp16, attention slicing)
- [x] 1.5 Test basic FLUX img2img upscaling

## 2. DINO Conditioning Adapter
- [x] 2.1 Create DINOConditioningAdapter class
- [x] 2.2 Implement feature projection from DINO embeddings to FLUX latent space
- [x] 2.3 Add spatial mapping for patch-to-tile alignment
- [x] 2.4 Integrate conditioning into FLUX UNet forward pass
- [x] 2.5 Test conditioning injection points

## 3. Tiled DINO-Guided Upscaling
- [x] 3.1 Update BasicUpscaler to use FLUX pipeline
- [x] 3.2 Implement tile-level DINO feature extraction
- [x] 3.3 Add DINO-guided denoising for each tile
- [x] 3.4 Ensure semantic consistency across tile boundaries
- [x] 3.5 Optimize memory usage for large images

## 4. Configuration and Parameters
- [x] 4.1 Add FLUX model configuration (model path, variant)
- [x] 4.2 Create upscaling parameters (steps, guidance, strength)
- [x] 4.3 Add DINO conditioning strength parameter
- [x] 4.4 Implement prompt support for additional guidance
- [x] 4.5 Add seed control for reproducibility

## 5. Testing and Validation
- [x] 5.1 Test FLUX upscaling quality vs bicubic
- [x] 5.2 Validate DINO conditioning effect on semantic preservation
- [x] 5.3 Compare with/without DINO guidance
- [x] 5.4 Test on various image types (portraits, landscapes, textures)
- [x] 5.5 Measure performance and memory usage

## 6. Documentation and Examples
- [x] 6.1 Update README with FLUX usage
- [x] 6.2 Document DINO conditioning parameters
- [x] 6.3 Add example comparing POC vs FLUX results
- [x] 6.4 Create troubleshooting guide for VRAM issues
- [x] 6.5 Update CONTRIBUTING with FLUX development notes
