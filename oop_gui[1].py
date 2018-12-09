import tkinter as tk
import datetime
import os
import os.path
import csv
import base64
from tkinter import Canvas
from tkinter import *
from tkinter import ttk
from functools import partial
from PIL import Image
from PIL import ImageTk
import http.client, urllib
import pandas as pd
import minimalmodbus,serial
import struct
from time import sleep
from time import clock
import time
import RPi.GPIO as gpio
import Adafruit_ADS1x15
import numpy as np
import threading,queue
import logging
import subprocess
import picamera
global adc_value
import json
##from google.cloud import pubsub_v1
##from oauth2client.client import GoogleCredentials
from tendo import singleton
import serial
import os, time
from escpos.printer import Usb
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

EMAIL = 'rajiangasfield@gmail.com'
PASSWORD = '13oct1994'

TO_EMAIL = 'rajian@egas.com.pk'


subprocess.call("sudo chmod 777 -R /home/pi/Dekstop/dispenser/data/", shell = True)
subprocess.call("sudo chmod 777 /home/pi/Desktop/dispenser/defaults.csv", shell = True)
##setting up gsm module
port = serial.Serial("/dev/ttyAMA0", baudrate = 115200, timeout = 1)
try:
    p = Usb(0x0483,0x5743, 0, 0x82, 0x01)
except:
    print('NO PRINTER')
##numbers = ["+923335101020", "+923422343434", "+923335344279", "+923225102421"]
numbers = ["+923335344279","+923422343434","+923235101094","+923335101020","+923225102421"]
##numbers = ["+923246426268", "+923335344279"]

last_check = 0
data_send = 1

##try:    
adc = Adafruit_ADS1x15.ADS1115(address = 0x4a)
GAIN = 1
##adc variables
adc_read1 = 0
adc_read2 = 0
adc_read3 = 0
adc_read4 = 0
offset = 6400

##except:
##    master_warning= "NO ADC DETECTED"

#initializing pins
gpio.setwarnings(False)
gpio.setmode(gpio.BCM)

gpio.setup(10, gpio.OUT, initial = gpio.HIGH)
#sen1_max
output_sen1_max = 26
gpio.setup(output_sen1_max, gpio.OUT, initial = gpio.LOW)
#sen1_min
output_sen1_min = 19
gpio.setup(output_sen1_min, gpio.OUT, initial = gpio.LOW)
#sen2_max
output_sen2_max = 13
gpio.setup(output_sen2_max, gpio.OUT, initial = gpio.LOW)
#sen2_min
output_sen2_min = 6
gpio.setup(output_sen2_min, gpio.OUT, initial = gpio.LOW)
#sen3_max
output_sen3_max = 5
gpio.setup(output_sen3_max, gpio.OUT, initial = gpio.LOW)
#sen3_min
output_sen3_min = 11
gpio.setup(output_sen3_min, gpio.OUT, initial = gpio.LOW)
#sen4_max
output_sen4_max = 9
gpio.setup(output_sen4_max, gpio.OUT, initial = gpio.LOW)
#sen4_min
output_sen4_min = 17
gpio.setup(output_sen4_min, gpio.OUT, initial = gpio.LOW)
#input pin 1
gpio.setup(21, gpio.IN, pull_up_down=gpio.PUD_DOWN)
#input pin 2
gpio.setup(20, gpio.IN, pull_up_down=gpio.PUD_DOWN)
#input pin 3
gpio.setup(16, gpio.IN, pull_up_down=gpio.PUD_DOWN)
#input pin 4
gpio.setup(12, gpio.IN, pull_up_down=gpio.PUD_DOWN)
#input pin 5
gpio.setup(7, gpio.IN, pull_up_down=gpio.PUD_DOWN)
#input pin 6
gpio.setup(8, gpio.IN, pull_up_down=gpio.PUD_DOWN)
#input pin 7
gpio.setup(25, gpio.IN, pull_up_down=gpio.PUD_DOWN)
#input pin 8
gpio.setup(24, gpio.IN, pull_up_down=gpio.PUD_DOWN)

#reset_message
reset_msg_string = ""

#font setttings

xxLARGE_FONT = ("Verdana" , 140)
xLARGE_FONT = ("Verdana" , 110)
Rs_font = ("Verdana" , 100)
LARGE_FONT = ('Verdana',90)
MEDIUM_FONT = ('Verdana' , 60)
SPECIAL_FONT = ('Verdana', 30)
SMALL_FONT = ('Verdana',12)

#Checking direcotories

print('RAN FILE CHECK')
folderpath = "/home/pi/Desktop/dispenser/data/"
folder_year_path = "/home/pi/Desktop/dispenser/data/" + datetime.datetime.now().strftime("%Y") +"/"
filepath = folder_year_path +datetime.datetime.now().strftime("%B")+"/"
##folder_updated = "/home/pi/Desktop/dispenser/update_logs/"
##queue_files = "/home/pi/Desktop/dispenser/queue_files/"
##all_data = "/home/pi/Desktop/dispenser/data/"

directory =  os.path.dirname(folderpath)
if not os.path.exists(directory):
    os.makedirs(directory)
directory =  os.path.dirname(folder_year_path)
if not os.path.exists(directory):
    os.makedirs(directory)
directory =  os.path.dirname(filepath)
if not os.path.exists(directory):
    os.makedirs(directory)





##getting folder Functions
def get_filename(file_path):
    show_file = file_path
    path ="%s" %show_file
    return os.listdir(path)
def get_foldername():
    path ="%s" %folderpath
    return os.listdir(path)
def get_folder_year_name():
    path ="%s" %folder_year_path
    return os.listdir(path)

##do nothing
def disable_event():
    pass
#getting serial
def getserial():
  # Extract serial from cpuinfo file
  j_1 = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        j_1 = line[10:26]
    f.close()
  except:
    j_1 = "ERROR000000000"
  return j_1
#Error Function
def raise_error(string):
    message = string
    error = tk.Tk()
    error.wm_title("WARNING")
    error.overrideredirect(True)
    connected = 0
    error.geometry("{0}x{1}+0+0".format(error.winfo_screenwidth(), error.winfo_screenheight()))
    error.wm_geometry("800x200+120+120")
    label = tk.Label(error , text =message, fg= "red", font = LARGE_FONT)
    label.pack()
    while (connected == 0):
        try:
            values = instrument.read_registers(250, 2, 3)
            b = struct.pack('HH', values[0],values[1])
            temp = int(struct.unpack('f',b)[0])
            if temp < 9:
                connected = 0
            else:
                connected = 1
                print("destroying msg")
                lambda : [error.destroy(),error.quit()]
                error.mainloop()
        except:
            print("running again")
            error.mainloop()
    error.mainloop()

#System Variables
dpress = []
dpress1 = []
keytext=''
temp = 00.0
rate = 55.81
unit = '/KG'
total = 0 #totalizer gas modbus call
amount = 0
stop_bit = 0
bit = 0
c_bit =0
save_bit = 0
total_check = 0
mass_inv = 0
divider_check = 0
mass_total1 = 0
flow =0
sms_sent = 0
currentTime = ''
current_inventory = 0.0
yest_inventory = 0.0
inventory1 = 0.0
current_userID = ''
current_license_plate = ''
trigger = 0
thread_check = 0
button_state = True

increment_hr = 3
increment_min = 0
increment_shut_off = 2
setting_btn = 0

reset_total_op = 0

hr_set = str(int(datetime.datetime.now().strftime('%H'))+increment_hr)
min_set = str(int(datetime.datetime.now().strftime('%M'))+increment_min)
shut_off = str(int(min_set)+increment_shut_off)

def time_repeat():
    global hr_set
    global min_set
    global shut_off
    hr_set = str(int(datetime.datetime.now().strftime('%H'))+increment_hr)
    min_set = str(int(datetime.datetime.now().strftime('%M'))+increment_min)

    if int(min_set) >= 60:
        min_set = (int(min_set) - 60)
        hr_set = str(int(datetime.datetime.now().strftime('%H'))+1)
    if  int(min_set) < 10:
        min_set = '0' + str(min_set)

    if  int(hr_set) < 10:
        hr_set = '0'+ str(hr_set)
    elif int(hr_set) >= 24:
        hr_set = '0' + str(int(hr_set) - 24)

    shut_off = str(int(min_set)+increment_shut_off)

    if int(shut_off) >=60:
        shut_off = '0'+str(int(shut_off)-60)
    if  int(shut_off) < 10:
        shut_off = '0'+str(shut_off)        

    print("HR SET : %s"%hr_set)
    print("MIN SET : %s"%min_set)
    print("SHUT OFF : %s"%shut_off)

time_repeat()

#sensor limits
sen1_max = 0.0
sen1_min = 0.0

sen2_max = 0.0
sen2_min = 0.0

sen3_max = 0.0
sen3_min = 0.0

sen4_max = 0.0
sen4_min = 0.0

sen1_max_reset_mech = 0
sen1_min_reset_mech = 0
sen2_max_reset_mech = 0
sen2_min_reset_mech = 0
sen3_max_reset_mech = 0
sen3_min_reset_mech = 0
sen4_max_reset_mech = 0
sen4_min_reset_mech = 0

sen1_range = 400
sen2_range = 400
sen3_range = 400
sen4_range = 400

unique_pass = "12-EE(P)-065"
userID = ""
license_plate = ""
index=int(0)
sButton =0
mng_pass = "0000"
admin_pass = "3728"
try:
    instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
    instrument.serial.baudrate = 9600
    instrument.serial.timeout = 1 
    instrument.serial.bytesize = 8
    instrument.serial.parity   = serial.PARITY_NONE
    instrument.serial.stopbits = 1
    instrument.serial.timeout  = 0.05   
    instrument.mode = minimalmodbus.MODE_RTU
    instrument.debug = False
except:
    raise_error("Communication error")


#initializing gsm module
try:
    port.flush()
    ##disable echo
    command = 'ATE0'+'\r\n'
    port.write(bytes(command, 'utf-8'))
    rcv = port.read(10)
    print("Disable echo")
    print(rcv.decode("utf-8"))
    time.sleep(1)
    ##select message format as text mode
    command = 'AT+CMGF=1\r\n'
    port.write(bytes(command, 'utf-8'))
    rcv = port.read(10)
    print("Enter into text mode")
    print(rcv.decode("utf-8"))
    time.sleep(1)
##            ##deleting all sms from storage
##            command = 'AT+CMGD=4'+'\r\n'
##            port.write(bytes(command, 'utf-8'))
##            rcv = port.read(10)
##            print(rcv.decode("utf-8"))
##            time.sleep(1)
    ##sending AT command reply should be "OK"
    command = 'AT\r\n'
    port.write(bytes(command, 'utf-8'))
    rcv = port.read(10)
    print("Getting ok")
    print(rcv.decode('utf-8'))
    time.sleep(1)

except:
    pass
def popup_msg():
    popup = tk.Tk()
    popup.wm_title("Authentication")
    popup.wm_geometry("400x700+120+120")
##    popup.overrideredirect(True)
##    popup.geometry("{0}x{1}+0+0".format(app.winfo_screenwidth(), app.winfo_screenheight()))
    
    #msg
    labelframe = tk.LabelFrame(popup, text = "", font = SMALL_FONT)
    labelframe.pack()
    label = tk.Label(labelframe, text = "Enter Pin", font = SMALL_FONT, relief = tk.RIDGE)
    label.grid(row = 0, column =0)

    #display
    s = StringVar(popup)
    ps = tk.Entry(labelframe, textvariable = s, font = SMALL_FONT, show="*")
    ps.grid(row=1, column=0)
##    ps = tk.Label(labelframe, text = s, font = MEDIUM_FONT, relief = tk.RIDGE)
##    ps.grid(row=1, column =0)

    #keypad

    
    def click(btn):
        global bit
        global mng_pass
        if btn == 'Del' and len(dpress) > 0:
            del dpress[-1]
        elif btn == 'Clear':
            del dpress[:]
        elif btn == 'Cancel':
            del dpress[:]
            bit =0
            popup.quit()
            popup.destroy()

        elif len(dpress) < 4 and btn != 'Del' and btn != 'Clear':
            dpress.append('%s' %btn)

        keytext = ''.join(dpress)
        s.set(keytext)
        if keytext == mng_pass:
            del dpress[:]
            bit =1
            popup.quit()
            popup.destroy()
        elif keytext == admin_pass:
            del dpress[:]
            bit =2
            popup.quit()
            popup.destroy()        
        elif len(keytext) == 4 and keytext != mng_pass:
            s.set("Wrong")

    keypadframe = tk.LabelFrame(popup, text = "", font = SMALL_FONT)
    keypadframe.pack()

    #print(dpress)
    #typical keypad
    btn_list = [
            '7',  '8',  '9',
            '4',  '5',  '6',
            '1',  '2',  '3',
            'Clear',  '0',  'Del',
            'Cancel']
    # create and position all buttons with a for-loop
    # r, c used for row, column grid values
    r = 1
    c = 0
    n = 0
    # list(range()) needed for Python3
    btn = list(range(len(btn_list)))
    for label in btn_list:
        # partial takes care of function and argument
        # create the button
        cmd = partial(click,label)
        btn[n] = tk.Button( keypadframe, text=label,font = SMALL_FONT , justify = LEFT
                           ,command = cmd, width=6, height=4)
        # position the button
        btn[n].grid(row=r, column=c , padx =4 ,pady =4)
        # increment button index
        n += 1
        # update row/column position
        c += 1
        if c == 3:
            c = 0
            r += 1

    popup.mainloop()
def condition_window(string,sensor_no):
        global stop_bit
        popup = tk.Tk()
        popup.wm_geometry("800x500+80+80")
        label = tk.Label(popup, font = MEDIUM_FONT, text = string)
        label.pack()
        def check_input():
            print("checking input")
            if gpio.input(25):
                popup.quit()
                popup.destroy()
            else:
                popup.after(1000,check_input())
        popup.after(1000,check_input)
        popup.mainloop()

def send_email():

    def send_email(subject, msg):
        try:
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.ehlo()
            server.starttls()
            server.login(EMAIL,PASSWORD)
            server.sendmail(EMAIL, TO_EMAIL, msg)
            server.sendmail(EMAIL, 'kamoonbhai@gmail.com', msg)
            server.quit()
            print("Success: Email sent!")
            try:
                with open('/home/pi/Desktop/dispenser/queue.csv','w', newline = '') as f:
                    f.truncate()
                f.close()
            except:
                print('NONE')
        except:
            print("Email failed to send.")
            try:
                with open('/home/pi/Desktop/dispenser/queue.csv','a', newline = '') as f:
                    w = csv.writer(f)
                    data = [filename_email]
                    w.writerow(data)
                f.close()
            except:
                print('NONE')

    subject = "Python Email Test"
    body = "This is an automated email generated.\n __author__ = 'Umair'"

    msg  = MIMEMultipart()
    msg['From'] = EMAIL
    msg['To'] = TO_EMAIL
    msg['Subject'] = subject

    msg.attach(MIMEText(body,'plain'))
    file_date = datetime.datetime.now().strftime('%Y')+'/'+datetime.datetime.now().strftime('%B')+'/'
    filename_email = '/home/pi/Desktop/dispenser/data/'+file_date+datetime.datetime.now().strftime('%d-%B-%Y')+'.csv'

