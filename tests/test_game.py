from app.routes.game import get_location_value

def test_get_location_value_happy_path():
    # 1 = Free Throw (1 pt)
    assert get_location_value(1) == 1

    # 2 & 3 = Inside Arc (2 pts)
    assert get_location_value(2) == 2
    assert get_location_value(3) == 2

    # 4, 5, 6 = Outside Arc (3 pts)
    assert get_location_value(4) == 3
    assert get_location_value(5) == 3
    assert get_location_value(6) == 3

def test_get_location_value_edge_cases():
    # Invalid zones should return 0
    assert get_location_value(0) == 0
    assert get_location_value(7) == 0
    assert get_location_value(-1) == 0
    assert get_location_value(100) == 0
