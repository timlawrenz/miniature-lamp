# Contributing to DINO-Guided Image Upscaler

## Development Setup

```bash
# Clone repository
git clone <repository-url>
cd miniature-lamp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_dino_extractor.py
```

## Code Style

We follow PEP 8 guidelines. Format code with Black:

```bash
black src/ tests/ examples/
```

## Project Structure

```
src/
  dino_extractor.py    # DINO feature extraction
  upscaler.py          # Upscaling pipeline
tests/
  test_dino_extractor.py
  test_upscaler.py
examples/
  simple_poc.py        # Proof of concept script
```

## Making Changes

1. Check `openspec/` for active proposals
2. Create a new change proposal if needed (see `openspec/AGENTS.md`)
3. Implement according to specs
4. Write tests
5. Update documentation
6. Submit PR

## Current Limitations (POC Phase)

- Uses simple bicubic upscaling (not diffusion-based)
- DINO features extracted but not yet used for conditioning
- No ControlNet integration
- Single-pass processing (not tiled for large images)

## Next Phase Goals

- Integrate Stable Diffusion img2img
- Train/adapt ControlNet for DINO conditioning
- Implement proper tiled processing
- Create ComfyUI custom node
