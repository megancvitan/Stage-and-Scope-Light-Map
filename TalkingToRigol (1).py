 # -*- coding: utf-8 -*-
"""

@author: ngutt

"""

import visa
import sys
import datetime
import os

import csv 
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
plt.style.use('seaborn-paper')

import time
import math
import spinmob as s
import scipy.integrate as integrate

from labjack import ljm

### CURRENT AVAILABLE COMMANDS
# instr is a Rigol scope

# General commands
# -- device_info(instr)

# For oscilloscope:
# -- get_data()
# -- take_screenshot()
# -- autoscale()

# Create a ResourceManager object and connect to the Rigol oscilloscope
# Comment out what is not connected
rm = visa.ResourceManager()
Rigol = rm.open_resource('TCPIP0::172.16.0.101::inst0::INSTR', write_termination='\n') 


# General commands
def device_info(instr):
    '''
    Prints out the device information.
    '''
    idn = instr.ask("*IDN?")
    idns = idn.split(',')
    print("Manufacturer: ", idns[0])
    print("Device: ", idns[1])
    print("Serial number: ", idns[2])
    print("Firmware version: ", idns[3])
    
###############################################################################       
# Commands specific to the Rigol oscilloscope    
###############################################################################   
def get_data(input_name = 'None'):
#    '''
#    Takes a screenshot and exports a .csv file at once.
#    '''
#    
#    Rigol.write(":DISP:DATA?")
#    bmpdata = Rigol.read_raw()[2+9:]
#  
    # Save image file
    name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print(input_name)
    
    if input_name != "None":
        name = name + "_" + input_name
    
    else:
        print("Enter a filename-safe description (or none). Hit return.")
        comment = input(name + '_')
        if(len(comment)):
            name = name + "_" + comment

#    try:
#        from PIL import Image
#  
#    except ImportError as e:
#        print("PIL(low) not imported because:", e)
#        filename = name + ".bmp"
#        print("Saving screen as", filename)
#        with open(filename, "wb") as f:
#            f.write(bmpdata)
#  
#    else:
#        print("PILlow", sys.version)
#        import io
#        filename = name + ".png"
#        print("Saving screen as", filename)
#        im = Image.open(io.BytesIO(bmpdata))
#
#    try:
#        overlay = Image.open("overlay100.png")
#    except IOError as e:
#        print("Overlay image file could not be opened because:", e)
#    else:
#        im.putalpha(255)
#        im = Image.alpha_composite(im, overlay)
#        im.save(filename)
#  
    #try:
    #    os.startfile(filename)
    #except AttributeError as e:
    #    print("Could not open image file in default application because:", e)
    
    # Put the scope in STOP mode
    Rigol.write('STOP')

    chanList = []
    for channel in ["CHAN1", "CHAN2", "CHAN3", "CHAN4", "MATH"]:
        response = Rigol.query(":" + channel + ":DISP?")
        if response == '1\n':
            chanList += [channel]

    # Will read only the displayed data when the scope is in RUN mode or when the MATH channel is select
    # Will read all the acquired data points when the scope is in STOP mode
    Rigol.write(":WAV:MODE NORM")
    Rigol.write(":WAV:STAR 0")
    Rigol.write(":WAV:MODE NORM")

    csv_buff = ""

    for channel in chanList:
        # Set WAVE parameters
        Rigol.write(":WAV:SOUR " + channel)
        Rigol.write(":WAV:FORM ASC")

        # MATH channel does not allow START and STOP to be set. They are always 0 and 1200
        if channel != "MATH":
            Rigol.write(":WAV:STAR 1")
            Rigol.write(":WAV:STOP 1200")

        buff = ""
        print("Data from channel '" + str(channel) + "', points " + str(1) + "-" + str(1200) + ": Receiving...")
        buffChunk = Rigol.query(":WAV:DATA?")

        # Append data chunks
        # Strip TMC Blockheader and terminator bytes
        buff += buffChunk[tmc_header_bytes(buffChunk):-1] + ","

        # Strip the last \n char
        buff = buff[:-1]

        # Process data
        buff_list = buff.split(",")

        # Put read data into csv_buff
        csv_buff_list = csv_buff.split(os.linesep)
        csv_rows = len(csv_buff_list)

        current_row = 0
        if csv_buff == "":
            csv_first_column = True
            csv_buff = str(channel) + os.linesep
        else:
            csv_first_column = False
            csv_buff = str(csv_buff_list[current_row]) + "," + str(channel) + os.linesep

        for point in buff_list:
            current_row += 1
            if csv_first_column:
                csv_buff += str(point) + os.linesep
            else:
                if current_row < csv_rows:
                    csv_buff += str(csv_buff_list[current_row]) + "," + str(point) + os.linesep
                else:
                    csv_buff += "," + str(point) + os.linesep

    # Save data as CSV
    filename = name + ".csv"
    scr_file = open(filename, "w")
    scr_file.write(csv_buff)
    scr_file.close()

    print("Saved file:", "'" + filename)
    
    Rigol.write("RUN")
    
    return name

def take_screenshot():
    '''
    Takes a screenshot.
    '''
    
    Rigol.write(":DISP:DATA?")
    bmpdata = Rigol.read_raw()[2+9:]
  
    # Save image file
    name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print("Enter a filename-safe description (or none). Hit return.")
    comment = input(name + '_')
    if(len(comment)):
        name = name + "_" + comment

    try:
        from PIL import Image
  
    except ImportError as e:
        print("PIL(low) not imported because:", e)
        filename = name + ".bmp"
        print("Saving screen as", filename)
        with open(filename, "wb") as f:
            f.write(bmpdata)
  
    else:
        print("PILlow", sys.version)
        import io
        filename = name + ".png"
        print("Saving screen as", filename)
        im = Image.open(io.BytesIO(bmpdata))

    try:
        overlay = Image.open("overlay100.png")
    except IOError as e:
        print("Overlay image file could not be opened because:", e)
    else:
        im.putalpha(255)
        im = Image.alpha_composite(im, overlay)
        im.save(filename)
  
    try:
        os.startfile(filename)
    except AttributeError as e:
        print("Could not open image file in default application because:", e)

def get_memory_depth(instr):
    '''
    Obtain the memory depth of the device.
    '''
    # Define number of horizontal grid divisions
    h_grid = 12

    # ACQuire:MDEPth
    mdep = instr.query(":ACQ:MDEP?")

    # If mdep is "AUTO"
    if mdep == "AUTO\n":
        # ACQuire:SRATe
        srate = instr.query(":ACQ:SRAT?")

        # TIMebase[:MAIN]:SCALe
        scal = instr.query(":TIM:SCAL?")

        # mdep = h_grid * scal * srate
        mdep = h_grid * float(scal) * float(srate)

    # Return mdep
    return int(mdep)

def tmc_header_bytes(buff):
    '''
    Used for export csv code.
    '''
    return 2 + int(buff[1])
    
def autoscale():
    '''
    Press the AUTO button on the oscilloscope.
    '''
    Rigol.write(":AUT") 