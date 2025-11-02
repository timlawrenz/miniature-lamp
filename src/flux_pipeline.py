"""
FLUX diffusion pipeline for img2img upscaling
"""
import torch
from diffusers import FluxPipeline
from PIL import Image
import numpy as np
from typing import Optional, Union
from pathlib import Path
import warnings


class FLUXUpscalePipeline:
    def __init__(
        self,
        variant: str = "schnell",
        model_path: Optional[str] = None,
        device: Optional[str] = None,
        enable_offloading: bool = True
    ):
        """
        Initialize FLUX pipeline for img2img upscaling
        
        Args:
            variant: "schnell" (4-step, fast) or "dev" (20-step, quality)
            model_path: Path to local model file or directory (takes precedence over variant)
            device: Target device (cuda/cpu), auto-detected if None
            enable_offloading: Enable CPU offloading to save VRAM
        """
        self.variant = variant
        self.model_path = model_path
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.enable_offloading = enable_offloading
        
        # Model configuration
        self.model_ids = {
            "schnell": "black-forest-labs/FLUX.1-schnell",
            "dev": "black-forest-labs/FLUX.1-dev"
        }
        
        # Default parameters per variant
        self.default_steps = {
            "schnell": 4,
            "dev": 20
        }
        
        self.pipe = None
        
        # Validate model_path if provided
        if self.model_path is not None:
            path = Path(self.model_path)
            if not path.exists():
                raise FileNotFoundError(f"Model path does not exist: {self.model_path}")
            
            if variant != "schnell" and variant != "dev":
                warnings.warn(f"model_path specified, ignoring variant='{variant}'")
    
    def load_model(self):
        """Load FLUX model with optimizations"""
        if self.pipe is not None:
            return
        
        # Use local path if provided, otherwise use HuggingFace
        if self.model_path is not None:
            print(f"Loading FLUX model from local path: {self.model_path}")
            model_source = self.model_path
        else:
            model_id = self.model_ids.get(self.variant)
            if not model_id:
                raise ValueError(f"Unknown variant: {self.variant}")
            print(f"Loading FLUX {self.variant} model from HuggingFace...")
            model_source = model_id
        
        # Load with fp16 for VRAM efficiency
        self.pipe = FluxPipeline.from_pretrained(
            model_source,
            torch_dtype=torch.float16,
            variant="fp16" if self.model_path is None else None
        )
        
        # Apply optimizations
        if self.device == "cuda":
            if self.enable_offloading:
                # Offload to CPU when not in use
                self.pipe.enable_model_cpu_offload()
                print("✓ CPU offloading enabled")
            else:
                self.pipe = self.pipe.to(self.device)
            
            # Enable attention slicing for memory efficiency
            self.pipe.enable_attention_slicing(1)
            print("✓ Attention slicing enabled")
        else:
            self.pipe = self.pipe.to(self.device)
        
        source_desc = "local file" if self.model_path else f"HuggingFace ({self.variant})"
        print(f"✓ FLUX loaded from {source_desc} on {self.device}")
    
    def upscale_tile(
        self,
        image: Union[Image.Image, np.ndarray],
        prompt: str = "high quality, detailed, sharp",
        num_steps: Optional[int] = None,
        guidance_scale: float = 3.5,
        strength: float = 0.3,
        seed: Optional[int] = None,
        dino_features: Optional[torch.Tensor] = None
    ) -> Image.Image:
        """
        Upscale a single tile using FLUX img2img
        
        Args:
            image: Input image tile
            prompt: Text prompt for guidance
            num_steps: Inference steps (uses default if None)
            guidance_scale: Guidance strength
            strength: Denoising strength (0.0-1.0)
            seed: Random seed for reproducibility
            dino_features: Optional DINO features for semantic conditioning
            
        Returns:
            Upscaled image tile
        """
        if self.pipe is None:
            self.load_model()
        
        # Convert to PIL if numpy
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        
        # Use default steps if not specified
        if num_steps is None:
            num_steps = self.default_steps[self.variant]
        
        # Set seed for reproducibility
        generator = None
        if seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(seed)
        
        # TODO: Integrate DINO features as conditioning
        # For now, FLUX runs with text prompt only
        if dino_features is not None:
            # Placeholder for DINO conditioning integration
            # This will be implemented in Stage 2
            pass
        
        # Run FLUX img2img
        with torch.inference_mode():
            result = self.pipe(
                prompt=prompt,
                image=image,
                num_inference_steps=num_steps,
                guidance_scale=guidance_scale,
                strength=strength,
                generator=generator
            ).images[0]
        
        return result
    
    def clear_memory(self):
        """Clear GPU memory"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