##    file_check()
    
    if os.path.isfile( filename_email) == True:               
        try:
            with open(filename_email, newline = '') as f:
                r = csv.reader(f)
                data = [line for line in r]
            if data[0][0] != 'Status':
                with open(filename_email, 'w', newline = '') as f:
                    w = csv.writer(f)
                    w.writerow(['Status','Date Time','UserID', 'Truck No.', 'Sensor1', 'Sensor2', 'Sensor3', 'Sensor4', 'Total(KG)', 'M Temp',
                                'Inventory', 'Flow Rate', 'INDEX'])
                    w.writerows(data)
                f.close()
        except:
            subprocess.call("sudo chmod 777 " + filename_email, shell = True)
            try:
                with open(filename_email, newline = '') as f:
                    r = csv.reader(f)
                    data = [line for line in r]
                with open(filename_email, 'w', newline = '') as f:
                    w = csv.writer(f)
                    w.writerow(['Status','Date Time','UserID', 'Truck No.', 'Sensor1', 'Sensor2', 'Sensor3', 'Sensor4', 'Total(KG)', 'M Temp',
                                'Inventory', 'Flow Rate', 'INDEX'])
                    w.writerows(data)
                f.close()
            except:
                print("failed to edit file.")
    else:
        try:
            with open(filename_email,"w" , newline = '') as fp:
                a = csv.writer(fp, delimiter = ",")
                data = [1,2,3,4,5,6,7,8,9,10,11,12,13]
                a.writerow(data)
            fp.close()
        except:
            subprocess.call("sudo chmod 777 -R /home/pi/Desktop/dispenser/data/", shell = True)
            try:
                with open(filename_email,"w" , newline = '') as fp:
                    a = csv.writer(fp, delimiter = ",")
                    data = [1,2,3,4,5,6,7,8,9,10,11,12,13]
                    a.writerow(data)
                fp.close()
            except:
                print('Failed')
            
        try:
            with open(filename_email, newline = '') as f:
                r = csv.reader(f)
                data = [line for line in r]
            with open(filename_email, 'w', newline = '') as f:
                w = csv.writer(f)
                w.writerow(['Status','Date Time','UserID', 'Truck No.', 'Sensor1', 'Sensor2', 'Sensor3', 'Sensor4', 'Total(KG)', 'M Temp',
                            'Inventory', 'Flow Rate', 'INDEX'])
                w.writerows(data)
            f.close()
        except:
            subprocess.call("sudo chmod 777 " + filename_email, shell = True)
            try:
                with open(filename_email, newline = '') as f:
                    r = csv.reader(f)
                    data = [line for line in r]
                with open(filename_email, 'w', newline = '') as f:
                    w = csv.writer(f)
                    w.writerow(['Status','Date Time','UserID', 'Truck No.', 'Sensor1', 'Sensor2', 'Sensor3', 'Sensor4', 'Total(KG)', 'M Temp',
                                'Inventory', 'Flow Rate', 'INDEX'])
                    w.writerows(data)
                f.close()
            except:
                print("failed to edit file.")        
            

    attachment = open(filename_email, 'rb')

    part = MIMEBase('application', 'octet-strean')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',"attachment; filename= "+datetime.datetime.now().strftime('%d-%B-%Y')+'.csv')

    msg.attach(part)
    text = msg.as_string()

    attachment.close()
    with open('/home/pi/Desktop/dispenser/queue.csv','r', newline = '') as f:
        r = csv.reader(f)
        data = [line for line in r]
        print(data)
        if data !=[]:
            if data[0] != []:
                n = 0
                for line in data:
                    if line[0] != '':
                        n += 1
                        attachment = open(str(line[0]), 'rb')
                        part = MIMEBase('application', 'octet-strean')
                        part.set_payload((attachment).read())
                        encoders.encode_base64(part)
                        p = line[0].find('-')- 2
                        part.add_header('Content-Disposition',"attachment; filename= "+str(n)+' : '+line[0][p:])

                        msg.attach(part)
                        text = msg.as_string()
                        attachment.close()
            else:
                print('None to be send')
    send_email(subject, text)
    

def mass_inventory():
    try:
        values = instrument.read_registers(262, 2, 3)
        b = struct.pack('HH', values[0],values[1])
        inventory = float(struct.unpack('f',b)[0])
        return inventory
    except IOError:
        raise_error("Communication Error")
        print("Failed")
        return 0.0
    
def reset_total():
    try:
        values = instrument.write_bit(55,1,5)
    except IOError:
        raise_error("Communication Error")
        print("Failed")
    
def mass_total():
    try:
        values = instrument.read_registers(258, 2, 3)
        b = struct.pack('HH', values[0],values[1])
        total = float(struct.unpack('f',b)[0])
        return total

    except IOError:
        raise_error("Communication Error")
        print("Failed")
        return 0.0

    
def flow_mass():
    try:
        
        values = instrument.read_registers(246, 2, 3)
        b = struct.pack('HH', values[0],values[1])
        flow = float(struct.unpack('f',b)[0])
        return flow

    except IOError:
        raise_error("Communication Error")
        print("Failed")
        return 0.0
def update_pressure(number):
    global stop_bit
    global adc_value
    try:
        adc_value = adc.read_adc(number, gain=GAIN)
    except:
        adc_value = 0
    return adc_value


    
def temp_set():
    try:
        global temp
        
        values = instrument.read_registers(250, 2, 3)
        b = struct.pack('HH', values[0],values[1])
        temp = float(struct.unpack('f',b)[0])
        return temp
    except:
        raise_error("Communication Error")
        return 0.0

def send_sms(number, payLoad):
    check = ''
    time_out = time.perf_counter() + 10
    print(number)
    command = 'AT+CMGS="{0}"'.format(number)+'\r'
    port.write(bytes(command, 'utf-8'))
    rcv = port.read(10)
    print(rcv.decode("utf-8"))
    time.sleep(1)
    command = payLoad
    print(command)
    port.write(bytes(command, 'utf-8'))
    rcv = port.read(10)
    print(rcv.decode("utf-8"))
    command = "\x1A"
    port.write(bytes(command, 'utf-8'))
    while True:
        rcv = port.read(10)
        check = rcv.decode('utf-8')
        print(check)
        if check.find('OK') != -1:
            break
        elif check.find('ERROR') != -1:
            break

        if time_out < time.perf_counter():
            print('breaking send sms check loop')
            break


for number in numbers:
    send_sms(number, "System Restarted \r\n")

def change_limits(sensor_string):
    global keytext
    global dpress
    popup = tk.Tk()
    popup.wm_title("CHANGE LIMIT")
    
    #msg
    labelframe = tk.LabelFrame(popup, text = "", font = SMALL_FONT)
    labelframe.pack()
    label = tk.Label(labelframe, text = sensor_string, font = SMALL_FONT, relief = tk.RIDGE)
    label.grid(row = 0, column =0)

    #display
    s = StringVar(popup)
    ps = tk.Entry(labelframe, font = SMALL_FONT, textvariable = s, width = 6)
    ps.grid(row=1, column =0)
##    s = ""
##    ps = tk.Label(labelframe, text = s, font = SMALL_FONT, relief = tk.RIDGE)
##    ps.grid(row=1, column =0)

    #keypad
    def click(btn):
        global sen1_max
        global sen1_min
        global sen2_max
        global sen2_min
        global sen3_max
        global sen3_min
        global sen4_max
        global sen4_min
        global sen1_range
        global sen2_range
        global sen3_range
        global sen4_range
        if btn == 'Del' and len(dpress) > 0:
            del dpress[-1]
        elif btn == 'Clear':
            del dpress[:]
        elif btn == 'Cancel':
            del dpress[:]
            popup.quit()
            popup.destroy()

        elif len(dpress) < 5 and btn != 'Del' and btn != 'Clear' and btn != 'Apply':
            dpress.append('%s' %btn)
        elif btn == 'Apply':
            print(sensor_string)
            if sensor_string == "sensor1 max":
                sen1_max = float(''.join(dpress))
            elif sensor_string == "sensor1 min":
                sen1_min = float(''.join(dpress))
            elif sensor_string == "sensor2 max":
                sen2_max = float(''.join(dpress))
            elif sensor_string == "sensor2 min":
                sen2_min = float(''.join(dpress))
            elif sensor_string == "sensor3 max":
                sen3_max = float(''.join(dpress))
            elif sensor_string == "sensor3 min":
                sen3_min = float(''.join(dpress))
            elif sensor_string == "sensor4 max":
                sen4_max = float(''.join(dpress))
            elif sensor_string == "sensor4 min":
                sen4_min = float(''.join(dpress))
            elif sensor_string == "sensor1 range":
                sen1_range = float(''.join(dpress))
            elif sensor_string == "sensor2 range":
                sen2_range = float(''.join(dpress))
            elif sensor_string == "sensor3 range":
                sen3_range = float(''.join(dpress))
            elif sensor_string == "sensor4 range":
                sen4_range = float(''.join(dpress))
            else:
                print("Error")

            if os.path.isfile( "/home/pi/Desktop/dispenser/SystemConfiguration.csv") == True:
                with open("/home/pi/Desktop/dispenser/SystemConfiguration.csv","w" , newline = '') as fp:
                    a = csv.writer(fp, delimiter = ",")
                    data = [sen1_max,sen1_min,sen2_max,sen2_min,sen3_max,sen3_min,sen4_max,sen4_min,
                            sen1_max_reset_mech,sen1_min_reset_mech,sen2_max_reset_mech,sen2_min_reset_mech,
                            sen3_max_reset_mech,sen3_min_reset_mech,sen4_max_reset_mech,sen4_min_reset_mech,
                            sen1_range,sen2_range,sen3_range,sen4_range]
                    a.writerow(data)
                fp.close()

            else:
                with open("/home/pi/Desktop/dispenser/SystemConfiguration.csv","w" , newline = '') as fp:
                    a = csv.writer(fp, delimiter = ",")
                    data = [sen1_max,sen1_min,sen2_max,sen2_min,sen3_max,sen3_min,sen4_max,sen4_min,
                            sen1_max_reset_mech,sen1_min_reset_mech,sen2_max_reset_mech,sen2_min_reset_mech,
                            sen3_max_reset_mech,sen3_min_reset_mech,sen4_max_reset_mech,sen4_min_reset_mech,
                            sen1_range,sen2_range,sen3_range,sen4_range]
                    a.writerow(data)
                fp.close()
            del dpress[:]
            popup.quit()
            popup.destroy()            
            
        keytext = ''.join(dpress)
        s.set(keytext)
        

    keypadframe = tk.LabelFrame(popup, text = "", font = SMALL_FONT)
    keypadframe.pack()

    #print(dpress)
    #typical keypad
    btn_list = [
            '7',  '8',  '9',
            '4',  '5',  '6',
            '1',  '2',  '3',
            '.',  '0',  'Del',
            'Cancel', '', 'Apply']
    # create and position all buttons with a for-loop
    # r, c used for row, column grid values
    r = 1
    c = 0
    n = 0
    # list(range()) needed for Python3
    btn = list(range(len(btn_list)))
    for label in btn_list:
        # partial takes care of function and argument
        # create the button
        cmd = partial(click,label)
        btn[n] = tk.Button( keypadframe, text=label,font = SMALL_FONT , justify = LEFT,
                            command = cmd, width=6, height=4)
        # position the button
        btn[n].grid(row=r, column=c , padx =4 ,pady =4)
        # increment button index
        n += 1
        # update row/column position
        c += 1
        if c == 3:
            c = 0
            r += 1

    popup.mainloop()

