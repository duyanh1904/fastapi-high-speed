from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session  # Hàm yield DB Session của bạn
from app.schemas.flight import FlightSearchRequest, FlightSearchResponse
from app.repositories.flight import FlightDBRepository, FlightCrawlerRepository
from app.services.flight import FlightFlightService

router = APIRouter(prefix="/crawler", tags=["Flight Modern Architecture"])

# Hàm Factory đóng vai trò Injector kết nối các lớp thông qua Protocol
def get_flight_service(db: AsyncSession = Depends(get_db_session)) -> FlightFlightService:
    db_repo = FlightDBRepository(db)
    crawler_repo = FlightCrawlerRepository()

    # Inject 2 thực thể vào Service (Service chỉ nhận diện qua lớp Protocol)
    return FlightFlightService(db_repo=db_repo, crawler_repo=crawler_repo)

@router.post(
    "/search",
    response_model=FlightSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Tìm kiếm vé kết hợp DB và Crawler chuẩn phong cách Protocol"
)
async def search_best_flights(
    payload: FlightSearchRequest,
    service: FlightFlightService = Depends(get_flight_service)
):
    try:
        return await service.get_and_process_all_deals(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống: {str(e)}"
        )