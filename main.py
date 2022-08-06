import uasyncio

from libs.dust import dust_gen
from libs.fan import fan_blink, fan_pwm
from libs.led import led_blink
from libs.wifi import Connect

from machine import Pin


async def main_led():
    print("led.py for 60 seconds")
    t1 = uasyncio.create_task(led_blink(25))
    t2 = uasyncio.create_task(fan_blink(0))
    # uasyncio.create_task(read_analog_sensor())
    await uasyncio.sleep_ms(60_000)
    t1.cancel()
    t2.cancel()


async def pi_dust(
        backend,
        cycle_delay_secs=10,
        on_threshold=100,
        off_threshold=100,
        above_threshold=None,
        below_threshold=None
):
    print("starting pidust...")

    try:
        toggle_state = False
        dust = dust_gen(led_pin_num=3, adc_pin_num=26)
        while True:
            # print("it: ", _)
            v = dust.send(None)
            if toggle_state == False and v.density >= on_threshold and above_threshold:
                above_threshold(v.density)
                toggle_state = True

            if toggle_state == True and v.density < off_threshold and below_threshold:
                below_threshold(v.density)
                toggle_state = False

            backend.report(v, toggle_state)
            print("reported", v)
            await uasyncio.sleep(cycle_delay_secs)  # seconds
    finally:
        print("end pidust done.")


def set_network():
    import secrets
    import libs.wifi
    libs.wifi.connect(secrets.SSID, secrets.PASSWORD)
    print("wifi connected", secrets.SSID)


def main():
    try:
        print("running pidust via main.py")
        import secrets
        uasyncio.create_task(led_blink(pin=25, sleep_ms=300))
        fan_pwm(0)
        uasyncio.create_task(led_blink(pin=25, sleep_ms=500))
        backend = Connect(secrets.SSID, secrets.PASSWORD, 'http://rashell.pl/rpi/index.php')
        uasyncio.create_task(led_blink(pin=25, sleep_ms=1000))

        relay = Pin(10, Pin.OUT)
        def enable(threshold=None):
            relay.value(1)
            print("enabling", threshold)
        def disable(threshold=None):
            relay.value(0)
            print("disabling", threshold)

        uasyncio.run(pi_dust(
            backend,
            cycle_delay_secs=10,
            on_threshold=70,
            off_threshold=55,
            above_threshold=enable,
            below_threshold=disable
        ))
    except KeyboardInterrupt:
        print("keyboard interrupt exception...")


main()
