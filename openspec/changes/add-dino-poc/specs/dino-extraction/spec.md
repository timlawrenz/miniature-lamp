## ADDED Requirements

### Requirement: DINO Model Loading
The system SHALL load a pre-trained DINOv2 model for semantic feature extraction.

#### Scenario: Successful model initialization
- **WHEN** DINOFeatureExtractor is instantiated
- **THEN** the facebook/dinov2-base model is loaded
- **AND** the model is moved to the appropriate device (CPU/GPU)
- **AND** the model is set to evaluation mode

#### Scenario: GPU availability detection
- **WHEN** DINOFeatureExtractor is instantiated
- **THEN** CUDA availability is checked
- **AND** the model uses GPU if available, otherwise CPU

### Requirement: Patch-Level Feature Extraction
The system SHALL extract semantic patch embeddings from input images.

#### Scenario: Extract features from PIL image
- **WHEN** extract_features() is called with a PIL Image
- **THEN** the image is processed through DINOv2
- **AND** patch embeddings are returned (excluding CLS token)
- **AND** the output shape is (num_patches, feature_dim)

#### Scenario: Extract features from numpy array
- **WHEN** extract_features() is called with a numpy array
- **THEN** the array is converted to PIL Image
- **AND** features are extracted as normal

#### Scenario: Handle different image sizes
- **WHEN** images of various sizes are processed
- **THEN** appropriate patch grids are computed
- **AND** features match the expected grid dimensions

### Requirement: Patch Grid Calculation
The system SHALL calculate patch grid dimensions for given image sizes.

#### Scenario: Calculate grid for standard image
- **WHEN** get_patch_grid_size() is called with image dimensions
- **THEN** grid size is computed based on 14x14 patch size
- **AND** dimensions are returned as (height_patches, width_patches)
