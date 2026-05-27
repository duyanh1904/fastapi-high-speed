from collections.abc import AsyncGenerator
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from app.config import settings

# ==============================================================================
# 1. CẤU HÌNH REDIS CACHE (High-Concurrency Connection Pool)
# ==============================================================================

# Khởi tạo Connection Pool dùng chung cho Redis để tối ưu hóa số lượng kết nối tái sử dụng
redis_pool = aioredis.ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=100,       # Giới hạn tối đa 100 kết nối đồng thời tới Redis Server
    decode_responses=True,      # Tự động giải mã bytes thành String khi đọc/ghi data
)

def get_redis_client() -> aioredis.Redis:
    """
    Dependency Provider trả về một thực thể Redis Client từ Pool.
    Có thể sử dụng trực tiếp qua Depends() tại tầng Controller hoặc Service.
    """
    return aioredis.Redis(connection_pool=redis_pool)


# ==============================================================================
# 2. CẤU HÌNH SQL DATABASE (Async Engine & Session cho TiDB / MySQL)
# ==============================================================================

# Khởi tạo Async Engine kết nối Database với các tham số tối ưu chịu tải cao
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,                 # Chuyển thành True khi cần debug, log toàn bộ SQL thô ra terminal
    pool_size=20,               # Số lượng kết nối tối đa được duy trì trong Pool
    max_overflow=10,            # Số lượng kết nối cho phép vượt ngưỡng khi hệ thống bị quá tải
    pool_recycle=3600,          # Tự động làm mới kết nối sau 1 giờ để tránh rớt socket (MySQL timeout)
    pool_pre_ping=False          # Kiểm tra trạng thái kết nối trước khi gửi câu lệnh SQL nhằm tránh lỗi connection chết
)

# Nhà máy (Factory) sản xuất các phiên làm việc bất đồng bộ (AsyncSession)
async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,     # Tránh lỗi Greenlet trong Async khi cố truy cập thuộc tính object sau khi commit
    autocommit=False,
    autoflush=False
)

# Base Class để các tầng Model (OrderModel, FlightModel) kế thừa định nghĩa cấu trúc bảng vật lý
Base = declarative_base()


# ==============================================================================
# 3. DEPENDENCY INJECTION PROVIDERS FOR FASTAPI
# ==============================================================================

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Quản lý vòng đời (Lifecycle) kết nối DB cho mỗi HTTP Request:
    - Cấp duy nhất một Session độc lập khi Request đi vào hệ thống.
    - Tự động hủy bỏ (Rollback) toàn bộ giao dịch nếu xảy ra lỗi ngầm ở Service/Controller.
    - Đảm bảo đóng Session (Close) an toàn để trả kết nối về Pool, chống Connection Leak.
    """
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()