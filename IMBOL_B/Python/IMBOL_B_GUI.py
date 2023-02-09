#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 15:27:02 2021

@author: bernardo
"""
from random import randrange
import pandas as pd

import tkinter
from functools import partial
import glob
import serial

import math
import numpy as np


import collections
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.

from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation

import time

SENSORS_READ   =int('0b00000001',2) #R

A_R1=0.00251428;#Current calibration constant A for the 4-20 ma receiver labeled as 1
B_R1=0.10016;#Current calibration constant B for the 4-20 ma receiver labeled as 1
P_Range=1000;#Preasure range in mbar from calibration on provided sensor documentation
I_Span_P1=15.998;# Current span in mA for sensor 1 from calibration on provided sensor documentation
I0_P1=4.001;#Current at 0 mbar from calibration on provided sensor documentation
A_P1= P_Range/I_Span_P1;
B_P1= -A_P1*I0_P1;

A_R=A_R1;
B_R=B_R1;
A_P=A_P1;
B_P=B_P1;


RNOMINAL=100.0
RREF=470
a=0.00390830
b=-0.0000005775






def T_C(T_ADC):
    R = int.from_bytes(T_ADC, "big")
    R *= RREF/32768
    Rrate = R/RNOMINAL
    T = a*a
    T -= 4*b*(1-Rrate)
    T = math.sqrt(T)
    T -= a
    T /= 2*b
    return T


def P_mbar(P_ADC):
    P = int.from_bytes(P_ADC, "big")
    P *= A_R
    P += B_R  # convert output to mA
    P *= A_P
    P += B_P  # convert output to mbar
    return P


    
def read_sensors_BOLI():
    adress=SENSORS_READ
    boli.write(adress.to_bytes(1,'big'))
    sensors=boli.read(6)
    T_AMB_n=sensors[:2]
    P_ABS_n=sensors[2:4]
    #T_SURF_n=sensors[2:4]
    #P_ABS_n=sensors[4:6]

    #return (T_C(T_AMB_n), T_C(T_SURF_n), P_mbar(P_ABS_n))
    return (T_C(T_AMB_n), P_mbar(P_ABS_n))


#def plot(T_AMB_new,T_SURF_new,P_new):
#    P_ABS.popleft()
#    P_ABS.append(P_new)
#    T_AMB.popleft()
#    T_AMB.append(T_AMB_new)
#    T_SURF.popleft()
#    T_SURF.append(T_SURF_new)
    
def plot(T_AMB_new,P_new):
    P_ABS.popleft()
    P_ABS.append(P_new)
    T_AMB.popleft()
    T_AMB.append(T_AMB_new)
    


    ax.cla()
    ax1.cla()
    ax2.cla()
    # plot P_ABS
    ax.plot(P_ABS)
    ax.scatter(len(P_ABS)-1, P_ABS[-1])
    ax.text(len(P_ABS)-1, P_ABS[-1]+2, '{:06.2f}mbar'.format(P_ABS[-1]))
    ax.set_ylim(0,1100)
    # plot T_AMB
    ax1.plot(T_AMB)
    ax1.scatter(len(T_AMB)-1, T_AMB[-1])
    ax1.text(len(T_AMB)-1, T_AMB[-1]+2, "{:06.2f}°C".format(T_AMB[-1]))
    ax1.set_ylim(0,100)
    # plot T_SURF
    #ax2.plot(T_SURF)
    #ax2.scatter(len(T_SURF)-1, T_SURF[-1])
    #ax2.text(len(T_SURF)-1, T_SURF[-1]+2, "{:06.2f}°C".format(T_SURF[-1]))
    #ax2.set_ylim(0,100)

# function to update the animation data
def animation_main(i):
    if ani_state==1:
        #(T_AMB_new,T_SURF_new,P_new)=read_sensors_BOLI()
        (T_AMB_new,P_new)=read_sensors_BOLI()
        #plot(T_AMB_new,T_SURF_new,P_new)
        plot(T_AMB_new,P_new)
        if log_state==1:
            #log(T_AMB_new,T_SURF_new,P_new)
            log(T_AMB_new,P_new)

    
ports = ['/dev/tty.usbmodem142101']
#if('boli' in globals() and boli.isOpen() == True):
#    boli.close()
    
for i in range(len(ports)):
    with serial.Serial(ports[i], 9600, timeout=1) as ser:
        query=ser.read(4)
    if query==b'BOLI':
        boli=serial.Serial(ports[i], 9600, timeout=1)
        print(boli.read(4))
        print('Connection successful ')
        time.sleep(0.5)
        break
    if i ==len(ports)-1 and query!='BOLI':
        print('Connection failed ')
        while True:
            1

# Get the initial configuration from the arduino, this variable will be used to store and display the current state of valves and motors
current_config = 0
#read_config_BOLI()
        

    
    
#log
P_ABS_log=np.zeros(1)
T_AMB_log=np.zeros(1)
#T_SURF_log=np.zeros(1)
log_state=0
i_log=0
n_samples=7200
def start_log():
    global n_samples
    global log_state
    global i_log
    global P_ABS_log
    global T_AMB_log
    #global T_SURF_log
    
    P_ABS_log=np.zeros(n_samples)
    T_AMB_log=np.zeros(n_samples)
    #T_SURF_log=np.zeros(n_samples)
    log_state=1
    i_log=0
    
def log(T_AMB_new,T_SURF_new,P_new):
    global P_ABS_log
    global T_AMB_log
    global T_SURF_log
    global i_log
    P_ABS_log[i_log]=P_new
    T_AMB_log[i_log]=T_AMB_new
    #T_SURF_log[i_log]=T_SURF_new
    i_log+=1
    if i_log==n_samples:
        end_log()
def end_log():
    global P_ABS_log
    global T_AMB_log
    #global T_SURF_log
    global log_state
    log_state=0
    #a = np.asarray(np.transpose([P_ABS_log, T_AMB_log, T_SURF_log ]))
    a = np.asarray(np.transpose([P_ABS_log, T_AMB_log ]))
    np.savetxt("/Users/bernardo/Desktop/log.csv", a, delimiter=",")

def set_log_time():
    global n_samples
    data=int(input_set_log.get())
    n_samples = data*120
    input_set_log.delete(0, tkinter.END)
    label_set_log.configure(text="Log time = "+ str(round(data))+" [min]")
    

# start collections with zeros

P_ABS  = collections.deque(np.zeros(100))
T_AMB  = collections.deque(np.zeros(100))
#T_SURF = collections.deque(np.zeros(100))
# define and adjust figure
fig = Figure(figsize=(5, 4), dpi=100)
ax  = fig.add_subplot(131)
ax1 = fig.add_subplot(132)
ax2 = fig.add_subplot(133)
#pause or resume animation animation state initially 1 (play)
ani_state=1;
def ani_pause_resume():
    global ani_state
    ani_state= not ani_state


root = tkinter.Tk()
root.wm_title("IMBOL_A")
canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.draw()

# pack_toolbar=False will make it easier to use a layout manager later on.
toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
toolbar.update()




button_exit = tkinter.Button(master=root, text="Quit", command=root.quit)
button_exit.pack(side=tkinter.BOTTOM)


#button_close_all = tkinter.Button(master=root, text="Close all", command=partial(
#    set_config_BOLI, 0))
#button_close_all.pack(side=tkinter.TOP)

#button_open_dosing = tkinter.Button(master=root, text="Open dosing", command=partial(
#    set_config_BOLI, OPEN_DOSING))
#button_open_dosing.pack(side=tkinter.TOP)

#button_fill_N2 = tkinter.Button(master=root, text="fill N2", command=partial(
#    set_config_BOLI, OPEN_N2))
#button_fill_N2.pack(side=tkinter.TOP)

#button_fill_NOVEC = tkinter.Button(master=root, text="fill NOVEC", command=partial(
#    set_config_BOLI, OPEN_NOVEC))
#button_fill_NOVEC.pack(side=tkinter.TOP)

#button_pump = tkinter.Button(master=root, text="Pump NOVEC", command=partial(
#    set_config_BOLI, PUMP_ON))
#button_pump.pack(side=tkinter.TOP)

#button_wipe = tkinter.Button(master=root, text="Wipe Surface", command=partial(
#    set_config_BOLI, WIPER_ON))
#button_wipe.pack(side=tkinter.TOP)

button_ani_control = tkinter.Button(master=root, text="Pause/Resume plot", command=ani_pause_resume)
button_ani_control.pack(side=tkinter.TOP)

#label_set_T=tkinter.Label(master=root, text="T_s (setpoint)= 0 [°C]")
#label_set_T.pack(side=tkinter.TOP)

#input_set_T=tkinter.Entry(master=root)
#input_set_T.pack(side=tkinter.TOP)

#button_set_T = tkinter.Button(master=root, text="Change T_setpoint", command=set_T_surf_button)
#button_set_T.pack(side=tkinter.TOP)

#label_config=tkinter.Label(master=root, text="Current state: "+format(current_config, '#010b'))
#label_config.pack(side=tkinter.TOP)

label_set_log=tkinter.Label(master=root, text="Log time = 60 [min]")
label_set_log.pack(side=tkinter.BOTTOM)

button_set_log = tkinter.Button(master=root, text="Change log time", command=set_log_time)
button_set_log.pack(side=tkinter.BOTTOM)

input_set_log=tkinter.Entry(master=root)
input_set_log.pack(side=tkinter.BOTTOM)

button_start_log = tkinter.Button(master=root, text="Start log", command=start_log)
button_start_log.pack(side=tkinter.BOTTOM)

button_end_log = tkinter.Button(master=root, text="End log", command=end_log)
button_end_log.pack(side=tkinter.BOTTOM)




    


toolbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)



# animate
ani = FuncAnimation(fig, animation_main, interval=500)
tkinter.mainloop()
