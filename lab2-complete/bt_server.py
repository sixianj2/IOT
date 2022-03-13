import bluetooth
import json
import subprocess
import picar_4wd as fc

hostMACAddress = "DC:A6:32:9F:DF:6B" # The address of Raspberry PI Bluetooth adapter on the server. The server might have multiple Bluetooth adapters.
port = 0
backlog = 1



cur_dir = "stopped"

def main():
    size = 1024
    s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    s.bind((hostMACAddress, port))
    s.listen(backlog)
    print("listening on port ", port)
    try:
        client, clientInfo = s.accept()
        print("server recv from: ", clientInfo)
        while 1:
            command = client.recv(1024)      # receive 1024 Bytes of message in binary format
            json_data = handle_command(command)
            if json_data:
                print(json_data)
                # send data to client
                client.sendall(bytes(json_data, encoding="utf-8"))
            else:
                print('json data is none')

    except:
        print("Closing socket")
        client.close()
        s.close()


def handle_command(command):
    global cur_dir
    print(f'data from is: {str(command)}')

    if command == b"forward":
        # move forward
        fc.forward(30)
        set_dir('forward')
        return get_dir()
    elif command == b"backward":
        # move backward
        fc.backward(30)
        set_dir('backward')
        return get_dir()
    elif command == b"left":
        # move backward
        fc.turn_left(30)
        set_dir('left')
        return get_dir()
    elif command == b"right":
        # move backward
        fc.turn_right(30)
        set_dir('right')
        return get_dir()
    elif command == b"stop":
        # move backward
        fc.stop()
        set_dir('stopped')
        return get_dir()
    elif command == b"data":
        return get_all_car_data()
    else:
        return None



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


if __name__ == "__main__":
    try:
        main()
    finally:
        fc.stop()

