"""
ComfyUI DINO FLUX Upscale Custom Node

Semantic-aware image upscaling using DINOv2 and FLUX diffusion models.
"""
import sys
from pathlib import Path

# Add parent directory (miniature-lamp) to path for src/ imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