class DispenserGui(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        #kilograme/hour
        try:
            values = instrument.write_register(38,75,numberOfDecimals=0,functioncode=6)
        except:
            pass

        tk.Tk.wm_title(self, "DispenserGUI")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

##        if os.path.isfile(filepath +datetime.datetime.now().strftime("%d-%B-%Y")+".csv") == False:
##            with open(filepath+datetime.datetime.now().strftime("%d-%B-%Y")+".csv" , "w", newline = "") as fp:
##                a = csv.writer(fp, delimiter = ",")
##                data = [["INDEX","TIME","AMOUNT","RATE","TEMP","UNIT","GAS"]]
##                a.writerows(data)
##            fp.close()
        if os.path.isfile( "/home/pi/Desktop/dispenser/SystemConfiguration.csv") == True:
            try:
                with open("/home/pi/Desktop/dispenser/SystemConfiguration.csv", 'r', newline = '') as df:
                    reader = list(csv.reader( df , delimiter = ','))
                    global sen1_max
                    global sen1_min
                    global sen2_max
                    global sen2_min
                    global sen3_max
                    global sen3_min
                    global sen4_max
                    global sen4_min
                    global sen1_max_reset_mech
                    global sen1_min_reset_mech
                    global sen2_max_reset_mech
                    global sen2_min_reset_mech
                    global sen3_max_reset_mech
                    global sen3_min_reset_mech
                    global sen4_max_reset_mech
                    global sen4_min_reset_mech
                    global sen1_range
                    global sen2_range
                    global sen3_range
                    global sen4_range
                    sen1_max = float(reader[0][0])
                    sen1_min = float(reader[0][1])
                    sen2_max = float(reader[0][2])
                    sen2_min = float(reader[0][3])
                    sen3_max = float(reader[0][4])
                    sen3_min = float(reader[0][5])
                    sen4_max = float(reader[0][6])
                    sen4_min = float(reader[0][7])
                    sen1_max_reset_mech = int(reader[0][8])
                    sen1_min_reset_mech = int(reader[0][9])
                    sen2_max_reset_mech = int(reader[0][10])
                    sen2_min_reset_mech = int(reader[0][11])
                    sen3_max_reset_mech = int(reader[0][12])
                    sen3_min_reset_mech = int(reader[0][13])
                    sen4_max_reset_mech = int(reader[0][14])
                    sen4_min_reset_mech = int(reader[0][15])
                    sen1_range = float(reader[0][16])
                    sen2_range = float(reader[0][17])
                    sen3_range = float(reader[0][18])
                    sen4_range = float(reader[0][19])
                    print("MAX MIN LIMITS SET")
                df.close()
            except:
                    sen1_max = 350.0
                    sen1_min = 50.0
                    sen2_max = 350.0
                    sen2_min = 50.0
                    sen3_max = 350.0
                    sen3_min = 50.0
                    sen4_max = 350.0
                    sen4_min = 50.0
                    sen1_max_reset_mech = 0
                    sen1_min_reset_mech = 0
                    sen2_max_reset_mech = 0
                    sen2_min_reset_mech = 0
                    sen3_max_reset_mech = 0
                    sen3_min_reset_mech = 0
                    sen4_max_reset_mech = 0
                    sen4_min_reset_mech = 0
                    sen1_range = 400
                    sen2_range = 400
                    sen3_range = 400
                    sen4_range = 400
        else:
            
                with open("/home/pi/Desktop/dispenser/SystemConfiguration.csv","w" , newline = '') as fp:
                    a = csv.writer(fp, delimiter = ",")
                    data = [sen1_max,sen1_min,sen2_max,sen2_min,sen3_max,sen3_min,sen4_max,sen4_min,
                            sen1_max_reset_mech,sen1_min_reset_mech,sen2_max_reset_mech,sen2_min_reset_mech,
                            sen3_max_reset_mech,sen3_min_reset_mech,sen4_max_reset_mech,sen4_min_reset_mech,
                            sen1_range,sen2_range,sen3_range,sen4_range]
                    a.writerow(data)
                fp.close()
        if os.path.isfile( "/home/pi/Desktop/dispenser/defaults.csv") == True:
                with open("/home/pi/Desktop/dispenser/defaults.csv","r" , newline = '') as df:
                    global yest_inventory
                    global inventory
                    global inventory1
                    global button_state
                    reader = list(csv.reader( df , delimiter = ','))
                    try:
                        inventory1 = float(reader[0][2])
                        print(inventory1)
                        yest_inventory = float(reader[0][3])
                        button_state = str(reader[0][6])
                    except:
                        inventory1 = 0
                        button_state = True
                        try:
                            values = instrument.read_registers(262, 2, 3)
                            b = struct.pack('HH', values[0],values[1])
                            inventory = float(struct.unpack('f',b)[0])
                        except:
                            inventory = 0.0
                        yest_inventory = inventory
                df.close()
        else:
            try:
                values = instrument.read_registers(262, 2, 3)
                b = struct.pack('HH', values[0],values[1])
                inventory = float(struct.unpack('f',b)[0])
            except:
                inventory = 0.0
            yest_inventory = inventory
        print(inventory1)

                  
        self.frames = {}
        for F in (StartPage, SettingPage, Error, SystemConfiguration, AdministrativeChanges, NewBatch):
            
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")
        if os.path.isfile("/sbin/key.csv") == True:
            with open("/sbin/key.csv", 'r', newline = '') as df:
                reader = list(csv.reader( df , delimiter = ','))
                try:
                    system_key = reader[0][0]
                    if not system_key == str(getserial()):
                        self.show_frame(Error)
                    else:
                        self.show_frame(StartPage)
                except:
                    self.show_frame(Error)
            df.close()
        else:
            self.show_frame(Error)
    def get_page(self, page_class):   
        return self.frames[page_class]

    def show_frame(self, cont):
        global stop_bit
        frame=self.frames[cont]
##        print(cont)
        if str(cont) == "<class '__main__.StartPage'>":
            stop_bit=0
            frame.tkraise()
            frame.event_generate("<<Start>>")
            print("event generated")
        elif str(cont) == "<class '__main__.SettingPage'>":
            stop_bit=1
            frame.tkraise()
            frame.event_generate("<<Stop>>")
        elif str(cont) == "<class '__main__.SystemConfiguration'>":
            popup_msg()
            if bit ==1:
                frame.tkraise()
            else:
                pass
        elif str(cont) == "<class '__main__.AdministrativeChanges'>":
            popup_msg()
            if bit ==2:
                frame.tkraise()
            else:
                pass
        else:
            frame.tkraise()

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        global index
        #date time label
        self.controller = controller
        self.date_time_string = StringVar()
        self.date_time_entry = tk.Entry(self, textvariable = self.date_time_string, font = SPECIAL_FONT)
        self.date_time_entry.place(x = 500, y = 700)
##        self.date_time_label = tk.Label(self, text= 0, font=SMALL_FONT)
##        self.date_time_label.place(x=500, y= 700)
        
        self.provider = tk.Label(self, text = '0', font= SMALL_FONT)
        self.provider.place(x=0, y=680)
        
        self.signal_label = tk.Label(self, text = '0', font= SMALL_FONT)
        self.signal_label.place(x=0, y=700)
        #Inventory
        self.inventory = StringVar()
        inventory_frame = tk.LabelFrame(self, text = "INVENTORY ---- KG" , font = SMALL_FONT)
        inventory_frame.place(x = 165, y =550)
        self.a = Entry(inventory_frame ,font= MEDIUM_FONT, textvariable= self.inventory , justify= RIGHT
                  , bg= "lawngreen" , fg= "red" , width=10)
        self.a.grid(row =0 , column = 0)

        #current entry
        current_frame = tk.LabelFrame(self, text = "Current Totalizer ---- KG" , font = SMALL_FONT)
        current_frame.place(x = 650, y =405)
        self.current_string = StringVar()
        self.currentTotalizer = Entry(current_frame ,font= MEDIUM_FONT, textvariable= self.current_string , justify= RIGHT
                  , bg= "white" , fg= "blue" , width=7)
        self.currentTotalizer.grid(row =0 , column = 0)

        # Last 3 filling Frame
        last_filling_frame = tk.LabelFrame(self, text = "RECENT BATCHES ---- KG" , font = SMALL_FONT)
        last_filling_frame.place(x = 650, y =270)

        #First Entry
        self.first_string = StringVar()
        self.first_entry = Entry(last_filling_frame ,font= MEDIUM_FONT, textvariable= self.first_string , justify= RIGHT
                  , bg= "black" , fg= "white" , width=7)
        self.first_entry.grid(row = 0, column =0)

        #Flow Frame
        flow_frame = tk.LabelFrame(self, text = "FLOW RATE ---- KG/HOUR" , font = SMALL_FONT)
        flow_frame.place(x = 650, y = 10)
        #Flow Entry
        self.flow_string = StringVar()
        self.flow_entry = Entry(flow_frame ,font= MEDIUM_FONT, textvariable= self.flow_string , justify= RIGHT
                  , bg= "orange" , fg= "black" , width=7)
        self.flow_entry.grid(row =0 , column = 0)

        #Temprature
        temp_frame = tk.LabelFrame(self, text = "TEMPRATURE ---- °C" , font = SMALL_FONT)
        temp_frame.place(x = 750, y =140)
        #temp_entry
        self.temp_string = StringVar()
        self.temp_entry = Entry(temp_frame ,font= MEDIUM_FONT, textvariable= self.temp_string , justify= RIGHT
                  , bg= "orange" , fg= "black" , width=5)
        self.temp_entry.grid(row =0, column=0)

        #24 hours totalizer frame
        totalizer_24hr = tk.LabelFrame(self, text = "24 HR TOTALIZER" , font = SMALL_FONT)
        totalizer_24hr.place(x = 275, y =10)

        #24 hours totalizer entry
        self.totalizer_24hr = StringVar()
        self.totalizer_24hr_entry = Entry(totalizer_24hr ,font= MEDIUM_FONT, textvariable= self.totalizer_24hr , justify= RIGHT
                  , bg= "blue" , fg= "white" , width=7)
        self.totalizer_24hr_entry.grid(row =0 , column = 0)

        #yesterday totalizer frame
        totalizer_yest = tk.LabelFrame(self, text = "YESTERDAY TOTALIZER" , font = SMALL_FONT)
        totalizer_yest.place(x = 275, y =140)

        #24 hours totalizer entry
        self.totalizer_yest = StringVar()
        self.totalizer_yest_entry = Entry(totalizer_yest ,font= MEDIUM_FONT, textvariable= self.totalizer_yest , justify= RIGHT
                  , bg= "blue" , fg= "white" , width=7)
        self.totalizer_yest_entry.grid(row =0 , column = 0)

        #ADC Sensor1 Frame
        ADC_frame1 = tk.LabelFrame(self, text = "PR 01---- BAR" , font = SMALL_FONT)
        ADC_frame1.place(x = 5, y = 10)

        #Sensor 1 entry
        self.sensor1 = StringVar()
        self.sensor1_entry = Entry(ADC_frame1 ,font= MEDIUM_FONT, textvariable= self.sensor1 , justify= RIGHT
                  , bg= "yellow" , fg= "red" , width=5)
        self.sensor1_entry.grid(row =0 , column = 0)

        #ADC Sensor2 Frame
        ADC_frame2 = tk.LabelFrame(self, text = "PR 02 ---- BAR" , font = SMALL_FONT)
        ADC_frame2.place(x = 5, y =140)

        #Sensor 2 entry
        self.sensor2 = StringVar()
        self.sensor2_entry = Entry(ADC_frame2 ,font= MEDIUM_FONT, textvariable= self.sensor2 , justify= RIGHT
                  , bg= "yellow" , fg= "red" , width=5)
        self.sensor2_entry.grid(row =1 , column = 0)

        #ADC Sensor3 Frame
        ADC_frame3 = tk.LabelFrame(self, text = "PR 03 ---- BAR" , font = SMALL_FONT)
        ADC_frame3.place(x = 5, y =270)

        #Sensor 3 entry
        self.sensor3 = StringVar()
        self.sensor3_entry = Entry(ADC_frame3 ,font= MEDIUM_FONT, textvariable= self.sensor3 , justify= RIGHT
                  , bg= "yellow" , fg= "red" , width=5)
        self.sensor3_entry.grid(row =2 , column = 0)

        #ADC Sensor4 Frame
        ADC_frame4 = tk.LabelFrame(self, text = "TEMP 01 ---- °C" , font = SMALL_FONT)
        ADC_frame4.place(x = 5, y =405)

        #Sensor 4 entry
        self.sensor4 = StringVar()
        self.sensor4_entry = Entry(ADC_frame4 ,font= MEDIUM_FONT, textvariable= self.sensor4 , justify= RIGHT
                  , bg= "yellow" , fg= "red" , width=5)
        self.sensor4_entry.grid(row =3 , column = 0)

        #Status LIGHT
        light_canvas = tk.LabelFrame( self, text = "Status" ,font = SMALL_FONT)
        light_canvas.place(x =5 ,y=540)

        self.canvas = Canvas(light_canvas , width=100, height =100)
        self.status_light = self.canvas.create_oval(5,5,90,90, fill = 'green')
        self.canvas.pack()

        #RECENT LICENSE PLATE
        recent_plate = tk.LabelFrame(self, text = "RECENT ---- " , font = SMALL_FONT)
        recent_plate.place(x = 275, y =270)

        #RECENT LICENSE PLATE ENTRY
        self.recent_plate_string = StringVar()
        self.recent_plate_entry = Entry(recent_plate ,font= MEDIUM_FONT, textvariable= self.recent_plate_string , justify= RIGHT
                  , bg= "black" , fg= "white" , width=7)
        self.recent_plate_entry.grid(row =3 , column = 0)

        #CURRENT PLATE FRAME
        current_plate = tk.LabelFrame(self, text = "CURRENT ---- " , font = SMALL_FONT)
        current_plate.place(x = 275, y =405)

        #CURRENT LICENSE PLATE ENTRY
        self.current_plate_string = StringVar()
        self.current_plate_entry = Entry(current_plate ,font= MEDIUM_FONT, textvariable= self.current_plate_string , justify= RIGHT
                  , bg= "white" , fg= "blue" , width=7)
        self.current_plate_entry.grid(row =0 , column = 0)        
        
##        temp_label =tk.Label(temp_frame , font = ('Verdana', 25), text = "°C" )
##        temp_label.grid(row = 0, column = 1)
        self.disable_time = 0
        def set_page():
            global stop_bit
            global setting_btn
            setting_btn = 1
            stop_bit = 1
            
        #settings page button
        self.setting_page = tk.Button(self, text = "Settings", font = SMALL_FONT, bg = "red", fg = "white",
                                 command = lambda: [set_page()])
        self.setting_page.place(x= 140, y=695)

##        #def updating fields:
##        def update_fields():
##            print("trying to update fields")
##            global license_plate
##            global userID
##            license_plate = plate_string.get()
##            print(license_plate)
##            userID = user_id_string.get()
##            print(userID)
        #stop button




##        #Push Recent Batch
##        def push_recent_batch():
##            global stop_bit
##            global index
##            global userID
##            global license_plate
##            global sButton
##            sButton =0
##            stop_bit = 1
##            
##            self.new_btn.config(text = "STOP", bg = "red", command = lambda: [stop_btn()], state = tk.DISABLED)
##                
##                
##            data_window = tk.Tk()
##            data_window.wm_title("STARTING NEW BATCH")
##            data_window.wm_geometry("800x500+80+80")
##            data_window.protocol('WM_DELETE_WINDOW', lambda: None)
##            entry_field_frame = tk.LabelFrame(data_window, font = SMALL_FONT)
##            entry_field_frame.place(x=400, y =20)
##
##            plate_number = tk.Label(entry_field_frame , text ="Licensce Plate Number", fg= "red", font = SMALL_FONT)
##            plate_number.grid(row =0 , column= 0)
##
##            self.plate_string = StringVar(data_window)
##            self.plate_entry = tk.Entry(entry_field_frame , font = MEDIUM_FONT,textvariable = self.plate_string, width = 7 )
##            self.plate_entry.grid(row=1, column=0, padx=5, pady=5)
##
##
##
##            user_id_label = tk.Label(entry_field_frame , text ="User ID", fg= "red", font = SMALL_FONT)
##            user_id_label.grid(row =2 , column= 0,)
##
##            self.user_id_string = StringVar(data_window)
##            self.user_id_entry = tk.Entry(entry_field_frame , font = MEDIUM_FONT,textvariable = self.user_id_string, width = 7)
##            self.user_id_entry.grid(row=3, column=0)
##
##            data_field_frame = tk.LabelFrame(data_window, font = SMALL_FONT)
##            data_field_frame.place(x=20, y =300)
##
##            date_field_label = tk.Label(data_field_frame, font = SMALL_FONT, text = "DATE/TIME")
##            date_field_label.grid(row=0, column=0)
##
##
##
##            self.date_time_label = tk.Label(data_field_frame, text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
##                                            font = SMALL_FONT)
##            self.date_time_label.grid(row = 1, column =0)
##
##
##            pressure_text = tk.Label(data_field_frame, text = "INITAIL PRESSIRE", font = SMALL_FONT)
##            pressure_text.grid(row =2, column=0)
##
##            self.pressure_label = tk.Label(data_field_frame, text =  self.sensor1.get(), font = SMALL_FONT)
##            self.pressure_label.grid(row = 3, column=0)
##
##            def OK_Button():
##              global stop_bit
##              global index
##              global userID
##              global license_plate
##              global data_send
##              global currentTime
##              global total1
##              global current_userID
##              global current_license_plate
##              global thread_check
##              currentTime = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
##              index += 1
##              stop_bit = 0
##              userID = self.user_id_string.get()
##              current_userID = self.user_id_string.get()
##              self.recent_plate_string.set(self.current_plate_string.get())
##              license_plate = self.plate_string.get()
##              current_license_plate = self.plate_string.get()
##              self.current_plate_string.set(self.plate_string.get())
##              self.setting_page.config(state = tk.DISABLED)
##
##              ##Saving data all in one place for local viewing
##              if os.path.isfile( "/home/pi/Desktop/dispenser/data/"+datetime.datetime.now().strftime("%Y")+"/"+datetime.datetime.now().strftime("%B")+"/"+datetime.datetime.now().strftime("%d-%B-%Y")+".csv") == True:
##                with open("/home/pi/Desktop/dispenser/data/"+datetime.datetime.now().strftime("%Y")+"/"+datetime.datetime.now().strftime("%B")+"/"+datetime.datetime.now().strftime("%d-%B-%Y")+".csv","a" , newline = '') as fp:
##                    a = csv.writer(fp, delimiter = ",")
##                    data = ["BATCH START",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.user_id_string.get(),self.plate_string.get()
##                            , self.sensor1.get(),self.sensor2.get(),self.sensor3.get(),self.sensor4.get(),
##                            self.current_string.get(),self.temp_string.get(),self.inventory.get(),self.flow_string.get(),index]
##                    a.writerow(data)
##                    print("file saved for local viewing")
##                fp.close()
##              else:
##                  with open("/home/pi/Desktop/dispenser/data/"+datetime.datetime.now().strftime("%Y")+"/"+datetime.datetime.now().strftime("%B")+"/"+datetime.datetime.now().strftime("%d-%B-%Y")+".csv","w" ,
##                            newline = '') as fp:
##                    a = csv.writer(fp, delimiter = ",")
##                    data = ["BATCH START",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.user_id_string.get(),self.plate_string.get()
##                            , self.sensor1.get(),self.sensor2.get(),self.sensor3.get(),self.sensor4.get(),
##                            self.current_string.get(),self.temp_string.get(),self.inventory.get(),self.flow_string.get(),index]
##                    a.writerow(data)
##                    print("else file saved for local viewing")
##                  fp.close()
##              ##recent batch save file in defaults.csv
##              if os.path.isfile( "/home/pi/Desktop/dispenser/defaults.csv") == True:
##                  with open("/home/pi/Desktop/dispenser/defaults.csv","w" , newline = '') as fp:
##                    a = csv.writer(fp, delimiter = ",")
##                    data = [self.current_string.get(),index,current_inventory,yest_inventory,self.recent_plate_string.get(),
##                            self.current_plate_string.get()]
##                    a.writerow(data)
##                    print("defaults saved")
##                  fp.close()
##              else:
##                  with open("/home/pi/Desktop/dispenser/defaults.csv","w" , newline = '') as fp:
##                    a = csv.writer(fp, delimiter = ",")
##                    data = [0,0,0.0,0.0,0,0]
##                    a.writerow(data)
##                  fp.close()
##              self.current_string.set("%0.1f"%float(mass_total()))
##              self.first_string.set(self.current_string.get())
##              data_send = 0
##              reset_total()
##              self.current_string.set("%0.1f"%float(mass_total()))
##              total1 = total
##              gpio.output(9, gpio.HIGH)
##              thread_check = 0
##              self.new_btn.config(state= tk.NORMAL)
##              data_window.quit()
##              data_window.destroy()
##              self.on_show_frame("<<Start>>")
            


            
##            ok_button = tk.Button(data_window, font = MEDIUM_FONT, text = "OK", bg = "green", fg = "white",
##                                       command = lambda: OK_Button(), width = 4, height =1)
##            ok_button.place(x =550 , y=300 )
##            data_window.mainloop()


        #button frame
        button_frame = tk.Frame(self)
        button_frame.place(x=700, y=555)


        #Start Button
        self.new_btn = tk.Button(button_frame, text= "NEW BATCH" , font = ('Verdana',25),
                             fg = "white", bg= "green", width =14, height =3,
                                 command = lambda : [self.thread_check_fc()])
        self.new_btn.grid(row =0, column = 1)

        #bill button
        self.print_bill = tk.Button(self, text= "PRINT\nBILL" , font = ('Verdana',25),
                             fg = "white", bg= "green", width =5, height =2,
                                 command = lambda : [self.print_bill_fc()])
        self.print_bill.place(x= 360, y=675)

        #inventory button
        self.iventory_bill = tk.Button(self, text= "PRINT\n24 HR" , font = ('Verdana',25),
                             fg = "white", bg= "green", width =5, height =2,
                                 command = lambda : [self.hr24_bill_fc()])
        self.iventory_bill.place(x=225, y=675)

        if button_state == 'False':
            print('running config of new_btn')
            self.new_btn.config(text = "STOP", bg = "red", command = lambda: [self.stop_btn()], state = tk.NORMAL)


        #setting file
        if os.path.isfile("/home/pi/Desktop/dispenser/defaults.csv") == True:
          try:
             with open("/home/pi/Desktop/dispenser/defaults.csv", 'r', newline = '') as df:
                reader = list(csv.reader( df , delimiter = ','))
                self.first_string.set(reader[0][0])
                index = int(reader[0][1])
                self.recent_plate_string.set(reader[0][4])
                self.current_plate_string.set(reader[0][5])
##                self.second_string.set(reader[0][1])
##                self.third_string.set(reader[0][2])
             df.close()
          except:
            pass
        else:
            with open("/home/pi/Desktop/dispenser/defaults.csv","w" , newline = '') as fp:
                a = csv.writer(fp, delimiter = ",")
                data = [0,0,0,0,0,0,0]
                a.writerow(data)
            fp.close()
            self.first_string.set("0")
    

        ##-------------------------------Thread Setting Area---------------------------------------##

        self.q = queue.Queue()
        self.t0 = threading.Thread(target = self.counter_thread)
        self.t1 = threading.Thread(target = self.totalizer_thread)
##        self.t2 = threading.Thread(target = self.trigger_email_thread)
        self.t3 = threading.Thread(target = self.sms_thread)
        self.t4 = threading.Thread(target = self.condition_thread)
        self.t0.deamon = True
        self.t1.deamon = True
##        self.t2.deamon = True
        self.t3.deamon = True
        self.t4.deamon = True
        self.t0.start()
        self.t1.start()
##        self.t2.start()
        self.t3.start()
        self.t4.start()

        #calling update function
        self.bind("<<Start>>",self.on_show_frame)
        self.on_show_frame(1)

        #setting toplevel
        self.top = None
    def print_bill_fc(self):
        global userID
        
        try:
            p = Usb(0x0483,0x5743, 0, 0x82, 0x01)
            p.text( '\t\t')
            p.image('/home/pi/Desktop/dispenser/egas.png')
            p.text( '\n\n\nRAJIAN GAS FIELD' + '\n'
                   + 'date/time: '+datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") +'\n'
                   + 'USER ID: '+'%s'%userID +'\n'
                   + 'TRUCK NO.: ' + self.recent_plate_string.get() +'\n'
                   + 'TEMPERATURE: '+ self.temp_string.get() + ' C\n'
                   + 'TOTAL(KG): '+ self.first_string.get() + ' KG\n'
                   + 'PRESSURE: %.1f'%adc_read1  + ' BAR\n'
                   )
            p.cut()
            p.close()
        except:
            print('Printer Disconnected')

    def hr24_bill_fc(self):
        global userID
        
        try:
            last_invent = "%.1f"%(inventory-current_inventory)
            print(type(last_invent))
            p = Usb(0x0483,0x5743, 0, 0x82, 0x01)
            p.text( '\t\t')
            p.image('/home/pi/Desktop/dispenser/egas.png')
            p.text(  '\n\n\nRAJIAN GAS FIELD' + '\n'
                   + 'date/time: '+ str(int(datetime.datetime.now().strftime("%d"))-1) + datetime.datetime.now().strftime("-%m-%Y") +'\n'
                   + '24 HR KG: ' + "%.1f"%float(self.totalizer_yest.get()) + ' KG' + '\n'
                   + 'INVENTORY: ' + last_invent + ' KG' + '\n'
                   )
            p.cut()
            p.close()        
        except:
            print('Printer Disconnected')
        
    def stop_btn(self):
        global reset_total_op
##            global data_send
##            data_send = 1
        global button_state
        global currentTime
        global adc_read1
        button_state = True
        currentTime = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        print("Running stop button function")
        global sButton
        new_batch_var = self.controller.get_page(NewBatch)
        sButton = 1
        gpio.output(9, gpio.LOW)
        self.recent_plate_string.set(self.current_plate_string.get())
        self.current_plate_string.set('')
        self.first_string.set(self.current_string.get())

##        file_check()

        ##Saving data all in one place for local viewing
        if os.path.isfile( "/home/pi/Desktop/dispenser/data/"+datetime.datetime.now().strftime("%Y")+"/"+
                    datetime.datetime.now().strftime("%B")+"/"+datetime.datetime.now().strftime("%d-%B-%Y")+".csv") == True:
          with open("/home/pi/Desktop/dispenser/data/"+datetime.datetime.now().strftime("%Y")+"/"+
                    datetime.datetime.now().strftime("%B")+"/"+datetime.datetime.now().strftime("%d-%B-%Y")+".csv","a" , newline = '') as fp:
            a = csv.writer(fp, delimiter = ",")
            data = ["BATCH STOP",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), new_batch_var.user_id_string.get(),self.recent_plate_string.get()
                    , self.sensor1.get(),self.sensor2.get(),self.sensor3.get(),self.sensor4.get(),
                    self.current_string.get(),self.temp_string.get(),self.inventory.get(),self.flow_string.get(),index]
            a.writerow(data)
          fp.close()
        else:
          with open("/home/pi/Desktop/dispenser/data/"+datetime.datetime.now().strftime("%Y")+"/"+
                    datetime.datetime.now().strftime("%B")+"/"+datetime.datetime.now().strftime("%d-%B-%Y")+".csv","w" ,
                    newline = '') as fp:
            a = csv.writer(fp, delimiter = ",")
            data = ["BATCH STOP",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), new_batch_var.user_id_string.get(),self.recent_plate_string.get()
                    , self.sensor1.get(),self.sensor2.get(),self.sensor3.get(),self.sensor4.get(),
                    self.current_string.get(),self.temp_string.get(),self.inventory.get(),self.flow_string.get(),index]
          fp.close()
        if os.path.isfile( "/home/pi/Desktop/dispenser/defaults.csv") == True:
            with open("/home/pi/Desktop/dispenser/defaults.csv","w" , newline = '') as fp:
                a = csv.writer(fp, delimiter = ",")
                data = [self.current_string.get(),index,inventory1,yest_inventory,self.recent_plate_string.get(),
                        self.current_plate_string.get(), button_state]
                a.writerow(data)
            fp.close()
            

        reset_total_op = 1
        self.new_btn.config(text = "NEW BATCH", bg = "green", command = lambda: [self.thread_check_fc()])
        for x in range(3):
            try:
                p = Usb(0x0483,0x5743, 0, 0x82, 0x01)
                p.text( '\t\t')
                p.image('/home/pi/Desktop/dispenser/egas.png')
                p.text( '\n\n\nRAJIAN GAS FIELD' + '\n'
                       + 'date/time: '+datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") +'\n'
                       + 'USER ID: '+'%s'%new_batch_var.user_id_string.get() +'\n'
                       + 'TRUCK NO.: ' + self.recent_plate_string.get() +'\n'
                       + 'TEMPERATURE: '+ self.temp_string.get() + ' C\n'
                       + 'TOTAL(KG): '+ self.current_string.get() + ' KG\n'
                       + 'PRESSURE: %.1f'%adc_read1  + ' BAR\n'
                       )
                p.cut()
                p.close()
            except:
                print('Printer Disconnected')

    def thread_check_fc(self):
        global stop_bit
        stop_bit = 1
        self.new_btn.config(state = tk.DISABLED)
            
    def setting_sms(self):
        global sButton
        global reset_msg_string
        global trigger
        global data_send
        data_send = 1
        if sButton==1:
            sms_status = "Status: {0}\n".format("BATCH STOP")
            sms_totalizer = "Total: {0} KG\n".format(self.first_string.get())
            sms_licensePlate = "Tr No: {0}\n".format(self.recent_plate_string.get())
        elif trigger == 1:
            sms_status = "Status: {0}\n".format(reset_msg_string)
        else:
            sms_status = "Status: {0}\n".format("BATCH START")
            sms_totalizer = "Total: {0} KG\n".format(self.current_string.get())
            sms_licensePlate = "Tr No: {0}\n".format(self.current_plate_string.get())
        sms_time = "Time: {0}\n".format(currentTime)
        sms_userID = "ID: {0}\n".format(current_userID)
        sms_flow = "Cur Flow: {0} KG\HR \n".format(self.flow_string.get())
        sms_inventory = "Inv: {0} KG\n".format(self.inventory.get())
        sms_temperature = "Mic Mot Temp: {0} C \n".format(self.temp_string.get())
        sms_sensor1 = "Pr 01: {0} BAR\n".format(self.sensor1.get())
        sms_sensor2 = "Pr 02: {0} BAR\n".format(self.sensor2.get())
        sms_sensor3 = "Pr 03: {0} BAR\n".format(self.sensor3.get())
        sms_sensor4 = "Temp: {0} C\n".format(self.sensor4.get())
        command = sms_status+sms_time+sms_userID+sms_licensePlate+sms_flow+sms_totalizer+sms_inventory+'\r\n'

        self.new_btn.config(state = tk.DISABLED)

        for number in numbers:
            send_sms(number, command)

        command = sms_temperature+sms_sensor1+sms_sensor2+sms_sensor3+sms_sensor4+'\r\n'
        for number in numbers:
            send_sms(number, command)

        self.new_btn.config(state = tk.NORMAL)

    def update_gui(self,worker):
        global stop_bit
        global adc_read1
        global adc_read2
        global adc_read3
        global adc_read4
