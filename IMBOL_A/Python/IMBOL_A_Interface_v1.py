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
RREF1=430
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
    A_R=0.00501575
    B_R=-0.034#I=Ax+B=4-20 ma **Updated:29-08-22
    P_Range=1000#Preasure range in mbar from calibration on provided sensor documentation
    I_Span_P=16.004# Current span in mA for sensor 1 from calibration on provided sensor documentation
    I0_P=3.997#Current at 0 mbar from calibration on provided sensor documentation
    A_P= P_Range/I_Span_P
    B_P= -A_P*I0_P
    P = int.from_bytes(P_ADC, "big")
    P *= A_R
    P += B_R  # convert output to mA
    P *= A_P
    P += B_P  # convert output to mbar
    return P

REGISTER_READ       =int('0x00',16)
REGISTER_REL        =int('0x01',16)
REGISTER_RTD1       =int('0x02',16)
REGISTER_RTD2       =int('0x03',16)
REGISTER_DOSE_T     =int('0x04',16)
REGISTER_DOSE_S     =int('0x05',16)
REGISTER_CONNECT    =int('0x06',16)
REGISTER_TOGGLE     =int('0x07',16)
REGISTER_TRIGGER    =int('0x08',16)
REGISTER_LIGHTSON   =int('0x09',16)
REGISTER_TRIG_PERIOD =int('0x0B',16)
REGISTER_TUNE_PID1 =int('0x0C',16)
REGISTER_TUNE_PID2 =int('0x0D',16)

REGISTER_WRITE_MCU_B       =int('0x00',16)
REGISTER_TOGGLE_MCU_B      =int('0x02',16)

connection_state_A = 0
connection_state_B = 0
def connect_MCUs():
    global connection_state_A
    global connection_state_B
    global MCU_A
    global MCU_B
    global MCU_A_port
    global MCU_B_port
    baudrate_MX = 20000000
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
                    if baudrates[i]==baudrate_Nano:
                        time.sleep(0.1)
                    ser.write(adress.to_bytes(1, 'big'))
                    query = ser.read_until('\n')
                    
                    

        if (query ==b'MCU_a\n') and (not connection_state_A):
                    MCU_A_port=ports[i]
                    MCU_A = serial.Serial(ports[i], baudrates[i], timeout=0.5)
                    connection_state_A = 1
        if (query ==b'MCU_b\n') and (not connection_state_B):
                    MCU_B_port=ports[i]
                    MCU_B = serial.Serial(ports[i], baudrates[i], timeout=0.5)
                    connection_state_B = 1






MCUA_REL_1      =int('0x01',16) #MAIN
MCUA_REL_2      =int('0x02',16) #VACUUM
MCUA_REL_3      =int('0x04',16) #N2
MCUA_REL_4      =int('0x08',16) #N7000
MCUA_REL_5      =int('0x10',16) #DOSING
MCUA_REL_6      =int('0x20',16) #RETRIEVE
MCUA_REL_8      =int('0x80',16) #R. LIGHT



def WRITE_READ(MCU,adress,nbytes_r=0,data_w=0,nbytes_w=0):
    MCU.write(adress.to_bytes(1,'big'))
    if nbytes_w>0:
        MCU.write(data_w.to_bytes(nbytes_w,'big'))
    if nbytes_r>0:
        return MCU.read(nbytes_r)



        
    

def MCU_A_READ():
    nbytes=16
    output=[]
    data=WRITE_READ(MCU_A,REGISTER_READ,nbytes)
    output.append(int.from_bytes(data[0:1],'big'))#relay
    output.append(int.from_bytes(data[1:2],'big'))#float
    output.append(P_mbar(data[2:4]))#P
    for x in range(4,7,2):
        output.append(T_C(data[x:x+2],RREF0))#T*2RREF0
    for x in range(8,11,2):
        output.append(T_C(data[x:x+2],RREF1))#T*2RREF1
    for x in range(12,15,2):
        adc=int.from_bytes(data[x:x+2],'big')
        adc_bits=int('0x0fff',16)
        output.append(adc/adc_bits*100)#ADC*2
    return output
