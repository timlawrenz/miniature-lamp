## 1. Local Model Path Support
- [x] 1.1 Add model_path parameter to FLUXUpscalePipeline.__init__()
- [x] 1.2 Implement file existence validation
- [x] 1.3 Add safetensors loading from local path
- [x] 1.4 Update model_path precedence (path > variant)
- [x] 1.5 Handle both single file and directory paths

## 2. Configuration Updates
- [x] 2.1 Add model_path field to FLUXConfig
- [x] 2.2 Update validation logic for path vs variant
- [x] 2.3 Add helper to detect model format (.safetensors)

## 3. CLI and Examples
- [x] 3.1 Add --model-path argument to flux_poc.py
- [x] 3.2 Update help text with local model examples
- [x] 3.3 Add error handling for invalid paths

## 4. Testing
- [x] 4.1 Test path validation
- [x] 4.2 Test precedence (path over variant)
- [x] 4.3 Test backward compatibility with HF loading

## 5. Documentation
- [x] 5.1 Document local model usage in README
- [x] 5.2 Add examples for ComfyUI users
- [x] 5.3 Document supported file formats