##        print("tried to run")
        while stop_bit == 0:

            ##-----------Sensor 1 ------------------##
            adc_read1 = float(sen1_range)*((update_pressure(0)-offset)/(32768-offset))
            self.sensor1.set("%.1f"%adc_read1)

            ##-----------Sensor 2 ------------------##
            adc_read2 = float(sen2_range)*((update_pressure(1)-6300)/(32768-6300))
            self.sensor2.set("%.1f"%adc_read2)

            ##-----------Sensor 3 ------------------##
##            adc_read3 = float(sen3_range)*((update_pressure(2)-offset)/(32768-offset))
            adc_read3 = 0.01
            self.sensor3.set("%.1f"%adc_read3)

            ##-----------Sensor 4 ------------------##
##            adc_read4 = float(sen4_range)*((update_pressure(3)-offset)/(32768-offset))
            adc_read4 = 0.01
            self.sensor4.set("%.1f"%adc_read4)

            self.date_time_string.set(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))

            time.sleep(0.4)


##    def trigger_sms(self,worker):
##        global stop_bit
##        run = 0
##        while stop_bit == 0:
##            if trigger == 1 and run == 0:
##                self.setting_sms()
##                run = 1
##            else:
##                print("running normally")
            
        
    def run_condition(self,worker):
        global stop_bit
        global reset_msg_string
        global trigger
        trigger = 0
        time.sleep(10)
        while stop_bit == 0:
            if adc_read1 >= float(sen1_max):
##                print("sen1_max condition met")
                if trigger == 0:
                    gpio.output(10, gpio.LOW)
                    trigger = 1
                self.sensor1_entry.config(bg = 'red', fg='white')
                self.canvas.itemconfig(self.status_light,fill = 'red')
                if sen1_max_reset_mech==1:
                    reset_msg_string = "Sensor 1 Max Limit"
                    
                    
            elif adc_read1 <= float(sen1_min):
##                print("sen1_min condition met")
                if trigger == 0:
                    gpio.output(10, gpio.LOW)
                    trigger = 1
                self.sensor1_entry.config(bg = 'medium turquoise', fg='white')
                self.canvas.itemconfig(self.status_light,fill = 'red')
                if sen1_min_reset_mech==1:
                    reset_msg_string = "Sensor 1 Min Limit"
                    
            else:
##                print("no condition met")
                if sen1_max_reset_mech !=1 and trigger == 1:
                    self.canvas.itemconfig(self.status_light,fill = 'green')
                    gpio.output(10, gpio.HIGH)
                    trigger = 0
                elif sen1_max_reset_mech !=1 and trigger == 1:
                    self.canvas.itemconfig(self.status_light,fill = 'green')
                    gpio.output(10, gpio.HIGH)
                    trigger = 0
                self.sensor1_entry.config(bg = 'yellow', fg='red')
            if adc_read2 >= float(sen2_max):
##                print("sen2_max condition met")
                if trigger == 0:
                    gpio.output(10, gpio.LOW)
                    trigger = 1
                self.sensor2_entry.config(bg = 'red', fg='white')
                self.canvas.itemconfig(self.status_light,fill = 'red')
                if sen2_max_reset_mech==1:
                    reset_msg_string = "Sensor 2 Max Limit"

            elif adc_read2 <= float(sen2_min):
##                print("sen2_min condition met")
                if trigger == 0:
                    gpio.output(10, gpio.LOW)
                    trigger = 1
                self.sensor2_entry.config(bg = 'medium turquoise', fg='white')
                self.canvas.itemconfig(self.status_light,fill = 'red')
                if sen2_min_reset_mech==1:
                    reset_msg_string = "Sensor 2 Min Limit"

            else:
##                print("no condition met")
                if sen2_max_reset_mech!=1 and trigger == 1:
                    self.canvas.itemconfig(self.status_light,fill = 'green')
                    gpio.output(10, gpio.HIGH)
                    trigger = 0
                elif sen2_min_reset_mech!=1 and trigger == 1:
                    self.canvas.itemconfig(self.status_light,fill = 'green')
                    gpio.output(10, gpio.HIGH)
                    trigger = 0
                self.sensor2_entry.config(bg = 'yellow', fg='red')
            if adc_read3 >= float(sen3_max):
##                print("sen3_max condition met")
                if trigger == 0:
                    gpio.output(10, gpio.LOW)
                    trigger = 1
                self.sensor3_entry.config(bg = 'red', fg='white')
                self.canvas.itemconfig(self.status_light,fill = 'red')
                if sen3_max_reset_mech==1:
                    reset_msg_string = "Sensor 3 Max Limit"

            elif adc_read3 <= float(sen3_min):
##                print("sen3_min condition met")
                if trigger == 0:
                    gpio.output(10, gpio.LOW)
                    trigger = 1
                self.sensor3_entry.config(bg = 'medium turquoise', fg='white')
                self.canvas.itemconfig(self.status_light,fill = 'red')
                if sen3_min_reset_mech==1:
                    reset_msg_string = "Sensor 3 Min Limit"

            else:
##                print("no condition met")
                if sen3_max_reset_mech!=1 and trigger == 1:
                    self.canvas.itemconfig(self.status_light,fill = 'green')
                    gpio.output(10, gpio.HIGH)
                    trigger = 0
                elif sen3_min_reset_mech!=1 and trigger == 1:
                    self.canvas.itemconfig(self.status_light,fill = 'green')
                    gpio.output(10, gpio.HIGH)
                    trigger = 0
                self.sensor3_entry.config(bg = 'yellow', fg='red')
            if adc_read4 >= float(sen4_max):
##                print("sen4_max condition met")
                if trigger == 0:
                    gpio.output(10, gpio.LOW)
                    trigger = 1
                self.sensor4_entry.config(bg = 'red', fg='white')
                self.canvas.itemconfig(self.status_light,fill = 'red')
                if sen4_max_reset_mech==1:
                    reset_msg_string = "Sensor 4 Max Limit"
                    
            elif adc_read4 <= float(sen4_min):
##                print("sen4_min condition met")
                if trigger == 0:
                    gpio.output(10, gpio.LOW)
                    trigger = 1
                self.sensor4_entry.config(bg = 'medium turquoise', fg='white')
                self.canvas.itemconfig(self.status_light,fill = 'red')
                if sen4_min_reset_mech==1:
                    reset_msg_string = "Sensor 4 Min Limit"
                 
            else:
##                print("no condition met")
                if sen4_max_reset_mech!=1 and trigger == 1:
                    self.canvas.itemconfig(self.status_light,fill = 'green')
                    gpio.output(10, gpio.HIGH)
                    trigger = 0
                elif sen4_min_reset_mech!=1 and trigger == 1:
                    self.canvas.itemconfig(self.status_light,fill = 'green')
                    gpio.output(10, gpio.HIGH)
                    trigger = 0
                self.sensor4_entry.config(bg = 'yellow', fg='red')
            if gpio.input(21) and trigger == 1:
                self.canvas.itemconfig(self.status_light,fill = 'green')
                gpio.output(10, gpio.HIGH)
                trigger = 0

    def update_totalizer(self,worker):
        global stop_bit
        global total
        global inventory
        global inventory1
        global temp
        global current_inventory
        global yest_inventory
        global hr_set
        global sms_sent
        global reset_total_op
        fc_ran = 0
        while stop_bit == 0:
            ##-------------------MASS TOTAL---------------##
            with self.lock:
                  try:
                      values = instrument.read_registers(258, 2, 3)
                      b = struct.pack('HH', values[0],values[1])
                      total = float(struct.unpack('f',b)[0])
