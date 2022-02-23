import network
import esp
esp.osdebug(None)


def connect():
    ssid = 'esameembedded'
    password = 'esp32meraviglia'
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(ssid, password)
        # I'm not putting any reconnecting logic to avoid loops that causes blocking
        # My device has a poor connectiviy problem, due to that it's better to avoid
        # to handle this problem now
    print('network config:', wlan.ifconfig())


connect()