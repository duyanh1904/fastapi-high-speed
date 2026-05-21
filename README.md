# fastapi-high-speed
fastapi-high-speed
# Run docker 
sudo docker build --no-cache -t fastapi-app:latest .

sudo docker run -d \                                                                                                  ─╯
-p 8000:8000 \
--name my-fastapi-container \
-e REDIS_URL="redis://host.docker.internal:6379/0" \
fastapi-app:latest

sudo docker logs -f my-fastapi-container

# Dock Api
http://127.0.0.1:8000/docs#/default/create_order_api_v1_orders_post