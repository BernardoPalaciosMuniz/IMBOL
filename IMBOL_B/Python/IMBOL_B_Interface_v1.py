from cgitb import text
from pickle import LONG_BINGET
from random import random
from textwrap import fill
from tracemalloc import start
from turtle import bgcolor
from datetime import datetime
import serial
import serial.tools.list_ports
import math
import time

RREF0=470
RREF1=470
def T_C(T_ADC,RREF):
    RNOMINAL=100.0
    a=0.00390830
    b=-0.0000005775
    R = int.from_bytes(T_ADC, "big")
    R *= RREF/32768
    Rrate = R/RNOMINAL
    T = a*a
    T -= 4*b*(1-Rrate)
    T = math.sqrt(T)
    T -= a
    T /= 2*b
    return T

def T_ADC(T,RREF):
    RNOMINAL=100.0
    a=0.00390830
    b=-0.0000005775
    T_ADC=a**2
    T_ADC-=(2*b*T+a)**2
    T_ADC/=4*b
    T_ADC=1-T_ADC
    T_ADC*=32768*RNOMINAL/RREF
    return int(T_ADC)
    

def P_mbar(P_ADC):
    A_R=0.005032358
    B_R=0.105867#I=Ax+B=4-20 ma **Updated:29-08-22
    P_Range=1000#Preasure range in mbar from calibration on provided sensor documentation
    I_Span_P=15.998# Current span in mA for sensor 1 from calibration on provided sensor documentation
    I0_P=4.001#Current at 0 mbar from calibration on provided sensor documentation
    A_P= P_Range/I_Span_P
    B_P= -A_P*I0_P
    P = int.from_bytes(P_ADC, "big")
    P *= A_R
    P += B_R  # convert output to mA
    P *= A_P
    P += B_P  # convert output to mbar
    return P

REGISTER_READ       =int('0x00',16)
REGISTER_CONNECT    =int('0x06',16)



connection_state_A = 0

def connect_MCUs():
    global connection_state_A
    global MCU_A
    global MCU_A_port

    baudrate_MX = 200000
    baudrate_Nano = 9600

    listports = serial.tools.list_ports.comports()
    ports = []
    baudrates = []

    for port, desc, hwid in sorted(listports):

        if desc == 'Feather M4 Express':
                ports.append("{}".format(port))
                baudrates.append(baudrate_MX)
        if desc == 'Arduino Due Prog. Port':
                ports.append("{}".format(port))
                baudrates.append(baudrate_MX)
        if desc == 'Arduino Nano Every':
                ports.append("{}".format(port))
                baudrates.append(baudrate_Nano)

    for i in range(len(ports)):

        with serial.Serial(ports[i], baudrates[i], timeout=0.5) as ser:
                    adress = REGISTER_CONNECT
                    time.sleep(0.5)
                    ser.write(adress.to_bytes(1, 'big'))
                    query = ser.read_until('\n')
                    
                    
                    

        if (query ==b'MCU_a\n') and (not connection_state_A):
                    MCU_A_port=ports[i]
                    MCU_A = serial.Serial(ports[i], baudrates[i], timeout=0.5)
                    connection_state_A = 1
                    print("I have conccted")











def WRITE_READ(MCU,adress,nbytes_r=0,data_w=0,nbytes_w=0):
    MCU.write(adress.to_bytes(1,'big'))
    if nbytes_w>0:
        MCU.write(data_w.to_bytes(nbytes_w,'big'))
    if nbytes_r>0:
        return MCU.read(nbytes_r)



        
    

def MCU_A_READ():
    nbytes=6
    output=[]
    data=WRITE_READ(MCU_A,REGISTER_READ,nbytes)
    output.append(P_mbar(data[0:2]))#P
    for x in range(2,5,2):
        output.append(T_C(data[x:x+2],RREF0))#T*2RREF0
    return output



#############PLOT############

from matplotlib.figure import Figure
import numpy as np
import collections

