## Why

Standard tiled upscalers hallucinate incorrect details (fur → woven texture, leaves → pebbles) because they lack semantic understanding. A proof-of-concept demonstrating DINO-guided upscaling will validate that semantic embeddings can constrain the upscaler's generation to maintain object identity.

## What Changes

- Add DINO feature extraction capability to generate semantic patch embeddings from images
- Implement basic 2x image upscaling using DINO guidance as conditioning
- Create POC script to demonstrate end-to-end flow: load image → extract DINO features → upscale → save result
- Establish project structure: dependencies, tests, and documentation

## Impact

- Affected specs: `dino-extraction` (new), `image-upscaling` (new)
- Affected code: New codebase - `src/dino_extractor.py`, `src/upscaler.py`, `examples/simple_poc.py`
- Infrastructure: Requires GPU-enabled environment for optimal performance
