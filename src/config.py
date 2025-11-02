"""Configuration for FLUX upscaling"""
from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass
class FLUXConfig:
    """Configuration for FLUX diffusion upscaling"""
    
    # Model settings
    variant: str = "schnell"  # "schnell" or "dev"
    model_path: Optional[str] = None  # Path to local model file/directory
    enable_offloading: bool = True
    device: Optional[str] = None  # Auto-detect if None
    
    # Generation parameters
    num_steps: Optional[int] = None  # Uses default per variant if None
    guidance_scale: float = 3.5
    strength: float = 0.3  # Denoising strength (0.0-1.0) - kept for backward compatibility
    prompt: str = "high quality, detailed, sharp, 8k"
    
    # DINO conditioning
    dino_conditioning_strength: float = 0.7  # 0.0 = disabled, 1.0 = full
    use_dino_guidance: bool = True
    
    # Tiling parameters
    tile_size: int = 1024  # Default for FLUX (512 for SD models)
    tile_overlap: int = 64
    
    # Reproducibility
    seed: Optional[int] = None
    
    def __post_init__(self):
        """Validate configuration"""
        if self.variant not in ["schnell", "dev"]:
            raise ValueError(f"variant must be 'schnell' or 'dev', got {self.variant}")
        
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError(f"strength must be between 0.0 and 1.0, got {self.strength}")
        
        if not 0.0 <= self.dino_conditioning_strength <= 1.0:
            raise ValueError(f"dino_conditioning_strength must be between 0.0 and 1.0")
        
        # Validate model_path if provided
        if self.model_path is not None:
            path = Path(self.model_path)
            if not path.exists():
                raise FileNotFoundError(f"Model path does not exist: {self.model_path}")
            
            # Check if it's a valid format
            if path.is_file() and not path.suffix == ".safetensors":
                raise ValueError(f"Model file must be .safetensors, got {path.suffix}")
    
    def is_local_model(self) -> bool:
        """Check if using local model path"""
        return self.model_path is not None
