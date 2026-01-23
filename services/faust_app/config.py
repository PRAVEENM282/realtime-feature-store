import os

KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "kafka://localhost:9092")
RAW_TOPIC_NAME = "raw_events"
PROCESSED_TOPIC_NAME = os.getenv("PROCESSED_TOPIC", "processed_features")
APP_NAME = "feature_extractor"
WINDOW_SIZE = 10.0 # seconds