def MCU_A_WRITE(data):
    return WRITE_READ(MCU_A,REGISTER_REL,0,data,1)
def MCU_A_TOGGLE(data):
    return WRITE_READ(MCU_A,REGISTER_TOGGLE,0,data,1)
def MCU_A_RTD1(T,RREF):
    data=T_ADC(T,RREF)
    output= WRITE_READ(MCU_A,REGISTER_RTD1,2,data,2)
    output=T_C(output,RREF0)
    return output
def MCU_A_RTD2(T,RREF):
    data=T_ADC(T,RREF)
    output= WRITE_READ(MCU_A,REGISTER_RTD2,2,data,2)
    output=T_C(output,RREF0)
    return output
def MCU_A_TUNE_PID1(data):
    return WRITE_READ(MCU_A,REGISTER_RTD1,2,data,2)
def MCU_A_TUNE_PID2(data):
    return WRITE_READ(MCU_A,REGISTER_RTD2,2,data,2)
def MCU_A_DOSE_T(data):
    return WRITE_READ(MCU_A,REGISTER_RTD1,2,data,2)
def MCU_A_TRIG_T(data):
    return WRITE_READ(MCU_A,REGISTER_TRIG_PERIOD,2,data,2)
def MCU_A_DOSE_S():
    WRITE_READ(MCU_A,REGISTER_DOSE_S)
def MCU_A_LIGHTSON():
    WRITE_READ(MCU_A,REGISTER_LIGHTSON)
def MCU_A_TRIGGER():
    global H
    output=[]
    data=WRITE_READ(MCU_A,REGISTER_TRIGGER,10)
    output.append(P_mbar(data[:2]))#P
    for x in range(2,5,2):
        output.append(T_C(data[x:x+2],RREF0))#T*2RREF0
    for x in range(6,9,2):
        output.append(T_C(data[x:x+2],RREF1))#T*2RREF1
    output.append(H)
    timestamp=datetime.today()
    output.append(timestamp.hour)
    output.append(timestamp.minute)
    output.append(timestamp.second)
    return output
    
def MCU_A_STOP():
    MCU_A_WRITE(0)


    




MCUB_EN_A       =int('0x01',16)
MCUB_DIR_A      =int('0x02',16)
MCUB_EN_B       =int('0x04',16)
MCUB_DIR_B      =int('0x08',16)

bits_MCU_B=0

def MCU_B_WRITE(data):
    global bits_MCU_B
    bits_MCU_B=data
    WRITE_READ(MCU_B,REGISTER_WRITE_MCU_B,0,data,1)
def MCU_B_TOGGLE(data):
    global bits_MCU_B
    bits_MCU_B^=data
    WRITE_READ(MCU_B,REGISTER_TOGGLE_MCU_B,0,data,1)



#############PLOT############

from matplotlib.figure import Figure
import numpy as np
import collections

animation_interval=500
plot_samples=100
plot_x=np.linspace(-plot_samples*animation_interval/1000,0,plot_samples)
# plot_labels=["P_abs [mbar]","T_surf [ºC]","T_res [ºC]","T_ext [ºC]","T_tip [ºC]","ADC_out [%](surf blue, res red)"]
# plot_units=['{:04.0f}mbar']+['{:03.1f}°C']*4+['{:03.1f}%']*2
plot_labels=["P [mbar]","T[ºC]","PWM_DutyC [%]"]
plot_units=['{:04.0f}mbar']+['{:03.1f}°C']*4+['{:03.1f}%']*2
plot_limits_high=[1050,60,105]
plot_limits_low=[0,19,0]

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
        ax.set_ylim(plot_limits_low[i],plot_limits_high[i])
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
        ax.set_ylim(plot_limits_low[i1],plot_limits_high[i1])
        ax.set_xlim(plot_x[0],plot_x[-1]+7)
        ax.set_ylabel(plot_labels[i1])
        


        
    
    
    