##                      print(total)
                  except:
                      total = 0.0
            ##-------------------INVENTORY---------------##
            with self.lock:
                  try:
                      values = instrument.read_registers(262, 2, 3)
                      b = struct.pack('HH', values[0],values[1])
                      inventory = float(struct.unpack('f',b)[0])
                  except:
                      inventory = 0.0
            ##-------------------TEMPRATURE---------------##    
            with self.lock:
                  try:
                      values = instrument.read_registers(250, 2, 3)
                      b = struct.pack('HH', values[0],values[1])
                      temp = float(struct.unpack('f',b)[0])
                  except:
                      temp = 0.0
            ##-------------------FLOW MASS---------------##
            with self.lock:
                  try:        
                      values = instrument.read_registers(246, 2, 3)
                      b = struct.pack('HH', values[0],values[1])
                      flow = float(struct.unpack('f',b)[0])
                  except:
                      flow = 0.0

            if reset_total_op == 1:
                    try:
                        values = instrument.write_bit(55,1,5)
                        reset_total_op = 0
                    except :
                        raise_error("Communication Error")
                        print("Failed")

            if datetime.datetime.now().strftime("%H:%M:%S") == "23:59:00" and fc_ran == 0:
##            if int(datetime.datetime.now().strftime("%H")>= int(hr_set) and int(datetime.datetime.now().strftime("%M")>= int(min_set) and fc_ran == 0:
                self.new_btn.config(state = tk.DISABLED)
                try:
                    p = Usb(0x0483,0x5743, 0, 0x82, 0x01)
                    p.text( '\t\t')
                    p.image('/home/pi/Desktop/dispenser/egas.png')
                    p.text(  '\n\n\nRAJIAN GAS FIELD' + '\n'
                           + 'date/time: '+datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S") +'\n'
                           + '24 HR KG: ' + "%.1f"%current_inventory + ' KG' + '\n'
                           + 'INVENTORY: ' + "%.1f"%inventory + ' KG' + '\n'
                           )
                    p.cut()
                    p.close()
                except:
                    print('Printer Disconnected')
                yest_inventory = current_inventory
                print(current_inventory)
                print(yest_inventory)
                inventory1 = inventory
                ##                    command = datetime.datetime.now().strftime("%d-%m-%Y") +" Inventory :{0}".format(yest_inventory)+ "\r\n"

                if os.path.isfile( "/home/pi/Desktop/dispenser/defaults.csv") == True:
                    with open("/home/pi/Desktop/dispenser/defaults.csv","w" , newline = '') as fp:
                        a = csv.writer(fp, delimiter = ",")
                        data = [self.current_string.get(),index,inventory1,yest_inventory,self.recent_plate_string.get(),
                                self.current_plate_string.get(), button_state]
                        a.writerow(data)
                    fp.close()
                fc_ran = 1

                    
                    
                    
            if datetime.datetime.now().strftime("%H:%M:%S") == "00:02:00" and fc_ran == 1:
                fc_ran = 0
                sms_sent = 0
                self.new_btn.config(state = tk.NORMAL)

            if temp != 0.0:
                self.flow_string.set("%.1f"%flow)
            
                self.temp_string.set("%.1f"%temp)
            
                self.current_string.set("%.1f" %total)
            
                self.inventory.set("%.1f" %inventory)
##                print(inventory1)
                current_inventory = inventory -  inventory1

                self.totalizer_24hr.set("%.1f"%float(current_inventory))

                self.totalizer_yest.set("%.1f"%float(yest_inventory))
                
            else:
                self.flow_string.set("Error")
            
                self.temp_string.set("Error")
            
                self.current_string.set("Error")
            
                self.inventory.set("Error")
                
    def run_sms(self, worker):
        global userID
        global license_plate
        global sButton
        global sms_sent
        global current_inventory
        global yest_inventory
        global trigger
        global hr_set
        if data_send == 0:
            self.setting_sms()
        check = ''
        while stop_bit == 0:
            print("Checking Operator")
            command = "AT+COPS?\r\n"
            port.write(bytes(command, 'utf-8'))
            rcv = port.read(10)
            print(rcv.decode('utf-8'))
            rcv = port.read(10)
            check_error = rcv.decode('utf-8')
            print(rcv.decode('utf-8'))
            rcv = port.read(10)
            print(rcv.decode('utf-8'))
            time.sleep(1)
            try:
                self.provider.config(text= check_error[4:8])
            except:
                self.provider.config(text= 'ERROR-151')
            #checking signal Strength
            command = "AT+CSQ\r\n"
            port.write(bytes(command, 'utf-8'))
            rcv = port.read(10)
            print("Checking Signal Strength")
            print(rcv.decode('utf-8'))
            try:
                self.signal_label.config(text= rcv)
            except:
                self.signal_label.config(text = 'ERROR-152')
            #deleting all sms
            command = "AT+CMGD=1,4\r\n"
            port.write(bytes(command, 'utf-8'))
            rcv = port.read(10)
            print("Deleting all sms")
            print(rcv.decode('utf-8'))
            ##indication for new sms
            command = "AT+CNMI=2,1,0,0,0\r\n"
            port.write(bytes(command, 'utf-8'))
            rcv = port.read(10)
            print("Set in Recieving mode")
            print(rcv.decode('utf-8'))
            ck= 1
            port.flush()
            rcv = ''
            check_time = time.perf_counter() + 30
            d_time = time.perf_counter() + 10
            print("d_time : %s" %d_time)
            while ck==1 and stop_bit == 0:

                run = 0

                if check_time < time.perf_counter():
                    #checking signal Strength
                    command = "AT+CSQ\r\n"
                    port.write(bytes(command, 'utf-8'))
                    rcv = port.read(10)
                    print("Checking Signal Strength")
                    print(rcv.decode('utf-8'))
                    try:
                        self.signal_label.config(text= rcv)
                    except:
                        self.signal_label.config(text = 'ERROR-152')
                    port.flush()
                    rcv = ''
                    check_time = time.perf_counter() + 30
                
                if sButton==1:
                    self.setting_sms()
                    port.flush()
                    rcv = ''
                    ck = 2
                    sButton=0
##                if trigger == 1 and run == 0 and time.perf_counter() > d_time:
##                    self.setting_sms()
##                    port.flush()
##                    rcv = ''
##                    run = 1
##                    ck = 2
##                    d_time = time.perf_counter()+ 10
##                    print("d_time : %s" %d_time
                if datetime.datetime.now().strftime("%H:%M:%S") == "23:59:01" and sms_sent == 0:
                    command = datetime.datetime.now().strftime("%d-%m-%Y") +"\n"+"24 HR KG : %.1f"%yest_inventory+ ' KG'+"\n" +"TOTAL INV: "+ "%.1f"%float(inventory) + ' KG'+"\r\n" 


                    for number in numbers:
                        send_sms(number, command)
                    try:
                        send_email()
                    except:
                        print("FAILED REASON UNKNOWN")
                    
                    port.flush()
                    rcv = ''

                    sms_sent = 1
                    ck = 2
                    

##                    if os.path.isfile( "/home/pi/Desktop/dispenser/defaults.csv") == True:
##                        with open("/home/pi/Desktop/dispenser/defaults.csv","w" , newline = '') as fp:
##                            a = csv.writer(fp, delimiter = ",")
##                            data = [self.current_string.get(),index,current_inventory,yest_inventory,self.recent_plate_string.get(),
##                                    self.current_plate_string.get()]
##                            a.writerow(data)
##                        fp.close()

##                if datetime.datetime.now().strftime("%H:%M:%S") == str(hr_set)+":"+str(shut_off)+":00" and sms_sent == 1:
##                    sms_sent = 0
                rcv = port.read(10)
                error_check = rcv.decode('utf-8')
                fd=rcv

                if error_check.find('ERROR') != -1:
                    ck = 2
##                print(rcv.decode('utf-8'))
                
                elif error_check.find('+CMTI') != -1:
                    ck=2
                    
                    rcv = port.read(10)
                    print(rcv.decode('utf-8'))
                    fd = fd+rcv
                    string_find= fd.decode('utf-8')
            ##            print(string_find)
                    p = string_find.find(",")
                    q = string_find.find("\r")
                    MsgNo=string_find[p+1:q-2]

            ##        print(MsgNo)
                    rd = port.write(bytes("AT+CMGR="+MsgNo+"\r\n", 'utf-8'))
                    msg=''
                    for j in range(10):
                        rcv = port.read(10)
                        msg= msg+rcv.decode('utf-8')
                    print(msg)
                    string_find = msg
                    ##print(string_find[21])
                    p = string_find.find("+9")
                    q = p+13
                    print(p)
                    print(q)
                    mobile_number = string_find[p:q]
                    print(mobile_number)
                    if msg.find("+923335344279") != -1 or msg.find("+923235101094") != -1 or msg.find("+923335101020") != -1 or msg.find("+923422343434") != -1 or msg.find("+923225102421") != -1:
                        print("Entered if condition")

                        if sButton==1:
                            sms_status = "Status: {0}\n".format("BATCH STOP")
                        else:
                            sms_status = "{0}\n".format("BATCH START")
                        sms_time = "Time: {0}\n".format(currentTime)
                        sms_userID = "ID: {0}\n".format(current_userID)
                        sms_licensePlate = "Truck No: {0}\n".format(self.current_plate_string.get())
                        sms_flow = "Current Flow: {0} KG\HR \n".format(self.flow_string.get())
                        sms_totalizer = "Total: {0} KG\n".format(self.current_string.get())
                        sms_inventory = "Inv: {0} KG\n".format(self.inventory.get())
                        sms_temperature = "Mic Mot Temp: {0} C \n".format(self.temp_string.get())
                        sms_sensor1 = "Pr 01: {0} BAR\n".format(self.sensor1.get())
                        sms_sensor2 = "Pr 02: {0} BAR\n".format(self.sensor2.get())
                        sms_sensor3 = "Pr 03: {0} BAR\n".format(self.sensor3.get())
                        sms_sensor4 = "Temp: {0} C\n".format(self.sensor4.get())
                        command = sms_status+sms_time+sms_userID+sms_licensePlate+sms_flow+sms_totalizer+sms_inventory+'\r\n'
                        self.new_btn.config(state = tk.DISABLED)
                        send_sms(mobile_number,command)
                        command = sms_temperature+sms_sensor1+sms_sensor2+sms_sensor3+sms_sensor4+'\r\n'
                        send_sms(mobile_number,command)
                        self.new_btn.config(state = tk.NORMAL)

                    else:
                        print("Entered else condition")
                        string_find = msg
                        ##print(string_find[21])
                        p = string_find.find("+9")
                        q = p+13
                        print(p)
                        print(q)
                        mobile_number = string_find[p:q]
                        print(mobile_number)
                        ##select message format as text mode
                        command = 'AT+CMGF=1\r\n'
                        port.write(bytes(command, 'utf-8'))
                        rcv = port.read(10)
                        print(rcv.decode("utf-8"))
                        time.sleep(1)
                        port.flush()
                        command = "Not Authorized to Check Data"+'\r\n'
                        self.new_btn.config(state = tk.DISABLED)
                        send_sms(mobile_number, command)
                        self.new_btn.config(state = tk.NORMAL)
                        
##                        ##sending a message to a particular number
##                        command = 'AT+CMGS="'+mobile_number+'"\r\n'
##                        port.write(bytes(command, 'utf-8'))
##                        rcv = port.read(10)
##                        print(rcv.decode("utf-8"))
##                        time.sleep(1)
##                        command = "Not Authorized to Check Data"+'\r\n'
##                        port.write(bytes(command, 'utf-8'))
##                        rcv = port.read(10)
##                        print(rcv.decode("utf-8"))
##                        command = "\x1A"
##                        port.write(bytes(command, 'utf-8'))

                    ##reading response from the gsm module
##                    for i in range(10):
##                        rcv = port.read(10)
##                        print(rcv.decode("utf-8"))
##                        time.sleep(0.1)
##            except:
##                pass

##    def trigger_email(self, worker):
##
##        while stop_bit == 1:
##
##            def send_email(subject, msg):
##                try:
##                    server = smtplib.SMTP('smtp.gmail.com:587')
##                    server.ehlo()
##                    server.starttls()
##                    server.login(EMAIL,PASSWORD)
##                    server.sendmail(EMAIL, TO_EMAIL, msg)
##                    server.quit()
##                    print("Success: Email sent!")
##                except:
##                    print("Email failed to send.")
##
##
##
##            if datetime.datetime.now().stfrtime('%H:%M:%S') == '14:35:00':
##                subject = "Python Email Test"
##                body = "This is an automated email generated.\n __author__ = 'Umair'"
##
##                msg  = MIMEMultipart()
##                msg['From'] = EMAIL
##                msg['To'] = TO_EMAIL
##                msg['Subject'] = subject
##
##                msg.attach(MIMEText(body,'plain'))
##                file_date = datetime.datetime.now().strftime('%Y')+'/'+datetime.datetime.now().strftime('%B')+'/'
##                filename_email = '/home/pi/Desktop/dispenser/data/'+file_date+datetime.datetime.now().strftime('%d-%B-%Y')+'.csv'
##                print(filename_email)
##                attachment = open(filename_email, 'rb')
##
##                part = MIMEBase('application', 'octet-strean')
##                part.set_payload((attachment).read())
##                encoders.encode_base64(part)
##                part.add_header('Content-Disposition',"attachment; filename= "+datetime.datetime.now().strftime('%d-%B-%Y'))
##
##                msg.attach(part)
##                text = msg.as_string()
##                send_email(subject, text)
##                attachment.close()
##            else:
##                time.sleep(1)
        
    def on_show_frame(self,event):
        print("running on show frame")
        global stop_bit
        try:
            values = instrument.read_registers(258, 2, 3)
            b = struct.pack('HH', values[0],values[1])
            total = float(struct.unpack('f',b)[0])
        except:
            total = 0.0
        stop_bit = 0
        self.new_btn.config(state = tk.NORMAL)
        if not self.t0.isAlive():
            print("t0 is alive")
            self.t0 = threading.Thread(target = self.counter_thread)
            self.t0.start()
        if not self.t1.isAlive():
            self.t1 = threading.Thread(target = self.totlizer_thread)
            self.t1.start()
##        if not self.t2.isAlive():
##            self.t2 = threading.Thread(target = self.trigger_email_thread)
##            self.t2.start()            
        if not self.t3.isAlive():
            self.t3 = threading.Thread(target = self.sms_thread)
            self.t3.start()
        if not self.t4.isAlive():
            self.t4 = threading.Thread(target = self.condition_thread)
            self.t4.start()
        self.q.put(0)
        self.q.put(1)
        self.q.put(2)
        self.q.put(3)
        self.q.put(4)
        self.q.put(5)
##        self.q.put(6)
        self.lock = threading.Lock()



    def counter_thread(self):
        while True:
            self.worker = self.q.get()
            self.update_gui(self.worker)
            self.q.task_done()
            self.q.join()
            self.tasks_done()
            
    def totalizer_thread(self):
        while True:
            self.worker = self.q.get()
            self.update_totalizer(self.worker)
            self.q.task_done()
    def trigger_email_thread(self):
        while True:
            self.worker = self.q.get()
            self.trigger_email(self.worker)
            self.q.task_done()

    def condition_thread(self):
        while True:
            self.worker = self.q.get()
            self.run_condition(self.worker)
            self.q.task_done()

    def sms_thread(self):
        while True:
            self.worker = self.q.get()
            self.run_sms(self.worker)
            self.q.task_done()

            
    def tasks_done(self):
        global stop_bit
        global thread_check
        global reset_msg_string
        gpio.output(9, gpio.LOW)
        print("all task completed")
        thread_check = 1
        if setting_btn == 1:
            self.controller.show_frame(SettingPage)
        else:
            self.controller.show_frame(NewBatch)
##        if stop_bit == 2:
##            top = Toplevel()
##            top.title("Warning")
##            top.config(height = 800, width = 500)
##            top_message = Message(top, font= MEDIUM_FONT, text=reset_msg_string)
##            top_message.pack()
##            def check_input():
##                if gpio.input(25):
##                    top.destroy()
##                    self.bind("<<onend>>", self.controller.show_frame(StartPage))
##                else:
##                    self.after(1000,check_input)
##            self.after(1000, check_input)
        
        
    
