import bluetooth
import json
host = "DC:A6:32:9F:DF:6B" # The address of Raspberry PI Bluetooth adapter on the server.
port = 1

def main():
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((host, port))
    print("listening on port ", port)
    while 1:
        text = input("Enter your command to Pi car: ")  # Note change to the old (Python 2) raw_input
        if text == "quit":
            break
        sock.send(text)
        data = sock.recv(1024)
        print_data(data)
    sock.close()


def print_data(raw_data):
    print("printing data")
    data = raw_data.decode("utf-8")
    print(f'data from server is {data}')

if __name__ == "__main__":
    try:
        main()
    finally:
        pass