#############GUI############

import tkinter
from tkinter import font as tkFont
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.animation import FuncAnimation

root = tkinter.Tk()
root.geometry("1920x1080")
root.wm_title("IMBOL_A")

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
LEDS_id=[]
LEDS=[]
def LED_init(frame,r,c,bit):
    hLED=15
    wLED=45
    log_LED=tkinter.Canvas(master=frame,width=wLED+2,height=hLED+2)
    log_LED.grid(row=r,column=c)
    log_LED_x=4
    log_LED_y=4
    log_LED_id=log_LED.create_rectangle(log_LED_x,log_LED_y,log_LED_x+wLED,log_LED_y+hLED,fill='red')
    LEDS.append(log_LED)
    LEDS_id.append(log_LED_id)

def LEDS_update(LEDS_bits):
    for i in range(len(LEDS)):
        if LEDS_bits[i]:
            LEDS[i].itemconfig(LEDS_id[i],fill='green')
        else:
            LEDS[i].itemconfig(LEDS_id[i],fill='red')

def enable_buttons(buttons):
        for button in buttons:
            button.configure(state=tkinter.NORMAL)
def disable_buttons(buttons):
        for button in buttons:
            button.configure(state=tkinter.DISABLED)


mainframe = make_frame(root,tkinter.TOP)

controlframe = make_frame(mainframe,tkinter.LEFT)
stateframe = make_frame(mainframe,tkinter.LEFT)
make_line()

manualframe = make_frame(root,tkinter.TOP)
make_line()

ambientframe = make_frame(root,tkinter.TOP)
make_line()

logframe = make_frame(root,tkinter.TOP)
logtableframe= make_frame(root,tkinter.TOP)



def test_command():
    print('press')


#############MAIN############
bit_trig=0
trig_tick=0
def TRIG():
    global bit_trig
    global trig_tick
    MCU_A_LIGHTSON()
    bit_trig=1
    trig_tick=time.time()
output_trig=0
def TRIG_poll():
    global bit_trig
    global trig_tick
    global output_trig
    if bit_trig:
        now=time.time()
        if (now-trig_tick>=1):
            
            bit_trig=0
            output_trig=MCU_A_TRIGGER()

bit_vacate=0
def VACATE():
    global bit_vacate
    MCU_A_WRITE(MCUA_REL_1|MCUA_REL_2)
    bit_vacate=1
def VACATE_poll(P):
    global bit_vacate
    global P_vac
    if bit_vacate:
        if (P<=P_vac):
            MCU_A_STOP()
            bit_vacate=0
bit_flush=0
def FLUSH():
    global bit_flush
    MCU_A_WRITE(MCUA_REL_1|MCUA_REL_3)
    bit_flush=1
def FLUSH_poll(P):
    global bit_flush
    global P_flush
    if bit_flush:
        if (P>=P_flush):
            MCU_A_STOP()
            bit_flush=0
i_run=0
def RUN():
    global i_run
    MCU_A_WRITE(MCUA_REL_1|MCUA_REL_2)
    i_run=1
def RUN_poll(P):
    global i_run
    if i_run:
        if i_run==1:
            if (P<=P_vac):
                MCU_A_WRITE(MCUA_REL_1|MCUA_REL_3)
                i_run=2
        elif i_run==2:
            if (P>=P_flush):
                MCU_A_WRITE(MCUA_REL_1|MCUA_REL_2)
                i_run=3
        elif i_run==3:
            if (P<=P_vac):
                MCU_A_STOP()
                i_run=0
def POLL(P):
    VACATE_poll(P)
    FLUSH_poll(P)
    RUN_poll(P)
def STOP():
    global i_run
    global bit_vacate
    global bit_flush
    MCU_A_STOP()
    i_run=0
    bit_flush=0
    bit_vacate=0
def RETRIEVE():
    MCU_A_WRITE(MCUA_REL_1|MCUA_REL_6)



