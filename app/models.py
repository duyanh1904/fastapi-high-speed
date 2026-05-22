from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class OrderModel(Base):
    __tablename__ = "orders"

    # Lưu ý: TiDB hỗ trợ AUTO_INCREMENT nhưng khuyến khích dùng SHARD_ROW_ID_BITS 
    # khi ghi dữ liệu lớn để tránh phân phối dữ liệu bị tập trung vào 1 Node (Hotspot).
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, index=True)
    item_id = Column(Integer)
    quantity = Column(Integer)
    price = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)