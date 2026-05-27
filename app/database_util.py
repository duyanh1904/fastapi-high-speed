import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger("DatabaseGuard")


class DatabaseInitializer:
    def __init__(self, engine: AsyncEngine, base_metadata: Any, retries: int = 12, delay: int = 5):
        self.engine = engine
        self.base_metadata = base_metadata
        self.retries = retries
        self.delay = delay

    async def wait_until_available(self) -> None:
        logger.info("[TiDB Guard] Checking database connectivity...")
        for attempt in range(1, self.retries + 1):
            try:
                async with self.engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                logger.info("[TiDB Guard] Database is ready.")
                return
            except Exception:
                logger.warning(
                    "[TiDB Guard] Retry %s/%s. Waiting %s seconds...",
                    attempt,
                    self.retries,
                    self.delay,
                )
                await asyncio.sleep(self.delay)

        raise RuntimeError("TiDB Cluster failed to initialize.")

    async def bootstrap_database(self) -> None:
        logger.info("[TiDB Guard] Ensuring database and tables...")
        async with self.engine.begin() as conn:
            await conn.execute(text("CREATE DATABASE IF NOT EXISTS test"))
            await conn.execute(text("USE test"))
            await conn.run_sync(self.base_metadata.create_all)
        logger.info("[TiDB Guard] Database bootstrap complete.")


def create_db_lifespan(engine: AsyncEngine, base_metadata: Any, retries: int = 12, delay: int = 5):
    initializer = DatabaseInitializer(
        engine=engine,
        base_metadata=base_metadata,
        retries=retries,
        delay=delay,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await initializer.wait_until_available()
        await initializer.bootstrap_database()
        yield
        await initializer.engine.dispose()

    return lifespan
