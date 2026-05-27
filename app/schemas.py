from pydantic import BaseModel, Field
from datetime import date
from typing import List

class OrderCreate(BaseModel):
    user_id: int
    item_id: int
    quantity: int = Field(gt=0, description="Số lượng phải lớn hơn 0")
    price: float

class OrderResponse(BaseModel):
    order_id: str
    status: str
    cached: bool

# Thông tin user gửi lên để yêu cầu tìm vé
class FlightSearchRequest(BaseModel):
    origin: str = Field(..., max_length=3, description="Mã sân bay đi (VD: HAN, SGN)")
    destination: str = Field(..., max_length=3, description="Mã sân bay đến (VD: DAD, CXR)")
    departure_date: date = Field(..., description="Ngày bay (YYYY-MM-DD)")

# Cấu trúc một chiếc vé máy bay thu thập được
class FlightTicket(BaseModel):
    airline: str = Field(..., description="Tên hãng hàng không")
    flight_number: str = Field(..., description="Số hiệu chuyến bay")
    departure_time: str = Field(..., description="Giờ cất cánh")
    arrival_time: str = Field(..., description="Giờ hạ cánh")
    price: float = Field(..., description="Giá vé (VNĐ)")
    is_best_price: bool = Field(False, description="Đánh dấu nếu đây là vé giá tốt")

# Danh sách kết quả trả về
class FlightSearchResponse(BaseModel):
    search_info: FlightSearchRequest
    total_found: int
    tickets: List[FlightTicket]