import patches

import faust
from datetime import timedelta
from config import (
    KAFKA_BROKER_URL, RAW_TOPIC_NAME, PROCESSED_TOPIC_NAME, 
    APP_NAME, WINDOW_SIZE
)
from models import RawEvent, ProcessedFeature
from agents import process_features
from logger import setup_logger

# Setup Logger
logger = setup_logger(APP_NAME)

# Initialize App
app = faust.App(
    APP_NAME,
    broker=KAFKA_BROKER_URL,
    store='rocksdb://',
    topic_partitions=1,
    datadir='/faust_data',
)

# Topics
raw_topic = app.topic(RAW_TOPIC_NAME, value_type=RawEvent)
processed_topic = app.topic(PROCESSED_TOPIC_NAME, value_type=ProcessedFeature)

# Tables

# Feature A: Rolling Window (Sum)
# Hopping window: 10s size, updates every 1s.
feature_table = app.Table(
    'feature_window_table',
    default=float,
    partitions=1
).hopping(
    timedelta(seconds=WINDOW_SIZE), 
    timedelta(seconds=1.0),
    expires=timedelta(seconds=WINDOW_SIZE + 5)
)

# Feature B: Global Count per user
count_table = app.Table(
    'user_counts_table',
    default=int,
    partitions=1
)

@app.agent(raw_topic)
async def main_agent(stream):
    """
    Main agent that orchestrates feature processing.
    """
    await process_features(stream, feature_table, count_table, processed_topic)

if __name__ == '__main__':
    app.main()
