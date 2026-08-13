import httpx
from datetime import datetime, date
from zoneinfo import ZoneInfo

from .database import save_electricity_price
from .models import ElectricityPrice
import math

'''
Runs on startup and retrieves electricity price data
Retrieves price for current 24 hour period and calculates lowest 25% of prices
'''

VAT_MULTIPLIER = 1.25
TIMEZONE = ZoneInfo("Europe/Copenhagen")

async def get_daily_threshold(area="DK2", percentile=0.25):
    today = date.today()

    url = (
        f"https://www.elprisenligenu.dk/api/v1/prices/"
        f"{today:%Y/%m-%d}_{area}.json"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        prices = response.json()

    values = sorted(price["DKK_per_kWh"] for price in prices)

    count = max(1, math.ceil(len(values) * percentile))
    return values[count - 1]


async def fetch_electricity_price():

    now = datetime.now(TIMEZONE)

    url = (
        f"https://www.elprisenligenu.dk/api/v1/prices/"
        f"{now.year}/{now.month:02d}-{now.day:02d}_DK2.json"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    response.raise_for_status()

    prices = response.json()

    current_time = datetime.now(TIMEZONE)

    for price in prices:
        time_start = datetime.fromisoformat(price["time_start"])
        time_end = datetime.fromisoformat(price["time_end"])

        if time_start <= current_time < time_end:

            electricity_price = ElectricityPrice(
                dkk_per_kwh=float(price["DKK_per_kWh"]),
                time_start=time_start,
                time_end=time_end,
                pris_inkl_vat=float(price["DKK_per_kWh"]) * VAT_MULTIPLIER,
            )

            await save_electricity_price(
                electricity_price.dkk_per_kwh,
                electricity_price.time_start,
                electricity_price.time_end,
                electricity_price.pris_inkl_vat,
            )

            return electricity_price

    raise Exception("No current electricity price found")


if __name__ == "__main__":
    import asyncio

    asyncio.run(fetch_electricity_price())
