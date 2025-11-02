# Implementation Tasks

## 1. Update Node Interface
- [x] 1.1 Add optional `model` input of type MODEL to INPUT_TYPES
- [x] 1.2 Add optional `vae` input of type VAE to INPUT_TYPES
- [x] 1.3 Add `tile_size` parameter (default: 1024 for FLUX, allow 512-2048 range)
- [x] 1.4 Add `sampler_name` parameter with dropdown of available samplers
- [x] 1.5 Add `scheduler` parameter with dropdown of available schedulers
- [x] 1.6 Rename `strength` parameter to `denoise` (keep `dino_strength` as-is)
- [x] 1.7 Update node docstring to document all new parameters
- [x] 1.8 Update upscale() function signature to accept all new parameters

## 2. Modify Pipeline Integration
- [x] 2.1 Update FLUXUpscalePipeline to accept external pipeline object
- [x] 2.2 Add logic to skip internal model loading when external model provided
- [x] 2.3 Add sampler_name and scheduler parameter support to upscale_tile()
- [x] 2.4 Rename strength parameter to denoise throughout pipeline code
- [ ] 2.5 Ensure pipeline configuration (offloading, device) still applies to external models
- [ ] 2.6 Add validation for external model compatibility

## 3. Update Initialization Logic
- [x] 3.1 Modify _initialize_models() to check for external model/vae first
- [x] 3.2 Add conditional logic: use external if provided, else load internal
- [ ] 3.3 Handle VAE attachment to pipeline when using external components
- [x] 3.4 Maintain lazy loading behavior for backward compatibility
- [x] 3.5 Pass tile_size, sampler_name, scheduler to upscaler
- [x] 3.6 Update all strength references to denoise in node code

## 4. Testing
- [ ] 4.1 Test with external model/vae from Load Checkpoint node
- [ ] 4.2 Test backward compatibility (no model/vae provided)
- [ ] 4.3 Test memory usage comparison (external vs internal loading)
- [ ] 4.4 Verify upscale quality unchanged with external models
- [ ] 4.5 Test different tile_size values (512 for SD models, 1024 for FLUX)
- [ ] 4.6 Test different sampler_name options (euler, dpmpp_2m, etc.)
- [ ] 4.7 Test different scheduler options (normal, karras, etc.)
- [ ] 4.8 Verify denoise vs dino_strength work independently
- [ ] 4.9 Verify strength→denoise rename maintains correct behavior

## 5. Documentation
- [x] 5.1 Update README with example workflow using external model/vae
- [x] 5.2 Document the optional inputs in node documentation
- [x] 5.3 Add migration notes for users expecting internal loading only
- [x] 5.4 Document tile_size recommendations for different model types
- [x] 5.5 Document sampler_name and scheduler options and recommendations
- [x] 5.6 Clarify difference between denoise (img2img strength) and dino_strength (DINO conditioning)
- [x] 5.7 Add migration note about strength→denoise rename
