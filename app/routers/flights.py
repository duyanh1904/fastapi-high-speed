import asyncio
from fastapi import APIRouter, status, HTTPException
from app.schemas import FlightSearchRequest, FlightSearchResponse
# 1. SỬA ĐOẠN IMPORT NÀY: Chỉ import hàm thực tế đang có
from app.crawler import crawl_flights_from_source

router = APIRouter(
    prefix="/api/v1/crawler",
    tags=["Flight Crawler Engine"]
)

@router.post(
    "/search",
    response_model=FlightSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Kích hoạt hệ thống cào vé máy bay giá tốt theo thời gian thực"
)
async def search_best_flights(payload: FlightSearchRequest):
    try:
        # 2. SỬA ĐOẠN GATHER NÀY: Gọi cùng 1 hàm nhưng truyền các string nguồn khác nhau
        results = await asyncio.gather(
            crawl_flights_from_source("Vietnam Airlines", payload),
            crawl_flights_from_source("VietJet Air", payload),
            crawl_flights_from_source("Bamboo Airways", payload),
            return_exceptions=True
        )

        all_tickets = []
        for src_result in results:
            if isinstance(src_result, Exception):
                print(f"⚠️ Phát hiện lỗi ở một nguồn crawler: {src_result}")
                continue
            if isinstance(src_result, list):
                all_tickets.extend(src_result)

        if not all_tickets:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy chuyến bay nào hợp lệ."
            )

        all_tickets.sort(key=lambda x: x.price)
        return FlightSearchResponse(
            search_info=payload,
            total_found=len(all_tickets),
            tickets=all_tickets
        )

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống trong quá trình vận hành crawler: {str(e)}"
        )