from app.data.presets import Preset
from app.parsers.categories import category_lookup

def test_categories():
    """Test categories with different values."""
    # name
    assert {x.key for x in category_lookup("restaurant") }== {"amenity/restaurant"}
    assert {x.key for x in category_lookup("ethiopian restaurant") }== {"amenity/restaurant"}
    # term
    assert {x.key for x in category_lookup("trekking") } == {'highway/trailhead'}
    # tag-value
    assert {x.key for x in category_lookup("agricultural engines")} == {'craft/agricultural_engines'}
    # similar name
    assert {x.key for x in category_lookup("restaurnt") } == {"amenity/restaurant"}
    assert not category_lookup("ethiopian restaurnt")
    # similar terms
    assert {x.key for x in category_lookup("treking")}  == {'highway/trailhead'}
    assert not category_lookup("extra words treking")
