from sqlalchemy import Column, Integer, String, Float, DateTime
import datetime
# IMPORT CHUẨN: Sử dụng Base dùng chung của hệ thống để liên kết với Engine
from app.core.database import Base

class OrderModel(Base):
    __tablename__ = "orders"

    """
    💡 Mẹo Tối ưu cho TiDB (High-Concurrency):
    TiDB hỗ trợ AUTO_INCREMENT nhưng với hệ thống chịu tải lớn, việc dùng ID tự tăng tuần tự
    có thể gây ra hiện tượng nghẽn cổ chai dữ liệu tập trung vào 1 Node (Write Hotspot).
    Trong thực tế sản xuất, bạn có thể cân nhắc chuyển trường 'id' này sang kiểu String(36)
    và sinh chuỗi ngẫu nhiên bằng UUID4, hoặc giữ nguyên kiểu Integer nhưng cấu hình thêm
    thuộc tính SHARD_ROW_ID_BITS ở tầng DB.
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, index=True, nullable=False) # Đánh index tăng tốc truy vấn đơn hàng của User
    item_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    # Sử dụng UTC để đồng bộ hóa múi giờ trên toàn bộ các cụm Cluster
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)