import asyncpg
import json
import logging
from models import FeatureResponse

async def get_feature(pool: asyncpg.Pool, user_id: str) -> FeatureResponse:
    """
    Fetch features for a user from the database.
    """
    query = "SELECT user_id, feature_a, feature_b, last_updated_timestamp FROM user_features WHERE user_id = $1"
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, user_id)
        
    if row:
        fea_a = json.loads(row['feature_a']) if isinstance(row['feature_a'], str) else row['feature_a']
        return FeatureResponse(
            user_id=row['user_id'],
            feature_a=fea_a,
            feature_b=row['feature_b'],
            last_updated_timestamp=row['last_updated_timestamp']
        )
    return None

async def get_recent_users(pool: asyncpg.Pool, limit: int = 10):
    """
    Fetch the most recently updated users.
    """
    query = "SELECT user_id FROM user_features ORDER BY last_updated_timestamp DESC LIMIT $1"
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, limit)
    return [row['user_id'] for row in rows]
