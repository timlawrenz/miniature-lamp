# ComfyUI Custom Node Integration

## Why

The DINO-guided FLUX upscaler is currently a standalone Python tool. To maximize adoption and integrate with existing ComfyUI workflows, we need to create a custom node that exposes this functionality within ComfyUI's visual workflow editor.

**Benefits:**
- **Workflow Integration** - Users can combine DINO upscaling with other ComfyUI nodes
- **Visual Interface** - No command-line knowledge required
- **Ecosystem Access** - Leverage ComfyUI's model management, prompt handling, and output systems
- **Debugging Tools** - ComfyUI's dev mode and API for testing
- **Community Reach** - ComfyUI has large user base for image generation

## What Changes

### Primary Deliverable
Create a ComfyUI custom node package that wraps our DINO-guided FLUX upscaler:
- Node registration and metadata
- Input/output tensor handling
- Integration with ComfyUI's model loading system
- UI parameter controls
- Proper error handling and progress reporting

### Research Areas
1. **ComfyUI Custom Node Architecture**
   - Node class structure and inheritance
   - Input/output type definitions
   - Parameter widgets and UI controls
   - Execution model and batching

2. **Model Integration**
   - How ComfyUI loads and manages models (FLUX, DINOv2)
   - Memory management and model offloading
   - Sharing models between nodes
   - Custom model loaders vs using existing ones

3. **Debugging & Development Workflow**
   - ComfyUI dev mode
   - API mode for automated testing
   - Hot reload for rapid iteration
   - Logging and error reporting
   - Testing nodes before packaging

4. **Ultimate SD Upscale Analysis**
   - Tiling implementation
   - Progress reporting
   - Parameter exposure
   - Integration with existing nodes
   - Code structure and best practices

5. **Distribution & Installation**
   - Package structure
   - Dependencies management
   - Installation via ComfyUI Manager
   - Documentation requirements

## Impact

**Affected Areas:**
- New directory: `comfyui_nodes/` for node implementation
- Affected specs: New spec for ComfyUI integration
- External: ComfyUI installation for testing

**Dependencies:**
- ComfyUI running on local machine
- Access to ComfyUI API mode
- Study of Ultimate SD Upscale node structure
- Understanding of ComfyUI's model management

**Risk Assessment:**
- **Medium Risk**: ComfyUI's API may change
- **Low Risk**: Our standalone tool continues to work independently
- **Mitigation**: Follow ComfyUI best practices, maintain backward compatibility

## Open Questions

### Technical Architecture
1. Should we create one monolithic node or split functionality across multiple nodes?
   - Option A: Single "DINO FLUX Upscale" node with all parameters
   - Option B: Separate nodes for DINO extraction, conditioning, and upscaling
   
2. How should we handle FLUX model loading?
   - Option A: Use ComfyUI's existing FLUX loader nodes
   - Option B: Create custom model loader for our specific needs
   - Option C: Hybrid approach

3. How do we expose tiled processing?
   - Option A: Automatic (transparent to user)
   - Option B: Explicit tile size parameter
   - Option C: Separate "tiled" variant node

4. What should the node inputs/outputs be?
   - Inputs: Image, prompt, model, DINO features, parameters
   - Outputs: Upscaled image, DINO features (for caching?)

### Development Workflow
5. What's the best way to develop and test nodes locally?
   - Can we use ComfyUI API for automated tests?
   - Hot reload workflow?
   - How to debug without restarting ComfyUI?

6. How do we handle our existing dependencies?
   - Are there conflicts with ComfyUI's torch/diffusers versions?
   - Should we vendor dependencies or rely on ComfyUI's?

7. What's the process for testing before release?
   - Manual testing in ComfyUI UI
   - Automated tests via API
   - Beta testing with users

### Ultimate SD Upscale Integration
8. Should we follow Ultimate SD Upscale's architecture exactly?
   - What patterns should we adopt?
   - What should we do differently?

9. Can we make our node compatible with Ultimate SD Upscale workflows?
   - Should we match their interface?
   - Can users switch between nodes easily?

### User Experience
10. How do we expose DINO conditioning strength effectively?
    - Simple slider? Separate node?
    - Should DINO be optional?

11. What defaults should we use for different scenarios?
    - Presets like "Conservative", "Balanced", "Creative"?
    - How to expose advanced parameters?

## Success Criteria

### Research Phase Success
- [ ] Understand ComfyUI custom node architecture
- [ ] Identify integration points for FLUX and DINO models
- [ ] Document debugging workflow with API mode
- [ ] Analyze Ultimate SD Upscale implementation
- [ ] Define node architecture (monolithic vs modular)
- [ ] Establish development and testing workflow

### Implementation Phase Success (Future)
- [ ] Working custom node in ComfyUI
- [ ] Proper integration with ComfyUI's model system
- [ ] Tiled processing working within node
- [ ] Good error handling and user feedback
- [ ] Documentation and examples
- [ ] Package ready for ComfyUI Manager

## Research Tasks

### Phase 1: ComfyUI Fundamentals
- [ ] Study ComfyUI custom node documentation
- [ ] Examine existing node examples from ComfyUI repo
- [ ] Understand node class structure and execution model
- [ ] Document input/output type system
- [ ] Understand widget system for parameters

### Phase 2: Ultimate SD Upscale Analysis
- [ ] Clone and review Ultimate SD Upscale source code
- [ ] Identify tiling implementation details
- [ ] Study how it handles progress reporting
- [ ] Understand its parameter structure
- [ ] Document reusable patterns

### Phase 3: ComfyUI API & Debugging
- [ ] Test ComfyUI API mode on local installation
- [ ] Create minimal test node for experimentation
- [ ] Document hot reload workflow
- [ ] Test debugging approaches
- [ ] Create development environment setup guide

### Phase 4: Integration Strategy
- [ ] Design node architecture
- [ ] Plan model loading strategy
- [ ] Define input/output schema
- [ ] Plan parameter exposure
- [ ] Document integration approach

## Resources

### Primary Resources
- **ComfyUI Repository**: https://github.com/comfyanonymous/ComfyUI
- **Custom Node Walkthrough**: https://docs.comfy.org/custom-nodes/walkthrough
- **Ultimate SD Upscale**: https://github.com/atdigit/ComfyUI_Ultimate_SD_Upscale

### Local Setup
- ComfyUI running on this machine
- ComfyUI API mode available for testing
- Existing standalone implementation working

### Documentation to Create
- `docs/COMFYUI_INTEGRATION.md` - Research findings
- `docs/COMFYUI_DEVELOPMENT.md` - Development workflow
- `comfyui_nodes/README.md` - Node usage documentation
- `comfyui_nodes/ARCHITECTURE.md` - Design decisions

## Next Steps

After research phase completes:
1. Create implementation proposal based on findings
2. Set up development environment
3. Create proof-of-concept node
4. Iterate with API testing
5. Package for distribution

## Timeline Estimate

- **Research Phase**: 2-3 sessions
  - Session 1: ComfyUI fundamentals + API testing
  - Session 2: Ultimate SD Upscale analysis
  - Session 3: Architecture design and documentation
  
- **Implementation Phase**: 5-7 sessions (future)
  - Proof of concept
  - Full feature implementation
  - Testing and refinement
  - Documentation and packaging
