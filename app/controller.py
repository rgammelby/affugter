from .shelly import set_state, get_state
from .database import save_state, get_latest_humidity, get_current_electricity_price
from .electricity import get_daily_threshold
from .state import app

'''
The controller plays different roles in a server-included or a server-based context.
Server-included: check_humidity runs once on startup. After this point, the server receives its readouts exclusively from the associated microcomputer.
Server-based: The server runs its own loop, calling price API and receiving humidity readouts only from the associated microcomputer. 
'''

MIN_HUMIDITY = 45
MAX_HUMIDITY = 55
EMERGENCY_THRESHOLD = 70

async def check_humidity(humidity, electricity_price):

    threshold = app.state.threshold

    current_state = await get_state()
    desired_state = current_state

    # humidity is below emergency threshold, operates normally
    if humidity < EMERGENCY_THRESHOLD and humidity > MIN_HUMIDITY:
        desired_state = electricity_price <= threshold

    # humidity is above emergency threshold and runs regardless of price
    if humidity >= EMERGENCY_THRESHOLD:
        desired_state = True

    # humidity is below minimum threshold and switches off
    if humidity <= MIN_HUMIDITY:
        desired_state = False

    print(
        f"Humidity: {humidity}% | "
        f"Electricity: {electricity_price} DKK/kWh | "
        f"Threshold: {threshold} DKK/kWh | "
        f"Current state: {'ON' if current_state else 'OFF'} | "
        f"Desired state: {'ON' if desired_state else 'OFF'}"
    )

    reason = ""

    # if desired_state != current_state:

    if humidity >= MAX_HUMIDITY:
        if electricity_price <= threshold:
            desired_state = True
            reason = (
                f"Humidity {humidity}% above maximum threshold and "
                f"electricity price {electricity_price} DKK/kWh "
                f"is below threshold {threshold} DKK/kWh"
            )
        else:
            desired_state = False
            reason = (
                f"Humidity {humidity}% above maximum threshold but "
                f"electricity price {electricity_price} DKK/kWh "
                f"is above threshold {threshold} DKK/kWh"
            )

    if humidity >= EMERGENCY_THRESHOLD:
        desired_state = True
        reason = (
            f"Emergency threshold crossed: humidity {humidity}% >= "
            f"{EMERGENCY_THRESHOLD}%"
        )

    if humidity <= MIN_HUMIDITY:
        desired_state = False
        reason = (
            f"Humidity {humidity}% below minimum threshold "
            f"{MIN_HUMIDITY}%"
        )

    print("Changing Shelly state...")

    if await set_state(desired_state):
        await save_state(desired_state, reason)

        print(f"TURNED {'ON' if desired_state else 'OFF'}: {reason}")
    else:
        print("Failed to change Shelly state")

    return {
        "humidity": humidity,
        "electricity_price": electricity_price,
        "threshold": threshold,
        "reason" : reason,
    }
