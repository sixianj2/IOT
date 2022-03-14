import picar_4wd as fc
import sys
import tty
import termios
import math
import asyncio
import time
from picar_4wd.servo import Servo
from picar_4wd.pwm import PWM
from picar_4wd.pin import Pin
from picar_4wd.ultrasonic import Ultrasonic
import numpy as np
from time import sleep

def simpletimer(timer):
    starttime = time.time()
    while time.time() < starttime + timer:
        continue
    return

def moveforward():
    return move(fc.forward, 20, 0.1)

def movebackward():
    return move(fc.backward, 20, 0.1)


def turnleft():
    return move(fc.turn_left, 18, 0.1)


def turnright():
    return move(fc.turn_right, 18, 0.1)

def move(func, speed, duration):
    """ make the move based on speed and duration and return the distance travelled"""
    speed4 = fc.Speed(25)
    speed4.start()
    func(speed)
    return None
# turn set power = 1.8 and time = 1.125