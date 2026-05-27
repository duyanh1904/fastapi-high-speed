from fastapi import APIRouter
from app.routers import flights

api_router = APIRouter(prefix="/api/v1")
# Đăng ký cụm API flight vào hệ thống tổng
api_router.include_router(flights.router, prefix="/flights", tags=["Flights Application"])