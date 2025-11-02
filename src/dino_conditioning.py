"""
DINO conditioning adapter for FLUX diffusion
Projects DINO embeddings into FLUX latent space for semantic guidance
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple


class DINOConditioningAdapter:
    def __init__(
        self,
        dino_dim: int = 768,
        flux_dim: int = 4096,
        device: Optional[str] = None
    ):
        """
        Initialize DINO conditioning adapter
        
        Args:
            dino_dim: DINO feature dimension (768 for dinov2-base)
            flux_dim: FLUX cross-attention dimension (4096 for FLUX.1)
            device: Target device (cuda/cpu), auto-detected if None
        """
        self.dino_dim = dino_dim
        self.flux_dim = flux_dim
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        # Simple linear projection from DINO space to FLUX space
        self.projection = nn.Linear(dino_dim, flux_dim).to(self.device)
        
        # Initialize with small random weights for stable conditioning
        nn.init.normal_(self.projection.weight, std=0.02)
        nn.init.zeros_(self.projection.bias)
        
        self.projection.eval()
    
    def project_features(
        self,
        dino_features: torch.Tensor,
        conditioning_strength: float = 0.5
    ) -> torch.Tensor:
        """
        Project DINO features to FLUX latent space
        
        Args:
            dino_features: DINO patch embeddings (num_patches, dino_dim)
            conditioning_strength: Strength of conditioning (0.0-1.0)
            
        Returns:
            Projected features (num_patches, flux_dim)
        """
        with torch.no_grad():
            # Move to device if needed
            if dino_features.device != self.device:
                dino_features = dino_features.to(self.device)
            
            # Project to FLUX space
            projected = self.projection(dino_features)
            
            # Apply conditioning strength
            projected = projected * conditioning_strength
            
            return projected
    
    def align_spatial_dimensions(
        self,
        dino_features: torch.Tensor,
        target_shape: Tuple[int, int],
        mode: str = "bilinear"
    ) -> torch.Tensor:
        """
        Align DINO patch features to target spatial dimensions
        
        Args:
            dino_features: DINO features (num_patches, feature_dim)
            target_shape: Target (height, width) in patches
            mode: Interpolation mode (bilinear, nearest, bicubic)
            
        Returns:
            Spatially aligned features (target_h*target_w, feature_dim)
        """
        # Infer source grid dimensions from number of patches
        num_patches = dino_features.shape[0]
        source_h = source_w = int(num_patches ** 0.5)
        
        # Validate square grid
        if source_h * source_w != num_patches:
            raise ValueError(f"DINO features must form square grid, got {num_patches} patches")
        
        target_h, target_w = target_shape
        
        # If dimensions match, no interpolation needed
        if (source_h, source_w) == (target_h, target_w):
            return dino_features
        
        # Reshape to spatial grid: (1, C, H, W)
        feature_dim = dino_features.shape[1]
        features_spatial = dino_features.reshape(source_h, source_w, feature_dim)
        features_spatial = features_spatial.permute(2, 0, 1).unsqueeze(0)
        
        # Interpolate to target shape
        features_aligned = F.interpolate(
            features_spatial,
            size=(target_h, target_w),
            mode=mode,
            align_corners=False if mode == "bilinear" else None
        )
        
        # Reshape back to (num_patches, feature_dim)
        features_aligned = features_aligned.squeeze(0).permute(1, 2, 0)
        features_aligned = features_aligned.reshape(target_h * target_w, feature_dim)
        
        return features_aligned
    
    def prepare_conditioning_embeddings(
        self,
        dino_features: torch.Tensor,
        text_embeddings: Optional[torch.Tensor] = None,
        target_shape: Optional[Tuple[int, int]] = None,
        conditioning_strength: float = 0.5
    ) -> torch.Tensor:
        """
        Prepare DINO features as conditioning embeddings for FLUX
        
        Args:
            dino_features: DINO patch embeddings
            text_embeddings: Optional text embeddings to concatenate
            target_shape: Optional target spatial shape for alignment
            conditioning_strength: Strength of DINO conditioning
            
        Returns:
            Conditioning embeddings ready for FLUX cross-attention
        """
        # Spatial alignment if target shape specified
        if target_shape is not None:
            dino_features = self.align_spatial_dimensions(dino_features, target_shape)
        
        # Project to FLUX space
        projected = self.project_features(dino_features, conditioning_strength)
        
        # Concatenate with text embeddings if provided
        if text_embeddings is not None:
            # Ensure text embeddings are on same device
            if text_embeddings.device != self.device:
                text_embeddings = text_embeddings.to(self.device)
            
            # Text embeddings: (batch, seq_len, dim)
            # DINO features: (num_patches, dim)
            # Add batch dimension to DINO if needed
            if projected.dim() == 2:
                projected = projected.unsqueeze(0)
            
            # Concatenate along sequence dimension
            combined = torch.cat([text_embeddings, projected], dim=1)
            return combined
        
        # Return DINO features with batch dimension
        if projected.dim() == 2:
            projected = projected.unsqueeze(0)
        
        return projected
    
    def calculate_latent_shape(
        self,
        image_size: Tuple[int, int],
        vae_scale_factor: int = 8,
        patch_size: int = 2
    ) -> Tuple[int, int]:
        """
        Calculate FLUX latent spatial dimensions for an image size
        
        Args:
            image_size: Input image (height, width)
            vae_scale_factor: VAE downsampling factor (default 8 for FLUX)
            patch_size: Patch size in latent space (default 2)
            
        Returns:
            Latent shape (latent_h, latent_w) in patches
        """
        h, w = image_size
        
        # VAE downsampling
        latent_h = h // vae_scale_factor
        latent_w = w // vae_scale_factor
        
        # Patch-based processing
        latent_h = latent_h // patch_size
        latent_w = latent_w // patch_size
        
        return (latent_h, latent_w)