class NewBatch(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
            
        entry_field_frame = tk.LabelFrame(self, font = SMALL_FONT)
        entry_field_frame.place(x=400, y =20)

        plate_number = tk.Label(entry_field_frame , text ="Licensce Plate Number", fg= "red", font = SMALL_FONT)
        plate_number.grid(row =0 , column= 0)

        self.plate_string = StringVar()
        self.plate_entry = tk.Entry(entry_field_frame , font = MEDIUM_FONT,textvariable = self.plate_string, width = 7 )
        self.plate_entry.grid(row=1, column=0, padx=5, pady=5)



        user_id_label = tk.Label(entry_field_frame , text ="User ID", fg= "red", font = SMALL_FONT)
        user_id_label.grid(row =2 , column= 0,)

        self.user_id_string = StringVar()
        self.user_id_entry = tk.Entry(entry_field_frame , font = MEDIUM_FONT, textvariable = self.user_id_string, width = 7)
        self.user_id_entry.grid(row=3, column=0)

        data_field_frame = tk.LabelFrame(self, font = SMALL_FONT)
        data_field_frame.place(x=20, y =300)

        date_field_label = tk.Label(data_field_frame, font = SMALL_FONT, text = "DATE/TIME")
        date_field_label.grid(row=0, column=0)



        self.date_time_label = tk.Label(data_field_frame, text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        font = SMALL_FONT)
        self.date_time_label.grid(row = 1, column =0)
            
        ok_button = tk.Button(self, font = MEDIUM_FONT, text = "OK", bg = "green", fg = "white",
                                   command = lambda: self.OK_Button(), width = 4, height =1)
        ok_button.place(x =550 , y=300 )

    def OK_Button(self):
        global stop_bit
        global index
        global userID
        global license_plate
        global data_send
        global currentTime
        global current_userID
        global current_license_plate
        global thread_check
        global button_state
        button_state = False
        currentTime = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        index += 1
        userID = self.user_id_string.get()
        current_userID = self.user_id_string.get()
        start_page_var = self.controller.get_page(StartPage)
        license_plate = self.plate_string.get()
        current_license_plate = self.plate_string.get()
        start_page_var.current_plate_string.set(self.plate_string.get())


##        file_check()        

        ##Saving data all in one place for local viewing
        if os.path.isfile( "/home/pi/Desktop/dispenser/data/"+datetime.datetime.now().strftime("%Y")+"/"+datetime.datetime.now().strftime("%B")+"/"+datetime.datetime.now().strftime("%d-%B-%Y")+".csv") == True:
            with open("/home/pi/Desktop/dispenser/data/"+datetime.datetime.now().strftime("%Y")+"/"+datetime.datetime.now().strftime("%B")+"/"+datetime.datetime.now().strftime("%d-%B-%Y")+".csv","a" , newline = '') as fp:
                a = csv.writer(fp, delimiter = ",")
                data = ["BATCH START",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.user_id_string.get(),self.plate_string.get()
                        , start_page_var.sensor1.get(),start_page_var.sensor2.get(),start_page_var.sensor3.get(),start_page_var.sensor4.get(),
                        start_page_var.current_string.get(),start_page_var.temp_string.get(),start_page_var.inventory.get(),start_page_var.flow_string.get(),index]
                a.writerow(data)
                print("file saved for local viewing")
            fp.close()
        else:
            with open("/home/pi/Desktop/dispenser/data/"+datetime.datetime.now().strftime("%Y")+"/"+datetime.datetime.now().strftime("%B")+"/"+datetime.datetime.now().strftime("%d-%B-%Y")+".csv","w" ,
                    newline = '') as fp:
                a = csv.writer(fp, delimiter = ",")
                data = ["BATCH START",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.user_id_string.get(),self.plate_string.get()
                        , start_page_var.sensor1.get(),start_page_var.sensor2.get(),start_page_var.sensor3.get(),start_page_var.sensor4.get(),
                        start_page_var.current_string.get(),start_page_var.temp_string.get(),start_page_var.inventory.get(),start_page_var.flow_string.get(),index]
                a.writerow(data)
                print("else file saved for local viewing")
            fp.close()
        ##recent batch save file in defaults.csv
        if os.path.isfile( "/home/pi/Desktop/dispenser/defaults.csv") == True:
            with open("/home/pi/Desktop/dispenser/defaults.csv","w" , newline = '') as fp:
                a = csv.writer(fp, delimiter = ",")
                data = [start_page_var.first_string.get(),index,inventory1,yest_inventory,start_page_var.recent_plate_string.get(),
                        start_page_var.current_plate_string.get(), button_state]
                a.writerow(data)
                print("defaults saved")
            fp.close()
        else:
            with open("/home/pi/Desktop/dispenser/defaults.csv","w" , newline = '') as fp:
                a = csv.writer(fp, delimiter = ",")
                data = [0,0,0.0,0.0,0,0,0]
                a.writerow(data)
            fp.close()

        data_send = 0
        start_page_var.current_string.set("%0.1f"%float(mass_total()))
        gpio.output(9, gpio.HIGH)
        thread_check = 0
        start_page_var.new_btn.config(text = "STOP", bg = "red", command = lambda: [start_page_var.stop_btn()], state = tk.NORMAL)
        self.controller.show_frame(StartPage)

class Error(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller
        self.Error_variable = StringVar()
        self.Key_variable = StringVar()
        Error_Label = tk.Label(self, text = "Error 104", font = SPECIAL_FONT, fg = "red" )
        Error_Label.place(x = 400, y =150)
        Error_Entry = tk.Entry(self, textvariable = self.Error_variable, font = SPECIAL_FONT, width = 16)
        Error_Entry.place(x =300, y = 200)
        Key_Entry = tk.Entry(self, textvariable = self.Key_variable, font = SPECIAL_FONT, width = 16, show = "*")
        Key_Entry.place(x =300, y = 300)
        Warning_Label = tk.Label(self, text = "WARNING!!! SYSTEM IS LOCKED \nCALL SYSTEM MANUFACTURER", font = SPECIAL_FONT, fg = "red" )
        Warning_Label.place(x = 200, y =450)

        Verify_button = tk.Button(self, text = "Verify", font = SPECIAL_FONT,
                                  command = lambda: self.Verify_Key())
        Verify_button.place(x = 400, y = 380)

    def Verify_Key(self):
        temp_key = getserial()
        print(temp_key)
        if self.Error_variable.get() == temp_key and self.Key_variable.get() == unique_pass:
            with open("/sbin/key.csv","w" , newline = '') as fp:
                a = csv.writer(fp, delimiter = ",")
                data = [temp_key]
                a.writerow(data)
            fp.close()
            self.controller.show_frame(StartPage)

        else:
            self.Error_variable.set("19u&K1Lp1-198")
            self.Key_variable.set("458-962-3")

        
class SettingPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
##        label = tk.Label(self, text = "Settings page", font= xLARGE_FONT )
##        label.pack()

        #back button
        back_button = tk.Button(self, text = "<-Back", font = SMALL_FONT, bg = 'blue', fg = 'white',
                                command= lambda: controller.show_frame(StartPage))
        back_button.place(x = 20, y= 665)
        #System configuration Button
        system_button = tk.Button(self,text = "System \nConfiguration", font=SMALL_FONT, bg = "red", fg="white",
                                  command= lambda:controller.show_frame(SystemConfiguration))
        system_button.place(x=840,y=15)

        #AdministrativeChanges Button
        system_button = tk.Button(self,text = "Administrative \nSettings", font=SMALL_FONT, bg = "blue", fg="white",
                                  command= lambda:controller.show_frame(AdministrativeChanges))
        system_button.place(x=840,y=70)
        #Folder Year Place
        folder_year_label = tk.LabelFrame(self, text= "YEAR" ,font =SMALL_FONT, bd=10)
        folder_year_label.place(x=20,y=10)

        self.g= Listbox(folder_year_label, height =5, selectmode = BROWSE , font = SMALL_FONT)
        self.g.grid(column=0, row=0, sticky=(N,S))
        m= ttk.Scrollbar(folder_year_label, orient = VERTICAL, command = self.g.yview)
        m.grid(column =1, row =0, sticky=(N,S))
        self.g['yscrollcommand'] = m.set

        for filename in get_foldername():
            self.g.insert(END, filename)

        #Folder Month Place
        folder_label = tk.LabelFrame(self, text= "MONTH" ,font =SMALL_FONT, bd=10)
        folder_label.place(x=290,y=10)

        self.f= Listbox(folder_label, height =5, selectmode = BROWSE , font = SMALL_FONT)
        self.f.grid(column=0, row=0, sticky=(N,S))
        n= ttk.Scrollbar(folder_label, orient = VERTICAL, command = self.f.yview)
        n.grid(column =1, row =0, sticky=(N,S))
        self.f['yscrollcommand'] = n.set

        #File place
        file_label = tk.LabelFrame(self, text= "DAY" ,font =SMALL_FONT, bd=10)
        file_label.place(x=560,y=10)

        self.l= Listbox(file_label, height =5, selectmode = BROWSE , font = SMALL_FONT)
        self.l.grid(column=0, row=0, sticky=(N,S))
        s= ttk.Scrollbar(file_label, orient = VERTICAL, command = self.l.yview)
        s.grid(column =1, row =0, sticky=(N,S))
        self.l['yscrollcommand'] = s.set

##        #camera file place
##        camera_label = tk.LabelFrame(self, text= "CAMERA FILES" ,font =SMALL_FONT, bd=10)
##        camera_label.place(x=750,y=450)
##
##        self.k= Listbox(camera_label, height =5, selectmode = BROWSE , font = SMALL_FONT)
##        self.k.grid(column=0, row=0, sticky=(N,S))
##        q= ttk.Scrollbar(camera_label, orient = VERTICAL, command = self.k.yview)
##        q.grid(column =1, row =0, sticky=(N,S))
##        self.k['yscrollcommand'] = q.set
##        self.file_path = "/home/pi/Desktop/dispenser/data/camera/"
##        for filename in get_filename(self.file_path):
##            self.k.insert(END, filename)


        self.file_path = ""
        self.file_year_path = ""

##        picture_canvas_frame = tk.LabelFrame(self)
##        picture_canvas_frame.place(x = 730, y= 145)
##
##        self.canvas_pic = tk.Canvas(picture_canvas_frame, width=300, height=300)
##
##        img = Image.open('/home/pi/Desktop/dispenser/data/camera/demo.png')
##        self.canvas_pic.image = ImageTk.PhotoImage(img)
##        self.canvas_pic.create_image(0, 0, image=self.canvas_pic.image, anchor='nw')
##
##        self.canvas_pic.pack(fill=BOTH, expand=1)
##
        canvas_frame =tk.LabelFrame(self)
        canvas_frame.place(x=20, y =145)

        canvas_reader = tk.Canvas(canvas_frame, width=710, height=490, scrollregion = (0,0,500,10000))

 

        scrollb=tk.Scrollbar(canvas_frame, orient = "vertical", command=canvas_reader.yview)
        scrollb.pack(side = "right", fill = "y")

        scrollx=tk.Scrollbar(canvas_frame, orient = "horizontal", command=canvas_reader.xview)
        scrollx.pack(side = "bottom", fill = "x")

        canvas_reader['yscrollcommand'] = scrollb.set
        canvas_reader.pack(side = 'right', fill = 'y')

        canvas_reader['xscrollcommand'] = scrollx.set
        canvas_reader.pack(side = 'bottom', fill = 'x')

        self.hide = tk.LabelFrame(canvas_reader, width =710, height=700)
        self.hide.place(x=0,y=0)

##        def show_camera_files():
##            items = self.k.curselection()
##            item_name = self.k.get(items)
##            self.canvas_pic.delete('all')
##            img = Image.open('/home/pi/Desktop/dispenser/data/camera/'+item_name)
##            self.canvas_pic.image = ImageTk.PhotoImage(img)
##            self.canvas_pic.create_image(0, 0, image=self.canvas_pic.image, anchor='nw')
                    

        def folder_callback():
            self.l.delete(0 , END)
            items = self.f.curselection()
            item_name = self.f.get(items)
            self.file_path = self.file_year_path + item_name + "/"
            for filename in get_filename(self.file_path):
                self.l.insert(END, filename)
        def folder_year_callback():
            self.f.delete(0 , END)
            items = self.g.curselection()
            item_name = self.g.get(items)
            self.file_year_path = folderpath + item_name + "/"
            for filename in get_folder_year_name():
              self.f.insert(END, filename)

        def callback():
            items = self.l.curselection()
            item_name = self.l.get(items)
            self.hide.tkraise()
            freader_label = tk.LabelFrame(canvas_reader, text = "", font = MEDIUM_FONT, bd =10, fg= 'red')
            freader_label.place(x=0, y=0)

            def onFrameConfigure(self):
                canvas_reader.configure(scrollregion = canvas_reader.bbox('all'))

            canvas_reader.create_window((4,4) ,window=freader_label, anchor = "nw",
                                    tags = "freader_label")
            freader_label.bind("<Configure>", onFrameConfigure)

            with open('/home/pi/Desktop/dispenser/header.csv', newline = '') as fp:
                reader = csv.reader(fp)            
                r=0
                for col in reader:
                        c=0
                        for row in col:

                            label = tk.Label(freader_label, width =18, height =2,
                                             text= row, relief = tk.RIDGE)
                            label.grid(row=r, column=c)
                            c +=1
                        r+=1
            fp.close()
            with open(self.file_path +item_name, newline = '') as file:
                reader = csv.reader(file)

                r=1
                for col in reader:
                        c=0
                        for row in col:

                            label = tk.Label(freader_label, width =18, height =2,
                                             text= row, relief = tk.RIDGE)
                            label.grid(row=r, column=c)
                            c +=1
                        r+=1
            file.close()

        button = tk.Button(file_label, text= "VIEW", command = callback, width = 1)
        button.grid(row=0, column=2, sticky= (N,S,E,W))
        folder_button = tk.Button(folder_label, text= "VIEW", command = folder_callback, width = 1)
        folder_button.grid(row=0, column=2, sticky= (N,S,E,W))
        folder_year_button = tk.Button(folder_year_label, text= "VIEW", command = folder_year_callback, width = 1)
        folder_year_button.grid(row=0, column=2, sticky= (N,S,E,W))

        self.bind("<<Stop>>", self.stop_threads)

    def stop_threads(self,event):
        global stop_bit
        global setting_btn
        setting_btn = 0
        stop_bit = 1
        gpio.output(9, gpio.LOW)

class SystemConfiguration(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)

        #back button
        back_button = tk.Button(self, text = "<-Back", font = SMALL_FONT, bg = 'blue', fg = 'white',
                                command= lambda: controller.show_frame(SettingPage))
        back_button.place(x = 800, y= 665)

        #-----------------------------------------------OUTPUT FRAME----------------------------------------------#
        output_frame = tk.LabelFrame(self, bd =10)
        output_frame.place(x=10, y=10)

        #------------------SENSOR 1 FRAME----------------------#
        sensor1_frame = tk.LabelFrame(output_frame, text = "Sensor1", bd =10)
        sensor1_frame.grid(row=1, column=0, padx=5, pady=5)
        #----------------PRESSURE SENSOR 1 MINIMUM LIMIT--------------------#
        #-----------LABEL---------#
        sensor1_min = tk.Label(sensor1_frame, font = SMALL_FONT, text = "Minimum Limit")
        sensor1_min.grid(row=0, column=0, padx=5,pady=5)
        #-----------TEXT STRING---------#
        self.sen1_min_string = tk.StringVar()
        #-----------ENTRY---------#
        self.sen1_min_entry = tk.Entry(sensor1_frame, font= SMALL_FONT, textvariable = self.sen1_min_string, width =4)
        self.sen1_min_entry.grid(row=0, column=1, padx=5, pady=5)
        #-----------BUTTON---------#
        self.sen1_min_button = tk.Button(sensor1_frame, font = SMALL_FONT, text = "CHANGE LIMIT",
                                         command = lambda: [change_limits("sensor1 min"),self.update_limits()])
        self.sen1_min_button.grid(row=0, column=2, padx=5, pady=5)


        #----------------PRESSURE SENSOR 1 MAXIMUM LIMIT--------------------#

        #-----------LABEL---------#
        sensor1_max = tk.Label(sensor1_frame, font = SMALL_FONT, text = "Maximum Limit")
        sensor1_max.grid(row=1, column=0, padx=5,pady=5)
        #-----------TEXT STRING---------#
        self.sen1_max_string = tk.StringVar()
        #-----------ENTRY---------#
        self.sen1_max_entry = tk.Entry(sensor1_frame, font= SMALL_FONT, textvariable = self.sen1_max_string, width =4)
        self.sen1_max_entry.grid(row=1, column=1, padx=5, pady=5)
        #-----------BUTTON---------#
        self.sen1_max_button = tk.Button(sensor1_frame, font = SMALL_FONT, text = "CHANGE LIMIT",
                                         command = lambda: [change_limits("sensor1 max"),self.update_limits()])
        self.sen1_max_button.grid(row=1, column=2, padx=5, pady=5)

        #----------------PRESSURE SENSOR 1 MAX RESET MECH--------------------#
        #-----------LABEL---------#
        sen1_max_reset_label = tk.Label(sensor1_frame, font = SMALL_FONT, text = "MAX")
        sen1_max_reset_label.grid(row=2, column= 0, padx=5, pady =5)
        #-----------FUNCTION BUTTON---------#
        def sen1_max_btn(reset_mech):
            global sen1_max_reset_mech
            sen1_max_reset_mech = reset_mech
            if os.path.isfile( "/home/pi/Desktop/dispenser/SystemConfiguration.csv") == True:
                with open("/home/pi/Desktop/dispenser/SystemConfiguration.csv","w" , newline = '') as fp:
                    a = csv.writer(fp, delimiter = ",")
                    data = [sen1_max,sen1_min,sen2_max,sen2_min,sen3_max,sen3_min,sen4_max,sen4_min,
                            sen1_max_reset_mech,sen1_min_reset_mech,sen2_max_reset_mech,sen2_min_reset_mech,
                            sen3_max_reset_mech,sen3_min_reset_mech,sen4_max_reset_mech,sen4_min_reset_mech,
                            sen1_range,sen2_range,sen3_range,sen4_range]
                    a.writerow(data)
                fp.close()
        #-----------TEXT STRING---------#
        self.sen1_max_reset_string = tk.StringVar()
        #-----------AUTO BUTTON---------#
        self.sen1_max_auto_button = tk.Button(sensor1_frame, font = SMALL_FONT, text = "AUTO",
                                          command = lambda : [sen1_max_btn(0) , self.update_limits()])
        self.sen1_max_auto_button.grid(row=3, column=0, padx=5, pady=5)
        #-----------RESET ENTRY---------#
        self.sen1_max_reset_entry = tk.Entry(sensor1_frame, font= SMALL_FONT, textvariable = self.sen1_max_reset_string, width =4)
        self.sen1_max_reset_entry.grid(row=3, column=1, padx=5, pady=5)
        #-----------MANUAL BUTTON---------#
        self.sen1_max_man_button = tk.Button(sensor1_frame, font = SMALL_FONT, text = "MANUAL",
                                         command = lambda : [sen1_max_btn(1) , self.update_limits()])
        self.sen1_max_man_button.grid(row=3, column=2, padx=5, pady=5)

        #----------------PRESSURE SENSOR 1 MIN RESET MECH--------------------#
        #-----------LABEL---------#
        sen1_min_reset_label = tk.Label(sensor1_frame, font = SMALL_FONT, text = "MIN")
        sen1_min_reset_label.grid(row=4, column= 0, padx=5, pady =5)
        #-----------FUNCTION BUTTON---------#
        def sen1_min_btn(reset_mech):
            global sen1_min_reset_mech
            sen1_min_reset_mech = reset_mech
            if os.path.isfile( "/home/pi/Desktop/dispenser/SystemConfiguration.csv") == True:
                with open("/home/pi/Desktop/dispenser/SystemConfiguration.csv","w" , newline = '') as fp:
                    a = csv.writer(fp, delimiter = ",")
                    data = [sen1_max,sen1_min,sen2_max,sen2_min,sen3_max,sen3_min,sen4_max,sen4_min,
                            sen1_max_reset_mech,sen1_min_reset_mech,sen2_max_reset_mech,sen2_min_reset_mech,
                            sen3_max_reset_mech,sen3_min_reset_mech,sen4_max_reset_mech,sen4_min_reset_mech,
                            sen1_range,sen2_range,sen3_range,sen4_range]
                    a.writerow(data)
                fp.close()
        #-----------TEXT STRING---------#
        self.sen1_min_reset_string = tk.StringVar()
        #-----------AUTO BUTTON---------#
        self.sen1_min_auto_button = tk.Button(sensor1_frame, font = SMALL_FONT, text = "AUTO",
                                          command = lambda : [sen1_min_btn(0) , self.update_limits()])
        self.sen1_min_auto_button.grid(row=5, column=0, padx=5, pady=5)
        #-----------RESET ENTRY---------#
        self.sen1_min_reset_entry = tk.Entry(sensor1_frame, font= SMALL_FONT, textvariable = self.sen1_min_reset_string, width =4)
        self.sen1_min_reset_entry.grid(row=5, column=1, padx=5, pady=5)
        #-----------MANUAL BUTTON---------#
        self.sen1_min_man_button = tk.Button(sensor1_frame, font = SMALL_FONT, text = "MANUAL",
                                         command = lambda : [sen1_min_btn(1) , self.update_limits()])
        self.sen1_min_man_button.grid(row=5, column=2, padx=5, pady=5)

        #------------------SENSOR 2 FRAME----------------------#
        sensor2_frame = tk.LabelFrame(output_frame,text = "Sensor2", bd =10)
        sensor2_frame.grid(row=1, column=1, padx=5, pady=5)
        #----------------PRESSURE SENSOR 2 MINIMUM LIMIT--------------------#
        #-----------LABEL---------#
        sensor2_min = tk.Label(sensor2_frame, font = SMALL_FONT, text = "Minimum Limit")
        sensor2_min.grid(row=0, column=0, padx=5,pady=5)
        #-----------TEXT STRING---------#
        self.sen2_min_string = tk.StringVar()
        #-----------ENTRY---------#
        self.sen2_min_entry = tk.Entry(sensor2_frame, font= SMALL_FONT, textvariable = self.sen2_min_string, width =4)
        self.sen2_min_entry.grid(row=0, column=1, padx=5, pady=5)
        #-----------BUTTON---------#
        self.sen2_min_button = tk.Button(sensor2_frame, font = SMALL_FONT, text = "CHANGE LIMIT",
                                         command = lambda: [change_limits("sensor2 min"),self.update_limits()])
        self.sen2_min_button.grid(row=0, column=2, padx=5, pady=5)


        #----------------PRESSURE SENSOR 2 MAXIMUM LIMIT--------------------#

        #-----------LABEL---------#
        sensor2_max = tk.Label(sensor2_frame, font = SMALL_FONT, text = "Maximum Limit")
        sensor2_max.grid(row=1, column=0, padx=5,pady=5)
        #-----------TEXT STRING---------#
        self.sen2_max_string = tk.StringVar()
        #-----------ENTRY---------#
        self.sen2_max_entry = tk.Entry(sensor2_frame, font= SMALL_FONT, textvariable = self.sen2_max_string, width =4)
        self.sen2_max_entry.grid(row=1, column=1, padx=5, pady=5)
        #-----------BUTTON---------#
        self.sen2_max_button = tk.Button(sensor2_frame, font = SMALL_FONT, text = "CHANGE LIMIT",
                                         command = lambda: [change_limits("sensor2 max"),self.update_limits()])
        self.sen2_max_button.grid(row=1, column=2, padx=5, pady=5)

        #----------------PRESSURE SENSOR 2 MAX RESET MECH--------------------#
        #-----------LABEL---------#
        sen2_max_reset_label = tk.Label(sensor2_frame, font = SMALL_FONT, text = "MAX")
        sen2_max_reset_label.grid(row=2, column= 0, padx=5, pady =5)
        #-----------FUNCTION BUTTON---------#
        def sen2_max_btn(reset_mech):
            global sen2_max_reset_mech
            sen2_max_reset_mech = reset_mech
            if os.path.isfile( "/home/pi/Desktop/dispenser/SystemConfiguration.csv") == True:
                with open("/home/pi/Desktop/dispenser/SystemConfiguration.csv","w" , newline = '') as fp:
                    a = csv.writer(fp, delimiter = ",")
                    data = [sen1_max,sen1_min,sen2_max,sen2_min,sen3_max,sen3_min,sen4_max,sen4_min,
                            sen1_max_reset_mech,sen1_min_reset_mech,sen2_max_reset_mech,sen2_min_reset_mech,
                            sen3_max_reset_mech,sen3_min_reset_mech,sen4_max_reset_mech,sen4_min_reset_mech,
                            sen1_range,sen2_range,sen3_range,sen4_range]
                    a.writerow(data)
                fp.close()
        #-----------TEXT STRING---------#
        self.sen2_max_reset_string = tk.StringVar()
        #-----------AUTO BUTTON---------#
        self.sen2_max_auto_button = tk.Button(sensor2_frame, font = SMALL_FONT, text = "AUTO",
                                          command = lambda : [sen2_max_btn(0) , self.update_limits()])
        self.sen2_max_auto_button.grid(row=3, column=0, padx=5, pady=5)
        #-----------RESET ENTRY---------#
        self.sen2_max_reset_entry = tk.Entry(sensor2_frame, font= SMALL_FONT, textvariable = self.sen2_max_reset_string, width =4)
        self.sen2_max_reset_entry.grid(row=3, column=1, padx=5, pady=5)
        #-----------MANUAL BUTTON---------#
        self.sen2_max_man_button = tk.Button(sensor2_frame, font = SMALL_FONT, text = "MANUAL",
                                         command = lambda : [sen2_max_btn(1) , self.update_limits()])
        self.sen2_max_man_button.grid(row=3, column=2, padx=5, pady=5)

        #----------------PRESSURE SENSOR 2 MIN RESET MECH--------------------#
        #-----------LABEL---------#
        sen2_min_reset_label = tk.Label(sensor2_frame, font = SMALL_FONT, text = "MIN")
        sen2_min_reset_label.grid(row=4, column= 0, padx=5, pady =5)
        #-----------FUNCTION BUTTON---------#
        def sen2_min_btn(reset_mech):
            global sen2_min_reset_mech
            sen2_min_reset_mech = reset_mech
            if os.path.isfile( "/home/pi/Desktop/dispenser/SystemConfiguration.csv") == True:
                with open("/home/pi/Desktop/dispenser/SystemConfiguration.csv","w" , newline = '') as fp:
                    a = csv.writer(fp, delimiter = ",")
                    data = [sen1_max,sen1_min,sen2_max,sen2_min,sen3_max,sen3_min,sen4_max,sen4_min,
                            sen1_max_reset_mech,sen1_min_reset_mech,sen2_max_reset_mech,sen2_min_reset_mech,
                            sen3_max_reset_mech,sen3_min_reset_mech,sen4_max_reset_mech,sen4_min_reset_mech,
                            sen1_range,sen2_range,sen3_range,sen4_range]
                    a.writerow(data)
                fp.close()
        #-----------TEXT STRING---------#
        self.sen2_min_reset_string = tk.StringVar()
        #-----------AUTO BUTTON---------#
        self.sen2_min_auto_button = tk.Button(sensor2_frame, font = SMALL_FONT, text = "AUTO",
                                          command = lambda : [sen2_min_btn(0) , self.update_limits()])
        self.sen2_min_auto_button.grid(row=5, column=0, padx=5, pady=5)
        #-----------RESET ENTRY---------#
        self.sen2_min_reset_entry = tk.Entry(sensor2_frame, font= SMALL_FONT, textvariable = self.sen2_min_reset_string, width =4)
        self.sen2_min_reset_entry.grid(row=5, column=1, padx=5, pady=5)
        #-----------MANUAL BUTTON---------#
        self.sen2_min_man_button = tk.Button(sensor2_frame, font = SMALL_FONT, text = "MANUAL",
                                         command = lambda : [sen2_min_btn(1) , self.update_limits()])
        self.sen2_min_man_button.grid(row=5, column=2, padx=5, pady=5)

        #------------------SENSOR 3 FRAME----------------------#
        sensor3_frame = tk.LabelFrame(output_frame,text = "Sensor3", bd =10)
        sensor3_frame.grid(row=3, column=0, padx=5, pady=5)

        #----------------PRESSURE SENSOR 3 MINIMUM LIMIT--------------------#
        #-----------LABEL---------#
        sensor3_min = tk.Label(sensor3_frame, font = SMALL_FONT, text = "Minimum Limit")
        sensor3_min.grid(row=0, column=0, padx=5,pady=5)
        #-----------TEXT STRING---------#
        self.sen3_min_string = tk.StringVar()
        #-----------ENTRY---------#
        self.sen3_min_entry = tk.Entry(sensor3_frame, font= SMALL_FONT, textvariable = self.sen3_min_string, width =4)
        self.sen3_min_entry.grid(row=0, column=1, padx=5, pady=5)
        #-----------BUTTON---------#
        self.sen3_min_button = tk.Button(sensor3_frame, font = SMALL_FONT, text = "CHANGE LIMIT",
                                         command = lambda: [change_limits("sensor3 min"),self.update_limits()])
        self.sen3_min_button.grid(row=0, column=2, padx=5, pady=5)


        #----------------PRESSURE SENSOR 3 MAXIMUM LIMIT--------------------#

        #-----------LABEL---------#
        sensor3_max = tk.Label(sensor3_frame, font = SMALL_FONT, text = "Maximum Limit")
        sensor3_max.grid(row=1, column=0, padx=5,pady=5)
        #-----------TEXT STRING---------#
        self.sen3_max_string = tk.StringVar()
        #-----------ENTRY---------#
        self.sen3_max_entry = tk.Entry(sensor3_frame, font= SMALL_FONT, textvariable = self.sen3_max_string, width =4)
        self.sen3_max_entry.grid(row=1, column=1, padx=5, pady=5)
        #-----------BUTTON---------#
        self.sen3_max_button = tk.Button(sensor3_frame, font = SMALL_FONT, text = "CHANGE LIMIT",
                                         command = lambda: [change_limits("sensor3 max"),self.update_limits()])
        self.sen3_max_button.grid(row=1, column=2, padx=5, pady=5)

        #----------------PRESSURE SENSOR 3 MAX RESET MECH--------------------#
        #-----------LABEL---------#
        sen3_max_reset_label = tk.Label(sensor3_frame, font = SMALL_FONT, text = "MAX")
        sen3_max_reset_label.grid(row=2, column= 0, padx=5, pady =5)
        #-----------FUNCTION BUTTON---------#
        def sen3_max_btn(reset_mech):
            global sen3_max_reset_mech
            sen3_max_reset_mech = reset_mech
            if os.path.isfile( "/home/pi/Desktop/dispenser/SystemConfiguration.csv") == True:
                with open("/home/pi/Desktop/dispenser/SystemConfiguration.csv","w" , newline = '') as fp:
                    a = csv.writer(fp, delimiter = ",")
                    data = [sen1_max,sen1_min,sen2_max,sen2_min,sen3_max,sen3_min,sen4_max,sen4_min,
                            sen1_max_reset_mech,sen1_min_reset_mech,sen2_max_reset_mech,sen2_min_reset_mech,
                            sen3_max_reset_mech,sen3_min_reset_mech,sen4_max_reset_mech,sen4_min_reset_mech,
                            sen1_range,sen2_range,sen3_range,sen4_range]
                    a.writerow(data)
                fp.close()
        #-----------TEXT STRING---------#
        self.sen3_max_reset_string = tk.StringVar()
        #-----------AUTO BUTTON---------#
        self.sen3_max_auto_button = tk.Button(sensor3_frame, font = SMALL_FONT, text = "AUTO",
                                          command = lambda : [sen3_max_btn(0) , self.update_limits()])
        self.sen3_max_auto_button.grid(row=3, column=0, padx=5, pady=5)
        #-----------RESET ENTRY---------#
        self.sen3_max_reset_entry = tk.Entry(sensor3_frame, font= SMALL_FONT, textvariable = self.sen3_max_reset_string, width =4)
        self.sen3_max_reset_entry.grid(row=3, column=1, padx=5, pady=5)
        #-----------MANUAL BUTTON---------#
        self.sen3_max_man_button = tk.Button(sensor3_frame, font = SMALL_FONT, text = "MANUAL",
                                         command = lambda : [sen3_max_btn(1) , self.update_limits()])
        self.sen3_max_man_button.grid(row=3, column=2, padx=5, pady=5)

        #----------------PRESSURE SENSOR 3 MIN RESET MECH--------------------#
        #-----------LABEL---------#
        sen3_min_reset_label = tk.Label(sensor3_frame, font = SMALL_FONT, text = "MIN")
        sen3_min_reset_label.grid(row=4, column= 0, padx=5, pady =5)
        #-----------FUNCTION BUTTON---------#
        def sen3_min_btn(reset_mech):
            global sen3_min_reset_mech
            sen3_min_reset_mech = reset_mech
            if os.path.isfile( "/home/pi/Desktop/dispenser/SystemConfiguration.csv") == True:
                with open("/home/pi/Desktop/dispenser/SystemConfiguration.csv","w" , newline = '') as fp:
                    a = csv.writer(fp, delimiter = ",")
                    data = [sen1_max,sen1_min,sen2_max,sen2_min,sen3_max,sen3_min,sen4_max,sen4_min,
                            sen1_max_reset_mech,sen1_min_reset_mech,sen2_max_reset_mech,sen2_min_reset_mech,
                            sen3_max_reset_mech,sen3_min_reset_mech,sen4_max_reset_mech,sen4_min_reset_mech,
                            sen1_range,sen2_range,sen3_range,sen4_range]
                    a.writerow(data)
                fp.close()
        #-----------TEXT STRING---------#
        self.sen3_min_reset_string = tk.StringVar()
        #-----------AUTO BUTTON---------#
        self.sen3_min_auto_button = tk.Button(sensor3_frame, font = SMALL_FONT, text = "AUTO",
                                          command = lambda : [sen3_min_btn(0) , self.update_limits()])
        self.sen3_min_auto_button.grid(row=5, column=0, padx=5, pady=5)
        #-----------RESET ENTRY---------#
        self.sen3_min_reset_entry = tk.Entry(sensor3_frame, font= SMALL_FONT, textvariable = self.sen3_min_reset_string, width =4)
        self.sen3_min_reset_entry.grid(row=5, column=1, padx=5, pady=5)
        #-----------MANUAL BUTTON---------#
        self.sen3_min_man_button = tk.Button(sensor3_frame, font = SMALL_FONT, text = "MANUAL",
                                         command = lambda : [sen3_min_btn(1) , self.update_limits()])
        self.sen3_min_man_button.grid(row=5, column=2, padx=5, pady=5)

        
        #------------------SENSOR 4 FRAME----------------------#
        sensor4_frame = tk.LabelFrame(output_frame,text = "Sensor4", bd =10)
        sensor4_frame.grid(row=3, column=1, padx=5, pady=5)

        #----------------PRESSURE SENSOR 4 MINIMUM LIMIT--------------------#
        #-----------LABEL---------#
        sensor4_min = tk.Label(sensor4_frame, font = SMALL_FONT, text = "Minimum Limit")
        sensor4_min.grid(row=0, column=0, padx=5,pady=5)
        #-----------TEXT STRING---------#
        self.sen4_min_string = tk.StringVar()
        #-----------ENTRY---------#
        self.sen4_min_entry = tk.Entry(sensor4_frame, font= SMALL_FONT, textvariable = self.sen4_min_string, width =4)
        self.sen4_min_entry.grid(row=0, column=1, padx=5, pady=5)
        #-----------BUTTON---------#
        self.sen4_min_button = tk.Button(sensor4_frame, font = SMALL_FONT, text = "CHANGE LIMIT",
                                         command = lambda: [change_limits("sensor4 min"),self.update_limits()])
        self.sen4_min_button.grid(row=0, column=2, padx=5, pady=5)


        #----------------PRESSURE SENSOR 4 MAXIMUM LIMIT--------------------#

        #-----------LABEL---------#
        sensor4_max = tk.Label(sensor4_frame, font = SMALL_FONT, text = "Maximum Limit")
        sensor4_max.grid(row=1, column=0, padx=5,pady=5)
        #-----------TEXT STRING---------#
        self.sen4_max_string = tk.StringVar()
        #-----------ENTRY---------#
        self.sen4_max_entry = tk.Entry(sensor4_frame, font= SMALL_FONT, textvariable = self.sen4_max_string, width =4)
        self.sen4_max_entry.grid(row=1, column=1, padx=5, pady=5)
        #-----------BUTTON---------#
        self.sen4_max_button = tk.Button(sensor4_frame, font = SMALL_FONT, text = "CHANGE LIMIT",
                                         command = lambda: [change_limits("sensor4 max"),self.update_limits()])
        self.sen4_max_button.grid(row=1, column=2, padx=5, pady=5)

        #----------------PRESSURE SENSOR 4 MAX RESET MECH--------------------#
        #-----------LABEL---------#
        sen4_max_reset_label = tk.Label(sensor4_frame, font = SMALL_FONT, text = "MAX")
        sen4_max_reset_label.grid(row=2, column= 0, padx=5, pady =5)
        #-----------FUNCTION BUTTON---------#
        def sen4_max_btn(reset_mech):
            global sen4_max_reset_mech
            sen4_max_reset_mech = reset_mech
            if os.path.isfile( "/home/pi/Desktop/dispenser/SystemConfiguration.csv") == True:
                with open("/home/pi/Desktop/dispenser/SystemConfiguration.csv","w" , newline = '') as fp:
                    a = csv.writer(fp, delimiter = ",")
                    data = [sen1_max,sen1_min,sen2_max,sen2_min,sen3_max,sen3_min,sen4_max,sen4_min,
                            sen1_max_reset_mech,sen1_min_reset_mech,sen2_max_reset_mech,sen2_min_reset_mech,
                            sen3_max_reset_mech,sen3_min_reset_mech,sen4_max_reset_mech,sen4_min_reset_mech,
                            sen1_range,sen2_range,sen3_range,sen4_range]
                    a.writerow(data)
                fp.close()
        #-----------TEXT STRING---------#
        self.sen4_max_reset_string = tk.StringVar()
        #-----------AUTO BUTTON---------#
        self.sen4_max_auto_button = tk.Button(sensor4_frame, font = SMALL_FONT, text = "AUTO",
                                          command = lambda : [sen4_max_btn(0) , self.update_limits()])
        self.sen4_max_auto_button.grid(row=3, column=0, padx=5, pady=5)
        #-----------RESET ENTRY---------#
        self.sen4_max_reset_entry = tk.Entry(sensor4_frame, font= SMALL_FONT, textvariable = self.sen4_max_reset_string, width =4)
        self.sen4_max_reset_entry.grid(row=3, column=1, padx=5, pady=5)
        #-----------MANUAL BUTTON---------#
        self.sen4_max_man_button = tk.Button(sensor4_frame, font = SMALL_FONT, text = "MANUAL",
                                         command = lambda : [sen4_max_btn(1) , self.update_limits()])
        self.sen4_max_man_button.grid(row=3, column=2, padx=5, pady=5)

        #----------------PRESSURE SENSOR 4 MIN RESET MECH--------------------#
        #-----------LABEL---------#
        sen4_min_reset_label = tk.Label(sensor4_frame, font = SMALL_FONT, text = "MIN")
        sen4_min_reset_label.grid(row=4, column= 0, padx=5, pady =5)
        #-----------FUNCTION BUTTON---------#
        def sen4_min_btn(reset_mech):
            global sen4_min_reset_mech
            sen4_min_reset_mech = reset_mech
            if os.path.isfile( "/home/pi/Desktop/dispenser/SystemConfiguration.csv") == True:
                with open("/home/pi/Desktop/dispenser/SystemConfiguration.csv","w" , newline = '') as fp:
                    a = csv.writer(fp, delimiter = ",")
                    data = [sen1_max,sen1_min,sen2_max,sen2_min,sen3_max,sen3_min,sen4_max,sen4_min,
                            sen1_max_reset_mech,sen1_min_reset_mech,sen2_max_reset_mech,sen2_min_reset_mech,
                            sen3_max_reset_mech,sen3_min_reset_mech,sen4_max_reset_mech,sen4_min_reset_mech,
                            sen1_range,sen2_range,sen3_range,sen4_range]
                    a.writerow(data)
                fp.close()
        #-----------TEXT STRING---------#
        self.sen4_min_reset_string = tk.StringVar()
        #-----------AUTO BUTTON---------#
        self.sen4_min_auto_button = tk.Button(sensor4_frame, font = SMALL_FONT, text = "AUTO",
                                          command = lambda : [sen4_min_btn(0) , self.update_limits()])
        self.sen4_min_auto_button.grid(row=5, column=0, padx=5, pady=5)
        #-----------RESET ENTRY---------#
        self.sen4_min_reset_entry = tk.Entry(sensor4_frame, font= SMALL_FONT, textvariable = self.sen4_min_reset_string, width =4)
        self.sen4_min_reset_entry.grid(row=5, column=1, padx=5, pady=5)
        #-----------MANUAL BUTTON---------#
        self.sen4_min_man_button = tk.Button(sensor4_frame, font = SMALL_FONT, text = "MANUAL",
                                         command = lambda : [sen4_min_btn(1) , self.update_limits()])
        self.sen4_min_man_button.grid(row=5, column=2, padx=5, pady=5)

        self.update_limits()
    def update_limits(self):
        self.sen1_max_string.set(sen1_max)
        self.sen1_min_string.set(sen1_min)
        self.sen2_max_string.set(sen2_max)
        self.sen2_min_string.set(sen2_min)
        self.sen3_max_string.set(sen3_max)
        self.sen3_min_string.set(sen3_min)
        self.sen4_max_string.set(sen4_max)
        self.sen4_min_string.set(sen4_min)
        self.sen1_max_reset_string.set(sen1_max_reset_mech)
        self.sen1_min_reset_string.set(sen1_min_reset_mech)
        self.sen2_max_reset_string.set(sen2_max_reset_mech)
        self.sen2_min_reset_string.set(sen2_min_reset_mech)
        self.sen3_max_reset_string.set(sen3_max_reset_mech)
        self.sen3_min_reset_string.set(sen3_min_reset_mech)
        self.sen4_max_reset_string.set(sen4_max_reset_mech)
        self.sen4_min_reset_string.set(sen4_min_reset_mech)

class AdministrativeChanges(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)

        #back button
        back_button = tk.Button(self, text = "<-Back", font = SMALL_FONT, bg = 'blue', fg = 'white',
                                command= lambda: controller.show_frame(SettingPage))
        back_button.place(x = 800, y= 665)

        #touch callibration button
        def t_callibration():
            try:
                subprocess.call(subprocess.call("sudo /etc/opt/elo-usb/elova &", shell = True))
            except:
                pass
        self.touch_callibration = tk.Button(self, text = "CALLIBRATE TOUCH", font = SMALL_FONT, bg = "blue", fg = "white",
                                       command = lambda: t_callibration())
        self.touch_callibration.place(x = 800, y = 615)

        #-----------------------------------------------OUTPUT FRAME----------------------------------------------#
        output_frame = tk.LabelFrame(self, bd =10)
        output_frame.place(x=10, y=10)

        #------------------SENSOR 1 RANGE FRAME----------------------#
        sensor1_range_frame = tk.LabelFrame(output_frame, text = "Sensor1 Range", bd =10)
        sensor1_range_frame.grid(row=0, column=0, padx=5, pady=5)
        #-----------LABEL---------#
        sensor1_range = tk.Label(sensor1_range_frame, font = SMALL_FONT, text = "Range")
        sensor1_range.grid(row=0, column=0, padx=5,pady=5)
        #-----------TEXT STRING---------#
        self.sen1_range_string = tk.StringVar()
        #-----------ENTRY---------#
        self.sen1_range_entry = tk.Entry(sensor1_range_frame, font= SMALL_FONT, textvariable = self.sen1_range_string, width =4)
        self.sen1_range_entry.grid(row=0, column=1, padx=5, pady=5)
        #-----------BUTTON---------#
        self.sen1_range_button = tk.Button(sensor1_range_frame, font = SMALL_FONT, text = "CHANGE LIMIT",
                                         command = lambda: [change_limits("sensor1 range"),self.update_limits()])
        self.sen1_range_button.grid(row=0, column=2, padx=5, pady=5)


        #------------------SENSOR 2 RANGE FRAME----------------------#
        sensor2_range_frame = tk.LabelFrame(output_frame, text = "Sensor2 Range", bd =10)
        sensor2_range_frame.grid(row=0, column=1, padx=5, pady=5)
        #-----------LABEL---------#
        sensor2_range = tk.Label(sensor2_range_frame, font = SMALL_FONT, text = "Range")
        sensor2_range.grid(row=0, column=0, padx=5,pady=5)
        #-----------TEXT STRING---------#
        self.sen2_range_string = tk.StringVar()
        #-----------ENTRY---------#
        self.sen2_range_entry = tk.Entry(sensor2_range_frame, font= SMALL_FONT, textvariable = self.sen2_range_string, width =4)
        self.sen2_range_entry.grid(row=0, column=1, padx=5, pady=5)
        #-----------BUTTON---------#
        self.sen2_range_button = tk.Button(sensor2_range_frame, font = SMALL_FONT, text = "CHANGE LIMIT",
                                         command = lambda: [change_limits("sensor2 range"),self.update_limits()])
        self.sen2_range_button.grid(row=0, column=2, padx=5, pady=5)


        #------------------SENSOR 3 RANGE FRAME----------------------#
        sensor3_range_frame = tk.LabelFrame(output_frame, text = "Sensor3 Range", bd =10)
        sensor3_range_frame.grid(row=2, column=0, padx=5, pady=5)
        #-----------LABEL---------#
        sensor3_range = tk.Label(sensor3_range_frame, font = SMALL_FONT, text = "Range")
        sensor3_range.grid(row=0, column=0, padx=5,pady=5)
        #-----------TEXT STRING---------#
        self.sen3_range_string = tk.StringVar()
        #-----------ENTRY---------#
        self.sen3_range_entry = tk.Entry(sensor3_range_frame, font= SMALL_FONT, textvariable = self.sen3_range_string, width =4)
        self.sen3_range_entry.grid(row=0, column=1, padx=5, pady=5)
        #-----------BUTTON---------#
        self.sen3_range_button = tk.Button(sensor3_range_frame, font = SMALL_FONT, text = "CHANGE LIMIT",
                                         command = lambda: [change_limits("sensor3 range"),self.update_limits()])
        self.sen3_range_button.grid(row=0, column=2, padx=5, pady=5)



        #------------------SENSOR 4 RANGE FRAME----------------------#
        sensor4_range_frame = tk.LabelFrame(output_frame, text = "Sensor4 Range", bd =10)
        sensor4_range_frame.grid(row=2, column=1, padx=5, pady=5)
        #-----------LABEL---------#
        sensor4_range = tk.Label(sensor4_range_frame, font = SMALL_FONT, text = "Range")
        sensor4_range.grid(row=0, column=0, padx=5,pady=5)
        #-----------TEXT STRING---------#
        self.sen4_range_string = tk.StringVar()
        #-----------ENTRY---------#
        self.sen4_range_entry = tk.Entry(sensor4_range_frame, font= SMALL_FONT, textvariable = self.sen4_range_string, width =4)
        self.sen4_range_entry.grid(row=0, column=1, padx=5, pady=5)
        #-----------BUTTON---------#
        self.sen4_range_button = tk.Button(sensor4_range_frame, font = SMALL_FONT, text = "CHANGE LIMIT",
                                         command = lambda: [change_limits("sensor4 range"),self.update_limits()])
        self.sen4_range_button.grid(row=0, column=2, padx=5, pady=5)
        

        self.update_limits()
    def update_limits(self):

        self.sen1_range_string.set(sen1_range)
        self.sen2_range_string.set(sen2_range)
        self.sen3_range_string.set(sen3_range)
        self.sen4_range_string.set(sen4_range)        
        

if __name__ == "__main__":
    app = DispenserGui()
##    app.protocol("WM_DELETE_WINDOW", disable_event)
##    app.overrideredirect(1)
    app.wm_geometry("1024x768+0+0")
    app.attributes('-fullscreen', True)
##    app.geometry("{0}x{1}+0+0".format(app.winfo_screenwidth(), app  .winfo_screenheight()))
    app.mainloop()
    gpio.cleanup()
    
