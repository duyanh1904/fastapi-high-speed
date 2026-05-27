from fastapi import FastAPI

from app.core.database import Base
from app.database import engine, redis_pool
from app.database_util import create_db_lifespan
from app.routers.api import api_router

db_lifespan = create_db_lifespan(engine, base_metadata=Base.metadata, retries=12, delay=5)

app = FastAPI(
    title="High-Performance API Demo",
    lifespan=db_lifespan,
)

app.include_router(api_router)

@app.on_event("shutdown")
async def shutdown_event():
    await redis_pool.disconnect()


@app.get("/")
async def root():
    return {"message": "FastAPI & TiDB Cluster are running perfectly!"}