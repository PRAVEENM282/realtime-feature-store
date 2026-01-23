from services.faust_app.state import update_count, update_window_aggregate

def test_update_count():
    assert update_count(0) == 1
    assert update_count(None) == 1
    assert update_count(10) == 11

def test_update_window():
    assert update_window_aggregate(0.0, 10.0) == 10.0
    assert update_window_aggregate(10.0, 5.0) == 15.0
    assert update_window_aggregate(None, 5.0) == 5.0
