from pydantic import BaseModel, Field

# 1. Schema phục vụ việc tiếp nhận dữ liệu tạo Đơn hàng từ Client gửi lên (DTO Vào)
class OrderCreate(BaseModel):
    user_id: int = Field(..., description="ID của người mua hàng")
    item_id: int = Field(..., description="ID của sản phẩm/vật phẩm")
    quantity: int = Field(..., gt=0, description="Số lượng đặt mua, phải lớn hơn 0")
    price: float = Field(..., gt=0, description="Giá của sản phẩm tại thời điểm mua")


# 2. Schema phục vụ việc chuẩn hóa dữ liệu trả về cho Client sau khi xử lý (DTO Ra)
class OrderResponse(BaseModel):
    order_id: str = Field(..., description="Mã đơn hàng duy nhất được hệ thống sinh ra")
    status: str = Field(..., description="Trạng thái đơn hàng (VD: pending, success, failed)")
    cached: bool = Field(default=False, description="Đánh dấu dữ liệu này có được lấy từ Redis Cache hay không")

    class Config:
        # Giúp Pydantic có thể tự động parse dữ liệu nếu sau này bạn chuyển
        # kết quả từ Object của SQLAlchemy Model (OrderModel) sang thẳng Schema này
        from_attributes = True