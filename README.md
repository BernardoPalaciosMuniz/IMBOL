#  IMBOL

This is a repository for all the code related to the Impact of Boiling Liquids experimental setups IMBOL A and IMBOL B.
- Arduino Code : Control of the setup
- Python Code: GUI
- MATLAB code: Image and data processing


## Required libraries

Make sure the required libraries are installed. For Arduino you can use the library manager ([instructions](https://docs.arduino.cc/software/ide-v1/tutorials/installing-libraries)). For Python you can use the [Anaconda](https://www.anaconda.com/products/distribution) distribution which includes most of these already.
### Arduino

- [PID_v2](https://www.arduino.cc/reference/en/libraries/pid_v2/)
### Python 
- [tkinter](https://docs.python.org/3/library/tkinter.html). Also see this great [guide](https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/index.html)
-  [glob](https://docs.python.org/3/library/glob.html)
- [PySerial](https://pyserial.readthedocs.io/en/latest/)
- [math](https://docs.python.org/3/library/math.html)
- [numpy](https://numpy.org) 

## GUI Usage  

If required. Upload Arduino code to the appropriate MCU 

### IMBOL A
- MCU_A: MIKROE [FLIP&CLICKSAM3X](https://www.mikroe.com/flip-n-click-sam3x)
- MCU_B: ADAFRUIT [FeatherM4Express](https://learn.adafruit.com/adafruit-feather-m4-express-atsamd51/overview) (Not yet implemented)

### IMBOL B
- MCU: MIKROE [FLIP&CLICKSAM3X](https://www.mikroe.com/flip-n-click-sam3x)

Run the python script. Eg, to run the GUI for IMBOL_A on MacOS, run the next command. Note: Replace *YourDirectory* for the actual folder on your system.
```bash
python3 /YourDirectory/IMBOL/IMBOL_A/Python/IMBOL_A.py
```

The GUI will pop up. Controls on the GUI are (mostly) self explanatory. An update of this repository will include a diagram of the electronics and a description of the GUI
