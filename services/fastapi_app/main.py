from fastapi import FastAPI, HTTPException, Request
from contextlib import asynccontextmanager
import asyncpg
from config import POSTGRES_DSN
from logger import setup_logger
from models import FeatureResponse, ErrorResponse
from validation import validate_user_id
from crud import get_feature

logger = setup_logger("fastapi_app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FastAPI application")
    try:
        app.state.pool = await asyncpg.create_pool(POSTGRES_DSN)
        logger.info("Database connection pool established")
        yield
    except Exception as e:
        logger.fatal(f"Failed to startup: {e}", exc_info=True)
        raise
    finally:
        logger.info("Shutting down")
        if hasattr(app.state, "pool"):
            await app.state.pool.close()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(lifespan=lifespan, title="Feature Store API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from crud import get_feature, get_recent_users

@app.get("/users")
async def read_users(request: Request):
    try:
        return await get_recent_users(request.app.state.pool)
    except Exception as e:
        logger.error(f"Error fetching users: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get(
    "/features/{user_id}", 
    response_model=FeatureResponse,
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}}
)
async def read_feature(user_id: str, request: Request):
    validate_user_id(user_id)
    
    try:
        data = await get_feature(request.app.state.pool, user_id)
        if not data:
            raise HTTPException(status_code=404, detail="Features not found for user")
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Internal error fetching features: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
