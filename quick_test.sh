#!/bin/bash
# Quick test with neutral parameters
# This should produce output closest to simple bicubic

IMAGE=$1

if [ -z "$IMAGE" ]; then
    echo "Usage: ./quick_test.sh <image>"
    echo ""
    echo "This runs FLUX with 'neutral' parameters that should"
    echo "produce output very similar to bicubic upscaling."
    exit 1
fi

echo "Testing FLUX with neutral parameters..."
echo "  - No DINO conditioning"
echo "  - strength=0.05 (minimal denoising)"
echo "  - Empty prompt (no text guidance)"
echo "  - guidance_scale=1.0 (minimal CFG)"
echo ""

python examples/flux_poc.py "$IMAGE" --flux \
    --no-dino \
    --strength 0.05 \
    --prompt "" \
    --steps 4 \
    --seed 42

echo ""
echo "Output saved. Compare with bicubic upscale:"
echo "  python examples/simple_poc.py $IMAGE"
