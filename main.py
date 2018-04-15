try:
    from .Settings import *
except Exception:  # ImportError
    from Settings import *
import time
from classes import Variable_Holder as VH
import pigpio
import math
import asyncio
import websocket
import json
import threading
import RPi.GPIO as GPIO

global pi

pi = pigpio.pi()


def set_servo(num):
    cos_input = math.cos(math.radians(num))
    servo_input = 1500 + (cos_input * 950)
    pi.set_servo_pulsewidth(Steering_Pin, servo_input)


def set_motor(servo, num):
    mid = (PWM_High + PWM_Low) / 2
    mid_scale = PWM_High - mid
    scale = (num / 100) * mid_scale
    if (math.sin(math.radians(servo)) < 0):
        scale = scale * -1
    pi.set_servo_pulsewidth(ESC_Pin, scale + mid)

def connect_to_ws(vars):
    def on_open(ws):
        print("Logging in...")
        data = {}
        data['type'] = "Login"
        data['password'] = Server_Password
        ws.send(json.dumps(data))

    def on_message(ws,message):
        data = json.loads(message)
        try:
            drive = data['drive']
            scale = data['scale']
            print("Drive|Scale", drive, scale)
            vars.append_to_array((drive, scale))
        except KeyError:
            print("KeyError, should ignore\n")

    def on_error(ws, error):
        print("Error: ", error)

    def on_close(ws):
        print("WS, closed")

    str = 'ws://' + domain + '/ws/' + Server_UUID + '/data/'
    print("Connecting to: ", str)
    ws = websocket.WebSocketApp(str,
        on_message = on_message,
        on_error = on_error,
        on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()

def ws_loop(vars):
    while True:
        connect_to_ws(vars)

def do_servos(vars):
    while True:
        data = vars.pop_array()
        print("Got data: ", data)
        set_servo(data[0])
        set_motor(data[0], data[1])
        time.sleep(vars.get_sleep_time() / 1000)


def init_servo():
    pi.set_servo_pulsewidth(ESC_Pin, PWM_High)
    time.sleep(1)
    pi.set_servo_pulsewidth(ESC_Pin, PWM_Low)
    time.sleep(1)


if __name__ == "__main__":
    print("Main function started:\n")
    GPIO.setmode(GPIO.BCM)
    print("Init servo function:\n")
    init_servo()
    vars = VH()
    servo_thread = threading.Thread(target=do_servos, args=(vars,))
    ws_thread = threading.Thread(target=ws_loop, args=(vars,))
    print("Starting tasks...\n")
    servo_thread.start()
    ws_thread.start()
