import picar_4wd as fc
import json
import subprocess

cur_dir = "stopped"
speed = 10


def handle_command(command):
    global cur_dir
    print(f'data from client is: {str(command)}')

    if command == b"forward":
        # move forward
        fc.forward(speed)
        set_dir('forward')
        return get_dir()
    elif command == b"backward":
        # move backward
        fc.backward(speed)
        set_dir('backward')
        return get_dir()
    elif command == b"left":
        # move left
        fc.turn_left(speed)
        set_dir('left')
        return get_dir()
    elif command == b"right":
        # move right
        fc.turn_right(speed)
        set_dir('right')
        return get_dir()
    elif command == b"stop":
        # stop
        fc.stop()
        set_dir('stopped')
        return get_dir()
    elif command == b"data":
        return get_all_car_data()
    else:
        return get_dir()


def set_dir(dir):
    global cur_dir
    cur_dir = dir


def get_dir():
    global cur_dir
    return cur_dir


def get_all_car_data():
    data = {
        'direction': get_dir(),
        'temperature': get_temperature(),
        'battery_level': power_read()
    }

    json_data = json.dumps(data)
    return json_data


def power_read():
    """ reference: picar_4wd library """
    from picar_4wd.adc import ADC
    power_read_pin = ADC('A4')
    power_val = power_read_pin.read()
    power_val = power_val / 4095.0 * 3.3
    # print(power_val)
    power_val = power_val * 3
    power_val = round(power_val, 2)
    return power_val


def get_temperature():
    """ reference: picar_4wd library """
    raw_cpu_temperature = subprocess.getoutput("cat /sys/class/thermal/thermal_zone0/temp")
    cpu_temperature = round(float(raw_cpu_temperature)/1000, 2)               # convert unit
    #cpu_temperature = 'Cpu temperature : ' + str(cpu_temperature)
    return cpu_temperature
