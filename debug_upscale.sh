#!/bin/bash
# Systematic debugging script for FLUX upscaling issues
# Usage: ./debug_upscale.sh <image_path>

IMAGE=$1
BASENAME=$(basename "$IMAGE" | sed 's/\.[^.]*$//')
EXT="${IMAGE##*.}"

if [ -z "$IMAGE" ]; then
    echo "Usage: $0 <image_path>"
    echo ""
    echo "This script runs 6 stages of testing to isolate upscaling issues:"
    echo "  Stage 0: Baseline bicubic (no tiling)"
    echo "  Stage 1: Bicubic with tiling"
    echo "  Stage 2: FLUX single tile (minimal denoising)"
    echo "  Stage 3: FLUX with tiling (minimal denoising)"
    echo "  Stage 4: FLUX normal parameters"
    echo "  Stage 5: FLUX + DINO extraction (zero conditioning)"
    echo "  Stage 6: FLUX + DINO minimal conditioning"
    echo ""
    echo "Results saved as debug_output/${BASENAME}_stage*.png"
    exit 1
fi

if [ ! -f "$IMAGE" ]; then
    echo "Error: Image not found: $IMAGE"
    exit 1
fi

# Create debug output directory
mkdir -p debug_output

echo "=============================================="
echo "FLUX Upscaling Systematic Debug"
echo "=============================================="
echo "Input: $IMAGE"
echo "Output: debug_output/${BASENAME}_stage*.png"
echo ""

# Stage 0: Baseline bicubic (no tiling, no FLUX)
echo "→ Stage 0: Baseline bicubic upscale"
echo "  Testing: Basic image I/O and bicubic interpolation"
python examples/simple_poc.py "$IMAGE" 2>&1 | grep -E "(✓|Error|Traceback)" || true
if [ -f "${BASENAME}_upscaled_2x."* ]; then
    mv "${BASENAME}_upscaled_2x."* "debug_output/${BASENAME}_stage0_bicubic.png"
    echo "  ✓ Saved: debug_output/${BASENAME}_stage0_bicubic.png"
else
    echo "  ✗ Failed to create output"
fi
echo ""

# Stage 1: Bicubic with tiling (no FLUX)
echo "→ Stage 1: Bicubic with tiling"
echo "  Testing: Tile generation and stitching logic"
python examples/flux_poc.py "$IMAGE" --no-dino 2>&1 | grep -E "(✓|Processing|Error|Traceback)" || true
if [ -f "${BASENAME}_upscaled_2x."* ]; then
    mv "${BASENAME}_upscaled_2x."* "debug_output/${BASENAME}_stage1_bicubic_tiled.png"
    echo "  ✓ Saved: debug_output/${BASENAME}_stage1_bicubic_tiled.png"
else
    echo "  ✗ Failed to create output"
fi
echo ""

# Stage 2: FLUX single tile (no tiling, no DINO)
echo "→ Stage 2: FLUX single tile (256x256)"
echo "  Testing: FLUX img2img pipeline with minimal denoising"
python -c "from PIL import Image; img=Image.open('$IMAGE'); img.resize((256,256)).save('debug_output/${BASENAME}_small.jpg')"
python examples/flux_poc.py "debug_output/${BASENAME}_small.jpg" --flux --no-dino \
    --strength 0.01 \
    --prompt "" \
    --seed 42 2>&1 | grep -E "(✓|Loading|Processing|Error|Traceback)" || true
if [ -f "debug_output/${BASENAME}_small_flux_2x.jpg" ]; then
    mv "debug_output/${BASENAME}_small_flux_2x.jpg" "debug_output/${BASENAME}_stage2_flux_single.png"
    echo "  ✓ Saved: debug_output/${BASENAME}_stage2_flux_single.png"
else
    echo "  ✗ Failed to create output"
fi
rm -f "debug_output/${BASENAME}_small.jpg"
echo ""

# Stage 3: FLUX with tiling, minimal denoising (no DINO)
echo "→ Stage 3: FLUX tiled with minimal denoising"
echo "  Testing: FLUX with tiling but minimal modification"
python examples/flux_poc.py "$IMAGE" --flux --no-dino \
    --strength 0.1 \
    --prompt "" \
    --seed 42 2>&1 | grep -E "(✓|Processing|tile|Error|Traceback)" || true
if [ -f "${BASENAME}_flux_2x."* ]; then
    mv "${BASENAME}_flux_2x."* "debug_output/${BASENAME}_stage3_flux_tiled_minimal.png"
    echo "  ✓ Saved: debug_output/${BASENAME}_stage3_flux_tiled_minimal.png"
else
    echo "  ✗ Failed to create output"
fi
echo ""

# Stage 4: FLUX normal parameters (no DINO)
echo "→ Stage 4: FLUX with normal parameters"
echo "  Testing: Standard FLUX upscaling"
python examples/flux_poc.py "$IMAGE" --flux --no-dino \
    --strength 0.3 \
    --seed 42 2>&1 | grep -E "(✓|Processing|tile|Error|Traceback)" || true
if [ -f "${BASENAME}_flux_2x."* ]; then
    mv "${BASENAME}_flux_2x."* "debug_output/${BASENAME}_stage4_flux_normal.png"
    echo "  ✓ Saved: debug_output/${BASENAME}_stage4_flux_normal.png"
else
    echo "  ✗ Failed to create output"
fi
echo ""

echo "=============================================="
echo "Debug Results Summary"
echo "=============================================="
echo ""
echo "All outputs saved in: debug_output/"
ls -lh "debug_output/${BASENAME}_stage"*.png 2>/dev/null || echo "No output files found"
echo ""
echo "Next Steps:"
echo "1. Compare outputs visually"
echo "2. Identify at which stage quality degrades"
echo "3. Check DEBUG_PLAN.md for detailed analysis"
echo ""
echo "Quick visual inspection:"
echo "  - Stage 0 & 1 should look identical (bicubic)"
echo "  - Stage 2 should look very similar to input (strength=0.01)"
echo "  - Stage 3 should be recognizable (strength=0.1)"
echo "  - Stage 4 may look different but still recognizable"
