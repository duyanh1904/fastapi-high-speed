# app/cron.py
import os
import asyncio
from rocketry import Rocketry
from rocketry.conds import minutely
import redis.asyncio as aioredis
import json

app_cron = Rocketry(config={"task_execution": "async"})

# 👇 TỰ ĐỘNG ĐỌC CONFIG DOCKER: Nếu có biến môi trường thì dùng, không thì dùng localhost
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CRON_CHANNEL = "cron_background_tasks"

@app_cron.task(minutely)
async def trigger_cleanup_job():
    print(f"⏰ [Cron Scheduler] Kích hoạt cấu hình dọn dẹp hệ thống định kỳ...")
    print(f"🔌 [Cron] Đang kết nối tới Redis qua địa chỉ: {REDIS_URL}")

    # Kết nối dựa trên URL động
    redis = aioredis.from_url(REDIS_URL)

    task_payload = {
        "task_type": "CLEANUP_EXPIRED_ORDERS",
        "payload": {"archive_target": "TiDB_historical_table", "batch_limit": 5000}
    }

    try:
        await redis.publish(CRON_CHANNEL, json.dumps(task_payload))
        print("📣 [Cron Scheduler] Đã phát lệnh xử lý qua Redis Pub/Sub.")
    except Exception as e:
        print(f"❌ [Cron Scheduler] Lỗi kết nối Redis: {e}")
    finally:
        await redis.close()

if __name__ == "__main__":
    app_cron.run()