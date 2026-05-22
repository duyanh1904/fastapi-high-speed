import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DatabaseGuard")

def create_db_lifespan(engine: AsyncEngine, base_metadata, retries: int = 12, delay: int = 5):
    """
    Lifespan Guard: Đợi TiDB Server mở cổng, tự động tạo database `test` và khởi tạo bảng.
    """
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("⏳ [TiDB Guard] Đang kiểm tra kết nối tới cụm lưu trữ...")
        connected = False

        for i in range(retries):
            try:
                # Ping thử kết nối vào database 'test' mặc định
                async with engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                logger.info("✅ [TiDB Guard] Đã kết nối được tới TiDB Server!")
                connected = True
                break
            except Exception:
                logger.warning(
                    f"⚠️ [TiDB Guard] [Thử lại {i+1}/{retries}]: TiDB chưa mở cổng 4000 hoặc đang khởi động cụm. "
                    f"Đang chờ {delay} giây..."
                )
                await asyncio.sleep(delay)

        if not connected:
            logger.critical("❌ [TiDB Guard] Thất bại: Không thể kết nối tới TiDB.")
            raise RuntimeError("TiDB Cluster failed to initialize.")

        # 🚀 TỰ ĐỘNG TẠO DATABASE NẾU CHƯA CÓ
        logger.info("⚙️ [TiDB Guard] Đang kiểm tra và khởi tạo database 'test'...")
        try:
            async with engine.connect() as conn:
                # Tắt chế độ tự động bọc transaction để chạy lệnh định nghĩa data (DDL)
                await conn.execute(text("CREATE DATABASE IF NOT EXISTS test"))
                # Trỏ phiên làm việc hiện tại vào test mới tạo
                await conn.execute(text("USE test"))
            logger.info("🎉 [TiDB Guard] Khởi tạo không gian lưu trữ 'test' thành công!")
        except Exception as e:
            logger.error(f"❌ [TiDB Guard] Không thể tạo database: {e}")

        # 🚀 CHẠY ĐỒNG BỘ CẤU TRÚC BẢNG (MẪU)
        logger.info("⚙️ [TiDB Guard] Đang tự động tạo cấu trúc bảng dữ liệu...")
        try:
            async with engine.begin() as conn:
                # Ép kết nối chạy trên db mới trước khi đồng bộ model
                await conn.execute(text("USE test"))
                await conn.run_sync(base_metadata.create_all)
            logger.info("🎉 [TiDB Guard] Đồng bộ cấu trúc bảng thành công!")
        except Exception as e:
            logger.error(f"❌ [TiDB Guard] Lỗi khi tạo cấu trúc bảng: {e}")

        yield  # FastAPI App bắt đầu phục vụ các request HTTP ổn định từ đây

        # Logic dọn dẹp khi tắt app
        logger.info("🔌 Đang đóng toàn bộ kết nối cơ sở dữ liệu...")
        await engine.dispose()

    return lifespan