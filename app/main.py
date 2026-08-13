import asyncio
from contextlib import asynccontextmanager

from .state import app
from fastapi import FastAPI
from .sensors import router as sensor_router
from .debug_router import router as debug_router
from .shelly import check_shelly
from .electricity import fetch_electricity_price, get_daily_threshold

# describes a loop for electricity price retrieval in a server-based context; not relevant in a server-inclusive context
async def electricity_price_loop():
    while True:
        try:
            price = await fetch_electricity_price()

            print(
                f"Electricity price updated: "
                f"{price.dkk_per_kwh} DKK/kWh | "
                f"({price.time_start} - {price.time_end}) | "
                f"{price.pris_inkl_vat} DKK inkl. moms"
            )

        except Exception as e:
            print(f"Electricity price update failed: {e}")

        await asyncio.sleep(300)

'''
App lifespan
Retrieves electricity price on startup and calculates lowest 25% threshold (daily threshold)
'''
@asynccontextmanager
async def lifespan(app: FastAPI):
    await check_shelly()

    try:
        app.state.threshold = await get_daily_threshold()

        print(
            f"Today's threshold: "
            f"{app.state.threshold:.5f} DKK/kWh"
        )

    except Exception as e:
        print(f"Threshold fetch failed: {e}")
        app.state.threshold = None

    try:
        price = await fetch_electricity_price()

        print(
            f"Electricity price loaded: {price.dkk_per_kwh} DKK/kWh | "
            f"({price.time_start} - {price.time_end}) | "
            f"{price.pris_inkl_vat} DKK inkl. moms"
        )

    except Exception as e:
        print(f"Electricity price fetch failed: {e}")

    price_task = asyncio.create_task(electricity_price_loop())

    try:
        yield
    finally:
        price_task.cancel()

        try:
            await price_task
        except asyncio.CancelledError:
            pass


app.router.lifespan_context = lifespan

app.include_router(sensor_router)
app.include_router(debug_router)