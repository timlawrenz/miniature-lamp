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
    def __init__(self, flux_pipeline=None, scale_factor=2.0, dino_extractor=None):
        self.scale_factor = scale_factor
        self.flux_pipeline = flux_pipeline
        self.dino_extractor = dino_extractor
    
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
        new_size = (int(w * self.scale_factor), int(h * self.scale_factor))
        upscaled = cv2.resize(image, new_size, interpolation=cv2.INTER_CUBIC)
        return Image.fromarray(upscaled)
    
    def _upscale_with_flux(self, image, dino_features=None, progress_callback=None, tile_size=1024, **flux_kwargs):
        """FLUX-based upscaling with optional DINO conditioning"""
        h, w = image.shape[:2]
        
        # If image is small enough, process directly
        if h <= 512 and w <= 512:
            # Extract DINO features if not provided
            if dino_features is None and self.dino_extractor is not None:
                dino_features = self.dino_extractor.extract_features(image)
            
            result = self.flux_pipeline.upscale_tile(
                image,
                dino_features=dino_features,
                scale_factor=self.scale_factor,
                **flux_kwargs
            )
            
            # Update progress for single tile
            if progress_callback:
                try:
                    progress_callback()
                except Exception:
                    # Stop signal received
                    raise
            
            return result
        
        # Otherwise, use tiled processing
        print(f"Image too large ({w}x{h}), using tiled processing...")
        
        # Calculate target dimensions (ensure integers)
        target_h = int(h * self.scale_factor)
        target_w = int(w * self.scale_factor)
        
        # Calculate input tile size based on output tile size and scale factor
        output_tile_size = tile_size
        input_tile_size = int(output_tile_size / self.scale_factor)
        
        # Ensure minimum tile size (don't go below 256 for quality)
        input_tile_size = max(256, input_tile_size)
        
        # Scale overlap proportionally (typically 1/8 of tile size)
        overlap = max(16, int(input_tile_size / 8))
        
        print(f"  Using {input_tile_size}x{input_tile_size} input tiles (→ {int(input_tile_size * self.scale_factor)}x{int(input_tile_size * self.scale_factor)} output)")
        
        # Generate tiles from original image
        tiles = self.generate_tiles(image, tile_size=input_tile_size, overlap=overlap)
        print(f"Processing {len(tiles)} tiles...")
        
        # Process each tile with FLUX
        upscaled_tiles = []
        for i, (tile, x, y) in enumerate(tiles):
            # Check for stop signal before processing
            if progress_callback:
                try:
                    progress_callback()
                except Exception:
                    print(f"  Stopped at tile {i+1}/{len(tiles)}")
                    raise
            
            print(f"  Processing tile {i+1}/{len(tiles)}...")
            
            # Extract DINO features for this tile
            tile_dino_features = None
            if self.dino_extractor is not None:
                tile_dino_features = self.dino_extractor.extract_features(tile)
            
            # Upscale this tile with FLUX and DINO guidance
            upscaled_tile = self.flux_pipeline.upscale_tile(
                tile,
                dino_features=tile_dino_features,
                scale_factor=self.scale_factor,
                **flux_kwargs
            )
            
            # Convert back to numpy for stitching
            upscaled_tile_np = np.array(upscaled_tile)
            
            # Scale coordinates for upscaled image (ensure integers)
            upscaled_tiles.append((
                upscaled_tile_np,
                int(x * self.scale_factor),
                int(y * self.scale_factor)
            ))
            
            # Clear GPU memory between tiles
            self.flux_pipeline.clear_memory()
        
        # Stitch upscaled tiles together
        print("Stitching tiles...")
        result = self.stitch_tiles(
            upscaled_tiles,
            output_size=(target_w, target_h),
            tile_size=int(input_tile_size * self.scale_factor),
            overlap=int(overlap * self.scale_factor)
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
