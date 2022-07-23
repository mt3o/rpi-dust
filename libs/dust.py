import time

import machine
import uasyncio

from collections import namedtuple

from utime import ticks_diff

DustResult = namedtuple('DustResult', ("density", "max"))


def print_DustResult(dustresult: DustResult):
    return "Density {density} ug/m3 | Max: {max_} ug/m3".format(
        density=dustresult.density,
        max_=dustresult.max
    )


def dust_gen(led_pin_num,
             adc_pin_num,
             sample_size=100,
             sampling_time=0.00028,
             sleep_time=0.01,
             voc=0.6,
             max_so_far=0,
             debug_print_each_update=True
             ):
    sleep_time = sleep_time - sampling_time
    # pin setup
    led_pin = machine.Pin(led_pin_num, machine.Pin.OUT)  # D0
    vo_pin = machine.ADC(machine.Pin(adc_pin_num))  # A0

    def calc_density(vo, k=0.5):
        nonlocal voc
        nonlocal max_so_far

        dv = vo - voc
        if dv < 0:
            dv = 0
            voc = vo
        density = dv / k * 100
        max_so_far = max(max_so_far, density)
        return density

    out = DustResult(-1, 0)

    async def updating():
        nonlocal out

        # value storage
        sumval = 0
        counter = 0

        if debug_print_each_update:
            print("starting dust scanner task")
        while True:
            try:
                led_pin.value(0)  # turn off sensor led
                # print("waiting sampling_time", sampling_time)
                await uasyncio.sleep(sampling_time)
                # print("waited sampling_time", sampling_time)

                t1 = time.ticks_ms()
                sumval += vo_pin.read_u16()  # collect the value
                counter += 1
                t2 = time.ticks_ms()
                led_pin.value(1)  # turn on sensor led
                slp = sleep_time - ticks_diff(t2, t1)
                # print("waiting sleep_time", sleep_time, "minus ticks diff", ticks_diff(t2, t1), "giving", slp)
                await uasyncio.sleep(slp)
                # print("waited sleep_time.")

                if counter < sample_size:
                    # print("not enough samples: ", counter, "should be at least", sample_size)
                    pass
                else:

                    avg = sumval / sample_size
                    volt = avg * 5 / 65535
                    density = calc_density(volt)

                    out = DustResult(
                        round(density, 2),
                        round(max_so_far, 2)
                    )
                    # finally, reset the values
                    sumval = 0
                    counter = 0
                    # print("has sample", out)

            except KeyboardInterrupt:
                break
            except Exception:
                raise
            finally:
                led_pin.value(0)

    # print("starting the generator")
    updater = uasyncio.create_task(updating())

    try:
        while True:
            # print("returning from dust gen", out)
            yield out

    except GeneratorExit:
        print("ending generator")
        updater.cancel()
