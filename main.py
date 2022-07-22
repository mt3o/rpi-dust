import uasyncio

from libs.dust import dust_gen
from libs.fan import fan_blink
from libs.led import led_blink


async def main_led():
    print("led.py for 60 seconds")
    t1 = uasyncio.create_task(led_blink(25))
    t2 = uasyncio.create_task(fan_blink(0))
    # uasyncio.create_task(read_analog_sensor())
    await uasyncio.sleep_ms(60_000)
    t1.cancel()
    t2.cancel()

async def pi_dust():
    print("starting pidust...")
    task_led = uasyncio.create_task(led_blink(pin=25))
    try:
        dust = dust_gen(led_pin_num=3, adc_pin_num=26)
        for _ in range(0,1000):
            print("it: ", _)
            v = dust.send(None)
            print(v)
            await uasyncio.sleep(1) #seconds
        print("end pidust.")
    finally:
        task_led.cancel()
        print("end pidust done.")

def set_network():
    import secrets
    import libs.wifi
    libs.wifi.connect(secrets.SSID, secrets.PASSWORD)
    print("wifi connected", secrets.SSID)

try:
    print("running pidust via main.py")
    uasyncio.run(pi_dust())
except KeyboardInterrupt:
    print("keyboard interrupt exception...")
