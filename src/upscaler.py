"""
Basic upscaler with DINO guidance support
"""
import torch
import numpy as np
from PIL import Image
import cv2
from typing import Optional, Union


class BasicUpscaler:
    def __init__(self, flux_pipeline=None):
        self.scale_factor = 2
        self.flux_pipeline = flux_pipeline
    
    def upscale(self, image, dino_features=None, use_flux=False, **flux_kwargs):
        """
        Upscale an image by 2x with optional DINO guidance
        
        Args:
            image: PIL Image or numpy array
            dino_features: Optional DINO features for semantic guidance
            use_flux: Use FLUX diffusion instead of bicubic
            **flux_kwargs: Additional parameters for FLUX (prompt, steps, etc.)
            
        Returns:
            Upscaled PIL Image
        """
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        if use_flux and self.flux_pipeline is not None:
            # Use FLUX for upscaling
            return self._upscale_with_flux(image, dino_features, **flux_kwargs)
        else:
            # Fall back to bicubic
            return self._upscale_bicubic(image)
    
    def _upscale_bicubic(self, image):
        """Simple bicubic upscaling"""
        h, w = image.shape[:2]
        new_size = (w * self.scale_factor, h * self.scale_factor)
        upscaled = cv2.resize(image, new_size, interpolation=cv2.INTER_CUBIC)
        return Image.fromarray(upscaled)
    
    def _upscale_with_flux(self, image, dino_features=None, **flux_kwargs):
        """FLUX-based upscaling with optional DINO conditioning"""
        # For now, process as single tile
        # TODO: Implement tiled processing for large images
        result = self.flux_pipeline.upscale_tile(
            image,
            dino_features=dino_features,
            **flux_kwargs
        )
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
        
        # Create blending weights for overlap regions
        blend_mask = self._create_blend_mask(tile_size, overlap)
        
        for tile, x, y in tiles:
            tile_h, tile_w = tile.shape[:2]
            mask = blend_mask[:tile_h, :tile_w]
            
            result[y:y+tile_h, x:x+tile_w] += tile * mask[:, :, np.newaxis]
            weights[y:y+tile_h, x:x+tile_w] += mask
        
        # Normalize by weights
        weights = np.maximum(weights, 1e-8)
        result = result / weights[:, :, np.newaxis]
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        return Image.fromarray(result)
    
    def _create_blend_mask(self, tile_size, overlap):
        """Create a blending mask for smooth tile transitions"""
        mask = np.ones((tile_size, tile_size), dtype=np.float32)
        
        if overlap > 0:
            fade = np.linspace(0, 1, overlap)
            # Fade in from left
            mask[:, :overlap] *= fade[np.newaxis, :]
            # Fade in from top
            mask[:overlap, :] *= fade[:, np.newaxis]
            # Fade out to right
            mask[:, -overlap:] *= fade[np.newaxis, ::-1]
            # Fade out to bottom
            mask[-overlap:, :] *= fade[::-1, np.newaxis]
        
        return mask
