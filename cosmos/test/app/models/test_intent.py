from app.crud import executors

from app.models.intent import funcs_for_openai


def test_funcs_for_openai():
    res = funcs_for_openai('area_near_constraint', module=executors)
    expected = (
        "def area_near_constraint(named_place_or_amenity_0: str, "
        "distance_or_time_0: str, named_place_or_amenity_1: str, "
        "distance_or_time_1: str, **kwargs)"
    )
    assert res == expected