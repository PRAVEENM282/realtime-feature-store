import faust
from typing import Dict

class RawEvent(faust.Record):
    user_id: str
    amount: float
    timestamp: float

class ProcessedFeature(faust.Record):
    user_id: str
    feature_a: Dict[str, float]
    feature_b: int
    last_updated_timestamp: float
