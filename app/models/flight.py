from sqlalchemy import Column, Integer, String, Float, Date
# Import Base dùng chung từ file Core Database
from app.core.database import Base

class FlightModel(Base):
    __tablename__ = "flights"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    origin = Column(String(3), nullable=False)
    destination = Column(String(3), nullable=False)
    price = Column(Float, nullable=False)
    departure_date = Column(Date, nullable=False)