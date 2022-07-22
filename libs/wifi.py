import network

def connect(ssid, password):
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(ssid, password)
    while not station.isconnected():
        print("Connecting...")
    print("WIFI Connected.")
    print(station.ifconfig())