animation_interval=500
plot_samples=100
plot_x=np.linspace(-plot_samples*animation_interval/1000,0,plot_samples)
# plot_labels=["P_abs [mbar]","T_surf [ºC]","T_res [ºC]","T_ext [ºC]","T_tip [ºC]","ADC_out [%](surf blue, res red)"]
# plot_units=['{:04.0f}mbar']+['{:03.1f}°C']*4+['{:03.1f}%']*2
plot_labels=["P [mbar]","T[ºC]"]
plot_units=['{:04.0f}mbar']+['{:03.1f}°C']*2
plot_limits=[1050,70]

def plot_init():
    nax=len(plot_labels)
    ndata=len(plot_units)
    zeros=[0]*ndata
    for i in range(ndata):
        zeros[i]=collections.deque(np.zeros(plot_samples))
    Plot = Figure(figsize=(9.6, 10.24), dpi=100)
    axes=[0]*nax
    if nax<=3: 
        ncols=1
        nrows=nax
    elif nax==4:
        ncols=2
        nrows=2
    else:
        ncols=2
        nrows=3
    for i in range(nax):
        axes[i]=Plot.add_subplot(nrows,ncols,i+1)
        ax=axes[i]
        y=zeros[i]
        ax.plot(plot_x,y)
        ax.scatter(0, y[-1])
        ax.text(0, y[-1], plot_units[i].format(y[-1]),horizontalalignment='left')
        ax.set_ylim(0,plot_limits[i])
        ax.set_xlim(plot_x[0],plot_x[-1]+7)
        ax.set_ylabel(plot_labels[i])
    return [Plot,zeros]
[Plot,data]=plot_init()

def plot_update(data_new):
    axes=Plot.get_axes()
    nax=len(axes)
    ndata=len(data)
    def plot(i,ax,col,lab):
        y=data[i]
        y.popleft()
        y.append(data_new[i])
        ax.plot(plot_x,y,c=col,label=lab+' '+plot_units[i].format(y[-1]))
        ax.scatter(0, y[-1],c=col)
        ax.legend()

        
    
        
    colors=['tab:blue','tab:orange','tab:red','tab:purple']
    labels=['P_abs','Surf','Res','Ext','Sample','Surf','Res']

    for i in range(ndata):

        if i==0:
            i1=0
            i2=0
            ax=axes[i1]
            ax.cla()
        if i==1:
            i1=1
            i2=0
            ax=axes[i1]
            ax.cla()
        if i==5:
            i1=2
            i2=0
            ax=axes[i1]
            ax.cla()
        
        plot(i,ax,colors[i2],labels[i])
        i2=i2+1
        ax.set_ylim(0,plot_limits[i1])
        ax.set_xlim(plot_x[0],plot_x[-1]+7)
        ax.set_ylabel(plot_labels[i1])
        


        
    
    
    


#############GUI############

import tkinter
from tkinter import font as tkFont
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.animation import FuncAnimation

root = tkinter.Tk()
root.geometry("1920x1080")
root.wm_title("IMBOL_B")

normal_width=12
normal_height=2
bigfont=tkFont.Font(size=16, weight='bold')



canvas = FigureCanvasTkAgg(Plot, master=root)  # A tk.DrawingArea.
canvas.draw()
# canvas.get_tk_widget().pack(side=tkinter.LEFT)
canvas.get_tk_widget().pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=1)

def make_line():
    xline=600
    line=tkinter.Canvas(master=root,width=xline,height=5)
    line.pack(side=tkinter.TOP)
    line.create_line(0,3,xline,3,fill="grey70")
def make_frame(mas,pos):
    frame=tkinter.Frame(master=mas)
    frame.pack(side=pos)
    return frame


def enable_buttons(buttons):
        for button in buttons:
            button.configure(state=tkinter.NORMAL)
def disable_buttons(buttons):
        for button in buttons:
            button.configure(state=tkinter.DISABLED)


