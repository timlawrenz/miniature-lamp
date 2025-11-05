# Implementation Tasks

## 1. Research ComfyUI Preview System
- [x] 1.1 Study how KSampler implements preview callbacks
- [x] 1.2 Identify ComfyUI preview image APIs (likely in comfy.utils or comfy.sample)
- [x] 1.3 Understand sampler callback signature (step, x0, x, total_steps)
- [x] 1.4 Understand preview image format requirements

## 2. Update ComfyUISamplerWrapper
- [x] 2.1 Add preview_callback parameter to upscale() method
- [x] 2.2 Create wrapper callback for comfy.sample.sample()
- [x] 2.3 Decode latent (x0) to image in callback
- [x] 2.4 Pass decoded image to preview_callback
- [x] 2.5 Pass wrapper to comfy.sample.sample(callback=...)

## 3. Update BasicUpscaler
- [x] 3.1 Pass preview_callback to comfyui_sampler.upscale()
- [x] 3.2 Ensure preview shows just the current tile (not stitched result)

## 4. Update DINOUpscale Node
- [x] 4.1 Create ComfyUI preview callback in upscale() method
- [x] 4.2 Pass preview callback through to upscaler
- [x] 4.3 Ensure preview works with existing progress bar

## 5. Testing
- [ ] 5.1 Test preview with single tile (small image)
- [ ] 5.2 Test preview with multi-tile upscaling (verify each tile shown individually)
- [ ] 5.3 Verify preview updates during sampling steps (progressive refinement)
- [ ] 5.4 Measure performance impact of VAE decoding per step
- [ ] 5.5 Test graceful degradation if preview system unavailable

## 6. Documentation
- [ ] 6.1 Update README.md with preview feature mention
- [ ] 6.2 Add code comments explaining preview callback flow
- [ ] 6.3 Document performance considerations of preview decoding
