import asyncio
import logging

from fastapi import APIRouter, Depends, status

from app.dependencies import get_order_service, rate_limiter
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order import OrderService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limiter)],
)
async def create_order(
    payload: OrderCreate,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    return await service.create_order(payload)


@router.post("/test/seed-orders", status_code=status.HTTP_202_ACCEPTED)
async def seed_million_orders(service: OrderService = Depends(get_order_service)):
    async def background_worker() -> None:
        try:
            await service.seed_orders(total_records=1_000_000, batch_size=20_000)
        except Exception:
            logger.exception("Seeding order batches failed")

    asyncio.create_task(background_worker())
    return {"message": "Order seeding has been started in background."}