buttons_control=[]
buttons_control_label=["RUN","STOP","VACATE","FLUSH","TRIG","RETRIEVE"]
buttons_control_command=[RUN,STOP,VACATE,FLUSH,TRIG,RETRIEVE]


for i in range(len(buttons_control_label)):

    buttons_control.append(tkinter.Button(master=controlframe, text=buttons_control_label[i],width=normal_width,height=normal_height,font=bigfont,state=tkinter.DISABLED, command=buttons_control_command[i]))
    buttons_control[i].pack(side=tkinter.TOP)
def LEDS_control_init():
    hLED=15
    wLED=45
    y0_LED=8
    textsize=10
    spacing_LED=10
    LED_LABEL=["MAIN","VACUUM","N2","N-7000","DOSING","RETRIEVE","REL7","R.Light","Float","Wiper","W.Dir."]
    nLED=len(LED_LABEL)
    LEDS_id=[0]*nLED
    LEDS_colors=['red']*nLED
    LEDS=tkinter.Canvas(master=stateframe,width=wLED*2.5,height=(nLED*hLED)+(nLED*spacing_LED)+(2*y0_LED))
    LEDS.pack(side=tkinter.TOP)
    y1_LED=y0_LED
    y2_LED=y0_LED+hLED
    for i in range(nLED):
        LEDS_id[i]=LEDS.create_rectangle(wLED*1.5, y1_LED, wLED*2.5, y2_LED,fill=LEDS_colors[i])
        LEDS.create_text(textsize,y1_LED+hLED/2,text=LED_LABEL[i],anchor=tkinter.W,font=tkFont.Font(size=textsize,weight='bold'))
        y1_LED=y2_LED+spacing_LED
        y2_LED=y1_LED+hLED
    return [LEDS,LEDS_id]
def LEDS_control_update(data):
    nLEDS=len(LEDS_control_ids)
    data=format(data, '#0'+str(2+nLEDS)+'b')
    data= [int(i) for i in reversed(data[2:])]
    for i in range(nLEDS):
        if data[i] :
            LEDS_control_canvas.itemconfig(LEDS_control_ids[i],fill='green')
        else:
            LEDS_control_canvas.itemconfig(LEDS_control_ids[i],fill='red')

[LEDS_control_canvas,LEDS_control_ids]=LEDS_control_init()

#############MANUAL############
    
tkinter.Label(master=manualframe, text='MANUAL CONTROL',fg='gray30' ).grid(row=0,column=0)
buttons_manual=[]
buttons_manual_label_MCUA=["MAIN","VACUUM","N2","N-7000","DOSING","R.LIGHT","RETRIEVE"]
buttons_manual_data_MCUA=[MCUA_REL_1,MCUA_REL_2,MCUA_REL_3,MCUA_REL_4,MCUA_REL_5,MCUA_REL_8,MCUA_REL_6]

buttons_manual_label_MCUB=["WIPER","W. DIR","CONNECT MCUs"]
buttons_manual_data_MCUB=[MCUB_EN_B,MCUB_DIR_B]

nA=len(buttons_manual_label_MCUA)
nB=len(buttons_manual_label_MCUB)
buttons_manual_data=buttons_manual_data_MCUA+buttons_manual_data_MCUB
buttons_manual_label=buttons_manual_label_MCUA+buttons_manual_label_MCUB

buttons_manual_command=[]
def buttons_manual_defcommand(i):
    def f():
        if i<nA :
            MCU_A_TOGGLE(buttons_manual_data[i])

        elif i<nA+nB-1:
            MCU_B_TOGGLE(buttons_manual_data[i])
            

        else:
            connect_MCUs()
            if connection_state_A:
                buttons_A=buttons_ambient+buttons_control+buttons_ambient+buttons_manual[:nA]+buttons_ambient+buttons_log
                enable_buttons(buttons_A)
            if connection_state_B:
                buttons_B=buttons_manual[nA:-1]
                enable_buttons(buttons_B)

    return f
