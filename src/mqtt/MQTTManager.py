from binascii import hexlify
from machine import ADC, Pin
import time
from micropython import const
from src.mqtt.MQTTClient import MQTTClient
import machine
import math
import esp32


class MQTTManager:
    def __init__(self):
        self.mqtt_server = 'qeb13781-internet-facing-eafbd847ca795c9a.elb.us-east-1.amazonaws.com'
        self.client_id = hexlify(machine.unique_id())
        self.topic_sub = b'esp/32/data'
        self.topic_pub = b'esp/32/data'
        self.last_message = 0
        self.message_interval = 5

    def sub_cb(self, topic, msg):
        print((topic, msg))

    def connect_and_subscribe(self):
        client = MQTTClient(self.client_id, self.mqtt_server,
                            user='esame', password='Embedded22')
        client.set_callback(self.sub_cb)
        client.connect()
        client.subscribe(self.topic_sub)
        print('Connected to %s MQTT broker, subscribed to %s topic' %
              (self.mqtt_server, self.topic_sub))
        return client

    def restart_and_reconnect(self):
        print('Failed to connect to MQTT broker. Reconnecting...')
        time.sleep_ms(100)
        self.connect_and_subscribe()

    def service(self):
        try:
            client = self.connect_and_subscribe()
        except OSError as err:
            print(err)
            self.restart_and_reconnect()

        try:
            client.check_msg()

            while ((time.time() - self.last_message) > self.message_interval):
                msg = bytearray(self.read())
                client.publish(self.topic_pub, msg)
                self.last_message = time.time()
        except OSError as err:
            print(err)
            self.restart_and_reconnect()

    def read(self):
        x_pin_adc: ADC = ADC(Pin(const(33), Pin.IN))
        y_pin_adc: ADC = ADC(Pin(const(32), Pin.IN))
        z_pin_adc: ADC = ADC(Pin(const(35), Pin.IN))
        gx: float = 0
        gy: float = 0
        gz: float = 0
        gx_prev: float = 0
        gy_prev: float = 0
        gz_prev: float = 0
        xadc: int = 0
        yadc: int = 0
        zadc: int = 0

        max_readings = const(10)
        for _ in range(max_readings):
            xadc += x_pin_adc.read()
            yadc += y_pin_adc.read()
            zadc += z_pin_adc.read()
            time.sleep_ms(500)

        xadc = xadc / max_readings
        yadc = yadc / max_readings
        zadc = zadc / max_readings

        gx_prev = gx
        gy_prev = gy
        gz_prev = gz
        gx = (xadc - 2048) / 330.0
        gy = (yadc - 2048) / 330.0
        gz = (zadc - 2048) / 330.0

        g: float = math.sqrt(gx * gx + gy * gy + gz * gz)
        g_prev: float = math.sqrt(
            gx_prev * gx_prev + gy_prev * gy_prev + gz_prev * gz_prev)

        hall = esp32.hall_sensor()  # read the internal hall sensor
        # read the internal temperature of the MCU, in Fahrenheit
        raw_temperature = esp32.raw_temperature()
        celsius_temperature = (raw_temperature - 32) * 5/9

        return (b'xadc:{:3.2f}, yadc:{:3.2f}, zadc:{:3.2f}, g{:3.1f}, g_prev{:3.1f}, hall:{:3.1f}, celsius:{:2.1f}'.format(
            xadc, yadc, zadc, g, g_prev, hall, celsius_temperature))

    def web_page(self):
        read = bytearray(self.read()).decode("utf-8")
        read_list = read.split(",")
        html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="icon" href="data:,"></head><body><h1>ESP32 Sensor with GY-61</h1>
        <table><tr><th>MEASUREMENT</th><th>VALUE</th></tr>
        <tr><td>X</td><td><span>""" + str(read_list[0]) + """</span></td></tr>
        <tr><td>Y</td><td><span>""" + str(read_list[1]) + """</span></td></tr>
        <tr><td>Z</td><td><span>""" + str(read_list[2]) + """</span></td></tr>
        <tr><td>G</td><td><span>""" + str(read_list[3]) + """</span></td></tr>
        <tr><td>Prev G</td><td><span>""" + str(read_list[4]) + """</span></td></tr>
        <tr><td>Hall</td><td><span>""" + str(read_list[5]) + """</span></td></tr>
        <tr><td>Temp. Celsius</td><td><span>""" + str(read_list[6]) + """</span></td></tr>
        
        </body></html>"""
        return html
