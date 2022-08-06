import machine
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


# pwm12.freq(500)
# pwm12.duty(512)
# Note that the duty cycle is
# between 0 (all off) and 1023 (all on),
# with 512 being a 50% duty.
# Values beyond this min/max will be clipped.
# If you print the PWM object then it will tell you its current configuration:
# pwm12
# PWM(12, freq=500, duty=512)


def fan_pwm(pin, freq=512, duty=65536):
    fan_pin = Pin(pin, Pin.OUT)
    fan = machine.PWM(fan_pin)
    fan.freq(freq)
    fan.duty_u16(duty)
