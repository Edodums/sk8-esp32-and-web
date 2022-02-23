from src.bleperipheral import ble
from src.mqtt.MQTTManager import MQTTManager
from src.xcar150a.EscInputState import CompletedState, IdleState, SpeedState, OnGoingState, ReadyState, StateMachine
import bluetooth
import json
import socket
import gc
try:
    import uasyncio as asyncio
except ImportError:
    try:
        import asyncio
    except ImportError:
        print("SKIP")
        raise SystemExit


def collect_garbage():
    gc.collect()


collect_garbage()

# Ble Task


def on_rx():
    if (ble_manager.any()):
        result = ble_manager.read().decode(
            'UTF-8').strip().replace("\\", "")[1:-1]

        json_parsed = """{}""".format(result)

        try:
            items = json.loads(json_parsed).items()
            for key, value, in items:
                esc_handler_task(key, value)

            print(items)
            ble_manager.write(result)
        except OSError as err:
            print("OS error: {0}".format(err))
            ble_manager.write("OS error")
        except ValueError:
            print("ValueError is not json")
            print(result)
            ble_manager.write("ValueError")
        except TypeError as err:
            print("err{err}")
            print(result)
        except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")
            ble_manager.write(f"Unexpected {err=}")
            raise


# machine state definitions start and Task
machine = StateMachine()
machine.add_state(IdleState())
machine.add_state(SpeedState())
machine.add_state(ReadyState())
machine.add_state(OnGoingState())
machine.add_state(CompletedState())


async def esc_task():
    print('ESC TASK')
    machine.go_to_state('idle')
    await asyncio.sleep_ms(100)


def esc_handler_task(key, value):
    machine.update(key=key, value=value)


# MQTT Task
async def mqtt_task():
    try:
        MQTTManager().service()
        await asyncio.sleep_ms(100)
    except OSError as err:
        print(err)


async def web_page_task():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 8080))
    s.listen(5)

    while True:
        try:
            if gc.mem_free() < 102000:
                gc.collect()
            conn, addr = s.accept()
            conn.settimeout(3.0)
            print('Got a connection from %s' % str(addr))
            request = conn.recv(1024)
            conn.settimeout(None)
            request = str(request)
            print('Content = %s' % request)
            response = MQTTManager().web_page()
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
            conn.close()
        except OSError as e:
            conn.close()
            print('Connection closed')


async def main():
    try:
        await mqtt_task()
        await esc_task()
        await web_page_task()
    except OSError as err:
        print(err)

asyncio.run(main())


try:
    _ble = bluetooth.BLE()
    ble_manager = ble.BLEManager(_ble)
    ble_manager.irq(handler=on_rx)
except BaseException as err:
    print(err)
    ble_manager.write(f"Unexpected {err=}, {type(err)=}")
except OSError as err:
    print(err)
