# ComfyUI Integration Research Questions

This document tracks specific questions to answer during the research phase.

## Node Architecture

### Q1: Monolithic vs Modular Design
**Question**: Should we create one node or multiple nodes for different stages?

**Options**:
- A) Single "DINO FLUX Upscale" node with all functionality
- B) Separate nodes: "DINO Extract" → "FLUX Upscale with DINO" → "Output"
- C) Hybrid: Core node + optional enhancement nodes

**Research Needed**:
- How does Ultimate SD Upscale handle this?
- What's the ComfyUI convention?
- User experience implications

**Status**: 🔍 Researching

---

### Q2: Model Loading Strategy
**Question**: How should we load FLUX and DINO models?

**Options**:
- A) Depend on existing ComfyUI model loader nodes
- B) Create custom model loader nodes
- C) Hybrid: Use ComfyUI for FLUX, custom for DINO

**Research Needed**:
- Can we reuse ComfyUI's FLUX loaders?
- Does ComfyUI have DINO support?
- Model sharing between nodes

**Status**: 🔍 Researching

---

### Q3: Input/Output Schema
**Question**: What should the node inputs and outputs be?

**Proposed Schema**:
```
Inputs:
  - image: IMAGE (required)
  - flux_model: MODEL (optional, if using ComfyUI loader)
  - prompt: STRING (default: "high quality, detailed, sharp")
  - strength: FLOAT (default: 0.3, range: 0.0-1.0)
  - dino_strength: FLOAT (default: 0.5, range: 0.0-1.0)
  - scale_factor: FLOAT (default: 2.0)
  - variant: ["schnell", "dev"] (default: "schnell")
  - seed: INT (optional)
  
Outputs:
  - image: IMAGE (upscaled result)
  - dino_features: LATENT (optional, for caching)
```

**Research Needed**:
- ComfyUI type system conventions
- How to handle optional inputs
- LATENT type for DINO features?

**Status**: 🔍 Researching

---

## Development Workflow

### Q4: API Mode for Testing
**Question**: Can we use ComfyUI API for automated testing?

**Research Needed**:
- How to start ComfyUI in API mode
- How to queue workflows programmatically
- How to retrieve results
- Can we run tests without GUI?

**Status**: 🔍 Researching

---

### Q5: Hot Reload Workflow
**Question**: How do we iterate on node code without restarting ComfyUI?

**Research Needed**:
- Does ComfyUI support hot reload?
- What's the recommended development workflow?
- Any tools or scripts to automate this?

**Status**: 🔍 Researching

---

### Q6: Debugging Approach
**Question**: How do we debug node execution?

**Research Needed**:
- Print statements vs logging
- Breakpoint debugging options
- Error handling best practices
- Progress reporting to UI

**Status**: 🔍 Researching

---

## Ultimate SD Upscale Analysis

### Q7: Tiling Implementation
**Question**: How does Ultimate SD Upscale implement tiling?

**Specific Questions**:
- Tile size and overlap strategy
- Progress reporting during tile processing
- How does it handle VAE encoding/decoding?
- Seam blending approach

**Status**: 🔍 Researching

---

### Q8: Parameter Exposure
**Question**: How does Ultimate SD Upscale expose parameters to users?

**Specific Questions**:
- Which parameters are configurable?
- How are presets handled?
- Advanced vs simple mode?
- Widget types used

**Status**: 🔍 Researching

---

### Q9: Model Integration
**Question**: How does Ultimate SD Upscale integrate with SD models?

**Specific Questions**:
- Does it use ComfyUI's model loaders?
- How does it handle different SD versions?
- Memory management approach
- VAE handling

**Status**: 🔍 Researching

---

## Technical Integration

### Q10: FLUX Model Access
**Question**: How do ComfyUI nodes access FLUX models?

**Research Needed**:
- ComfyUI's FLUX loader nodes
- Model cache and memory management
- Can we reuse loaded models?
- Offloading strategy

**Status**: 🔍 Researching

---

### Q11: DINO Integration
**Question**: Does ComfyUI have existing DINO support?

**Research Needed**:
- Search for existing DINO nodes
- DINOv2 model loading in ComfyUI
- Should we bundle DINO or make it a dependency?

**Status**: 🔍 Researching

---

### Q12: Tensor Formats
**Question**: What image tensor format does ComfyUI use?

**Research Needed**:
- IMAGE type: shape, dtype, range
- Conversion between PIL/numpy/torch
- Batch dimension handling
- Color space (RGB vs BGR)

**Status**: 🔍 Researching

---

## User Experience

### Q13: Parameter Defaults
**Question**: What should the default parameters be for typical users?

**Proposed Defaults**:
- strength: 0.2 (conservative)
- dino_strength: 0.5 (balanced)
- variant: "schnell" (fast)
- scale_factor: 2.0 (standard)

**Research Needed**:
- What do users expect?
- Should we offer presets?

**Status**: 🔍 Researching

---

### Q14: Progress Reporting
**Question**: How should we report progress to users?

**Options**:
- A) Silent (just show result)
- B) Progress bar for overall operation
- C) Per-tile progress updates
- D) Detailed logging to console

**Research Needed**:
- ComfyUI progress API
- What Ultimate SD Upscale does
- User preferences

**Status**: 🔍 Researching

---

### Q15: Error Handling
**Question**: How should we handle errors gracefully?

**Scenarios**:
- Out of VRAM
- Model not loaded
- Invalid parameters
- Image too large

**Research Needed**:
- ComfyUI error handling conventions
- User-friendly error messages
- Recovery strategies

**Status**: 🔍 Researching

---

## Distribution

### Q16: Package Structure
**Question**: What's the proper package structure for a ComfyUI custom node?

**Research Needed**:
- Required files and folders
- `__init__.py` requirements
- Dependencies specification
- Installation via ComfyUI Manager

**Status**: 🔍 Researching

---

### Q17: Dependency Management
**Question**: How do we handle our Python dependencies?

**Challenges**:
- diffusers, transformers, torch versions
- Potential conflicts with ComfyUI
- Should we vendor dependencies?

**Research Needed**:
- ComfyUI dependency system
- How other nodes handle this
- Best practices

**Status**: 🔍 Researching

---

## Next Steps

Update this document as research progresses:
- ✅ = Question answered
- 🔍 = Currently researching  
- ⏸️ = Blocked/deferred
- ❌ = Not applicable

Document answers in the research findings document.
