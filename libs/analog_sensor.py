import machine
import uasyncio

async def read_analog_sensor():
    analog_dust_sensor = machine.ADC(26)
    while True:
        reading = analog_dust_sensor.read_u16()
        print("ADC: ", reading)
        await uasyncio.sleep_ms(500)

