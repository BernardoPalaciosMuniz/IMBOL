#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 15:27:02 2021

@author: bernardo
"""


import tkinter
from tkinter import font as tkFont
from tkinter import messagebox
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
from datetime import datetime



CONFIG_READ     =int('0b00000000',2) #R
CONFIG_WRITE    =int('0b10000000',2) #R
OPEN_N2         =int('0b00000001',2) # 1st bit of the CONFIG adress is the state of the N2 valve
OPEN_NOVEC      =int('0b00000010',2) # 2nd bit of the CONFIG adress is the state of the NOVEC valve
OPEN_DOSING     =int('0b00000100',2) # 3rd bit of the CONFIG adress is the state of the dosing valve
OVERFLOW_TRGD   =int('0b00001000',2) # 4th bit of the CONFIG adress is the state of overflow sensor
WIPER_ON        =int('0b00010000',2)
PUMP_ON         =int('0b00100000',2)
WIPER_DIR       =int('0b01000000',2)
SINGLE_DOSE     =int('0b10000000',2)


SENSORS_READ   =int('0b00000001',2) #R
TEMP_SURF_WRITE =int('0b10000001',2) #W
DOSE_INTERVAL_WRITE=int('0b10000010',2) #W

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

current_config = 0




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


def read_config_BOLI():
    global connection_state
    global current_config
    if(connection_state==1):
        adress=CONFIG_READ
        boli.write(adress.to_bytes(1,'big'))
        state=int.from_bytes(boli.read(),'big')
        current_config=state
  
    
def set_config_BOLI(data):
    global connection_state
    global current_config
    if(connection_state==1):
        adress=CONFIG_WRITE
        send = adress << 8
        send += data
        boli.write(send.to_bytes(2, 'big'))
        state=int.from_bytes(boli.read(),'big')
        current_config=state
    
    
def read_sensors_BOLI():
    global connection_state
    if(connection_state==1):
        adress=SENSORS_READ
        boli.write(adress.to_bytes(1,'big'))
        sensors=boli.read(6)
        T_AMB_n=sensors[:2]
        T_SURF_n=sensors[2:4]
        P_ABS_n=sensors[4:6]
        return (T_C(T_AMB_n), T_C(T_SURF_n), P_mbar(P_ABS_n))
    else:
        return (0,0,0)

ani_interval=500
plot_samples=100
t_plot=-plot_samples*ani_interval/1000
def plot(T_AMB_new,T_SURF_new,P_new):
    global ani_interval
    global plot_samples
    global t_plot
    
    P_ABS.popleft()
    P_ABS.append(P_new)
    T_AMB.popleft()
    T_AMB.append(T_AMB_new)
    T_SURF.popleft()
    T_SURF.append(T_SURF_new)
    x=np.linspace(t_plot,0,plot_samples)


    ax.cla()
    ax1.cla()
    ax2.cla()
    # plot P_ABS
    ax.plot(x,P_ABS)
    ax.scatter(0, P_ABS[-1])
    ax.text(0, P_ABS[-1]+50, '{:04.0f}mbar'.format(P_ABS[-1]),horizontalalignment='left')
    ax.set_ylim(0,1100)
    ax.set_xlim(t_plot,7)
    ax.set_ylabel('P_abs [mbar]')

    # plot T_AMB
    ax1.plot(x,T_AMB)
    ax1.scatter(0, T_AMB[-1])
    ax1.text(0, T_AMB[-1]+5, "{:04.1f}°C".format(T_AMB[-1]),horizontalalignment='left')
    ax1.set_ylim(0,100)
    ax1.set_xlim(t_plot,7)
    ax1.set_ylabel('T_amb [°C]')

    # plot T_SURF
    ax2.plot(x,T_SURF)
    ax2.scatter(0, T_SURF[-1])
    ax2.text(0, T_SURF[-1]+5, "{:04.1f}°C".format(T_SURF[-1]),horizontalalignment='left')
    ax2.set_ylim(0,100)
    ax2.set_ylabel('T_surf [°C]')
    ax2.set_xlabel('t [s]')
    ax2.set_xlim(t_plot,7)

# function to update the animation data

def animation_main(i):
    global current_config
    read_config_BOLI()
    label_config.configure(text=format(current_config, '#010b'))
    LED_state_colors_update()
    (T_AMB_new,T_SURF_new,P_new)=read_sensors_BOLI()
    check_vac(P_new)
    check_flush(P_new)
    log_LED_update()
    
    
    #if (connection_state==1)&(ani_state==1):
    if (ani_state==1):
        plot(T_AMB_new,T_SURF_new,P_new)
    if log_state==1:
        log(T_AMB_new,T_SURF_new,P_new)


#Handshake of arduino
ports=glob.glob('/dev/cu.*')
#if('boli' in globals() and boli.isOpen() == True):
#    boli.close()
    
for i in range(len(ports)):
    with serial.Serial(ports[i], 9600, timeout=1) as ser:
        query=ser.read(4)
    if query==b'BOLI':
        boli=serial.Serial(ports[i], 9600, timeout=1)
        print(boli.read(4))
        print('Connection successful ')
        connection_state=1;
        time.sleep(0.5)
        break
    if i ==len(ports)-1 and query!='BOLI':
        print('Connection failed ')
        connection_state=0;
        #while True:
        #    1



# Get the initial configuration from the arduino, this variable will be used to store and display the current state of valves and motors

read_config_BOLI()


#log

#EXPERIMENT
nexp=1000
P_ABS_EXP_log=np.zeros(nexp)
T_AMB_EXP_log=np.zeros(nexp)
T_SURF_EXP_log=np.zeros(nexp)
i_EXP_log=0

def EXP_log(T_AMB_new,T_SURF_new,P_new):
    global P_ABS_EXP_log
    global T_AMB_EXP_log
    global T_SURF_EXP_log
    global i_EXP_log

    P_ABS_EXP_log[i_EXP_log]=P_new
    T_AMB_EXP_log[i_EXP_log]=T_AMB_new
    T_SURF_EXP_log[i_EXP_log]=T_SURF_new
    i_EXP_log=i_EXP_log+1
    
def end_EXP_log():
    global P_ABS_EXP_log
    global T_AMB_EXP_log
    global T_SURF_EXP_log
    global i_EXP_log
    
    export=np.transpose([P_ABS_EXP_log, T_AMB_EXP_log, T_SURF_EXP_log ])
    export=export[0:i_EXP_log,:]
    
    timestamp=datetime.today().strftime('%Y_%m_%d_%H_%M_%S')
    
    np.savetxt("/Users/bernardo/Desktop/explog"+timestamp+".csv", export, delimiter=",", header="P_ABS,T_AMB,T_SURF")
    
    P_ABS_EXP_log=np.zeros(nexp)
    T_AMB_EXP_log=np.zeros(nexp)
    T_SURF_EXP_log=np.zeros(nexp)
    i_EXP_log=0

    

#AMBIENT
P_ABS_log=np.zeros(1)
T_AMB_log=np.zeros(1)
T_SURF_log=np.zeros(1)
log_state=0
i_log=0
n_samples=7200

def start_log():
    global n_samples
    global log_state
    global i_log
    global P_ABS_log
    global T_AMB_log
    global T_SURF_log
    
    P_ABS_log=np.zeros(n_samples)
    T_AMB_log=np.zeros(n_samples)
    T_SURF_log=np.zeros(n_samples)
    log_state=1
    i_log=0
    
def log(T_AMB_new,T_SURF_new,P_new):
    global P_ABS_log
    global T_AMB_log
    global T_SURF_log
    global i_log
    P_ABS_log[i_log]=P_new
    T_AMB_log[i_log]=T_AMB_new
    T_SURF_log[i_log]=T_SURF_new
    i_log+=1
    if i_log==n_samples:
        end_log()
def end_log():
    global P_ABS_log
    global T_AMB_log
    global T_SURF_log
    global log_state
    global ani_interval
    log_state=0
    t=np.arange(1,len(P_ABS_log))
    dt=ani_interval/1000
    t=t*dt
    timestamp=datetime.today().strftime('%Y_%m_%d_%H_%M_%S')
    a = np.asarray(np.transpose([P_ABS_log, T_AMB_log, T_SURF_log ]))
    np.savetxt("/Users/bernardo/Desktop/log"+timestamp+".csv", a, delimiter=",", header="P_ABS,T_AMB,T_SURF")


    

# start collections with zeros



P_ABS  = collections.deque(np.zeros(plot_samples))
T_AMB  = collections.deque(np.zeros(plot_samples))
T_SURF = collections.deque(np.zeros(plot_samples))

# define and adjust figure
fig = Figure(figsize=(5, 4), dpi=100)
ax  = fig.add_subplot(311)
ax1 = fig.add_subplot(312)
ax2 = fig.add_subplot(313)
#pause or resume animation animation state initially 1 (play)
ani_state=1;
def ani_pause_resume():
    global ani_state
    ani_state= not ani_state


root = tkinter.Tk()
root.geometry("1200x900")
root.wm_title("IMBOL_A")
canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.draw()
canvas.get_tk_widget().pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=1)

#toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
#toolbar.update()
#toolbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)


###############
###############
#GUI
###############
###############

normal_width=10
normal_height=2
bigfont=tkFont.Font(size=16, weight='bold')

xline=300
nlines=10
lines=[]
def make_line():
    global i_line
    lines.append(tkinter.Canvas(master=root,width=xline,height=5))
    lines[-1].pack(side=tkinter.TOP)
    lines[-1].create_line(0,3,xline,3,fill="grey70")
    
###############
#CONTROL AND STATE


mainframe = tkinter.Frame(master=root)
mainframe.pack( side = tkinter.TOP )

controlframe = tkinter.Frame(master=mainframe)
controlframe.pack( side = tkinter.LEFT )

stateframe = tkinter.Frame(master=mainframe)
stateframe.pack( side = tkinter.LEFT )



###CONTROL


vacate_state=0
flush_state=0
dose_timer=500
P_ABS_EXP=0
T_AMB_EXP=0
T_SURF_EXP=0

def close_all():
    global vacate_state
    global flush_state
    set_config_BOLI(0)
    vacate_state=0
    flush_state=0
    manual_enable()

def VACATE():
    global vacate_state
    vacate_state=1
    set_config_BOLI(0)
    manual_disable()
    
def check_vac(P):
    global vacate_state
    global P_vacuum
    if vacate_state and(P<P_vacuum):
            set_config_BOLI(0)
            vacate_state=0
            manual_enable()
            messagebox.showinfo("P_vac reached \n IMBOL_A","Close valve and turn off vacuum pump",icon=messagebox.WARNING)

def FLUSH():
    global flush_state
    flush_state=1
    set_config_BOLI(OPEN_N2)
    manual_disable()
    
def check_flush(P):
    global flush_state
    global P_flush
    if flush_state and P>P_flush :
            set_config_BOLI(0)
            flush_state=0
            manual_enable()
  
            
def DOSE():
    global P_ABS_EXP
    global T_AMB_EXP
    global T_SURF_EXP

    (T_AMB_EXP,T_SURF_EXP,P_ABS_EXP)=read_sensors_BOLI()
    set_config_BOLI(OPEN_DOSING|SINGLE_DOSE)
    button_dose.configure(state=tkinter.DISABLED)#NORMAL
    
def RECORD():
    global P_ABS_EXP
    global T_AMB_EXP
    global T_SURF_EXP
    EXP_log(T_AMB_EXP,T_SURF_EXP,P_ABS_EXP)
    button_dose.configure(state=tkinter.NORMAL)
    
def ENABLE_DOSE():
    button_dose.configure(state=tkinter.NORMAL)
    
        

button_close_all = tkinter.Button(master=controlframe, text="FULL STOP",width=normal_width,height=normal_height,font=bigfont, command=close_all)
button_close_all.pack(side=tkinter.TOP)
button_vacate = tkinter.Button(master=controlframe, text="VACATE",width=normal_width,height=normal_height,font=bigfont, command=VACATE)
button_vacate.pack(side=tkinter.TOP)
button_flush = tkinter.Button(master=controlframe, text="FLUSH",width=normal_width,height=normal_height,font=bigfont, command=FLUSH)
button_flush.pack(side=tkinter.TOP)
button_dose = tkinter.Button(master=controlframe, text="DOSE",width=normal_width,height=normal_height,font=bigfont, command=DOSE)
button_dose.pack(side=tkinter.TOP)

saveframe = tkinter.Frame(master=controlframe)
saveframe.pack( side = tkinter.TOP )
button_record = tkinter.Button(master=saveframe, text="SAVE",width=normal_width//2-2,height=normal_height, command=RECORD)
button_record.pack(side=tkinter.LEFT)
button_enable_dose = tkinter.Button(master=saveframe, text="OK",width=normal_width//2-2,height=normal_height, command=ENABLE_DOSE)
button_enable_dose.pack(side=tkinter.LEFT)



###STATE



def LED_state_colors_update():
    global current_config
    LED_state=[OPEN_N2,OPEN_NOVEC,OPEN_DOSING,OVERFLOW_TRGD,WIPER_ON,PUMP_ON,WIPER_DIR,SINGLE_DOSE]
    
    for i in range(nLED):
        color=LED_state[i]&current_config
        if color ==0:
            LEDS.itemconfig(LEDS_id[i],fill='red')
        else:
            LEDS.itemconfig(LEDS_id[i],fill='green')




#tkinter.Label(master=ambientframe, text='AMBIENT CONTROL',fg='gray30' ).grid(row=0,column=0)

label_config=tkinter.Label(master=stateframe, text="Current state: "+format(current_config, '#010b'))
label_config.pack(side=tkinter.TOP)

LED_LABEL=["N2","Novec","Dosing","O.F.","Wiper","Pump","W.D.","S. Dose"]


nLED=len(LED_LABEL)
hLED=7
wLED=20
x0_LED=2*wLED
x0_text=3;
y0_LED=8
spacing_LED=10
LEDS_id=[0]*nLED
LEDS_colors=['red']*nLED
LEDS=tkinter.Canvas(master=stateframe,width=wLED*3,height=(nLED*hLED)+(nLED*spacing_LED)+(2*y0_LED))
LEDS.pack(side=tkinter.TOP)
y1_LED=y0_LED
y2_LED=y0_LED+hLED
for i in range(nLED):
    
    LEDS_id[i]=LEDS.create_rectangle(x0_LED, y1_LED, x0_LED+wLED, y2_LED,fill=LEDS_colors[i])
    LEDS.create_text(x0_text,y1_LED+hLED/2,text=LED_LABEL[i],anchor=tkinter.W,font=tkFont.Font(size=10))
    y1_LED=y2_LED+spacing_LED
    y2_LED=y1_LED+hLED

###############
#MANUAL

make_line()
manualframe = tkinter.Frame(master=root)
manualframe.pack( side = tkinter.TOP )


def toggle_config(state):
    global current_config
    new_config=current_config ^ state
    set_config_BOLI(new_config)
    
def toggle_dosing():
    toggle_config(OPEN_DOSING)
def toggle_N2():
    toggle_config(OPEN_N2)
def toggle_novec():
    toggle_config(OPEN_NOVEC)
def toggle_pump():
    toggle_config(PUMP_ON)
    


tkinter.Label(master=manualframe, text='MANUAL CONTROL',fg='gray30' ).grid(row=0,column=0)

button_manual_dosing = tkinter.Button(master=manualframe, text="Dosing",width=normal_width,height=normal_height, command=toggle_dosing)
button_manual_dosing.grid(row=1, column=0)

button_manual_N2 = tkinter.Button(master=manualframe, text="N2",width=normal_width,height=normal_height, command=toggle_N2)
button_manual_N2.grid(row=1, column=1)

button_manual_NOVEC = tkinter.Button(master=manualframe, text="NOVEC",width=normal_width,height=normal_height, command=toggle_novec)
button_manual_NOVEC.grid(row=2, column=0)

button_pump = tkinter.Button(master=manualframe, text="Pump",width=normal_width,height=normal_height, command=toggle_pump)
button_pump.grid(row=2, column=1)

def switch_wiper():
    toggle_config(WIPER_ON)
    
#def switch_wiper():
#    global current_config
#    wiper_config= current_config&(WIPER_ON|WIPER_DIR)
#    new_config=wiper_config ^ WIPER_ON
#    set_config_BOLI(new_config)
    
def switch_wiper_dir():
    toggle_config(WIPER_DIR)
    
button_wipe = tkinter.Button(master=manualframe, text="Wiper",width=normal_width,height=normal_height, command=switch_wiper)
button_wipe.grid(row=3, column=0)

button_wipe_dir = tkinter.Button(master=manualframe, text="WIPER DIR",width=normal_width,height=normal_height, command=switch_wiper_dir)
button_wipe_dir.grid(row=3, column=1)

manual_button_list=[button_manual_N2,button_manual_dosing,button_manual_NOVEC,button_pump,button_wipe,button_wipe_dir]
def manual_disable():
        for button in manual_button_list:
            button.configure(state=tkinter.DISABLED)
def manual_enable():
        for button in manual_button_list:
            button.configure(state=tkinter.NORMAL)

###############
#PAUSE PLOT
#button_ani_control = tkinter.Button(master=root, text="Pause/Resume plot",width=normal_width,height=normal_height, command=ani_pause_resume)
#button_ani_control.pack(side=tkinter.TOP)

###############
#AMBIENT
make_line()
ambientframe = tkinter.Frame(master=root)
ambientframe.pack( side = tkinter.TOP )

P_vacuum=50;
P_flush=900;

def set_P_vacuum():
    global P_vacuum
    P_vacuum=int(input_set_P_vacuum.get())
    input_set_P_vacuum.delete(0, tkinter.END)
    label_set_P_vacuum.configure(text="P_vac= "+ str(P_vacuum)+" [mbar]")
    
def set_P_flush():
    global P_flush
    P_flush=int(input_set_P_flush.get())
    input_set_P_flush.delete(0, tkinter.END)
    label_set_P_flush.configure(text="P_N2= "+ str(P_flush)+" [mbar]")


def set_T_surf(data):
    adress=TEMP_SURF_WRITE
    send = adress << 8
    send += data
    boli.write(send.to_bytes(2, 'big'))
    t_set=boli.read(2)
    return T_C(t_set)
def set_T_surf_button():
    data=int(input_set_T.get())
    new_T=set_T_surf(data)
    input_set_T.delete(0, tkinter.END)
    label_set_T.configure(text="T_s= "+ str(round(new_T))+" [°C]")
    
def set_dose_interval(data):
    adress=DOSE_INTERVAL_WRITE
    send = adress << 16
    send += data
    boli.write(send.to_bytes(3, 'big'))
    timer_set=boli.read(2)
    timer_set=int.from_bytes(timer_set, "big")
    return timer_set
def set_dose_interval_button():
    data=int(input_set_interval.get())
    new_interval=set_dose_interval(data)
    input_set_interval.delete(0, tkinter.END)
    label_set_interval.configure(text="t_D= "+ str(new_interval)+" [ms]")
    
tkinter.Label(master=ambientframe, text='AMBIENT CONTROL',fg='gray30' ).grid(row=0,column=0)

label_set_P_vacuum=tkinter.Label(master=ambientframe, text="P_vac= "+ str(P_vacuum)+" [mbar]")
label_set_P_vacuum.grid(row=1, column=0)

input_set_P_vacuum=tkinter.Entry(master=ambientframe,width=normal_width)
input_set_P_vacuum.grid(row=2, column=0)

button_set_P_vacuum = tkinter.Button(master=ambientframe, text="Set P_v",width=normal_width,height=normal_height, command=set_P_vacuum)
button_set_P_vacuum.grid(row=3, column=0)

label_set_P_flush=tkinter.Label(master=ambientframe, text="P_f= "+ str(P_flush)+" [mbar]")
label_set_P_flush.grid(row=1, column=1)

input_set_P_flush=tkinter.Entry(master=ambientframe,width=normal_width)
input_set_P_flush.grid(row=2, column=1)

button_set_P_flush = tkinter.Button(master=ambientframe, text="Set P_f",width=normal_width,height=normal_height, command=set_P_flush)
button_set_P_flush.grid(row=3, column=1)


label_set_T=tkinter.Label(master=ambientframe, text="T_s = 0 [°C]")
label_set_T.grid(row=4, column=0)

input_set_T=tkinter.Entry(master=ambientframe,width=normal_width)
input_set_T.grid(row=5, column=0)

button_set_T = tkinter.Button(master=ambientframe, text="Set T_surf",width=normal_width,height=normal_height, command=set_T_surf_button)
button_set_T.grid(row=6, column=0)


label_set_interval=tkinter.Label(master=ambientframe, text="t_D= 500 [ms]")
label_set_interval.grid(row=4, column=1)


input_set_interval=tkinter.Entry(master=ambientframe,width=normal_width)
input_set_interval.grid(row=5, column=1)

button_set_interval = tkinter.Button(master=ambientframe, text="Set t_dose",width=normal_width,height=normal_height, command=set_dose_interval_button)
button_set_interval.grid(row=6, column=1)







###############
#LOG
make_line()

def set_log_time():
    global n_samples
    data=int(input_set_log.get())
    
    n_samples = data*(60000//ani_interval)
    
    input_set_log.delete(0, tkinter.END)
    label_set_log.configure(text="T_log = "+ str(round(data))+" [min]")
    

def log_LED_update():
    if log_state==0:
        log_LED.itemconfig(log_LED_id,fill='red')
    else :
        log_LED.itemconfig(log_LED_id,fill='green')

logframe = tkinter.Frame(master=root)
logframe.pack( side = tkinter.TOP )


tkinter.Label(master=logframe, text='AMBIENT LOG',fg='gray30' ).grid(row=0,column=0)

label_set_log=tkinter.Label(master=logframe, text="T_log = 60 [min]")
label_set_log.grid(row=1,column=1)

button_set_log = tkinter.Button(master=logframe, text="Set T_log",width=normal_width,height=normal_height, command=set_log_time)
button_set_log.grid(row=3,column=1)

input_set_log=tkinter.Entry(master=logframe,width=normal_width)
input_set_log.grid(row=2,column=1)

logw=120
logh=logw/3
log_LED=tkinter.Canvas(master=logframe,width=logw,height=logh);
log_LED.grid(row=1,column=0)
log_LED_x=(logw/2)-(wLED/2)
log_LED_y=(logh/2)-(hLED/2)
log_LED_id=log_LED.create_rectangle(log_LED_x,log_LED_y,log_LED_x+wLED,log_LED_y+hLED,fill='red')



button_start_log = tkinter.Button(master=logframe, text="Start log",width=normal_width,height=normal_height, command=start_log)
button_start_log.grid(row=2,column=0)

button_end_log = tkinter.Button(master=logframe, text="End log",width=normal_width,height=normal_height, command=end_log)
button_end_log.grid(row=3,column=0)


make_line()
button_end_log = tkinter.Button(master=root, text="SAVE EXP LOG",width=normal_width*2,height=normal_height, command=end_EXP_log)
button_end_log.pack(side=tkinter.TOP)




# animate
ani = FuncAnimation(fig, animation_main, interval=ani_interval)
tkinter.mainloop()
