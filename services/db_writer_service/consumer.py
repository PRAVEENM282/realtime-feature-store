import json
import logging
import asyncio
from aiokafka import AIOKafkaConsumer
from config import KAFKA_BROKER_URL, PROCESSED_TOPIC
from db import upsert_feature

logger = logging.getLogger(__name__)

async def start_consumer(pool):
    """
    Starts the Kafka consumer and processes messages.
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
                    await upsert_feature(pool, user_id, feature_a, feature_b, timestamp)
                else:
                    logger.warning(f"Received message without user_id: {data}")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    finally:
        await consumer.stop()
        logger.info("Stopped Consumer")
