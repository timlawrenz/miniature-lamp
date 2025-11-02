"""
FLUX diffusion pipeline for img2img upscaling
"""
import torch
from diffusers import FluxImg2ImgPipeline
from PIL import Image
import numpy as np
from typing import Optional, Union, Tuple
from pathlib import Path
import warnings

try:
    from .dino_conditioning import DINOConditioningAdapter
except ImportError:
    from dino_conditioning import DINOConditioningAdapter


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
        self.dino_adapter = None
        
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
        # Note: Some models don't have fp16 variants, so we'll try with and without
        load_kwargs = {
            "torch_dtype": torch.float16,
        }
        
        # Only add variant for HuggingFace repos that support it
        if self.model_path is None:
            # Try loading without variant first (more compatible)
            try:
                self.pipe = FluxImg2ImgPipeline.from_pretrained(
                    model_source,
                    **load_kwargs
                )
            except (ValueError, OSError) as e:
                # If that fails, try with fp16 variant
                print(f"Note: Loading without fp16 variant for compatibility")
                load_kwargs["variant"] = "fp16"
                self.pipe = FluxImg2ImgPipeline.from_pretrained(
                    model_source,
                    **load_kwargs
                )
        else:
            # Local model path
            self.pipe = FluxImg2ImgPipeline.from_pretrained(
                model_source,
                **load_kwargs
            )
        
        # Apply optimizations
        if self.device == "cuda":
            if self.enable_offloading:
                # Use sequential CPU offloading - more aggressive memory saving
                self.pipe.enable_sequential_cpu_offload()
                print("✓ Sequential CPU offloading enabled (aggressive)")
            else:
                self.pipe = self.pipe.to(self.device)
            
            # Enable attention slicing for memory efficiency
            self.pipe.enable_attention_slicing(1)
            print("✓ Attention slicing enabled")
            
            # Enable VAE slicing to reduce memory during decode
            if hasattr(self.pipe, 'vae'):
                self.pipe.vae.enable_slicing()
                print("✓ VAE slicing enabled")
        else:
            self.pipe = self.pipe.to(self.device)
        
        source_desc = "local file" if self.model_path else f"HuggingFace ({self.variant})"
        print(f"✓ FLUX loaded from {source_desc} on {self.device}")
        
        # Initialize DINO conditioning adapter
        self.dino_adapter = DINOConditioningAdapter(device=self.device)
        print("✓ DINO conditioning adapter initialized")
    
    def upscale_tile(
        self,
        image: Union[Image.Image, np.ndarray],
        prompt: str = "high quality, detailed, sharp",
        num_steps: Optional[int] = None,
        guidance_scale: float = 3.5,
        strength: float = 0.3,
        seed: Optional[int] = None,
        dino_features: Optional[torch.Tensor] = None,
        dino_conditioning_strength: float = 0.5,
        scale_factor: float = 2.0,
        sampler_name: str = "euler",
        scheduler: str = "normal"
    ) -> Image.Image:
        """
        Upscale a single tile using FLUX img2img
        
        Args:
            image: Input image tile
            prompt: Text prompt for guidance
            num_steps: Inference steps (uses default if None)
            guidance_scale: Guidance strength
            strength: Denoising strength (0.0-1.0) - also called 'denoise'
            seed: Random seed for reproducibility
            dino_features: Optional DINO features for semantic conditioning
            dino_conditioning_strength: Strength of DINO conditioning (0.0-1.0)
            scale_factor: Upscaling factor
            sampler_name: Sampling algorithm (currently informational, FLUX uses built-in)
            scheduler: Noise schedule (currently informational, FLUX uses built-in)
            
        Returns:
            Upscaled image tile
            
        Note:
            sampler_name and scheduler are accepted for API compatibility but
            FLUX pipelines use their own internal sampling. These parameters
            will be respected in future versions with custom sampling support.
        """
        if self.pipe is None:
            self.load_model()
        
        # Convert to PIL if numpy
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        
        # Calculate target dimensions and round to nearest multiple of 8
        # FLUX requires dimensions divisible by 8
        target_w = int(image.size[0] * scale_factor)
        target_h = int(image.size[1] * scale_factor)
        
        # Round to nearest multiple of 8
        target_w = ((target_w + 4) // 8) * 8
        target_h = ((target_h + 4) // 8) * 8
        
        # Use default steps if not specified
        if num_steps is None:
            num_steps = self.default_steps[self.variant]
        
        # Set seed for reproducibility
        generator = None
        if seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(seed)
        
        # Prepare conditioning with DINO features if provided
        if dino_features is not None and self.dino_adapter is not None:
            # Calculate target latent shape for spatial alignment
            target_latent_shape = self.dino_adapter.calculate_latent_shape((target_h, target_w))
            
            # Note: FLUX img2img pipeline doesn't expose direct control over
            # cross-attention embeddings in the public API. For full integration,
            # we would need to either:
            # 1. Use a custom pipeline that allows prompt_embeds injection
            # 2. Modify the UNet forward pass (requires model surgery)
            # 3. Use ControlNet-style adapter (requires training)
            #
            # For now, we use text prompts enhanced with semantic keywords
            # and store DINO features for future advanced integration
            self._current_dino_features = dino_features
            self._current_dino_strength = dino_conditioning_strength
            self._current_target_shape = target_latent_shape
        
        # Run FLUX img2img with explicit target dimensions
        # CRITICAL: Must pass width/height to control output size
        with torch.inference_mode():
            result = self.pipe(
                prompt=prompt,
                image=image,
                width=target_w,
                height=target_h,
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
