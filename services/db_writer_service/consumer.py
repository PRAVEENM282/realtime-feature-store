import os
import json
import logging
import asyncio
import redis.asyncio as redis
from aiokafka import AIOKafkaConsumer
from config import KAFKA_BROKER_URL, PROCESSED_TOPIC
from db import upsert_feature

logger = logging.getLogger(__name__)

# Initialize Redis client (with a fallback for local testing)
REDIS_URL = os.getenv("REDIS_URL")
redis_client = redis.from_url(REDIS_URL)

async def update_redis_cache(client, user_id: str, data: dict):
    """
    Helper function to update the Redis cache asynchronously.
    Includes error handling so a Redis failure doesn't crash the Kafka consumer.
    """
    try:
        await client.set(f"user_features:{user_id}", json.dumps(data))
    except Exception as e:
        logger.error(f"Failed to update Redis cache for user {user_id}: {e}")

async def start_consumer(pool):
    """
    Starts the Kafka consumer and processes messages concurrently to Redis and Postgres.
    """
    consumer = AIOKafkaConsumer(
        PROCESSED_TOPIC,
        bootstrap_servers=KAFKA_BROKER_URL,
        group_id="db_writer_group",
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='earliest'
    )
    
    await consumer.start()
    logger.info(f"Started Consumer for topic {PROCESSED_TOPIC}")
    
    try:
        async for msg in consumer:
            try:
                data = msg.value
                # Expecting format from Faust Agent:
                # user_id, feature_a, feature_b, last_updated_timestamp
                user_id = data.get("user_id")
                feature_a = data.get("feature_a")
                feature_b = data.get("feature_b")
                timestamp = data.get("last_updated_timestamp")
                
                if user_id:
                    # 1. Prepare the dictionary payload for Redis
                    feature_data = {
                        "user_id": user_id,
                        "feature_a": feature_a,
                        "feature_b": feature_b,
                        "last_updated_timestamp": timestamp
                    }
                    
                    # 2. Concurrently write to Redis (instant serving) and Postgres (durable history)
                    # This guarantees the "zero-latency impact" mentioned on your resume.
                    await asyncio.gather(
                        update_redis_cache(redis_client, user_id, feature_data),
                        upsert_feature(pool, user_id, feature_a, feature_b, timestamp)
                    )
                else:
                    logger.warning(f"Received message without user_id: {data}")
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
    finally:
        await consumer.stop()
        logger.info("Stopped Consumer")