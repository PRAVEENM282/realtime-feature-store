import re
from fastapi import HTTPException

def validate_user_id(user_id: str):
    """
    Validates that user_id is alphanumeric or UUID.
    Raises HTTPException if invalid.
    """
    if not re.match(r'^[a-zA-Z0-9-]+$', user_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid user_id format. Must be alphanumeric or UUID."
        )
