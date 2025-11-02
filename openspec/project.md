# Project Context

## Purpose
DINO-Guided Image Upscaler - A ComfyUI custom node that uses DINOv2 vision transformer embeddings to guide semantic-aware tiled image upscaling. The goal is to create an "Ultimate SD Upscale" style node that maintains semantic consistency during the upscaling process by using DINO embeddings as a ControlNet-style condition.

**Current Stage:** Proof of concept that loads a specified image and upscales it to twice its resolution using DINO guidance.

**End Goal:** Full-fledged ComfyUI custom node similar to "Ultimate SD Upscale" with DINO-guided semantic preservation.

## Tech Stack
- **Python** - Primary language for ComfyUI nodes
- **PyTorch** - Deep learning framework
- **DINOv2** - Vision transformer for semantic patch embeddings
- **Stable Diffusion** - Image generation model for img2img upscaling
- **ComfyUI** - Node-based UI framework for Stable Diffusion workflows
- **ControlNet** - Architecture pattern for conditional image generation

## Project Conventions

### Code Style
- Follow ComfyUI custom node conventions
- Python PEP 8 style guidelines
- Clear, descriptive variable names for diffusion model components
- Document complex semantic embedding operations

### Architecture Patterns
- **ComfyUI Custom Node Pattern**: Implement as custom nodes with INPUT_TYPES, RETURN_TYPES, and FUNCTION
- **ControlNet-Style Conditioning**: DINO embeddings act as additional conditioning signal alongside text prompts and image tiles
- **Tiled Processing**: Break large images into manageable tiles for processing, maintain semantic consistency across tile boundaries
- **Pipeline Stages**:
  1. Extract DINO patch embeddings from source image
  2. Tile the image for upscaling
  3. Feed DINO embeddings as condition during img2img denoising
  4. Stitch tiles back together

### Testing Strategy
- Visual quality assessment of upscaled images
- Semantic consistency verification (DINO embeddings should remain coherent)
- Test with various image types (portraits, landscapes, textures)
- Comparison against standard tiled upscaling without DINO guidance

### Git Workflow
- Feature branches for new capabilities
- Clear commits describing changes to upscaling pipeline or DINO integration

## Domain Context

### Image Upscaling Challenges
- **Hallucination Problem**: Standard tiled upscalers can generate incorrect details (e.g., turning fur into woven texture, leaves into pebbles)
- **Semantic Consistency**: Need to maintain object identity and characteristics across tiles
- **Low Denoising Strength**: Tiled upscalers use img2img with low denoising to add detail without destroying structure

### DINO (Vision Transformer)
- **Semantic Understanding**: DINOv2 creates patch-level embeddings that understand semantic meaning (e.g., "fur", "eye", "tree bark")
- **Self-Supervised Learning**: Trained without labels, learns rich visual representations
- **Patch-Based**: Operates on image patches, creating a semantic map of the image

### ControlNet Architecture
- **Conditional Generation**: Feeds extra conditions (depth, edges, pose) into diffusion UNet to control output
- **Multiple Conditions**: Can combine text prompts, source images, and additional conditioning signals
- **Tile Model**: ControlNet Tile specifically designed for upscaling tasks

### ComfyUI Ecosystem
- **Node-Based Workflow**: Visual programming interface for Stable Diffusion pipelines
- **Custom Nodes**: Python classes that implement specific operations
- **Ultimate SD Upscale**: Reference implementation for advanced tiled upscaling

## Important Constraints
- Must be compatible with ComfyUI node architecture
- DINO embedding extraction can be computationally expensive
- Need to balance semantic guidance strength with creative detail generation
- Memory constraints when processing large images with tiles

## External Dependencies
- **DINOv2 Model**: Pre-trained vision transformer (likely from Meta/Facebook Research)
- **Stable Diffusion Models**: Compatible checkpoint files
- **ControlNet Models**: Tile-based ControlNet weights
- **ComfyUI Framework**: Base framework for node execution