ncols=4
for i in range(len(buttons_manual_label_MCUA)+len(buttons_manual_label_MCUB)):
    buttons_manual_command.append(buttons_manual_defcommand(i))
    buttons_manual.append(tkinter.Button(master=manualframe, text=buttons_manual_label[i],width=normal_width,height=normal_height,state=tkinter.DISABLED, command=buttons_manual_command[i]))
    buttons_manual[i].grid(row=i//ncols+1,column=i%ncols)
buttons_manual[-1].configure(state=tkinter.NORMAL)
LED_init(manualframe,4,1,connection_state_A)
LED_init(manualframe,4,2,connection_state_B)


#############AMBIENT############
tkinter.Label(master=ambientframe, text='AMBIENT CONTROL',fg='gray30' ).grid(row=0,column=0)
buttons_ambient=[]
labels_ambient=[]
inputs_ambient=[]
ncols=5
buttons_ambient_label=["P_vac","P_N2","T_srf","T_res","t_trig","t_dose","t_log","H_fall"]
buttons_ambient_units=["[mbar]","[mbar]","[°C]","[°C]","[ms]","[ms]","[s]","[mm]"]
init_values_ambient=[50,950,0,0,6000,500,3600,1200]

P_vac=init_values_ambient[0]
def ambient_set_P_vac():
    global P_vac
    i=0
    P_vac=int(inputs_ambient[i].get())
    data=P_vac
    inputs_ambient[i].delete(0,tkinter.END)
    labels_ambient[i].configure(text=buttons_ambient_label[i]+"="+str(data)+str(buttons_ambient_units[i]))
P_flush=init_values_ambient[1]
def ambient_set_P_flush():
    global P_flush
    i=1
    P_flush=int(inputs_ambient[i].get())
    data=str(P_flush)
    inputs_ambient[i].delete(0,tkinter.END)
    labels_ambient[i].configure(text=buttons_ambient_label[i]+"="+data+str(buttons_ambient_units[i]))

def ambient_set_T_surf():
    i=2
    data=float(inputs_ambient[i].get())
    data=MCU_A_RTD1(data,RREF0)
    data=round(data,1)
    inputs_ambient[i].delete(0,tkinter.END)
    labels_ambient[i].configure(text=buttons_ambient_label[i]+"="+str(data)+str(buttons_ambient_units[i]))

def ambient_set_T_res():
    i=3
    data=float(inputs_ambient[i].get())
    data=MCU_A_RTD2(data,RREF0)
    data=round(data,1)
    inputs_ambient[i].delete(0,tkinter.END)
    labels_ambient[i].configure(text=buttons_ambient_label[i]+"="+str(data)+str(buttons_ambient_units[i]))

def ambient_set_t_trig():
    i=4
    data=int(inputs_ambient[i].get())
    data=MCU_A_TRIG_T(data)
    data=int.from_bytes(data,'big')
    inputs_ambient[i].delete(0,tkinter.END)
    labels_ambient[i].configure(text=buttons_ambient_label[i]+"="+str(data)+str(buttons_ambient_units[i]))

def ambient_set_t_dose():
    i=5
    data=int(inputs_ambient[i].get())
    data=MCU_A_DOSE_T(data)
    data=int.from_bytes(data,'big')
    inputs_ambient[i].delete(0,tkinter.END)
    labels_ambient[i].configure(text=buttons_ambient_label[i]+"="+str(data)+str(buttons_ambient_units[i]))

t_log=init_values_ambient[6]
def ambient_set_t_log():
    global t_log
    i=6
    data=int(inputs_ambient[i].get())
    t_log=int(data)
    inputs_ambient[i].delete(0,tkinter.END)
    labels_ambient[i].configure(text=buttons_ambient_label[i]+"="+str(data)+str(buttons_ambient_units[i]))

H=init_values_ambient[7]
def ambient_set_H():
    global H
    i=7
    data=int(inputs_ambient[i].get())
    H=int(data)
    inputs_ambient[i].delete(0,tkinter.END)
    labels_ambient[i].configure(text=buttons_ambient_label[i]+"="+str(data)+str(buttons_ambient_units[i]))


  


buttons_ambient_command=[ambient_set_P_vac,ambient_set_P_flush,ambient_set_T_surf,ambient_set_T_res,ambient_set_t_trig,ambient_set_t_dose,ambient_set_t_log,ambient_set_H]

for i in range(len(buttons_ambient_label)):
    labels_ambient.append(tkinter.Label(master=ambientframe, text=buttons_ambient_label[i]+"="+str(init_values_ambient[i])+str(buttons_ambient_units[i]),width=normal_width,height=normal_height))
    labels_ambient[i].grid(row=(i//ncols)*3+1,column=i%ncols)
    inputs_ambient.append(tkinter.Entry(master=ambientframe ,width=normal_width))
    inputs_ambient[i].grid(row=(i//ncols)*3+2,column=i%ncols)
    buttons_ambient.append(tkinter.Button(master=ambientframe, text=buttons_ambient_label[i],width=normal_width,height=normal_height, state=tkinter.DISABLED,command=buttons_ambient_command[i]))
    buttons_ambient[i].grid(row=(i//ncols)*3+3,column=i%ncols)

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
    head="P [mbar],T_surf [°C],T_res [°C],T_ext [°C],T_needle [°C]"
    interval='{:04d}'.format(animation_interval)
    timestamp=datetime.today().strftime('%Y_%m_%d_%H_%M_%S')
    a = np.array(log)
    np.savetxt("/Users/bernardo/Desktop/log_"+interval+"ms_"+timestamp+".csv", a, delimiter=",", header=head)
log_exp=[]
timestamp_session=datetime.today().strftime('%Y_%m_%d_%H_%M_%S')
def log_trig():
    global output_trig
    global log_exp
    global timestamp_session
    if output_trig:
        log_exp.append(output_trig)
        head="P [mbar],T_surf [°C],T_res [°C],T_ext [°C],T_needle [°C],H_set [mm],time_H,time_M,time_S"
        timestamp=timestamp_session
        a = np.array(log_exp)
        np.savetxt("/Users/bernardo/Desktop/exp_log_"+timestamp+".csv", a, delimiter=",", header=head)
        cells_log_update()
        output_trig=0


tkinter.Label(master=logframe, text='LOG',fg='gray30' ).grid(row=0,column=0)
buttons_log=[]
buttons_log_label=["Start log","Stop log","Save TRIG"]
buttons_log_command=[log_start,log_stop,log_trig]




for i in range(len(buttons_log_label)):
    buttons_log.append(tkinter.Button(master=logframe, text=buttons_log_label[i],width=normal_width,height=normal_height,state=tkinter.DISABLED, command=buttons_log_command[i]))
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
LED_init(logframe,2,1,bit_log)




def animation_main(i):
    global log
    global t0_log
    global t_log
    data_led=0
    if connection_state_A:
        data_new_A=MCU_A_READ()
        bits_relay=data_new_A[0]
        bit_float=data_new_A[1]
        P=data_new_A[2]
        POLL(P)
        data_led|=bits_relay&int('0xff',16)
        data_led|=bit_float<<8
        plot_update(data_new_A[2:])
        if (not bit_float) and(P<950):
            MCU_A_WRITE(bits_relay&(~MCUA_REL_4))        

    if connection_state_B:
        data_new_B=bits_MCU_B<<7
        data_led|=data_new_B
    if bit_log:
        if (time.time()-t0_log<=t_log):
            log.append(data_new_A[2:-2])
        else: 
            log_stop()
    TRIG_poll()
    LEDS_control_update(data_led)
    LEDS_bits=[connection_state_A,connection_state_B,bit_log]
    LEDS_update(LEDS_bits)
    
    
ani = FuncAnimation(Plot, animation_main, interval=animation_interval)
tkinter.mainloop()

