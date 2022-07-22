# minicom -o -D /dev/ttyACM0

# analog output z czujnika -> analog 0, digital input na rpi pin GPIO 26 ADC
# digital output czujnika -> GPIO 3
# wiatraczek - GPIO 0, PWM
# led wewnętrzny pin 25


import uasyncio

from machine import PWM
from machine import Pin


async def led_blink_pwm(pin, sleep_ms=1000):
    pwm = PWM(Pin(pin))
    pwm.freq(1000)
    while True:
        for duty in range(65025):
            pwm.duty_u16(duty)
            await uasyncio.sleep_ms(1)
        for duty in range(65025, 0, -1):
            pwm.duty_u16(duty)
            await uasyncio.sleep_ms(1)


async def led_blink(pin, sleep_ms=1000, print_debug=False):
    try:
        if print_debug:
            print("led blink using pin", pin)
        led = Pin(pin, Pin.OUT)
        while True:
            led.value(1)
            if print_debug:
                print("led on")
            await uasyncio.sleep_ms(sleep_ms)
            led.value(0)
            if print_debug:
                print("led off")
            await uasyncio.sleep_ms(sleep_ms)
    except Exception as e:
        print("Exception in led_blink", e)
        raise






