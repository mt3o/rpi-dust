import machine
import uasyncio


class DustResult:
    def __init__(self):
        self.density = -1
        self.mv = 0
        self.voc = 0
        self.max = 0
        self.fresh = True

    def __str__(self):
        return "{mv} mV / {density} ug/m3 (Voc={voc}) | Max: {max_} ug/m3 Fresh: {fresh}".format(
            mv=self.mv,
            density=self.density,
            voc=self.voc,
            max_=self.max,
            fresh=self.fresh
        )


def dust_gen(led_pin_num,
             adc_pin_num,
             sample_size=100,
             sampling_time=0.00028,
             delta_time=0.00004,
             sleep_time=0.00968,
             voc=0.6,
             max_so_far=0,
             debug_print_each_update=True
             ):

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

    out = DustResult()
    out.density = -1
    out.mv = 0
    out.voc = -1
    out.max = -1
    out.fresh = False

    async def updating():
        nonlocal out
        vals = []
        if debug_print_each_update:
            print("starting dust scanner task")
        while True:
            try:
                led_pin.value(0)  # turn off sensor led
                await uasyncio.sleep(sampling_time)
                vals.append(vo_pin.read_u16())  # collect the value
                await uasyncio.sleep(delta_time)
                led_pin.value(1)  # turn on sensor led
                await uasyncio.sleep(sleep_time)

                if len(vals) < sample_size:
                    #print("not enough samples: ", len(vals), "should be at least", sample_size)
                    pass
                else:
                    avg = sum(vals) / len(vals)
                    volt = avg * 3.3 / 65535
                    density = calc_density(volt)
                    mv = volt * 1000

                    out = DustResult()
                    out.density = round(density, 2)
                    out.mv = mv
                    out.voc = voc
                    out.max = max_so_far
                    out.fresh = True

                    # if debug_print_each_update:
                    #     print("collected so far", out)
                    vals = []
                    # if debug_print_each_update:
                    #     print("dust scan done.")
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
            out.fresh = False

    except GeneratorExit:
        print("ending generator")
        updater.cancel()
