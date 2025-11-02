"""Tests for upscaling functionality"""
import pytest
import numpy as np
from PIL import Image
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from upscaler import BasicUpscaler


@pytest.fixture
def upscaler():
    return BasicUpscaler()


@pytest.fixture
def sample_image():
    return Image.new("RGB", (256, 256), color=(100, 150, 200))


def test_upscaler_initialization(upscaler):
    """Test upscaler initializes correctly"""
    assert upscaler.scale_factor == 2


def test_basic_upscale(upscaler, sample_image):
    """Test basic 2x upscaling"""
    result = upscaler.upscale(sample_image)
    
    assert result.size[0] == sample_image.size[0] * 2
    assert result.size[1] == sample_image.size[1] * 2


def test_upscale_preserves_aspect_ratio(upscaler):
    """Test that upscaling maintains aspect ratio"""
    image = Image.new("RGB", (200, 100), color=(50, 100, 150))
    result = upscaler.upscale(image)
    
    assert result.size[0] / result.size[1] == image.size[0] / image.size[1]


def test_upscale_with_numpy_array(upscaler):
    """Test upscaling from numpy array"""
    image_array = np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8)
    result = upscaler.upscale(image_array)
    
    assert isinstance(result, Image.Image)
    assert result.size == (256, 256)


def test_generate_tiles(upscaler, sample_image):
    """Test tile generation"""
    tiles = upscaler.generate_tiles(sample_image, tile_size=128, overlap=32)
    
    assert len(tiles) > 0
    for tile, x, y in tiles:
        assert tile.shape[0] <= 128
        assert tile.shape[1] <= 128
        assert x >= 0
        assert y >= 0


def test_tile_coverage(upscaler):
    """Test that tiles cover the entire image"""
    image = Image.new("RGB", (300, 300), color=(0, 0, 0))
    tiles = upscaler.generate_tiles(image, tile_size=128, overlap=32)
    
    # Verify we have enough tiles to cover the image
    assert len(tiles) >= 4  # At minimum for 300x300 with 128 tiles


def test_stitch_tiles(upscaler):
    """Test tile stitching"""
    # Create simple tiles
    tiles = [
        (np.ones((128, 128, 3), dtype=np.uint8) * 100, 0, 0),
        (np.ones((128, 128, 3), dtype=np.uint8) * 150, 96, 0),
    ]
    
    result = upscaler.stitch_tiles(tiles, output_size=(224, 128), tile_size=128, overlap=32)
    
    assert isinstance(result, Image.Image)
    assert result.size == (224, 128)


def test_blend_mask_creation(upscaler):
    """Test blend mask for smooth transitions"""
    mask = upscaler._create_blend_mask(height=128, width=128, overlap=32)
    
    assert mask.shape == (128, 128)
    assert mask.min() >= 0
    assert mask.max() <= 1
    # Check that corners have lower values (blending)
    assert mask[0, 0] < mask[64, 64]


def test_upscale_with_dino_features(upscaler, sample_image):
    """Test upscaling with DINO features (placeholder for now)"""
    # Create fake DINO features
    fake_features = np.random.randn(256, 768)
    
    result = upscaler.upscale(sample_image, dino_features=fake_features)
    
    # Should still work even with features (they're not used yet in POC)
    assert result.size[0] == sample_image.size[0] * 2
    assert result.size[1] == sample_image.size[1] * 2
