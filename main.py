from .Settings import *
import time
from classes import Variable_Holder as VH
import pigpio
import math
import asyncio
import websockets
import json
import threading


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


def connect_to_ws():
    async def connect():
        str = 'ws://' + domain + '/ws/' + Server_UUID + '/data/'
        data = {}
        data['type'] = "Login"
        data['password'] = Server_Password

        async with websockets.connect(str) as websocket:
            sleep(1)
            await websocket.send(json.dumps(data))
            while True:
                data = await websockets.recv()
                data = json.loads(data)
                try:
                    drive = data['drive']
                    scale = data['scale']
                except KeyError:
                    print("KeyError, should ignore\n")
                vars.append_to_array((drive, scale))
    asyncio.get_event_loop().run_until_complete(connect())


def do_servos():
    while True:
        data = VH.pop_array()
        set_servo(data[0])
        set_motor(data[0], data[1])
        time.sleep(VH.get_sleep_time() / 1000)


def init_servo():
    pi.set_servo_pulsewidth(ESC_Pin, setting.PWM_High)
    time.sleep(1)
    pi.set_servo_pulsewidth(ESC_Pin, setting.PWM_Low)
    time.sleep(1)


def main():
    GPIO.setmode(GPIO.BCM)
    init_servo()
    global vars
    vars = VH()
    global pi
    pi = pigpio.pi()
    servo_thread = threading.Thread(target=do_servos)
    servo_thread = threading.Thread(target=connect_to_ws)


if __name__ == "__main__":
    main()
