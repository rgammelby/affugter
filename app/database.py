import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

'''
Establishes connection to the associated database and inserts data received from Arduino and electricity price API
'''


async def get_connection():
    return await psycopg.AsyncConnection.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


async def save_humidity(percent, temperature):
    conn = await get_connection()

    async with conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO Humidity (percent, temperature)
                VALUES (%s, %s)
                """,
                (percent, temperature),
            )


async def get_latest_humidity():
    conn = await get_connection()

    async with conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT percent
                FROM Humidity
                ORDER BY timestamp DESC
                LIMIT 1
                """)

            result = await cur.fetchone()

            if result is None:
                raise Exception("No humidity readings found")

            return float(result[0])


async def get_current_electricity_price():
    conn = await get_connection()

    async with conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT DKK_per_kWh
                FROM Electricity_Prices
                WHERE NOW() >= time_start
                AND NOW() < time_end
                ORDER BY time_start DESC
                LIMIT 1
                """)

            result = await cur.fetchone()

            if result is None:
                raise Exception("No electricity price found for current time")

            return float(result[0])


async def save_electricity_price(dkk_per_kwh, time_start, time_end, pris_inkl_vat):
    conn = await get_connection()

    async with conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO Electricity_Prices
                (
                    DKK_per_kWh,
                    time_start,
                    time_end,
                    Pris_inkl_VAT
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (time_start, time_end)
                DO NOTHING
                """,
                (
                    dkk_per_kwh,
                    time_start,
                    time_end,
                    pris_inkl_vat,
                ),
            )


async def save_state(state, reason):
    conn = await get_connection()

    async with conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO Humidifier_State (state, reason)
                VALUES (%s, %s)
                """,
                (state, reason),
            )
