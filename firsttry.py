import picar_4wd as fc
import sys
import tty
import termios
import asyncio

power_val = 50
key = 'status'
print("If you want to quit.Please press q")
def Keyborad_control():
    while True:
        global power_val
        key=readkey()
        if key=='6':
            if power_val <=90:
                power_val += 10
                print("power_val:",power_val)
        elif key=='4':
            if power_val >=10:
                power_val -= 10
                print("power_val:",power_val)
        if key=='w':
            fc.forward(power_val)
        elif key=='a':
            fc.turn_left(power_val)
        elif key=='s':
            fc.backward(power_val)
        elif key=='d':
            fc.turn_right(power_val)
        else:
            fc.stop()
        if key=='q':
            print("quit")  
            break  
if __name__ == '__main__':
    Keyborad_control()