import pytest
from app.routes.game import get_location_value

def test_get_location_value_free_throw():
    # Zone 1 is free throw, should return 1
    assert get_location_value(1) == 1

def test_get_location_value_inside_arc():
    # Zones 2 and 3 are inside the arc, should return 2
    assert get_location_value(2) == 2
    assert get_location_value(3) == 2

def test_get_location_value_outside_arc():
    # Zones 4, 5, 6 are outside the arc, should return 3
    assert get_location_value(4) == 3
    assert get_location_value(5) == 3
    assert get_location_value(6) == 3

def test_get_location_value_invalid_zones():
    # Edge cases and invalid zones should return 0
    assert get_location_value(0) == 0
    assert get_location_value(7) == 0
    assert get_location_value(-1) == 0
    assert get_location_value(100) == 0
