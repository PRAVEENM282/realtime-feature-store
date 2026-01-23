import asyncio
import json
import os
import random
import time
import uuid
import logging
from aiokafka import AIOKafkaProducer

# Configuration
KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "localhost:9092")
TOPIC_NAME = "raw_events"
EVENTS_PER_SECOND = int(os.getenv("EVENTS_PER_SECOND", "1000"))

# Setup Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("data_generator")

async def generate_events(producer):
    """
    Generates high-throughput events and sends them to Kafka.
    """
    logger.info(f"Starting data generator against {KAFKA_BROKER_URL} on topic {TOPIC_NAME}")
    
    user_pool = [str(uuid.uuid4()) for _ in range(1000)] # Pool of users to simulate realistic traffic
    logger.info(f"TESTING INFO: Valid user_id to query: {user_pool[0]}")
    
    while True:
        start_time = time.time()
        
        try:
            # Create a batch of events
            tasks = []
            for _ in range(EVENTS_PER_SECOND):
                event = {
                    "user_id": random.choice(user_pool),
                    "amount": round(random.uniform(1.0, 100.0), 2),
                    "timestamp": time.time()
                }
                tasks.append(producer.send_and_wait(TOPIC_NAME, json.dumps(event).encode("utf-8")))
            
            # Send batch
            await asyncio.gather(*tasks)
            
            elapsed = time.time() - start_time
            sleep_time = max(0, 1.0 - elapsed)
            
            logger.info(f"Sent {EVENTS_PER_SECOND} events in {elapsed:.4f}s. Sleeping for {sleep_time:.4f}s")
            
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        except Exception as e:
            logger.error(f"Error sending batch: {e}. Sleeping for 5s before retry.")
            await asyncio.sleep(5)

async def main():
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BROKER_URL)
    while True:
        try:
            await producer.start()
            logger.info("Kafka Producer started")
            break
        except Exception as e:
            logger.error(f"Failed to start producer: {e}. Retrying in 5s...")
            await asyncio.sleep(5)

    try:
        await generate_events(producer)
    except asyncio.CancelledError:
        logger.info("Stopping data generator...")
    finally:
        await producer.stop()
        logger.info("Kafka Producer stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
