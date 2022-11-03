from pickle import LONG_BINGET
from random import random
from textwrap import fill
from turtle import bgcolor
import serial
import serial.tools.list_ports
import math
import time

RREF0=470
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
    A_R=0.00251428;#Current calibration constant A for the 4-20 ma receiver labeled as 1
    B_R=0.10016;#Current calibration constant B for the 4-20 ma receiver labeled as 1
    P_Range=1000;#Preasure range in mbar from calibration on provided sensor documentation
    I_Span_P=15.998;# Current span in mA for sensor 1 from calibration on provided sensor documentation
    I0_P=4.001;#Current at 0 mbar from calibration on provided sensor documentation
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
MCUA_REL_2      =int('0x02',16) #N7000
MCUA_REL_3      =int('0x04',16) #N2
MCUA_REL_4      =int('0x08',16) #VACUUM
MCUA_REL_5      =int('0x10',16) #DOSING


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
    output.append(int.from_bytes(data[2:4],'big'))#P
    for x in range(4,11,2):
        output.append(T_C(data[x:x+2],RREF0))#T*4
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
def MCU_A_DOSE_T(data):
    return WRITE_READ(MCU_A,REGISTER_RTD1,2,data,2)
def MCU_A_DOSE_S():
    WRITE_READ(MCU_A,REGISTER_RTD1)
def MCU_A_TRIGGER():
    nbytes=16
    output=[]
    printstr=''
    output_labels=["P_abs = ",", T_1 = ",", T_2 = ",", T_3 = ",", T_4 = "]
    data=WRITE_READ(MCU_A,REGISTER_READ,nbytes)
    output.append(int.from_bytes(data[2:4],'big'))#P
    for x in range(4,11,2):
        output.append(round(T_C(data[x:x+2],RREF0),2))#T*4
    
    for i in range(len(output)):
        printstr=printstr+output_labels[i]
        printstr=printstr+str(output[i])
    print(printstr)
    
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
plot_labels=["P_abs [12 bits]","T_0 [ºC]","T_1 [ºC]","T_2 [ºC]","T_3 [ºC]","ADC_out [%]"]
plot_units=['{:04.0f}']+['{:03.1f}°C']*4+['{:03.1f}%']*2
plot_limits=[4100]+[50]*4+[100]*2

def plot_init():
    nax=len(plot_labels)
    ndata=len(plot_units)
    zeros=[0]*ndata
    for i in range(ndata):
        zeros[i]=collections.deque(np.zeros(plot_samples))
    Plot = Figure(figsize=(19.20, 10.24), dpi=100)
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
        ax.text(0, y[-1]+plot_limits[i]*.05, plot_units[i].format(y[-1]),horizontalalignment='left')
        ax.set_ylim(0,plot_limits[i])
        ax.set_xlim(plot_x[0],plot_x[-1]+7)
        ax.set_ylabel(plot_labels[i])
    return [Plot,zeros]
[Plot,data]=plot_init()

def plot_update(data_new):
    axes=Plot.get_axes()
    nax=len(axes)
    def plot(i,ax,col):
        y=data[i]
        y.popleft()
        y.append(data_new[i])
        ax.plot(plot_x,y,c=col)
        ax.scatter(0, y[-1],c=col)
        ax.text(0, y[-1]+plot_limits[i]*.05, plot_units[i].format(y[-1]),horizontalalignment='left')
    for i in range(nax):
        ax=axes[i]
        ax.cla()
        plot(i,ax,'b')
        if i==nax-1:
            plot(i+1,ax,'b')
        ax.set_ylim(0,plot_limits[i])
        ax.set_xlim(plot_x[0],plot_x[-1]+7)
        ax.set_ylabel(plot_labels[i])

        
    
    
    


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
canvas.get_tk_widget().pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=1)

def make_line():
    xline=400
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



def test_command():
    print('press')


#############MAIN############

buttons_control=[]
buttons_control_label=["RUN","STOP","VACATE","FLUSH","FILL","DOSE","TRIG"]
buttons_control_command=[test_command]*3
buttons_control_command=[test_command,MCU_A_STOP]+buttons_control_command+[MCU_A_DOSE_S,MCU_A_TRIGGER]


for i in range(len(buttons_control_label)):

    buttons_control.append(tkinter.Button(master=controlframe, text=buttons_control_label[i],width=normal_width,height=normal_height,font=bigfont,state=tkinter.DISABLED, command=buttons_control_command[i]))
    buttons_control[i].pack(side=tkinter.TOP)
def LEDS_control_init():
    hLED=15
    wLED=45
    y0_LED=8
    textsize=10
    spacing_LED=10
    LED_LABEL=["MAIN","N-7000","N2","VACUUM","DOSING","Float","Pump","P. Dir","Wiper","W.Dir."]
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
buttons_manual_label_MCUA=["MAIN","N-7000","N2","VACUUM","DOSING"]
buttons_manual_data_MCUA=[MCUA_REL_1,MCUA_REL_2,MCUA_REL_3,MCUA_REL_4,MCUA_REL_5]

