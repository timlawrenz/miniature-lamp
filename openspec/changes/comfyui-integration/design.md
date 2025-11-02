# ComfyUI Integration - Design Document

## Status: Research Phase

This is a **research proposal** to investigate how to create a ComfyUI custom node for the DINO-guided FLUX upscaler. Unlike implementation proposals, this doesn't define spec changes yet - it defines what we need to learn.

## Objective

Research and document how to integrate our DINO-guided FLUX upscaler as a ComfyUI custom node, including:
1. ComfyUI custom node architecture
2. Development and debugging workflow
3. Model integration strategy
4. Design decisions for our specific node

## Why This Is Important

Currently our upscaler is a standalone tool. ComfyUI integration would:
- Make it accessible to non-technical users
- Allow integration with existing ComfyUI workflows
- Leverage ComfyUI's model management and UI
- Reach a large community of users

## Research Resources Provided

1. **ComfyUI Repository**: https://github.com/comfyanonymous/ComfyUI
   - Main codebase to study
   - Example nodes in `comfy/nodes/`
   
2. **Custom Node Documentation**: https://docs.comfy.org/custom-nodes/walkthrough
   - Official guide for creating nodes
   - Node structure and conventions
   
3. **Ultimate SD Upscale**: https://github.com/atdigit/ComfyUI_Ultimate_SD_Upscale
   - Reference implementation of tiled upscaling
   - Our inspiration and similar use case
   
4. **Local ComfyUI Installation**
   - Running on this machine
   - API mode available for testing
   - Can test iterations quickly

## Key Research Questions

See `research-questions.md` for detailed list. High priority questions:

1. **Architecture**: One node or multiple nodes?
2. **Model Loading**: Use ComfyUI's loaders or create custom ones?
3. **Development**: How to debug and iterate quickly?
4. **Tiling**: How does Ultimate SD Upscale implement it?
5. **API Testing**: Can we automate testing via ComfyUI's API?

## Deliverables

After completing research:

1. **COMFYUI_INTEGRATION.md** - Research findings
   - Node architecture patterns
   - Model integration approaches
   - Development workflow
   - Best practices

2. **COMFYUI_DEVELOPMENT.md** - Developer guide
   - Environment setup
   - Hot reload workflow
   - Debugging techniques
   - Testing with API

3. **NODE_DESIGN.md** - Architecture specification
   - Input/output schema
   - Parameter structure
   - Model loading strategy
   - Error handling approach

4. **Implementation Proposal** - Next phase
   - Spec deltas for new code
   - Task breakdown
   - Timeline estimate

## Success Criteria

Research phase is complete when we can answer:

- ✅ How to structure a ComfyUI custom node
- ✅ How to integrate FLUX and DINO models
- ✅ How to develop and debug nodes efficiently
- ✅ What our node architecture should look like
- ✅ How to handle tiling within ComfyUI
- ✅ What the development timeline will be

## Next Steps

1. Start with Phase 1 tasks (ComfyUI fundamentals)
2. Study Ultimate SD Upscale implementation
3. Set up and test development environment
4. Document findings
5. Create implementation proposal

## Notes

- This is a **research proposal**, not an implementation proposal
- No code changes or spec deltas yet
- Focus is on learning and documentation
- Implementation proposal will follow after research
