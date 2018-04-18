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


global vars

global pi

pi = pigpio.pi()

vars = VH()

def set_servo(num):
    cos_input = math.cos(math.radians(num))
    mid_servo = (Servo_High + Servo_Low)/2
    mid_servo_scale = Servo_High - mid_servo
    servo_input = mid_servo + (cos_input * mid_servo_scale)
    pi.set_servo_pulsewidth(Steering_Pin, servo_input)


def set_motor(servo, num):
    mid = (PWM_High + PWM_Low) / 2
    mid_scale = PWM_High - mid
    scale = (num / 100) * mid_scale
    if (math.sin(math.radians(servo)) < 0):
        scale = scale * -1

    if Invert_Motor:
        scale = scale * -1

    pi.set_servo_pulsewidth(ESC_Pin, scale + mid)

def connect_to_ws(vars):
    def on_open(ws):
        print("Logging in...")
        data = {}
        data['type'] = "Login"
        data['password'] = Server_Password
        ws.send(json.dumps(data))
        vars.status_connected = False

    def on_message(ws,message):
        data = json.loads(message)
        try:
            drive = data['drive']
            scale = data['scale']
            if isinstance(drive, type("abc")):
                drive = int(drive)
            if isinstance(scale, type("abc")):
                scale = int(scale)
            vars.append_to_array((drive, scale))
            print("Input: ", drive," ", scale)
        except KeyError:
            print("KeyError, should ignore\n")

    def on_error(ws, error):
        print("Error: ", error)

    def on_close(ws):
        vars.status_connected = True
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
        set_servo(data[0])
        set_motor(data[0], data[1])
        time.sleep(vars.get_sleep_time() / 1000)


def init_servo():
    pi.set_servo_pulsewidth(ESC_Pin, PWM_High)
    time.sleep(1)
    pi.set_servo_pulsewidth(ESC_Pin, PWM_Low)
    time.sleep(1)


def set_blinkstick():
    from blinkstick import blinkstick
    while True:
        for bs in blinkstick.find_all():
            if status_initial or status_error or status_connected:
                if status_initial:
                    try:
                        bs.blink(name="Yellow", repeats=3, delay=1000)
                    except:
                        bs.turn_off()
                if status_error:
                    try:
                        bs.blink(name="Red", repeats=3, delay=1000)
                    except:
                        bs.turn_off()
                if status_connected:
                    try:
                        bs.blink(name="Blue", repeats=3, delay=1000)
                    except:
                        bs.turn_off()
            else:
                bs.set_color(name="Green")


def set_headlights():
    while True:
        if status_initial or status_error or status_connected:
            time.sleep(1)
            GPIO.output(Headlights_Pin,GPIO.LOW)
            time.sleep(1)
            GPIO.output(Headlights_Pin,GPIO.HIGH)

if __name__ == "__main__":
    print("Main function started:\n")
    GPIO.setmode(GPIO.BCM)
    vars.status_initial = True
    if Using_Blinkstick:
        print("Blinkstick plugged in, starting...")
        blinkstick_lights_thread = threading.Thread(target=set_blinkstick, args=(vars,))
        blinkstick_lights_thread.start()
    if Headlights_Pin not False:
        print("Headlights plugged in, start...")
        headlights_thread = threading.Thread(target=set_headlights, args=(vars,))
        headlights_thread.start()
    print("Init servo function:\n")
    init_servo()
    servo_thread = threading.Thread(target=do_servos, args=(vars,))
    ws_thread = threading.Thread(target=ws_loop, args=(vars,))
    print("Starting tasks...\n")
    servo_thread.start()
    ws_thread.start()
    vars.status_initial = False
