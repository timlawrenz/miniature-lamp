# ComfyUI Node Specification

## ADDED Requirements

### Requirement: External Model Input
The DINOFLUXUpscale node SHALL accept an optional MODEL input from the ComfyUI workflow to use instead of loading FLUX internally.

#### Scenario: User provides external model
- **WHEN** a MODEL input is connected to the node
- **THEN** the node SHALL use the provided model for upscaling
- **AND** SHALL NOT load a new FLUX model internally

#### Scenario: No external model provided
- **WHEN** the MODEL input is not connected
- **THEN** the node SHALL load FLUX model based on the `flux_variant` parameter as before
- **AND** maintain backward compatibility with existing workflows

### Requirement: External VAE Input
The DINOFLUXUpscale node SHALL accept an optional VAE input from the ComfyUI workflow to use with the model.

#### Scenario: User provides external VAE
- **WHEN** a VAE input is connected to the node
- **THEN** the node SHALL use the provided VAE for encoding/decoding
- **AND** SHALL NOT load a new VAE internally

#### Scenario: No external VAE provided
- **WHEN** the VAE input is not connected
- **THEN** the node SHALL use the default VAE from the model or pipeline
- **AND** maintain backward compatibility

### Requirement: Model Compatibility Validation
The node SHALL validate that external models are compatible with the FLUX img2img pipeline.

#### Scenario: Compatible model provided
- **WHEN** a FLUX-compatible MODEL is provided
- **THEN** the node SHALL successfully initialize the pipeline
- **AND** proceed with upscaling

#### Scenario: Incompatible model provided
- **WHEN** an incompatible model type is provided
- **THEN** the node SHALL emit a clear error message
- **AND** SHALL NOT crash or produce invalid results

### Requirement: Memory Efficiency
When external models are provided, the node SHALL NOT allocate additional memory for redundant model loading.

#### Scenario: External model reduces memory usage
- **WHEN** a pre-loaded MODEL from another node is used
- **THEN** the total memory footprint SHALL be lower than loading models twice
- **AND** workflow execution SHALL be faster due to shared model resources

#### Scenario: Multiple upscale nodes share one model
- **WHEN** multiple DINOFLUXUpscale nodes use the same external MODEL
- **THEN** all nodes SHALL operate correctly using the shared model
- **AND** memory usage SHALL remain constant regardless of node count

### Requirement: Input Type Declaration
The node SHALL declare MODEL and VAE as optional inputs in INPUT_TYPES.

#### Scenario: ComfyUI recognizes optional inputs
- **WHEN** the node is loaded in ComfyUI
- **THEN** MODEL and VAE inputs SHALL appear as optional connection points
- **AND** SHALL allow connection from compatible output types (MODEL, VAE)
- **AND** SHALL not require connection for the node to execute

### Requirement: Pipeline Configuration
External models SHALL respect node configuration parameters like offloading and device settings where applicable.

#### Scenario: Offloading applied to external model
- **WHEN** enable_offloading is true and an external model is provided
- **THEN** the node SHALL apply offloading optimizations to the external model if possible
- **AND** handle cases where external model already has offloading configured

#### Scenario: Device compatibility
- **WHEN** an external model is on a different device than expected
- **THEN** the node SHALL handle device transfer appropriately
- **OR** emit a warning if device mismatch could affect performance

### Requirement: Configurable Tile Size
The node SHALL allow users to configure the output tile size to match different model architectures' optimal processing dimensions.

#### Scenario: FLUX model with 1024x1024 tiles
- **WHEN** a FLUX model is used with tile_size set to 1024
- **THEN** the upscaler SHALL use 1024x1024 output tiles
- **AND** calculate appropriate input tile sizes based on scale_factor
- **AND** process tiles at the model's optimal resolution

#### Scenario: SD model with 512x512 tiles
- **WHEN** an SD-based model is used with tile_size set to 512
- **THEN** the upscaler SHALL use 512x512 output tiles
- **AND** maintain quality appropriate for SD architecture

#### Scenario: Custom tile size
- **WHEN** tile_size is set to a value between 512 and 2048
- **THEN** the node SHALL use that tile size for processing
- **AND** adjust overlap and stride calculations proportionally

### Requirement: Strength Parameter Clarity
The node SHALL use `denoise` for img2img denoising strength (following ComfyUI conventions) and `dino_strength` for DINO conditioning strength as separate controls.

#### Scenario: Independent strength controls
- **WHEN** both denoise and dino_strength are configured
- **THEN** denoise SHALL control img2img denoising amount (0.0 = no change, 1.0 = full denoise)
- **AND** dino_strength SHALL control DINO feature conditioning weight (0.0 = no DINO, 1.0 = full DINO)
- **AND** both SHALL operate independently without interfering

#### Scenario: Low denoising with high DINO guidance
- **WHEN** denoise is 0.2 and dino_strength is 0.8
- **THEN** the output SHALL preserve most of the input structure (low denoise)
- **AND** SHALL strongly respect DINO semantic features
- **AND** produce semantically consistent upscaling with minimal creative deviation

### Requirement: Sampler Selection
The node SHALL accept a `sampler_name` parameter to control the sampling algorithm used during img2img upscaling.

#### Scenario: User selects specific sampler
- **WHEN** sampler_name is set to a valid sampler (e.g., "euler", "dpmpp_2m")
- **THEN** the pipeline SHALL use that sampler for all tile processing
- **AND** maintain consistent sampling behavior across tiles

#### Scenario: Default sampler
- **WHEN** sampler_name is not specified or set to default
- **THEN** the pipeline SHALL use an appropriate default sampler for the model type
- **AND** maintain backward compatibility with existing behavior

#### Scenario: Invalid sampler name
- **WHEN** an unsupported sampler_name is provided
- **THEN** the node SHALL emit a clear error message listing valid options
- **AND** SHALL NOT proceed with invalid configuration

### Requirement: Scheduler Selection
The node SHALL accept a `scheduler` parameter to control the noise schedule used during sampling.

#### Scenario: User selects specific scheduler
- **WHEN** scheduler is set to a valid option (e.g., "karras", "exponential")
- **THEN** the pipeline SHALL use that scheduler for noise scheduling
- **AND** apply the scheduler consistently across all tiles

#### Scenario: Default scheduler
- **WHEN** scheduler is not specified or set to default
- **THEN** the pipeline SHALL use an appropriate default scheduler for the model
- **AND** maintain backward compatibility

#### Scenario: Scheduler-sampler compatibility
- **WHEN** a sampler and scheduler combination is used
- **THEN** the pipeline SHALL verify compatibility
- **OR** use reasonable defaults if the combination is not optimal
- **AND** emit warnings for suboptimal combinations if applicable

