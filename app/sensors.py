from fastapi import APIRouter

from .database import (
    save_humidity,
    save_electricity_price,
    save_state,
)
from .models import (
    HumidityReading,
    ElectricityPriceReading,
    ShellyState,
)
from datetime import datetime

router = APIRouter()

'''
TODO: Rename

Hosts endpoints for retrieval of Arduino data, including hard sensor readings and electricity prices
Any changes in the state of the Shelly plug are also logged with reasoning and saved in the database
'''

@router.post("/humidity")
async def receive_humidity(data: HumidityReading):
    print(
        f"Humidity: {data.humidity}% "
        f"Temperature: {data.temperature} C "
        f"Timestamp: {datetime.now()}"
    )

    await save_humidity(data.humidity, data.temperature)

    return {"status": "ok"}


@router.post("/electricity-price")
async def receive_electricity_price(data: ElectricityPriceReading):
    print(
        f"Electricity price: {data.dkk_per_kwh:.5f} DKK/kWh "
        f"Threshold: {data.threshold:.5f} DKK/kWh "
        f"Maximum normal price: {data.max_normal_electricity_price:.5f} DKK/kWh "
        f"Period: {data.time_start} - {data.time_end}"
    )

    print(f"data.dkk_per_kwh: {data.dkk_per_kwh}")
    print(f"data.time_start: {data.time_start}")
    print(f"data.time_end: {data.time_end}")
    print(f"data.pris_inkl_vat: {data.pris_inkl_vat}")

    await save_electricity_price(
        data.dkk_per_kwh, data.time_start, data.time_end, data.pris_inkl_vat
    )

    return {"status": "ok"}


@router.post("/humidifier-state")
async def receive_humidifier_state(data: ShellyState):
    print(
        f"Humidifier: {'ON' if data.state else 'OFF'} "
        f"Reason: {data.reason} "
        f"Timestamp: {datetime.now()}"
    )

    print(f"State: {data.state}")
    print(f"Reason: {data.reason}")

    await save_state(data.state, data.reason)

    return {"status": "ok"}
