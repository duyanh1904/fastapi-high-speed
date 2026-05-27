import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

# 1. Cấu hình chuỗi kết nối Database (Database URL)
# Trong môi trường Production lớn, URL này bắt buộc phải lấy từ biến môi trường (Environment Variable)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+aiomysql://root:password@127.0.0.1:3306/flight_db"
)

# 2. Khởi tạo Async Engine
# Cấu hình Pool Connection nhằm tối ưu hóa số lượng kết nối đồng thời (High-Concurrency)
async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,                 # Chuyển thành True nếu muốn log toàn bộ câu lệnh SQL thô ra terminal để debug
    pool_size=20,               # Số lượng connection tối đa được duy trì trong pool
    max_overflow=10,            # Số lượng connection được phép vượt ngưỡng khi pool bị quá tải
    pool_recycle=3600,          # Tự động làm mới kết nối sau 1 giờ để tránh lỗi "MySQL server has gone away"
    pool_pre_ping=True          # Tự động kiểm tra trạng thái kết nối trước khi dùng để tránh gửi lệnh vào connection chết
)

# 3. Khởi tạo Factory sản xuất Session bất đồng bộ (AsyncSession)
async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,     # Giữ lại dữ liệu của Object sau khi Commit để tránh lỗi Greenlet trong Async
    autocommit=False,
    autoflush=False
)

# 4. Base Class để các tầng Model (ví dụ: FlightModel) kế thừa nhằm định nghĩa cấu trúc bảng
Base = declarative_base()

# 5. Dependency Provider: Hàm yield DB Session cho FastAPI Injector
# Hàm này tuân thủ nguyên lý quản lý tài nguyên êm đẹp (Context Manager)
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Mỗi Request từ Client đến sẽ được cấp duy nhất một DB Session độc lập.
    Sau khi API xử lý xong và trả kết quả cho User, Session sẽ tự động đóng (Close).
    """
    async with async_session_factory() as session:
        try:
            yield session
            # Nếu toàn bộ luồng xử lý ở Controller/Service không có lỗi, lệnh commit sẽ chạy ngầm (tùy chọn)
            # Hoặc bạn có thể chủ động commit tại tầng Repository/Service.
        except Exception:
            await session.rollback() # Nếu dính bất kỳ lỗi hệ thống nào, tự động hủy bỏ mọi thao tác (Rollback)
            raise
        finally:
            await session.close()     # Đảm bảo trả kết nối về Pool một cách an toàn, chống rò rỉ cổng mạng (Connection Leak)