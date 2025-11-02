"""
DINO FLUX Upscale ComfyUI Node

Semantic-aware image upscaling using DINOv2 features and FLUX diffusion.
"""
import os
import sys
import torch

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.realpath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import utils - try relative first, then absolute
try:
    from .utils import comfyui_to_pil, pil_to_comfyui
except ImportError:
    from utils import comfyui_to_pil, pil_to_comfyui

# Import our existing upscaler components
try:
    # Try relative import first (when installed as package)
    from .src.dino_extractor import DINOFeatureExtractor
    from .src.flux_pipeline import FLUXUpscalePipeline
    from .src.upscaler import BasicUpscaler
except ImportError:
    # Fall back to absolute import (when loaded by ComfyUI)
    from src.dino_extractor import DINOFeatureExtractor
    from src.flux_pipeline import FLUXUpscalePipeline
    from src.upscaler import BasicUpscaler


class DINOFLUXUpscale:
    """
    DINO-guided FLUX upscaling node for ComfyUI
    
    Combines semantic understanding from DINOv2 with FLUX diffusion
    for high-quality, semantically-aware image upscaling.
    """
    
    def __init__(self):
        """Initialize node (models loaded lazily on first use)"""
        self.dino_extractor = None
        self.flux_pipeline = None
        self.upscaler = None
    
    @classmethod
    def INPUT_TYPES(cls):
        """Define node inputs"""
        return {
            "required": {
                # Input image
                "image": ("IMAGE",),
                
                # Core upscaling parameters
                "scale_factor": ("FLOAT", {
                    "default": 2.0,
                    "min": 1.0,
                    "max": 4.0,
                    "step": 0.1,
                    "display": "slider"
                }),
                
                # FLUX parameters
                "strength": ("FLOAT", {
                    "default": 0.2,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider"
                }),
                
                "flux_variant": (["schnell", "dev"], {
                    "default": "schnell"
                }),
                
                "steps": ("INT", {
                    "default": 4,
                    "min": 1,
                    "max": 100,
                    "step": 1
                }),
                
                # DINO parameters
                "dino_enabled": ("BOOLEAN", {
                    "default": True
                }),
                
                "dino_strength": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider"
                }),
                
                # Misc
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xffffffffffffffff
                }),
            },
            "optional": {
                "prompt": ("STRING", {
                    "default": "high quality, detailed, sharp",
                    "multiline": True
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("upscaled_image",)
    FUNCTION = "upscale"
    CATEGORY = "image/upscaling"
    
    def _initialize_models(self, flux_variant, scale_factor, dino_enabled):
        """Lazy initialization of models on first use"""
        if self.flux_pipeline is None:
            print(f"[DINO FLUX Upscale] Loading FLUX {flux_variant} model...")
            self.flux_pipeline = FLUXUpscalePipeline(
                variant=flux_variant,
                enable_offloading=True
            )
            print("[DINO FLUX Upscale] ✓ FLUX model loaded")
        
        if self.upscaler is None:
            print("[DINO FLUX Upscale] Initializing upscaler...")
            self.upscaler = BasicUpscaler(
                flux_pipeline=self.flux_pipeline,
                scale_factor=scale_factor,
                dino_extractor=None  # Will add if enabled
            )
            print("[DINO FLUX Upscale] ✓ Upscaler initialized")
        
        if dino_enabled and self.dino_extractor is None:
            print("[DINO FLUX Upscale] Loading DINOv2 model...")
            print("[DINO FLUX Upscale] (Downloads ~350MB from HuggingFace on first use)")
            self.dino_extractor = DINOFeatureExtractor()
            self.upscaler.dino_extractor = self.dino_extractor
            print("[DINO FLUX Upscale] ✓ DINOv2 model loaded")
    
    def upscale(self, image, scale_factor, strength, flux_variant, steps,
                dino_enabled, dino_strength, seed, prompt="high quality, detailed, sharp"):
        """
        Main upscaling function
        
        Args:
            image: ComfyUI image tensor [B, H, W, C]
            scale_factor: Upscaling factor (1.0-4.0)
            strength: FLUX denoising strength (0.0-1.0)
            flux_variant: "schnell" or "dev"
            steps: Number of inference steps
            dino_enabled: Whether to use DINO conditioning
            dino_strength: DINO conditioning strength (0.0-1.0)
            seed: Random seed for reproducibility
            prompt: Text prompt for FLUX guidance
            
        Returns:
            Tuple of (upscaled_image_tensor,)
        """
        try:
            # Initialize models if needed
            self._initialize_models(flux_variant, scale_factor, dino_enabled)
            
            # Convert ComfyUI tensor to PIL (process first image in batch)
            print(f"[DINO FLUX Upscale] Processing image {image.shape}")
            pil_image = comfyui_to_pil(image, batch_index=0)
            
            # Extract DINO features if enabled
            dino_features = None
            if dino_enabled and self.dino_extractor is not None:
                print("[DINO FLUX Upscale] Extracting DINO features...")
                dino_features = self.dino_extractor.extract_features(pil_image)
                print(f"[DINO FLUX Upscale] ✓ Extracted {dino_features.shape[0]} patch features")
            
            # Upscale using our existing code
            print(f"[DINO FLUX Upscale] Upscaling {scale_factor}x with strength={strength}...")
            result_pil = self.upscaler.upscale(
                pil_image,
                dino_features=dino_features,
                use_flux=True,
                prompt=prompt,
                num_steps=steps,
                strength=strength,
                seed=seed,
                dino_conditioning_strength=dino_strength
            )
            
            # Convert result back to ComfyUI tensor
            result_tensor = pil_to_comfyui(result_pil)
            
            print(f"[DINO FLUX Upscale] ✓ Complete! Output: {result_tensor.shape}")
            
            return (result_tensor,)
            
        except Exception as e:
            print(f"[DINO FLUX Upscale] ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            raise


# Register node with ComfyUI
NODE_CLASS_MAPPINGS = {
    "DINOFLUXUpscale": DINOFLUXUpscale
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DINOFLUXUpscale": "DINO FLUX Upscale"
}
