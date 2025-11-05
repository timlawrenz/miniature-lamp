# Tiled Upscaling Capability

## ADDED Requirements

### Requirement: Individual Tile Preview During Sampling

The system SHALL display a preview of the current individual tile being processed during each sampling step of the denoising process.

#### Scenario: Preview during sampling steps
- **WHEN** a tile is being processed through the sampler
- **THEN** a preview is displayed after each denoising step
- **AND** the preview shows the progressively refined tile
- **AND** preview updates occur for every sampling step (e.g., 20 previews for 20 steps)

#### Scenario: Multi-tile preview shows individual tiles
- **WHEN** upscaling a large image requiring multiple tiles
- **THEN** each tile shows preview updates during its sampling
- **AND** the preview shows only the current tile (e.g., 1024x1024)
- **AND** the preview does NOT show the merged or stitched result

#### Scenario: Preview updates per tile
- **WHEN** processing tile 1 of 4
- **THEN** preview shows only tile 1 during its sampling steps
- **WHEN** processing tile 2 of 4
- **THEN** preview shows only tile 2 during its sampling steps
- **AND** preview does not show tiles 1 and 2 combined

#### Scenario: Preview with progress bar
- **WHEN** tile preview is enabled
- **THEN** both the progress bar and tile preview operate simultaneously
- **AND** progress bar increments match preview updates (one per tile)

#### Scenario: Preview system unavailable
- **WHEN** ComfyUI preview system is not available
- **THEN** the upscaler continues processing without preview
- **AND** no errors or warnings are displayed
- **AND** the progress bar still functions normally

### Requirement: Sampler Callback Integration

The system SHALL integrate with ComfyUI's native sampler callback mechanism to emit preview images during denoising.

#### Scenario: Sampler callback propagation
- **WHEN** DINOUpscale node receives an upscale request
- **THEN** it creates a preview callback
- **AND** passes the callback to BasicUpscaler
- **AND** BasicUpscaler passes it to ComfyUISamplerWrapper
- **AND** ComfyUISamplerWrapper creates wrapper callback for comfy.sample.sample()
- **AND** wrapper callback decodes latent and emits preview

#### Scenario: Latent decoding in callback
- **WHEN** ComfyUI sampler invokes callback with latent (x0)
- **THEN** the latent is decoded to image using VAE
- **AND** decoded image is passed to preview callback
- **AND** preview is displayed to user

#### Scenario: Preview image format
- **WHEN** preview callback is invoked
- **THEN** the image is in ComfyUI tensor format [1, H, W, C]
- **AND** pixel values are in range [0, 1]
- **AND** the tensor represents only the current tile at current denoising step
- **AND** the tensor is on CPU (not GPU) for display

### Requirement: Progressive Preview Decoding

The system SHALL decode latent tensors to images for preview display during sampling.

#### Scenario: Decode latent per sampling step
- **WHEN** sampler callback is invoked with latent tensor
- **THEN** the latent is decoded to image using VAE
- **AND** decoded image is displayed as preview
- **AND** decoding happens for each sampling step

#### Scenario: Preview timing
- **WHEN** sampler completes a denoising step
- **THEN** callback receives predicted denoised latent (x0)
- **AND** latent is decoded immediately
- **AND** preview is displayed before next sampling step
- **AND** preview shows progressive refinement of tile

### Requirement: Graceful Degradation

The system SHALL handle missing preview functionality without errors.

#### Scenario: Import failure handling
- **WHEN** ComfyUI preview APIs cannot be imported
- **THEN** preview functionality is silently disabled
- **AND** upscaling continues normally
- **AND** no error messages are logged

#### Scenario: Callback error handling
- **WHEN** preview callback raises an exception
- **THEN** the exception is caught and logged
- **AND** upscaling continues with remaining tiles
- **AND** the error does not crash the node
