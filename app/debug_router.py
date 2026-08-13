from fastapi import APIRouter

from .database import (
    save_state,
    get_latest_humidity,
    get_current_electricity_price,
)
from .controller import check_humidity
from .shelly import set_state


router = APIRouter(prefix="/debug")

'''
Endpoints for debugging
Each test is described in `tests.py`
Called from venv with 'python -m app.tests <test> <value>'
'''

@router.post("/test/high_price")
async def test_high_price():
    humidity = await get_latest_humidity()

    result = await check_humidity(
        humidity=humidity,
        electricity_price=100,
    )

    return result


@router.post("/test/low_price")
async def test_low_price():
    humidity = await get_latest_humidity()

    result = await check_humidity(
        humidity=humidity,
        electricity_price=0.10,
    )

    return result

@router.post("/test/humidity/{val}")
async def test_low_price(val: int):
    electricity_price = await get_current_electricity_price()
    humidity = val

    result = await check_humidity(
        humidity=humidity,
        electricity_price=electricity_price,
    )

    return result

@router.post("/test/price/{val}")
async def test_low_price(val: float):
    electricity_price = val
    humidity = await get_latest_humidity()

    result = await check_humidity(
        humidity=humidity,
        electricity_price=electricity_price,
    )

    return result

@router.post("/test/custom/{hum}/{price}")
async def test_custom(hum: int, price: float):
    result = await check_humidity(
        humidity=hum,
        electricity_price=price,
    )

    return result


@router.post("/test/high_humidity")
async def test_high_humidity():
    electricity_price = await get_current_electricity_price()

    result = await check_humidity(
        humidity=100,
        electricity_price=electricity_price,
    )

    return result


@router.post("/test/low_humidity")
async def test_low_humidity():
    electricity_price = await get_current_electricity_price()

    result = await check_humidity(
        humidity=0,
        electricity_price=electricity_price,
    )

    return result


@router.post("/test/real")
async def test_real():
    humidity = await get_latest_humidity()
    electricity_price = await get_current_electricity_price()

    result = await check_humidity(
        humidity=humidity,
        electricity_price=electricity_price,
    )

    return result


@router.post("/test/on")
async def test_on():
    if await set_state(True):
        await save_state(True, "Testing")
        return {"status": "ok"}

    return {"status": "failed"}


@router.post("/test/off")
async def test_off():
    if await set_state(False):
        await save_state(False, "Testing")
        return {"status": "ok"}

    return {"status": "failed"}