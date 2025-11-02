## ADDED Requirements

### Requirement: FLUX Model Loading
The system SHALL load and initialize FLUX diffusion model for img2img generation.

#### Scenario: Load FLUX schnell variant
- **WHEN** FLUXPipeline is initialized with variant="schnell"
- **THEN** the FLUX schnell model is loaded from Hugging Face
- **AND** the model uses fp16 precision for VRAM efficiency
- **AND** the pipeline is moved to GPU if available

#### Scenario: Enable VRAM optimizations
- **WHEN** VRAM is limited (<16GB)
- **THEN** model offloading is enabled
- **AND** attention slicing is configured
- **AND** memory usage is kept under 12GB

### Requirement: FLUX img2img Pipeline
The system SHALL perform image-to-image generation using FLUX.

#### Scenario: Basic img2img upscaling
- **WHEN** an image tile is provided for upscaling
- **THEN** the tile is encoded to latent space
- **AND** FLUX denoising is applied with specified strength
- **AND** the denoised latent is decoded to image space
- **AND** output resolution is 2x the input

#### Scenario: Configurable generation parameters
- **WHEN** upscaling with FLUX
- **THEN** inference steps, guidance scale, and denoising strength are configurable
- **AND** seed can be set for reproducible results
- **AND** optional text prompt can guide generation

#### Scenario: Memory-efficient processing
- **WHEN** processing large images
- **THEN** tiles are processed sequentially to limit memory usage
- **AND** model components are offloaded when not in use
- **AND** VRAM is cleared between tiles if needed

### Requirement: Model Variant Selection
The system SHALL support multiple FLUX model variants.

#### Scenario: Use schnell for speed
- **WHEN** variant="schnell" is specified
- **THEN** FLUX schnell (4-step) model is used
- **AND** default inference steps is 4

#### Scenario: Use dev for quality
- **WHEN** variant="dev" is specified  
- **THEN** FLUX dev model is used
- **AND** default inference steps is 20
- **AND** higher quality output is generated
