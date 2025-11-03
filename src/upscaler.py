"""
Basic upscaler with DINO guidance support
"""
import torch
import numpy as np
from PIL import Image
import cv2
from typing import Optional, Union

try:
    from .dino_extractor import DINOFeatureExtractor
except ImportError:
    from dino_extractor import DINOFeatureExtractor


class BasicUpscaler:
    def __init__(self, comfyui_sampler=None, scale_factor=2.0, dino_extractor=None):
        self.scale_factor = scale_factor
        self.comfyui_sampler = comfyui_sampler
        self.dino_extractor = dino_extractor
    
    def upscale(self, image, dino_features=None, use_diffusion=False, **kwargs):
        """
        Upscale an image with optional DINO guidance
        
        Args:
            image: PIL Image or numpy array
            dino_features: Optional DINO features for semantic guidance
            use_diffusion: Use diffusion model instead of bicubic
            **kwargs: Additional parameters (prompt, steps, sampler_name, etc.)
            
        Returns:
            Upscaled PIL Image
        """
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        if use_diffusion:
            # Use ComfyUI sampler
            if self.comfyui_sampler is not None:
                return self._upscale_with_comfyui(image, dino_features, **kwargs)
            else:
                print("[Upscaler] ERROR: No ComfyUI sampler available!")
                raise ValueError("ComfyUI sampler is required for diffusion upscaling")
        else:
            # Fall back to bicubic
            return self._upscale_bicubic(image)
    
    def _upscale_bicubic(self, image):
        """Simple bicubic upscaling"""
        h, w = image.shape[:2]
        new_size = (int(w * self.scale_factor), int(h * self.scale_factor))
        upscaled = cv2.resize(image, new_size, interpolation=cv2.INTER_CUBIC)
        return Image.fromarray(upscaled)
    
    def _upscale_with_comfyui(self, image, dino_features=None, progress_callback=None, 
                              sampler_name="euler", scheduler="normal", steps=20, 
                              denoise=0.4, cfg=7.0, seed=0, **kwargs):
        """ComfyUI native upscaling with model-agnostic sampling"""
        # TODO: Integrate DINO features into conditioning
        # For now, just use the sampler without DINO
        result = self.comfyui_sampler.upscale(
            image,
            scale_factor=self.scale_factor,
            denoise=denoise,
            steps=steps,
            cfg=cfg,
            sampler_name=sampler_name,
            scheduler=scheduler,
            seed=seed,
            dino_features=dino_features
        )
        
        # Update progress
        if progress_callback:
            try:
                progress_callback()
            except Exception:
                # Stop signal received
                raise
        
        return result
    
    def generate_tiles(self, image, tile_size=512, overlap=64):
        """
        Generate overlapping tiles from an image
        
        Args:
            image: PIL Image or numpy array
            tile_size: Size of each tile (default 512)
            overlap: Pixel overlap between tiles (default 64)
            
        Returns:
            List of (tile, x, y) tuples
        """
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        h, w = image.shape[:2]
        stride = tile_size - overlap
        tiles = []
        
        for y in range(0, h, stride):
            for x in range(0, w, stride):
                y_end = min(y + tile_size, h)
                x_end = min(x + tile_size, w)
                
                # Adjust start if we're at the edge
                y_start = max(0, y_end - tile_size)
                x_start = max(0, x_end - tile_size)
                
                tile = image[y_start:y_end, x_start:x_end]
                tiles.append((tile, x_start, y_start))
        
        return tiles
    
    def stitch_tiles(self, tiles, output_size, tile_size=512, overlap=64):
        """
        Stitch tiles back into a single image with blending
        
        Args:
            tiles: List of (tile, x, y) tuples
            output_size: (width, height) of final image
            tile_size: Size of each tile
            overlap: Pixel overlap between tiles
            
        Returns:
            Stitched PIL Image
        """
        w, h = output_size
        result = np.zeros((h, w, 3), dtype=np.float32)
        weights = np.zeros((h, w), dtype=np.float32)
        
        for i, (tile, x, y) in enumerate(tiles):
            tile_h, tile_w = tile.shape[:2]
            
            # Ensure tile doesn't exceed canvas boundaries
            max_h = min(tile_h, h - y)
            max_w = min(tile_w, w - x)
            
            # Crop tile if it exceeds boundaries
            if max_h < tile_h or max_w < tile_w:
                tile = tile[:max_h, :max_w]
                tile_h, tile_w = tile.shape[:2]
            
            # Create blend mask matching the exact (possibly cropped) tile dimensions
            mask = self._create_blend_mask(tile_h, tile_w, overlap)
            
            # Convert to proper shape for broadcasting
            mask_3d = mask[:, :, np.newaxis]
            
            # Apply mask
            result[y:y+tile_h, x:x+tile_w] += tile * mask_3d
            weights[y:y+tile_h, x:x+tile_w] += mask
        
        # Normalize by weights
        weights = np.maximum(weights, 1e-8)
        result = result / weights[:, :, np.newaxis]
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        return Image.fromarray(result)
    
    def _create_blend_mask(self, height, width, overlap):
        """Create a blending mask for smooth tile transitions"""
        mask = np.ones((height, width), dtype=np.float32)
        
        if overlap > 0:
            # Calculate fade region size (use smaller of overlap or available space)
            fade_h = min(overlap, height)
            fade_w = min(overlap, width)
            
            if fade_h > 0:
                fade = np.linspace(0, 1, fade_h)
                # Fade in from top
                mask[:fade_h, :] *= fade[:, np.newaxis]
                # Fade out to bottom
                mask[-fade_h:, :] *= fade[::-1, np.newaxis]
            
            if fade_w > 0:
                fade = np.linspace(0, 1, fade_w)
                # Fade in from left
                mask[:, :fade_w] *= fade[np.newaxis, :]
                # Fade out to right
                mask[:, -fade_w:] *= fade[np.newaxis, ::-1]
        
        return mask
