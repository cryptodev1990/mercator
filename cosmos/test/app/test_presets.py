from app.data.presets import presets, Preset
from collections.abc import Mapping

def test_preset_exists() -> None:
    """Test that the presets object exists."""
    assert isinstance(presets, Mapping)
    assert len(presets) > 1000
    assert all(isinstance(v, Preset) for v in presets.values())
    assert all(isinstance(k, str) for k in presets.keys())

