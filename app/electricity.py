import httpx
from datetime import datetime
from zoneinfo import ZoneInfo
import os

from .database import save_electricity_price
from .models import ElectricityPrice


VAT_MULTIPLIER = 1.25
TIMEZONE = ZoneInfo("Europe/Copenhagen")

async def fetch_electricity_price():

    now = datetime.now(TIMEZONE)
    today = now.date()

    url = (
        "https://danishgrid.com/v1/electricity-price"
        f"?date={today.isoformat()}"
    )

    headers = {
        "x-api-key": os.getenv("DANISHGRID_API_KEY"),
        "User-Agent": "UserAgent/1.0"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=headers,
        )

        response.raise_for_status()
        prices = response.json()["records"]

    dk2_prices = [
        price
        for price in prices
        if price["area"] == "DK2"
    ]

    if len(dk2_prices) < 4 * 24:
        raise Exception(
            f"Expected at least 96 DK2 electricity prices for {today}, "
            f"but received {len(dk2_prices)}"
        )

    for price in dk2_prices:

        time_start = datetime.fromisoformat(
            price["startTime"]
        ).replace(tzinfo=TIMEZONE)

        time_end = datetime.fromisoformat(
            price["endTime"]
        ).replace(tzinfo=TIMEZONE)

        await save_electricity_price(
            float(price["dkkPerKwh"]),
            time_start,
            time_end,
        )

        if time_start <= now < time_end:
            current_price = ElectricityPrice(
                dkk_per_kwh=float(price["dkkPerKwh"]),
                time_start=time_start,
                time_end=time_end,
            )

    if "current_price" not in locals():
        raise Exception("No current electricity price found")

    return current_price
if __name__ == "__main__":
    import asyncio

    asyncio.run(fetch_electricity_price())