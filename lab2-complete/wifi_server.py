import socket
from util import *

HOST = "10.0.0.116" # IP address of your Raspberry PI
PORT = 65432          # Port to listen on (non-privileged ports are > 1023)

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        try:
            while 1:
                client, clientInfo = s.accept()
                command = client.recv(1024)      # receive 1024 Bytes of message in binary format
                json_data = handle_command(command)
                if json_data:
                    print(json_data)
                    # send data to client
                    client.sendall(bytes(json_data, encoding="utf-8"))
        except:
            print("Closing socket")
            client.close()
            s.close()



if __name__ == "__main__":
    try:
        main()
    finally:
        fc.stop()
