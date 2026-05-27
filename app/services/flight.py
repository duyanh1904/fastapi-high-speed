import asyncio
from typing import List
from app.repositories.interfaces import FlightRepositoryInterface, FlightCrawlerRepositoryInterface
from app.schemas.flight import FlightSearchRequest, FlightSearchResponse, FlightTicket

class FlightFlightService:
    def __init__(
        self, 
        db_repo: FlightRepositoryInterface, 
        crawler_repo: FlightCrawlerRepositoryInterface
    ):
        self.db_repo = db_repo
        self.crawler_repo = crawler_repo

    async def get_and_process_all_deals(self, payload: FlightSearchRequest) -> FlightSearchResponse:
        # 1. Chạy song song cào mạng từ 3 nguồn qua crawler_repo
        crawler_tasks = asyncio.gather(
            self.crawler_repo.crawl_flights_from_source("Vietnam Airlines", payload),
            self.crawler_repo.crawl_flights_from_source("VietJet Air", payload),
            self.crawler_repo.crawl_flights_from_source("Bamboo Airways", payload),
            return_exceptions=True
        )
        
        # 2. Đọc song song dữ liệu từ Database hệ thống qua db_repo
        db_task = self.db_repo.find_flights_from_db(payload)

        # Đợi tất cả các nguồn dữ liệu cùng hoàn thành
        crawler_results, db_flights = await asyncio.gather(crawler_tasks, db_task)

        all_tickets: List[FlightTicket] = []

        # Gộp dữ liệu cào được từ internet
        for src_result in crawler_results:
            if isinstance(src_result, list):
                all_tickets.extend(src_result)

        # Gộp dữ liệu lấy ra từ Database (Chuẩn hóa từ DB Model sang Ticket Schema)
        for db_flight in db_flights:
            all_tickets.append(
                FlightTicket(
                    airline=f"DB: {db_flight.origin}",
                    flight_number=f"DB-{db_flight.id}",
                    departure_time="00:00",
                    arrival_time="00:00",
                    price=db_flight.price,
                    is_best_price=db_flight.price < 1200000
                )
            )

        # Xử lý thuật toán nghiệp vụ: Sắp xếp giá vé từ thấp đến cao
        all_tickets.sort(key=lambda x: x.price)

        return FlightSearchResponse(
            search_info=payload,
            total_found=len(all_tickets),
            tickets=all_tickets
        )