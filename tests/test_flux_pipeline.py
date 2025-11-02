"""Tests for FLUX pipeline"""
import pytest
import torch
import numpy as np
from PIL import Image
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from flux_pipeline import FLUXUpscalePipeline
from config import FLUXConfig


@pytest.fixture
def sample_tile():
    """Create a small test tile"""
    return Image.new("RGB", (64, 64), color=(100, 150, 200))


def test_flux_config_defaults():
    """Test default FLUX configuration"""
    config = FLUXConfig()
    assert config.variant == "schnell"
    assert config.guidance_scale == 3.5
    assert config.dino_conditioning_strength == 0.7


def test_flux_config_validation():
    """Test configuration validation"""
    with pytest.raises(ValueError):
        FLUXConfig(variant="invalid")
    
    with pytest.raises(ValueError):
        FLUXConfig(strength=1.5)
    
    with pytest.raises(ValueError):
        FLUXConfig(dino_conditioning_strength=-0.1)
    
    with pytest.raises(FileNotFoundError):
        FLUXConfig(model_path="/nonexistent/path/model.safetensors")


def test_flux_config_local_model():
    """Test configuration with local model path"""
    import tempfile
    
    # Create a temporary safetensors file
    with tempfile.NamedTemporaryFile(suffix=".safetensors", delete=False) as f:
        temp_path = f.name
    
    try:
        config = FLUXConfig(model_path=temp_path)
        assert config.is_local_model()
        assert config.model_path == temp_path
    finally:
        import os
        os.unlink(temp_path)


def test_flux_config_invalid_file_format():
    """Test that non-safetensors files are rejected"""
    import tempfile
    
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        temp_path = f.name
    
    try:
        with pytest.raises(ValueError, match="safetensors"):
            FLUXConfig(model_path=temp_path)
    finally:
        import os
        os.unlink(temp_path)


def test_flux_pipeline_initialization():
    """Test FLUX pipeline initialization"""
    pipe = FLUXUpscalePipeline(variant="schnell")
    
    assert pipe.variant == "schnell"
    assert pipe.default_steps["schnell"] == 4
    assert pipe.default_steps["dev"] == 20
    assert pipe.pipe is None  # Not loaded yet


def test_flux_pipeline_device_detection():
    """Test device auto-detection"""
    pipe = FLUXUpscalePipeline()
    
    if torch.cuda.is_available():
        assert pipe.device == "cuda"
    else:
        assert pipe.device == "cpu"


def test_flux_pipeline_variant_selection():
    """Test variant selection"""
    schnell = FLUXUpscalePipeline(variant="schnell")
    assert schnell.model_ids[schnell.variant] == "black-forest-labs/FLUX.1-schnell"
    
    dev = FLUXUpscalePipeline(variant="dev")
    assert dev.model_ids[dev.variant] == "black-forest-labs/FLUX.1-dev"


def test_flux_pipeline_local_model_path():
    """Test local model path support"""
    import tempfile
    
    with tempfile.NamedTemporaryFile(suffix=".safetensors", delete=False) as f:
        temp_path = f.name
    
    try:
        pipe = FLUXUpscalePipeline(model_path=temp_path)
        assert pipe.model_path == temp_path
        assert pipe.pipe is None  # Not loaded yet
    finally:
        import os
        os.unlink(temp_path)


def test_flux_pipeline_invalid_model_path():
    """Test that invalid paths are rejected"""
    with pytest.raises(FileNotFoundError):
        FLUXUpscalePipeline(model_path="/nonexistent/model.safetensors")


@pytest.mark.skipif(not torch.cuda.is_available(), reason="Requires GPU")
@pytest.mark.slow
def test_flux_model_loading():
    """Test FLUX model loading (slow, requires GPU)"""
    pipe = FLUXUpscalePipeline(variant="schnell", enable_offloading=True)
    pipe.load_model()
    
    assert pipe.pipe is not None
    # Model should be loaded, don't test actual inference (too slow)


def test_flux_clear_memory():
    """Test memory clearing"""
    pipe = FLUXUpscalePipeline()
    # Should not error even if model not loaded
    pipe.clear_memory()
