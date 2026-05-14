import os
import asyncpg
import json
import logging
import redis.asyncio as redis
from models import FeatureResponse

logger = logging.getLogger(__name__)

# Ensure REDIS_URL is pulled from the environment (defaulting to localhost for local testing)
REDIS_URL = os.getenv("REDIS_URL")
redis_client = redis.from_url(REDIS_URL)

async def get_feature(pool: asyncpg.Pool, user_id: str) -> FeatureResponse:
    """
    Fetch features for a user using a Dual-Storage strategy.
    1. Attempt sub-millisecond retrieval from Redis.
    2. Fallback to PostgreSQL for historical consistency.
    """
    cache_key = f"user_features:{user_id}"

    # --- STEP 1: Attempt Redis Cache Read ---
    try:
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            # Cache Hit: Parse JSON and return instantly
            data = json.loads(cached_data)
            return FeatureResponse(**data)
    except Exception as e:
        # Graceful degradation: If Redis is down, log the error and fallback to Postgres
        logger.error(f"Redis cache read error for user {user_id}: {e}")

    # --- STEP 2: Fallback to PostgreSQL ---
    query = "SELECT user_id, feature_a, feature_b, last_updated_timestamp FROM user_features WHERE user_id = $1"
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, user_id)
        
    if row:
        fea_a = json.loads(row['feature_a']) if isinstance(row['feature_a'], str) else row['feature_a']
        
        feature_response = FeatureResponse(
            user_id=row['user_id'],
            feature_a=fea_a,
            feature_b=row['feature_b'],
            last_updated_timestamp=row['last_updated_timestamp']
        )

        # --- STEP 3: Populate Redis for future requests ---
        try:
            # We use model_dump_json() (Pydantic v2) to safely serialize datetimes to JSON
            await redis_client.set(cache_key, feature_response.model_dump_json())
        except Exception as e:
            logger.error(f"Failed to write to Redis cache for user {user_id}: {e}")

        return feature_response

    return None

async def get_recent_users(pool: asyncpg.Pool, limit: int = 10):
    """
    Fetch the most recently updated users.
    """
    query = "SELECT user_id FROM user_features ORDER BY last_updated_timestamp DESC LIMIT $1"
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, limit)
    return [row['user_id'] for row in rows]