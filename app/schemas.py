from pydantic import BaseModel, Field

class OrderCreate(BaseModel):
    user_id: int
    item_id: int
    quantity: int = Field(gt=0, description="Số lượng phải lớn hơn 0")
    price: float

class OrderResponse(BaseModel):
    order_id: str
    status: str
    cached: bool