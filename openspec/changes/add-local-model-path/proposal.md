## Why

Currently, FLUXUpscalePipeline only supports loading models from Hugging Face Hub, requiring ~10GB downloads. Users with local FLUX safetensors files (e.g., from ComfyUI, downloaded separately, or custom fine-tuned models) should be able to use them directly by providing a file path.

## What Changes

- Add `model_path` parameter to FLUXUpscalePipeline to accept local file paths
- Support loading `.safetensors` files directly
- Maintain backward compatibility with HuggingFace Hub loading
- Update configuration to support both path and variant selection
- Add validation for file existence and format

## Impact

- Affected specs: `flux-integration` (modified)
- Affected code:
  - `src/flux_pipeline.py` - Add path-based loading
  - `src/config.py` - Add model_path field
  - `examples/flux_poc.py` - Add --model-path argument
- Benefits: Faster startup, offline usage, custom model support
- No breaking changes: Existing HuggingFace loading still works
