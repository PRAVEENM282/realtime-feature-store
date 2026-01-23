from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class FeatureResponse(BaseModel):
    user_id: str
    feature_a: Optional[Dict[str, float]]
    feature_b: Optional[int]
    last_updated_timestamp: Optional[datetime]

class ErrorResponse(BaseModel):
    detail: str
