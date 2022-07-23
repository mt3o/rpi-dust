import network
import time

import uasyncio
import urequests
import gc
import machine

from collections import deque

from libs.dust import print_DustResult

socket_delay_ms = 50


class World():
    def __init__(self, backend):
        self.backend = backend
        self.deq = deque((), 100)

        # set date from the internet, or set to fixed moment
        self.rtc = machine.RTC()
        resp = urequests.request("GET", "https://rashell.pl/rpi/time.php")
        if resp.status_code == 200:
            year, month, day, hour, minute, seconds = resp.text.split("\t")
            moment = (int(year), int(month), int(day), int(hour), int(minute), int(seconds), 0, 0)
            print("Setting time to", moment)
            self.rtc.datetime(moment)
            print("Set time to", self.rtc.datetime()[0:3],'year month day weekday hour minute seconds, mircoseconds, nanosecs')
        else:
            self.rtc.datetime((2022, 1, 1))

        # finally clear memory
        gc.collect()

        self.autopush_task = uasyncio.create_task(self.autopush())

    def report(self, data):
        self.deq.append((self.rtc.datetime(), data))

    async def autopush(self):
        while True:
            while len(self.deq) > 0:
                now, data = self.deq.popleft()
                for retry in range(0, 5):  # max number of retries
                    try:
                        response = urequests.request(
                            'POST',
                            self.backend,
                            data="{}\t{}".format(now, print_DustResult(data)),
                            headers={
                                'Content-type': 'application/text'
                            })
                        if response.status_code != 200:
                            print('response NOT ok', response.status_code, "\n", response.text)
                        gc.collect()
                        break  # successfully pushed to the server, breaking the retry loop
                    except OSError as e:
                        print("failed to push data over network", e)
                        gc.collect()
                        continue
                    finally:
                        await uasyncio.sleep_ms(100)
            await uasyncio.sleep(1)


class WorldNoop:
    def __init__(self):
        pass

    async def report(self, data):
        pass


class Connect:
    def __init__(self, ssid, password, server, max_attempts=5, delay_secs=1000):
        self.station = network.WLAN(network.STA_IF)
        self.station.active(True)
        self.station.connect(ssid, password)
        print("Connecting...")
        for _ in range(0, max_attempts):
            if self.station.isconnected():
                print("WIFI Connected.")
                print(self.station.ifconfig())
                self.backend = World(server)
                break
            time.sleep(delay_secs)
        else:
            self.backend = WorldNoop()
            print("Failed to connect")

    def is_connected(self):
        return self.station.isconnected()

    def report(self, data):
        self.backend.report(data)
