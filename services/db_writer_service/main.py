import asyncio
from db import get_db_pool
from consumer import start_consumer
from logger import setup_logger

logger = setup_logger("db_writer")

async def main():
    logger.info("Starting DB Writer Service")
    while True:
        try:
            pool = await get_db_pool()
            await start_consumer(pool)
        except Exception as e:
            logger.error(f"Service crashed or failed to start: {e}. Retrying in 5s...", exc_info=True)
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