manualframe= make_frame(root,tkinter.TOP)
logframe = make_frame(root,tkinter.TOP)
logtableframe= make_frame(root,tkinter.TOP)


#############MANUAL############
ncols=4
tkinter.Label(master=manualframe, text='MANUAL CONTROL',fg='gray30' ).grid(row=0,column=0)
buttons_manual=[]
buttons_manual_label=["CONNECT MCUs"]
buttons_manual_command=[connect_MCUs]
buttons_manual.append(tkinter.Button(master=manualframe, text=buttons_manual_label[0],width=normal_width,height=normal_height,state=tkinter.NORMAL, command=buttons_manual_command[0]))
buttons_manual[0].grid(row=0//ncols+1,column=0%ncols)





#############LOG############
log=[]
def log_start():
    global bit_log
    global t0_log
    global log
    log=[]
    t0_log=time.time()
    bit_log=1
def log_stop():
    global bit_log
    bit_log=0
    head="P [mbar],T_1 [°C],T_2 [°C]"
    interval='{:04d}'.format(animation_interval)
    timestamp=datetime.today().strftime('%Y_%m_%d_%H_%M_%S')
    a = np.array(log)
    np.savetxt("/Users/bernardo/Desktop/log_"+interval+"ms_"+timestamp+".csv", a, delimiter=",", header=head)
log_exp=[]
timestamp_session=datetime.today().strftime('%Y_%m_%d_%H_%M_%S')
def log_trig():
    
    global log_exp
    global timestamp_session
    timestamp=datetime.today()
    output=MCU_A_READ()
    output.append(timestamp.hour)
    output.append(timestamp.minute)
    output.append(timestamp.second)
    log_exp.append(output)
    head="P [mbar],T_surf [°C],T_res [°C],T_ext [°C],T_needle [°C],H_set [mm],time_H,time_M,time_S"
    timestamp=timestamp_session
    a = np.array(log_exp)
    np.savetxt("/Users/bernardo/Desktop/exp_log_"+timestamp+".csv", a, delimiter=",", header=head)
    cells_log_update()
    


tkinter.Label(master=logframe, text='LOG',fg='gray30' ).grid(row=0,column=0)
buttons_log=[]
buttons_log_label=["Start log","Stop log","Save current"]
buttons_log_command=[log_start,log_stop,log_trig]




for i in range(len(buttons_log_label)):
    buttons_log.append(tkinter.Button(master=logframe, text=buttons_log_label[i],width=normal_width,height=normal_height,state=tkinter.NORMAL, command=buttons_log_command[i]))
    buttons_log[i].grid(row=i//2+1,column=i%2)



nrows_log=8
head_log=['P','T_s','T_r','T_e','T_n','H_set','h','m','s']
ncols_log=len(head_log)

cells_log=[]
for i in range((nrows_log+1)*ncols_log):
    if i<ncols_log:
        text_log=head_log[i]
    else:
        text_log=''
    cells_log.append(tkinter.Label(master=logtableframe, text=text_log,width=normal_width//3,height=normal_height//3))
    cells_log[i].grid(row=i//ncols_log,column=i%ncols_log)
def cells_log_update():
    global log_exp
    if nrows_log>len(log_exp):
        r_start=-len(log_exp)
    else: 
        r_start=-nrows_log
    for r in range(r_start,0):
        for c in range(-ncols_log,0):
            i=-(r+nrows_log+1)*ncols_log+ncols_log+c
            textnew=str(round(log_exp[r][c]))
            cells_log[i].configure(text=textnew)



bit_log=0





def animation_main(i):
    global log
    global t0_log
    global t_log
    if connection_state_A:
        data_new_A=MCU_A_READ()
        P=data_new_A[0]
        plot_update(data_new_A[0:3])
          

    if bit_log:
        if (time.time()-t0_log<=t_log):
            log.append(data_new_A[2:-2])
        else: 
            log_stop()
    
    
    
ani = FuncAnimation(Plot, animation_main, interval=animation_interval)
tkinter.mainloop()

