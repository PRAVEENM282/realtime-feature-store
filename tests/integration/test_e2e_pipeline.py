import pytest
import requests
import json
import time
import uuid
from kafka import KafkaProducer

import os

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
RAW_TOPIC = "raw_events"

@pytest.fixture
def kafka_producer():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    yield producer
    producer.close()

def test_pipeline_flow(kafka_producer):
    """
    Test the full pipeline:
    1. Verify user usually doesn't exist (or new user).
    2. Produce event.
    3. Wait for processing.
    4. Verify API returns feature.
    """
    user_id = str(uuid.uuid4())
    
    # 1. Check API - should be 404
    resp = requests.get(f"{API_URL}/features/{user_id}")
    assert resp.status_code == 404
    
    # 2. Produce Event
    event = {
        "user_id": user_id,
        "amount": 100.0,
        "timestamp": time.time()
    }
    kafka_producer.send(RAW_TOPIC, event)
    kafka_producer.flush()
    
    # 3. Wait for processing (Faust + DB Writer)
    # Exponential backoff or simple polling
    found = False
    for _ in range(60): # Try for 60 seconds
        time.sleep(1)
        resp = requests.get(f"{API_URL}/features/{user_id}")
        if resp.status_code == 200:
            found = True
            break
            
    assert found, f"Feature not found for user {user_id} after waiting"
    
    data = resp.json()
    assert data['user_id'] == user_id
    assert data['feature_b'] >= 1 # Count should be at least 1
    # Check feature_a structure if needed
    assert 'sum_10s' in data['feature_a']
