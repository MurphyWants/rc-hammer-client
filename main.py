try:
    from .Settings import *
except Exception:  # ImportError
    from Settings import *
import time
from classes import Variable_Holder as VH
import pigpio
import math
import asyncio
import websockets
import json
import threading
import RPi.GPIO as GPIO

global vars
global pi

vars = VH()
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


async def connect_to_ws():
    str = 'ws://' + domain + '/ws/' + Server_UUID + '/data/'
    print("Connecting to: ", str)
    data = {}
    data['type'] = "Login"
    data['password'] = Server_Password
    print("Connecting to server:\n")
    async with websockets.connect(str) as websocket:
        sleep(1)
        await websocket.send(json.dumps(data))
        while True:
            data = await websockets.recv()
            data = json.loads(data)
            try:
                drive = data['drive']
                scale = data['scale']
                print("Drive|Scale", drive, scale)
                vars.append_to_array((drive, scale))
            except KeyError:
                print("KeyError, should ignore\n")


async def do_servos():
    while True:
        data = VH.pop_array()
        print("Got data: ", data)
        set_servo(data[0])
        set_motor(data[0], data[1])
        time.sleep(VH.get_sleep_time() / 1000)


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
    '''servo_thread = threading.Thread(target=do_servos)
    ws_thread = threading.Thread(target=connect_to_ws)
    servo_thread.start()
    ws_thread.start()'''
    print("Set tasks...\n")
    tasks = [
        asyncio.ensure_future(connect_to_ws),
        asyncio.ensure_future(do_servos),
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
