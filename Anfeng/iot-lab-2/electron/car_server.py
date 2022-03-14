import socket
import movecontrol as mc
import sys
import _thread
import time

HOST = "192.168.0.125" # IP address of your Raspberry PI
PORT = 65432          # Port to listen on (non-privileged ports are > 1023)
GlobalMove = False
Movedirect = ""

def print_time( threadName, delay):
   count = 0
   while count < 5:
      time.sleep(delay)
      count += 1
      print ("%s: %s" % ( threadName, time.ctime(time.time()) ))

def receivemsg(threadName):
    global GlobalMove
    global Movedirect
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        try:
            while 1:
                client, clientInfo = s.accept()
                print("server recv from: ", clientInfo)
                data = client.recv(1024)      # receive 1024 Bytes of message in binary format
                data2 = data[:len(data)-2]
                if data2 == b"87":
                    GlobalMove = True
                    Movedirect = "87"
                elif data2 == b"83":
                    GlobalMove = True
                    Movedirect = "83"
                elif data2 == b"65":
                    GlobalMove = True
                    Movedirect = "65"
                elif data2 == b"68":
                    GlobalMove = True
                    Movedirect = "68"
                else:
                    GlobalMove = False
                    Movedirect = ""
                if data != b"":
                    print(data)     
                    client.sendall(data) # Echo back to client
        except: 
            print("Closing socket")
            print(sys.exc_info()[0])
            client.close()
            s.close()   

def movecar(threadName):
    global GlobalMove
    global Movedirect
    try:
        while 1:
            if GlobalMove == False or Movedirect == "":
                continue
            elif Movedirect == "87":
                mc.moveforward()
                GlobalMove = False
                Movedirect = ""
            elif Movedirect == "83":
                mc.movebackward()
                GlobalMove = False
                Movedirect = ""
            elif Movedirect == "65":
                mc.turnleft()
                GlobalMove = False
                Movedirect = ""
            elif Movedirect == "68":
                mc.turnright()
                GlobalMove = False
                Movedirect = ""
    except:
        return 

try:
    _thread.start_new_thread( receivemsg, ("Thread-1",))
    _thread.start_new_thread( movecar, ("Thread-2",))
except:
   print(sys.exc_info())
   print("can's start")

while 1:
    pass