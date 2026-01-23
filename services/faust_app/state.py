from models import ProcessedFeature
# This module defines how we manage state, though Faust Tables are defined at the App level.
# We can define helper functions for state updates here.

def update_window_aggregate(current_value: float, new_event_amount: float) -> float:
    """
    Updates the rolling window sum. 
    Faust handles window buckets automatically; this just sums values in the bucket.
    """
    return (current_value or 0.0) + new_event_amount

def update_count(current_count: int) -> int:
    """
    Increments the user event count.
    """
    return (current_count or 0) + 1
