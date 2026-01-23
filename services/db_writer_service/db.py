import asyncpg
import logging
import json
from config import POSTGRES_DSN

logger = logging.getLogger(__name__)

async def get_db_pool():
    """Create a connection pool to Postgres."""
    try:
        pool = await asyncpg.create_pool(POSTGRES_DSN)
        logger.info("Database connection pool created")
        return pool
    except Exception as e:
        logger.error(f"Failed to create DB pool: {e}")
        raise

async def upsert_feature(pool, user_id: str, feature_a: dict, feature_b: int, last_updated: float):
    """
    Idempotent UPSERT of features into postgres.
    """
    query = """
    INSERT INTO user_features (user_id, feature_a, feature_b, last_updated_timestamp)
    VALUES ($1, $2, $3, to_timestamp($4))
    ON CONFLICT (user_id)
    DO UPDATE SET
        feature_a = EXCLUDED.feature_a,
        feature_b = EXCLUDED.feature_b,
        last_updated_timestamp = EXCLUDED.last_updated_timestamp;
    """
    try:
        async with pool.acquire() as conn:
            # asyncpg requires JSON to be string if column is JSONB? 
            # Actually asyncpg handles dict to jsonb automatically if we use json_codec or just pass string.
            # But standard is to pass string for jsonb usually, or rely on automatic conversion if set up.
            # To be safe, we dump feature_a to str.
            await conn.execute(query, user_id, json.dumps(feature_a), feature_b, last_updated)
            logger.debug(f"Upserted features for user {user_id}")
    except Exception as e:
        logger.error(f"Error upserting features for user {user_id}: {e}")
        # We don't raise here to avoid crashing the consumer loop completely, 
        # but in production we might want to dead-letter queue this.
        # For now, we log error.
