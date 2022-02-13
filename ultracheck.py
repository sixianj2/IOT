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

def get_distance_at(angle):
    servo = Servo(PWM("P0"), offset=10)
    servo.set_angle(angle)
    time.sleep(0.04)
    us = Ultrasonic(Pin('D8'), Pin('D9'))
    distance = us.get_distance()
    angle_distance = [angle, distance]
    return distance  

def checkultra(angle):
    distance = get_distance_at(angle)
    sleep(1)
    print(distance)
    checkultra(angle)
      
if __name__ == '__main__':
    angle = int(input())
    checkultra(angle)
    