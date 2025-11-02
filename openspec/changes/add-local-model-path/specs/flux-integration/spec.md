## MODIFIED Requirements

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

#### Scenario: Load from local safetensors file
- **WHEN** model_path points to a .safetensors file
- **THEN** the model is loaded from the local file path
- **AND** no download from Hugging Face occurs
- **AND** the same optimizations (fp16, offloading) are applied

#### Scenario: Load from local model directory
- **WHEN** model_path points to a directory with model files
- **THEN** the model is loaded from the directory
- **AND** all required components are found locally

#### Scenario: Path takes precedence over variant
- **WHEN** both model_path and variant are specified
- **THEN** model_path is used
- **AND** variant is ignored
- **AND** a warning is logged about precedence

#### Scenario: Validate file existence
- **WHEN** model_path is provided
- **THEN** the path is validated for existence
- **AND** clear error message is shown if path doesn't exist
- **AND** file format is validated (.safetensors or directory)

## ADDED Requirements

### Requirement: Local Model Support
The system SHALL support loading FLUX models from local filesystem paths.

#### Scenario: ComfyUI model compatibility
- **WHEN** user provides path to ComfyUI FLUX model
- **THEN** the model loads successfully
- **AND** works identically to HuggingFace-loaded models

#### Scenario: Offline usage
- **WHEN** no internet connection is available
- **THEN** local model path can be used
- **AND** upscaling works without network access
