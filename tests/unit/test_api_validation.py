from services.fastapi_app.validation import validate_user_id
from fastapi import HTTPException
import pytest

def test_valid_user_id():
    # Should not raise
    validate_user_id("user123")
    validate_user_id("uuid-v4-format-123")

def test_invalid_user_id():
    with pytest.raises(HTTPException):
        validate_user_id("user@name")
    
    with pytest.raises(HTTPException):
        validate_user_id("user name")
