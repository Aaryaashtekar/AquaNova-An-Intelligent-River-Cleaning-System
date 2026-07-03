import serial
import time

ser = serial.Serial('/dev/ttyACMO',9600,timeout=1)

time.sleep(2)

while True:
    cmd= input("Enter Command")

    if cmd:
        ser.write((cmd+"\n").encode())
        print("Sent:", cmd)