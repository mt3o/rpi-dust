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

        for i in range(0,25):
            try:
                # set date from the internet, or set to fixed moment
                self.rtc = machine.RTC()
                resp = urequests.request("GET", "https://rashell.pl/rpi/time.php")
                if resp.status_code == 200:
                    year, month, day, dayofweek, hour, minute, seconds = resp.text.split("\t")
                    moment = (int(year), int(month), int(day), int(dayofweek), int(hour), int(minute), int(seconds), 0)
                    print("Setting time to", moment)
                    self.rtc.datetime(moment)
                    print("Set time to", self.rtc.datetime(), 'year month day weekday hour minute seconds, mircoseconds')
                else:
                    print("setting time to fallback")
                    self.rtc.datetime((2022, 1, 1, 0,0,0,0,0))
                break #positive end
            except OSError as e:
                print("Got error while setting time, waiting for 10s and will retry",e)
                time.sleep(10)
                continue
        else:
            print("failed to set time, using fallback")
            self.rtc.datetime((2022, 2, 1,0,0,0,0,0))


        # finally clear memory
        gc.collect()

        self.autopush_task = uasyncio.create_task(self.autopush())

    def report(self, data, status=None):
        if(len(self.deq))==100:
            print('autopush queue full, dropping items')
        self.deq.append((self.rtc.datetime(), data, status))

    async def autopush(self):
        print("autopush started")
        while True:
            # print("autopush iteration")
            #Should be rewritten with MQTT
            while len(self.deq) > 0:
                now, data, status = self.deq.popleft()
                for retry in range(0, 5):  # max number of retries
                    try:
                        response = urequests.request(
                            'POST',
                            self.backend,
                            data="{}\t{}\tstatus:{}".format(now, print_DustResult(data), status),
                            headers={
                                'Content-type': 'application/text'
                            })
                        if response.status_code != 200:
                            print('response NOT ok', response.status_code, "\n", response.text)
                        gc.collect()
                        # print("autopush iter done")
                        break  # successfully pushed to the server, breaking the retry loop
                    except OSError as e:
                        print("failed to push data over network", e)
                        gc.collect()
                        continue
                    finally:
                        await uasyncio.sleep_ms(10)
            await uasyncio.sleep(0.1)


class WorldNoop:
    def __init__(self):
        pass

    async def report(self, data, *args, **kwargs):
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

    def report(self, data, status):
        self.backend.report(data, status)
