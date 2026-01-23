import pytest
import os
import sys

# Ensure services are in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def valid_user_id():
    return "user-123-uuid"
