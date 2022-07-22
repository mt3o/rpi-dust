import uasyncio
from machine import Pin


async def fan_blink(pin, run_duration=2000, off_duration=5000, debug_messages=False):
    fan = Pin(pin, Pin.OUT)
    while True:
        if debug_messages:
            print("fan on")
        fan.value(1)
        await uasyncio.sleep_ms(run_duration)
        if debug_messages:
            print("fan off")
        fan.value(0)
        await uasyncio.sleep_ms(off_duration)
