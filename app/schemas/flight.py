from pydantic import BaseModel, Field
from datetime import date
from typing import List

# Dữ liệu khách hàng truyền lên để tìm kiếm
class FlightSearchRequest(BaseModel):
    origin: str = Field(..., max_length=3, min_length=3, example="HAN")
    destination: str = Field(..., max_length=3, min_length=3, example="SGN")
    departure_date: date

# Dữ liệu chuẩn hóa trả về cho khách hàng
class FlightResponse(BaseModel):
    id: int
    origin: str
    destination: str
    price: float
    departure_date: date

# Cấu trúc một chiếc vé máy bay thu thập được từ bot crawler
class FlightTicket(BaseModel):
    airline: str
    flight_number: str
    departure_time: str
    arrival_time: str
    price: float
    is_best_price: bool

# Cấu trúc dữ liệu phản hồi cuối cùng của API
class FlightSearchResponse(BaseModel):
    search_info: FlightSearchRequest
    total_found: int
    tickets: List[FlightTicket]

class Config:
    from_attributes = True  # Cho phép Pydantic đọc data từ SQLAlchemy Model