import asyncio
import httpx
import random
from app.schemas import FlightTicket, FlightSearchRequest

async def crawl_flights_from_source(source_name: str, search_info: FlightSearchRequest) -> list[FlightTicket]:
    """
    Giả lập một Worker đi cào dữ liệu từ 1 nguồn cụ thể (VD: Agoda, Traveloka, hoặc VietnamAirlines)
    """
    # Trong thực tế, bạn sẽ dùng httpx.get() để lấy HTML hoặc API Chuyến bay:
    # async with httpx.AsyncClient() as client:
    #     response = await client.get(f"https://api.example.com/flights?from={search_info.origin}...")

    # Giả lập thời gian trễ mạng (I/O Bound) khi cào dữ liệu mất từ 1 đến 2 giây
    await asyncio.sleep(random.uniform(1.0, 2.0))

    # Giả lập dữ liệu cào về được
    mock_airlines = ["Vietnam Airlines", "VietJet Air", "Bamboo Airways", "Vietravel Airlines"]
    tickets = []

    for i in range(random.randint(3, 7)):
        price = random.randint(800000, 2500000)
        ticket = FlightTicket(
            airline=random.choice(mock_airlines),
            flight_number=f"{source_name[:2].upper()}-{random.randint(100, 999)}",
            departure_time=f"{random.randint(5, 22):02d}:{random.choice([0, 15, 30, 45]):02d}",
            arrival_time=f"{random.randint(7, 23):02d}:00",
            price=price,
            is_best_price=price < 1200000  # Định nghĩa giá tốt là dưới 1.2M
        )
        tickets.append(ticket)

    return tickets