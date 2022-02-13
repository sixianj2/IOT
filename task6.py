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

def movesquare(speed, turnrate, timer):
    fc.forward(speed)
    simpletimer(timer)
    fc.turn_left(turnrate)
    simpletimer(1.125)
    fc.forward(speed)
    simpletimer(timer)
    fc.turn_left(turnrate)
    simpletimer(1.125)
    fc.forward(speed)
    simpletimer(timer)
    fc.turn_left(turnrate)
    simpletimer(1.125)
    fc.forward(speed)
    simpletimer(timer)
    return

if __name__ == '__main__':
    fc.stop()
    movesquare(20,18,4)
    fc.stop()

# turn set power = 1.8 and time = 1.125