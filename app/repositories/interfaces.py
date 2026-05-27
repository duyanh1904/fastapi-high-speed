from typing import Protocol, List, runtime_checkable
from app.models.flight import FlightModel  # Giả định Model SQLAlchemy đã có sẵn
from app.schemas.flight import FlightSearchRequest, FlightTicket

@runtime_checkable
class FlightRepositoryInterface(Protocol):
    """Interface chịu trách nhiệm tương tác với Database hệ thống (TiDB/MySQL)"""
    async def find_flights_from_db(self, criteria: FlightSearchRequest) -> List[FlightModel]:
        ...

@runtime_checkable
class FlightCrawlerRepositoryInterface(Protocol):
    """Interface chịu trách nhiệm kết nối mạng cào dữ liệu thời gian thực bên ngoài"""
    async def crawl_flights_from_source(self, source_name: str, search_info: FlightSearchRequest) -> List[FlightTicket]:
        ...