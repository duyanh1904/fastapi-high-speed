import asyncio
import random
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.flight import FlightModel
from app.schemas.flight import FlightSearchRequest, FlightTicket

class FlightDBRepository:
    """Triển khai thực tế giao tiếp TiDB/MySQL sử dụng SQLAlchemy Async"""
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def find_flights_from_db(self, criteria: FlightSearchRequest) -> List[FlightModel]:
        query = select(FlightModel).where(
            FlightModel.origin == criteria.origin,
            FlightModel.destination == criteria.destination,
            FlightModel.departure_date == criteria.departure_date
        )
        result = await self.db.execute(query)
        return result.scalars().all()


class FlightCrawlerRepository:
    """Triển khai thực tế Network I/O để cào dữ liệu từ internet"""
    async def crawl_flights_from_source(self, source_name: str, search_info: FlightSearchRequest) -> List[FlightTicket]:
        # Giả lập thời gian trễ mạng khi gửi request HTTP (1s - 2s)
        await asyncio.sleep(random.uniform(1.0, 2.0))

        mock_airlines = ["Vietnam Airlines", "VietJet Air", "Bamboo Airways", "Vietravel Airlines"]
        tickets = []

        for _ in range(random.randint(3, 6)):
            price = random.randint(800000, 2500000)
            ticket = FlightTicket(
                airline=random.choice(mock_airlines),
                flight_number=f"{source_name[:2].upper()}-{random.randint(100, 999)}",
                departure_time=f"{random.randint(5, 22):02d}:{random.choice([0, 30, 45]):02d}",
                arrival_time=f"{random.randint(7, 23):02d}:00",
                price=price,
                is_best_price=price < 1200000
            )
            tickets.append(ticket)

        return tickets