from app.crud.executors import _prepare_args_for_area_near_constraint

def test__prepare_args_for_area_near_constraint():
    """Test _prepare_args_for_area_near_constraint."""
    args = {
        'named_place_or_amenity_0': 'San Francisco',
        'distance_or_time_0': '500m',
        'named_place_or_amenity_1': 'Sacre Coeur',
        'distance_or_time_1': '250m',
    }
    res = _prepare_args_for_area_near_constraint(args)
    assert len(res) == 2
    assert res[0].entity.lookup == 'San Francisco'
    assert res[0].distance_in_meters == 500
    assert res[1].entity.lookup == 'Sacre Coeur'
    assert res[1].distance_in_meters == 250

    # Test kwargs
    args = {
        'named_place_or_amenity_0': 'San Francisco',
        'distance_or_time_0': '500m',
        'named_place_or_amenity_1': 'Sacre Coeur',
        'distance_or_time_1': '250m',
        'named_place_or_amenity_2': 'Sacre Coeur',
        'distance_or_time_2': '250m',
    }
    res = _prepare_args_for_area_near_constraint(args)
    assert len(res) == 3
    assert res[2].entity.lookup == 'Sacre Coeur'
    assert res[2].distance_in_meters == 250


def test__prepare_args_for_area_near_constraint_bad_inputs():
    """Test _prepare_args_for_area_near_constraint."""

    # Test missing distance or time
    try:
        args = {
            'named_place_or_amenity_0': 'San Francisco',
            'named_place_or_amenity_1': 'Sacre Coeur',
            'distance_or_time_1': '250m',
        }
        res = _prepare_args_for_area_near_constraint(args)
    except ValueError as e:
        assert str(e) == "Number of elements mismatched"
    
    try:
        args = {
            'named_place_or_amenity_0': 'San Francisco',
            'distance_or_time_0': '20 minutes',
            'named_place_or_amenity_0': 'Sacramento',
            'distance_or_time_0': '500m',
        }
        res = _prepare_args_for_area_near_constraint(args)
    except NotImplementedError as e:
        assert str(e) == "Time is not yet supported"

    # Test mismatched args
    try:
        args = {
            'named_place_or_amenity_0': 'San Francisco',
            'distance_or_time_0': '500m',
            'named_place_or_amenity_2': 'Sacre Coeur',
            'distance_or_time_3': '250m',
        }
        res = _prepare_args_for_area_near_constraint(args)
    except AssertionError as e:
        assert str(e) == "Missing a distance or time"


    # Test invalid key
    try:
        args = {
            'banana_stand_0': 'San Francisco',
            'banana_stand_1': 'San Francisco',
            'named_place_or_amenity_0': 'Sacre Coeur',
            'distance_or_time_0': '500m',
            'named_place_or_amenity_1': 'Sacre Coeur',
            'distance_or_time_1': '250m',
        }
    except AssertionError as e:
        assert str(e) == "Invalid key, can only start with named_place_or_amenity_ or distance_or_time_"
    