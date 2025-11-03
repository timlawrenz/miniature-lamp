# Changelog

## [1.0.2] - 2024-11-03

### Changed
- Renamed project from "DINO FLUX Upscale" to "DINO Upscale" for broader compatibility
- Updated node class name from `DINOFLUXUpscale` to `DINOUpscale`
- Generalized messaging to support any diffusion model backend

### Fixed
- Module import issues in ComfyUI installations

## [1.0.1] - 2024-11-02

### Added
- ComfyUI Registry publishing support
- External model/VAE support for memory efficiency
- Configurable tile sizes, samplers, and schedulers

## [Unreleased] - 2024-11-02

### Added
- **DINO Conditioning Adapter** - Complete implementation for projecting DINO features to FLUX latent space
- **Comprehensive Parameter Documentation** - Full parameter reference in README with use cases
- **Debugging Tools** - `debug_upscale.sh` for systematic multi-stage testing
- **Parameter Inspection** - `check_params.py` for viewing default configurations
- **Quick Test Script** - `quick_test.sh` for fast neutral parameter testing
- **Documentation Suite** in `docs/`:
  - `TROUBLESHOOTING.md` - Parameter tuning and issue resolution
  - `DEBUG_PLAN.md` - Systematic debugging methodology
  - `DINO_CONDITIONING.md` - DINO parameter guide
  - `BUG_FIX_FLUX_UPSCALE.md` - Critical bug analysis
  - `IMPLEMENTATION_SUMMARY.md` - Technical details
- **Test Coverage** - 9 new tests for DINO conditioning adapter (36 total tests)

### Fixed
- **Critical: FLUX Upscaling Bug** - Added missing `width` and `height` parameters to FLUX pipeline
  - Without these, FLUX was auto-selecting sizes causing 4x upscaling instead of 2x
  - Fixed aspect ratio distortion in single-tile processing
- **Scale Factor Application** - Fixed `scale_factor` not being passed in single-tile path
- **Import Issues** - Added try/except for relative imports to support both module and script usage

### Changed
- **README.md** - Complete rewrite with:
  - Full parameter reference tables
  - Usage examples for different scenarios
  - Performance benchmarks
  - Troubleshooting section
  - Quick start guide
- **CONTRIBUTING.md** - Added FLUX development notes and debugging tips
- **Documentation Organization** - Moved all guides to `docs/` folder

### Technical Details
- FLUX img2img pipeline now receives explicit target dimensions
- DINO features extracted per tile for tiled processing
- Adapter supports feature projection (768→4096 dims), spatial alignment, and conditioning strength
- All tests passing with CPU fallback for CI/CD compatibility

## [0.1.0] - 2024-11-01

### Added
- Initial FLUX integration (schnell and dev variants)
- Basic DINO feature extraction
- Tiled processing with seamless blending
- Memory optimizations (CPU offloading, FP16, attention slicing)
- Configuration system with FLUXConfig
- Example scripts (simple_poc.py, flux_poc.py)

### Infrastructure
- OpenSpec-based development workflow
- Test suite foundation
- Project documentation structure
