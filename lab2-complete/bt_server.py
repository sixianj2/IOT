import bluetooth
from util import *
hostMACAddress = "DC:A6:32:9F:DF:6B" # The address of Raspberry PI Bluetooth adapter on the server. The server might have multiple Bluetooth adapters.
port = 0
backlog = 1

def main():
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


if __name__ == "__main__":
    try:
        main()
    finally:
        fc.stop()

