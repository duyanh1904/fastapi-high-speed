# ==========================================
# Giai đoạn 1: Build & Cài đặt thư viện
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Cài đặt các thư viện hệ thống cần cho việc compile (nếu có)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Cài đặt toàn bộ thư viện vào thư mục độc lập /install (không dùng cờ --user)
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ==========================================
# Giai đoạn 2: Tạo Image chạy thực tế (Runtime)
# ==========================================
FROM python:3.11-slim AS runner

WORKDIR /app

# Biến môi trường tối ưu cho Python trong Docker
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# COPY TOÀN BỘ thư viện và file thực thi (bao gồm cả uvicorn) vào thẳng hệ thống Global của Runner
COPY --from=builder /install /usr/local

# Copy mã nguồn ứng dụng FastAPI của bạn vào thư mục /app/app
COPY ./app ./app

# Tạo user bảo mật không có quyền root để chạy ứng dụng
RUN useradd -u 1001 fastapiuser && chown -R fastapiuser:fastapiuser /app
USER fastapiuser

EXPOSE ${PORT}

# Chạy trực tiếp uvicorn (hệ thống sẽ tự nhận diện trong /usr/local/bin)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]