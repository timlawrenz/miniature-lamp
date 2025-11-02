"""Tests for DINO feature extraction"""
import pytest
import torch
import numpy as np
from PIL import Image
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dino_extractor import DINOFeatureExtractor


@pytest.fixture
def extractor():
    return DINOFeatureExtractor()


@pytest.fixture
def sample_image():
    # Create a simple test image
    return Image.new("RGB", (224, 224), color=(73, 109, 137))


def test_model_initialization(extractor):
    """Test that DINO model loads correctly"""
    assert extractor.model is not None
    assert extractor.processor is not None
    assert extractor.device in [torch.device("cuda"), torch.device("cpu")]


def test_model_eval_mode(extractor):
    """Test that model is in evaluation mode"""
    assert not extractor.model.training


def test_extract_features_pil(extractor, sample_image):
    """Test feature extraction from PIL image"""
    features = extractor.extract_features(sample_image)
    
    assert features is not None
    assert len(features.shape) == 2  # (num_patches, feature_dim)
    assert features.shape[1] == 768  # dinov2-base feature dimension


def test_extract_features_numpy(extractor):
    """Test feature extraction from numpy array"""
    image_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    features = extractor.extract_features(image_array)
    
    assert features is not None
    assert len(features.shape) == 2


def test_patch_grid_size(extractor):
    """Test patch grid calculation"""
    grid_size = extractor.get_patch_grid_size((224, 224))
    
    # 224 / 14 = 16 patches per dimension
    assert grid_size == (16, 16)


def test_patch_grid_different_sizes(extractor):
    """Test patch grid with non-square images"""
    grid_size = extractor.get_patch_grid_size((224, 448))
    assert grid_size == (16, 32)


def test_feature_shape_matches_grid(extractor, sample_image):
    """Test that extracted features match expected grid size"""
    features = extractor.extract_features(sample_image)
    grid_size = extractor.get_patch_grid_size(sample_image.size[::-1])
    
    expected_patches = grid_size[0] * grid_size[1]
    assert features.shape[0] == expected_patches
