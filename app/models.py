from datetime import datetime

from pydantic import BaseModel

# contains object for sensor readings; humidity (%) and temperature (degrees C) 
class HumidityReading(BaseModel):
    humidity: float
    temperature: float

# electricity price as retrieved in a server-based context
class ElectricityPrice(BaseModel):
    dkk_per_kwh: float
    time_start: datetime
    time_end: datetime
    pris_inkl_vat: float

# electricity price as retrieved in a server-inclusive context (posted via microcomputer)
class ElectricityPriceReading(BaseModel):
    dkk_per_kwh: float
    time_start: datetime
    time_end: datetime
    pris_inkl_vat: float
    current_price: float
    threshold: float
    max_normal_electricity_price: float

# shelly state along with a reason, eg. "shelly was turned off because the humidity went below minimum threshold (45%)"
class ShellyState(BaseModel):
    state: bool
    reason: str