buttons_manual_label_MCUB=["PUMP","PUMP_DIR","WIPER","W. DIR","CONNECT MCUs"]
buttons_manual_data_MCUB=[MCUB_EN_A,MCUB_DIR_A,MCUB_EN_B,MCUB_DIR_B]

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
                buttons_A=buttons_ambient+buttons_control+buttons_ambient+buttons_manual[:5]+buttons_ambient+buttons_log
                enable_buttons(buttons_A)
            if connection_state_B:
                buttons_B=buttons_manual[5:-1]
                enable_buttons(buttons_B)

    return f

for i in range(len(buttons_manual_label_MCUA)+len(buttons_manual_label_MCUB)):
    buttons_manual_command.append(buttons_manual_defcommand(i))
    buttons_manual.append(tkinter.Button(master=manualframe, text=buttons_manual_label[i],width=normal_width,height=normal_height,state=tkinter.DISABLED, command=buttons_manual_command[i]))
    buttons_manual[i].grid(row=i//3+1,column=i%3)
buttons_manual[-1].configure(state=tkinter.NORMAL)
LED_init(manualframe,4,1,connection_state_A)
LED_init(manualframe,4,2,connection_state_B)


#############CALIBRATE############
tkinter.Label(master=ambientframe, text='AMBIENT CONTROL',fg='gray30' ).grid(row=0,column=0)
buttons_ambient=[]
labels_ambient=[]
inputs_ambient=[]
ncols=3
buttons_ambient_label=["I_P","P_N2","T_srf","T_res","t_dose","t_log"]
buttons_ambient_units=["[mA]","[mbar]","[°C]","[°C]","[ms]","[s]"]
init_values_ambient=[20,900,20,20,500,3600]
def cal():
    nbytes=16
    output=[]
    data=WRITE_READ(MCU_A,REGISTER_READ,nbytes)
    output.append(int.from_bytes(data[2:4],'big'))#P
    for x in range(4,11,2):
        output.append(int.from_bytes(data[x:x+2],'big'))#T*4
    return output


dataP_I=[]
dataP_ADC=[]

def P_cal():
    i=0
    data=float(inputs_ambient[i].get())
    data_ADC=cal()
    data_ADC=data_ADC[0]
    dataP_I.append(data)
    dataP_ADC.append(data_ADC)
    print(dataP_ADC)
    print(dataP_I)
    print(np.polyfit(dataP_ADC,dataP_I,1))
    inputs_ambient[i].delete(0,tkinter.END)
    labels_ambient[i].configure(text=buttons_ambient_label[i]+"="+str(data)+str(buttons_ambient_units[i]))


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

def ambient_set_t_dose():
    i=4
    data=int(inputs_ambient[i].get())
    data=MCU_A_DOSE_T(data)
    data=int.from_bytes(data,'big')
    inputs_ambient[i].delete(0,tkinter.END)
    labels_ambient[i].configure(text=buttons_ambient_label[i]+"="+str(data)+str(buttons_ambient_units[i]))


buttons_ambient_command=[test_command]*len(buttons_ambient_label)
buttons_ambient_command[0]=P_cal
buttons_ambient_command[2]=ambient_set_T_surf
buttons_ambient_command[3]=ambient_set_T_res
buttons_ambient_command[4]=ambient_set_t_dose

for i in range(len(buttons_ambient_label)):
    labels_ambient.append(tkinter.Label(master=ambientframe, text=buttons_ambient_label[i]+"="+str(init_values_ambient[i])+str(buttons_ambient_units[i]),width=normal_width,height=normal_height))
    labels_ambient[i].grid(row=(i//ncols)*3+1,column=i%ncols)
    inputs_ambient.append(tkinter.Entry(master=ambientframe ,width=normal_width))
    inputs_ambient[i].grid(row=(i//ncols)*3+2,column=i%ncols)
    buttons_ambient.append(tkinter.Button(master=ambientframe, text=buttons_ambient_label[i],width=normal_width,height=normal_height, state=tkinter.DISABLED,command=buttons_ambient_command[i]))
    buttons_ambient[i].grid(row=(i//ncols)*3+3,column=i%ncols)

#############LOG############

tkinter.Label(master=logframe, text='LOG',fg='gray30' ).grid(row=0,column=0)
buttons_log=[]
buttons_log_label=["Start log","Stop log","Save TRIG"]
buttons_log_command=[test_command]*len(buttons_log_label)
for i in range(len(buttons_log_label)):
    buttons_log.append(tkinter.Button(master=logframe, text=buttons_log_label[i],width=normal_width,height=normal_height,state=tkinter.DISABLED, command=buttons_log_command[i]))
    buttons_log[i].grid(row=i//2+1,column=i%2)

bit_log=0
LED_init(logframe,2,1,bit_log)




def animation_main(i):
    data_led=0
    if connection_state_A:
        data_new_A=MCU_A_READ()
        data_led|=data_new_A[0]
        data_led|=data_new_A[1]<<5
        plot_update(data_new_A[2:])
        
        
        

    if connection_state_B:
        data_new_B=bits_MCU_B<<6
        data_led|=data_new_B
        
    LEDS_control_update(data_led)
    LEDS_bits=[connection_state_A,connection_state_B,bit_log]
    LEDS_update(LEDS_bits)
    
ani = FuncAnimation(Plot, animation_main, interval=animation_interval)
tkinter.mainloop()

