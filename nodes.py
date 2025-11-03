"""
DINO Upscale ComfyUI Node

Semantic-aware image upscaling using DINOv2 features and diffusion models.
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
    from .src.upscaler import BasicUpscaler
    from .src.comfyui_sampler import ComfyUISamplerWrapper
except ImportError:
    # Fall back to absolute import (when loaded by ComfyUI)
    from src.dino_extractor import DINOFeatureExtractor
    from src.upscaler import BasicUpscaler
    from src.comfyui_sampler import ComfyUISamplerWrapper


class DINOUpscale:
    """
    DINO-guided upscaling node for ComfyUI
    
    Combines semantic understanding from DINOv2 with diffusion models
    for high-quality, semantically-aware image upscaling.
    
    Accepts optional external MODEL and VAE inputs for memory efficiency.
    Supports configurable tile sizes, samplers, and schedulers.
    """
    
    def __init__(self):
        """Initialize node (models loaded lazily on first use)"""
        self.dino_extractor = None
        self.comfyui_sampler = None
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
                
                # Sampling parameters
                "denoise": ("FLOAT", {
                    "default": 0.2,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider"
                }),
                
                "tile_size": ("INT", {
                    "default": 1024,
                    "min": 512,
                    "max": 2048,
                    "step": 64
                }),
                
                "sampler_name": (["euler", "euler_a", "heun", "dpm_2", "dpm_2_a", "lms", 
                                 "dpm_fast", "dpm_adaptive", "dpmpp_2s_a", "dpmpp_2m", 
                                 "dpmpp_2m_sde", "dpmpp_3m_sde", "ddim", "uni_pc", "uni_pc_bh2"], {
                    "default": "euler"
                }),
                
                "scheduler": (["normal", "karras", "exponential", "sgm_uniform", "simple", "ddim_uniform"], {
                    "default": "normal"
                }),
                
                "steps": ("INT", {
                    "default": 20,
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
                "model": ("MODEL",),
                "vae": ("VAE",),
                "clip": ("CLIP",),
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
    
    def _initialize_models(self, scale_factor, dino_enabled, model=None, vae=None, clip=None):
        """Lazy initialization of models on first use"""
        # Require external model - no more FLUX fallback
        if model is None or vae is None:
            raise ValueError(
                "[DINO Upscale] ERROR: External MODEL and VAE are required!\n"
                "Please connect a 'Load Checkpoint' node to the MODEL and VAE inputs.\n"
                "This node no longer includes internal diffusion models."
            )
        
        # Use external model (ComfyUI native)
        if self.comfyui_sampler is None:
            print("[DINO Upscale] Using external model from workflow...")
            self.comfyui_sampler = ComfyUISamplerWrapper(
                model=model,
                vae=vae,
                clip=clip
            )
            print("[DINO Upscale] ✓ ComfyUI native sampler initialized")
        else:
            # Update CLIP if it changes
            self.comfyui_sampler.clip = clip
            
        if self.upscaler is None:
            print("[DINO Upscale] Initializing upscaler...")
            self.upscaler = BasicUpscaler(
                comfyui_sampler=self.comfyui_sampler,
                scale_factor=scale_factor,
                dino_extractor=None  # Will add if enabled
            )
            print("[DINO Upscale] ✓ Upscaler initialized")
        
        if dino_enabled and self.dino_extractor is None:
            print("[DINO Upscale] Loading DINOv2 model...")
            print("[DINO Upscale] (Downloads ~350MB from HuggingFace on first use)")
            self.dino_extractor = DINOFeatureExtractor()
            self.upscaler.dino_extractor = self.dino_extractor
            print("[DINO Upscale] ✓ DINOv2 model loaded")
    
    def _estimate_tiles(self, h, w, scale_factor, tile_size):
        """Estimate number of tiles for progress bar"""
        # Calculate input tile size based on output tile size and scale factor
        input_tile_size = int(tile_size / scale_factor)
        input_tile_size = max(256, input_tile_size)
        overlap = max(16, int(input_tile_size / 8))
        stride = input_tile_size - overlap
        
        # Calculate grid dimensions on INPUT image
        tiles_y = (h + stride - 1) // stride
        tiles_x = (w + stride - 1) // stride
        
        return tiles_y * tiles_x
    
    def upscale(self, image, scale_factor, denoise, tile_size, sampler_name, scheduler,
                steps, dino_enabled, dino_strength, seed, 
                model=None, vae=None, clip=None, prompt="high quality, detailed, sharp"):
        """
        Main upscaling function
        
        Args:
            image: ComfyUI image tensor [B, H, W, C]
            scale_factor: Upscaling factor (1.0-4.0)
            denoise: Denoising strength for img2img (0.0-1.0)
            tile_size: Output tile size (512-2048)
            sampler_name: Sampling algorithm to use
            scheduler: Noise schedule to use
            steps: Number of inference steps
            dino_enabled: Whether to use DINO conditioning
            dino_strength: DINO conditioning strength (0.0-1.0)
            seed: Random seed for reproducibility
            model: External MODEL from workflow (REQUIRED)
            vae: External VAE from workflow (REQUIRED)
            prompt: Text prompt for guidance
            
        Returns:
            Tuple of (upscaled_image_tensor,)
        """
        try:
            # Import ComfyUI progress utilities
            try:
                from comfy.utils import ProgressBar
                has_progress = True
            except ImportError:
                print("[DINO Upscale] Warning: ComfyUI progress bar not available")
                has_progress = False
                ProgressBar = None
            
            # Initialize models if needed
            self._initialize_models(scale_factor, dino_enabled, model, vae, clip)
            
            # Update scale factor (in case it changed since initialization)
            if self.upscaler is not None:
                self.upscaler.scale_factor = scale_factor
            
            # Estimate number of tiles for progress bar
            h, w = image.shape[1:3]
            num_tiles = self._estimate_tiles(h, w, scale_factor, tile_size)
            
            # Create progress bar (also handles stop button)
            pbar = ProgressBar(num_tiles) if has_progress else None
            
            # Convert ComfyUI tensor to PIL (process first image in batch)
            print(f"[DINO Upscale] Processing image {image.shape}")
            pil_image = comfyui_to_pil(image, batch_index=0)
            
            # Extract DINO features if enabled
            dino_features = None
            if dino_enabled and self.dino_extractor is not None:
                print("[DINO Upscale] Extracting DINO features...")
                dino_features = self.dino_extractor.extract_features(pil_image)
                print(f"[DINO Upscale] ✓ Extracted {dino_features.shape[0]} patch features")
            
            # Upscale using our existing code with progress callback
            print(f"[DINO Upscale] Upscaling {scale_factor}x with denoise={denoise}, tile_size={tile_size}")
            print(f"[DINO Upscale] Sampler: {sampler_name}, Scheduler: {scheduler}")
            result_pil = self.upscaler.upscale(
                pil_image,
                dino_features=dino_features,
                use_diffusion=True,
                prompt=prompt,
                num_steps=steps,
                strength=denoise,
                seed=seed,
                dino_conditioning_strength=dino_strength,
                tile_size=tile_size,
                sampler_name=sampler_name,
                scheduler=scheduler,
                progress_callback=lambda: pbar.update(1) if pbar else None
            )
            
            # Convert result back to ComfyUI tensor
            result_tensor = pil_to_comfyui(result_pil)
            
            print(f"[DINO Upscale] ✓ Complete! Output: {result_tensor.shape}")
            
            return (result_tensor,)
            
        except Exception as e:
            print(f"[DINO Upscale] ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            raise


# Register node with ComfyUI
NODE_CLASS_MAPPINGS = {
    "DINOUpscale": DINOUpscale
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DINOUpscale": "DINO Upscale"
}
