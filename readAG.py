from tkinter import *
from tkinter import messagebox,ttk
import serial
import serial.tools.list_ports
import time
import datetime
import requests

meter_ser = serial.Serial(
            port='COM8',
            baudrate=9600,
            timeout=1,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            xonxoff=False
        )

meter_ser.isOpen()
resulti=""
count=0
time1 = datetime.datetime.now()

try:
    while True:
        meter_ser.write("D".encode())
        bytesToRead = meter_ser.inWaiting()
        data = meter_ser.read(bytesToRead)
        print(data)
        if len(data)>0:
            resulti = resulti + str(data).split("'")[1]
        time.sleep(0.3)
except:
    pass

f = open("data"+datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+".txt",'w')
f.write(resulti)
print(resulti)

    