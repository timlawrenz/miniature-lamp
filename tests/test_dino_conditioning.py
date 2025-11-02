"""Tests for DINO conditioning adapter"""
import pytest
import torch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dino_conditioning import DINOConditioningAdapter


def test_adapter_initialization():
    """Test adapter initialization"""
    adapter = DINOConditioningAdapter(device="cpu")
    assert adapter.dino_dim == 768
    assert adapter.flux_dim == 4096
    assert adapter.projection is not None


def test_feature_projection():
    """Test DINO feature projection to FLUX space"""
    adapter = DINOConditioningAdapter(device="cpu")
    
    # Simulate DINO features (16x16 patches, 768-dim)
    dino_features = torch.randn(256, 768)
    
    # Project features
    projected = adapter.project_features(dino_features, conditioning_strength=0.5)
    
    assert projected.shape == (256, 4096)
    assert projected.dtype == torch.float32


def test_spatial_alignment():
    """Test spatial dimension alignment"""
    adapter = DINOConditioningAdapter(device="cpu")
    
    # Simulate DINO features (16x16 grid = 256 patches)
    dino_features = torch.randn(256, 768)
    
    # Align to different spatial dimensions (32x32)
    target_shape = (32, 32)
    aligned = adapter.align_spatial_dimensions(dino_features, target_shape)
    
    assert aligned.shape == (1024, 768)  # 32*32 = 1024 patches


def test_spatial_alignment_same_shape():
    """Test that same shape alignment is no-op"""
    adapter = DINOConditioningAdapter(device="cpu")
    
    # 16x16 grid
    dino_features = torch.randn(256, 768)
    target_shape = (16, 16)
    
    aligned = adapter.align_spatial_dimensions(dino_features, target_shape)
    
    # Should return same tensor
    assert torch.equal(aligned, dino_features)


def test_prepare_conditioning_embeddings():
    """Test preparing conditioning embeddings for FLUX"""
    adapter = DINOConditioningAdapter(device="cpu")
    
    # DINO features
    dino_features = torch.randn(256, 768)
    
    # Prepare without text embeddings
    embeddings = adapter.prepare_conditioning_embeddings(dino_features)
    
    assert embeddings.shape == (1, 256, 4096)  # (batch, seq_len, dim)


def test_prepare_conditioning_with_text():
    """Test preparing conditioning with text embeddings"""
    adapter = DINOConditioningAdapter(device="cpu")
    
    # DINO features
    dino_features = torch.randn(256, 768)
    
    # Simulated text embeddings (batch, seq_len, dim)
    text_embeddings = torch.randn(1, 77, 4096)
    
    # Prepare combined embeddings
    embeddings = adapter.prepare_conditioning_embeddings(
        dino_features,
        text_embeddings=text_embeddings
    )
    
    # Should concatenate along sequence dimension
    assert embeddings.shape == (1, 77 + 256, 4096)


def test_calculate_latent_shape():
    """Test latent shape calculation"""
    adapter = DINOConditioningAdapter(device="cpu")
    
    # Test common image sizes
    latent_shape = adapter.calculate_latent_shape((512, 512))
    assert latent_shape == (32, 32)  # 512/8/2 = 32
    
    latent_shape = adapter.calculate_latent_shape((1024, 768))
    assert latent_shape == (64, 48)  # 1024/8/2=64, 768/8/2=48


def test_conditioning_strength():
    """Test conditioning strength parameter"""
    adapter = DINOConditioningAdapter(device="cpu")
    
    dino_features = torch.randn(256, 768)
    
    # Test different strengths
    projected_weak = adapter.project_features(dino_features, conditioning_strength=0.1)
    projected_strong = adapter.project_features(dino_features, conditioning_strength=1.0)
    
    # Strong conditioning should have larger magnitude
    assert torch.abs(projected_strong).mean() > torch.abs(projected_weak).mean()


def test_spatial_alignment_non_square():
    """Test spatial alignment with non-square input"""
    adapter = DINOConditioningAdapter(device="cpu")
    
    # Non-square grid should raise error
    dino_features = torch.randn(200, 768)  # Not a perfect square
    
    with pytest.raises(ValueError, match="square grid"):
        adapter.align_spatial_dimensions(dino_features, (16, 16))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
