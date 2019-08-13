# -*- coding: utf-8 -*-
"""
Created on Wed Jul 02 10:24:45 2019

@author: Megan Cvitan
@author: Tianyang Yu
"""
import pyvisa as visa
import time 
import StageController as sc
from StageController import onemm #In the Z direction.
import sillyscope as sco
import csv 
import seaborn as sns
import pandas as pd
import spinmob as s
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os.path 
import datetime

#Important variables
scope_model = 'RigolDS1074Z'
Rigol = sco.Sillyscope(scope_model) #Name the scope.
name = datetime.datetime.now().strftime("_%Y-%m-%d_%H-%M") #Current date and time.
onemmy = 3148 #In the Y direction. There is a slight variation in this calibration parmeter between axes.
File_name = ""
output_dir = ""
time_scale = Rigol.query('TIM:SCALE?')

#Default
#Grid positions of the area that will be mapped - don't go past 55 mm

#zpositions = list(range(10, 50, 1)) #Given a positive number, this motor will move away from home.
#ypositions = list(range(10, 50, 1)) #Given a positive number, this motor will move away from home.
#negypositions = list(range(50, 10, -1)) #Given a positive number, this motor will move away from home.

#Moving in a grid simplified
start = 0
stop = 50
move = 1

startneg = stop-move
stopneg = start - move
moveneg = -move

xpositions = []
zpositions = list(range(start, stop, move)) #Given a positive number, this motor will move away from home.
ypositions = list(range(start, stop, move)) #Given a positive number, this motor will move away from home.
negypositions = list(range(startneg, stopneg, moveneg)) #Given a positive number, this motor will move away from home.

#Moving in a grid with positions that are decimal numbers
#zpositionsint = list(range(start, stop, move)) #Given a positive number, this motor will move away from home.
#ypositionsint = list(range(start, stop, move)) #Given a positive number, this motor will move away from home.
#negypositionsint = list(range(startneg, stopneg, moveneg)) #Given a positive number, this motor will move away from home.
#
#zpositions =[]
#ypositions = []
#negypositions = []
#
#for z in zpositionsint:
#    zpositions.append(z/10.0)
#    
#for y in ypositionsint:
#    ypositions.append(y/10.0)
#    
#for negy in negypositionsint:
#    negypositions.append(negy/10.0)
    
#data = []

#Will prepare the databox in which the waveforms will be stored.
def make_databox(): 
    #Create the databox.
    d = s.data.databox(delimiter = ',') 
    
    #Set the header names.
    d.insert_header('Time and Date', name)
    d.insert_header('Scope Name', scope_model)
    
    #Initialize the column names
    d['Integral Value'] = None
    d['Trigger Signal'] = None
    
    return d

#Integrates over waveform from the given bounds: a to b
def channel_integrator(databox, pulses): 
    #Need to input the column of the databox in which we will save the data
    CH = databox[1]
    
    #Looking for the lowest value in the x value array.
    min_value = min(CH) 
    
    #Correcting for minimum values that are not 0
    if (min_value) != 0:
        if min_value < 0: 
            #If it's negative
            #Add the lowest value to every entry to bring the lowest value to 0.
           CH= np.add(CH, abs(min_value)) 
        else: 
            #And if it's positive
            CH = np.add(CH, min_value)
     
        
    #We integrate by adding up the measurements and multiplying by the time scale, acquired from the scope.
    int_arr = []
    for pulse in pulses:
        num = 0.0
        for i in CH[pulse[0]:pulse[1]+1]:
            num += i
            integral = float(num*float(time_scale)/10.0) #Divide by 10 to get the units to correspond.
        int_arr.append(integral)
        #print("The integral is ", integral)

    return int_arr
    

#Comparing pairs of data points and checking the magnitude of the differences to locate the peak in an interval where 1 peak is already suspected to exist.
def compare(data):
    #Important variables
    index_of_data_stop = 0
    index_of_data_start = 0
    diff = []
    
    #Collect all the differences between voltage measurements and store them away.
    for i in range(len(data)):
        if i == len(data)-1:
            break
        diff.append(data[i+1] - data[i])
 
    #Get the absolute value of all the differences, and the max value of this array.
    abs_diff = np.absolute(diff)
    abs_diff = list(abs_diff)
    
    #The max of this array must be either a positive or negative edge of a peak.
    m = max(abs_diff)
    
    #We get the index at which this max occurs.
    pulse = abs_diff.index(m)
    
    #We need to classify the peak once we find it.
    if (diff[pulse] < 0):
        index_of_data_start = pulse+1
        index_of_data_stop = pulse
    elif (diff[pulse] > 0):
        index_of_data_start = pulse
        index_of_data_stop = pulse+1
        
    return index_of_data_start, index_of_data_stop

#Finds the bounds for the integration of the waveform later on.
def channel_differentiator(databox):
    #Will check at what point in time the differences in the voltage measurement derivatives exceed 3 sigma
    x = databox[0]
    y = databox[1]
    der = []
    mu = []
    pulse_interval = []
    
    #Find the derivatives and store them away.
    for i in range(len(x)):
        if i == len(x)-1:
            #When it gets to the last data point.
            print("Reached end of dataset.")
            break 
        der.append((y[i+1] - y[i])/(x[i+1] - x[i]))
    plt.figure()
    plt.plot(range(1199),der)
    plt.show()
    plt.figure()
    print(len(der))
    print(max(der))
    print(min(der))
    
    #Take the derivatives and separate them into intervals of 10.
    for j in range(len(der)):
        #Make and populate the intervals of 10.
        der_1190 = der[:1190]
        intervals = np.reshape(der_1190, [119, 10])
        intervals = np.ndarray.tolist(intervals)
        #And the remaining 9 points (since the scope gives 1200 points).
        intervals.append(der[1190:len(der)])
        
    #Turn it into a numpy array for later.
    intervals = np.asarray(intervals)
    
    #Get the means for each interval.
    for k in range(len(intervals)):
        mu.append(np.mean(intervals[k]))
    
    #Get the std dev for this collection of means.
    std_dev = np.std(mu)

    #Go through the intervals of the means of these derivatives and compare to std_dev
    for l in range(len(mu)):
        #If a specific mean differs by 3 or more sigma
        if (mu[l] > 3*std_dev) or (mu[l] < -3*std_dev):
            #Then we are interested in these intervals, where the mean spikes.
            #We will save the index where the interval of interest is found.
            pulse_interval.append(l)
            print("A pulse can be found in the", l,"th interval.")
         
    cond = False
    stop = 0
    start = 0
    integrals = []
    #We go over the individual data points in the intervals of interest.
    for m in range(len(pulse_interval)):
        y = list(y)
        
        #We take the voltage measurements from this interval.
        data_interval = y[(pulse_interval[m]*10) : ((pulse_interval[m]+1)*10)+1]
        
        #Providing the index of the interval of interest, we get the indices where the pulses exist.
        trig_start, trig_stop = compare(data_interval)
        
        #Record a positive edge first, and only then can a negative edge be detected.
        if (trig_start > trig_stop) and cond:
            stop = (pulse_interval[m]*10)+trig_start
            cond = False
        elif (trig_start < trig_stop):
            start = (pulse_interval[m]*10)+trig_stop
            cond = True
        
        if (stop>start):
            print("The trigger starts and stops from ", x[start], " to ", x[stop], " in this detected waveform.")
    
            #We integrate the wave from the detected start and stop times of the pulse, between a positive and negative edge.
            integrals.append(channel_integrator(databox, start, stop))

    return integrals

def pulse_finder(databox):
    #Will check at what point in time the differences in the voltage measurement derivatives exceed 3 sigma
    x = databox[0]
    y = databox[1]
    der = []
    
    #Find the derivatives and store them away.
    for i in range(len(x)):
        if i == len(x)-1:
            #When it gets to the last data point.
            print("Reached end of dataset.")
            break 
        der.append((y[i+1] - y[i])/(x[i+1] - x[i]))
    plt.figure()
    plt.plot(range(1199),der)
    plt.show()
    plt.figure()
    
    std = np.std(np.array(der))
    
    print("std: %f", std)
    
    starts = []
    stops = []
    
    #Issue here
    cond = False
    for e, d in enumerate(der):
        if d > 3.0*std and cond == False:
            starts.append(e)
            cond=True
            continue
        if d < -3.0*std and cond == True:
            stops.append(e)
            cond=False
            continue
        
        
    print(len(starts), len(stops))
    
    for i, val in enumerate(stops):
        if val < starts[0]: stops.pop(i) 
        
    for i, val in enumerate(starts):
        if val > stops[-1]: starts.pop(i) 
        
    print(stops)
    print(starts)
    
    pulses = set(zip(starts, stops))
    #print(pulses)
    #for pulse in pulses: print(pulse[0])
    
    print(pulses)
    return pulses
    

#Scanning with sillyscope.
def scan_silly(zpositions, ypositions, negypositions): 
    #Moves stage and collects data along y axis.
    #Setting up file for saving position data and integral measurement
    #File_name = output_dir + '\\' + file + ".csv"
    File_name = "test" + name + ".csv"
    File_object = open(File_name,"a") #Change to variable from input.
    print("Saving data to " + File_name)
    
    #Writing the column headers for the data file.
    File_object.write("X (mm)" +", "+ "Y (mm)" + ", " + "Z (mm)" + "," + "Light Integral" + "," + "Trigger START Time" + "," + "Trigger STOP Time" + "\n")
    
    for enum, z in enumerate(zpositions):
        print('Moving Z')
        #Moves the Z axis to the designated position in mm found in the zth entry.
        sc.movezto(z) 
        print('Done moving Z')
        print('Current Z position: ' + str(z))
        
        #This is where the waveforms will be stored.
        d = make_databox()
        
        #Check odd or even row number to determine direction of Y axis.
        if enum%2 == 0: 
            #For each mm we want to scan from our grid array
            for y in ypositions: 
                print('Moving Y')
                #Move the stage one position in mm at a time.
                sc.moveyto(y) 
                print('Done moving Y')
                print('Current position (y,z): (' + str(y) + ',' + str(z) + ')')
                
                #Collect the data
                for n in range(0, 5): 
                    #Number of trials for each position.
                    #Load the positions into the header of the databox
                    d.insert_header('X(mm)', 'Axis not in use')
                    d.insert_header('Y(mm)', y)
                    d.insert_header('Z(mm)', z)
                    
                    #Load the waveforms and time values in columns in a databox
                    d['Pulse Signal'] = Rigol.get_waveform(channel = 1, include_x = True)
                    d['Trigger Signal'] = Rigol.get_waveform(channel = 2, include_x = True)
                    
                    #Will get the bounds of integration, and the integral of the detected waveform.
                    integrate_signal = channel_differentiator(d['Pulse Signal'])
                    
                    #Save the two different files
                    #The waveforms for each position measurements from a databox, and the position+integral+bounds data in a .csv
                    d.save_file('_Waveforms_' + name + '.csv') 
                    File_object.write("None" + ", " + str(y) + ", " + str(z) + "," + str(integrate_signal) + "," + "" + "," + "" "\n") 
                    
                    print("Measuement trial " + n + " of this postition completed.")
                    print("Recorded data.")
                    
                    time.sleep(2) #Wait to ensure data collection occurred.
                    Rigol.clear() #Clears the scope.
                         
        else:
            #For each cm we want to scan from our array
            for y in negypositions: 
                print('Moving Y')
                #Move the stage one position in mm at a time.
                sc.moveyto(y) 
                print('Done moving Y')
                print('Current position (y,z): (' + str(y) + ',' + str(z) + ')')
                
                #Collect the data
                for n in range(0, 5): 
                    #Number of trials for each position.
                    #Load the positions into the header of the databox
                    d.insert_header('X(mm)', 'Axis not in use')
                    d.insert_header('Y(mm)', y)
                    d.insert_header('Z(mm)', z)
                    
                    #Load the waveforms and time values in columns
                    d['Pulse Signal'] = Rigol.get_waveform(channel = 1, include_x = True)
                    d['Trigger Signal'] = Rigol.get_waveform(channel = 2, include_x = True)
                    
                    #Save the two different files
                    #d.save_file(name + '.csv')
                    #File_object.write("None" + ", " + str(y) + ", " + str(z) + "," + str(channel_integrator(1)) + "\n") 
                    
                    print("Measuement trial " + n + " of this postition.")
                    print("Recorded data")
                    
                    time.sleep(2) #Wait to ensure data collection occurred.
                    Rigol.clear() #Clears the scope.
                
    File_object.close()

def heatmap(filenameWithDir):
    #Can also change parameters of the plot later on, separately from the scan.
    sns.set()
    
    #Settings for the plot.
    plt.rcParams['font.size'] = 20
    bg_color = (0.88,0.85,0.95)
    plt.rcParams['figure.facecolor'] = bg_color
    plt.rcParams['axes.facecolor'] = bg_color
    fig, ax = plt.subplots(1)
    
    #Create data frame from csv file 
    print('Reading from data file...')
    df1 = pd.pivot_table(pd.read_csv(filenameWithDir),
                        index='Y (mm)',
                        values=' Voltage (V)',
                        columns=' Z (mm)')
    df1.head()
    print('Read from data file...')
    
    #Plot the data in a heatmap; can adjust the style and labels.
    plt.figure(figsize=(16,16))
    sns.heatmap(df1, robust = True)
    
    #Axis titles and size.
    plt.xlabel('Stage Y Axis Position')
    plt.ylabel('Stage Z Axis Position')
    #plt.title(file)
    ax.set_ylim((start, stop))
    
def IPCheck():
    #Determine that the correct IP address is in the resource name.
        ipCheck = input("Are you on the EXO-SW5 computer?:  ")
        if ipCheck == "no" or "n" or "non":
            print("Check IP of scope and edit talkingtorigol.py before continuing.")
        if ipCheck == "yes" or "y" or "oui":
            print("Good! Continuing on...")
    
def scan_with_SillyScope():
    #IPCheck()

    #Rename the file with a name of your choice.
    #file = input("Enter file name (without extension).  ")
    
    #Creating a new folder to save all the data from one scan in one place.
#    current_dir = os.getcwd()  
#    print ("The current working directory is %s" % current_dir)  
#    output_dir = file + name
#    
#    try:  
#        os.mkdir(output_dir)
#    except OSError:
#        print ("Creation of the directory %s failed" % output_dir)
#    else:  
#        print ("Successfully created the directory %s " % output_dir)
    
    #sc.initialization() #Initialize the linear stage.
    #time.sleep(0.5) #Wait 1s before setting home position.
    #sc.Home() #Home the stage.
    #time.sleep(10)

    print('Ready to take data.')
    
    #Scan and take data
    #scan(zpositions, ypositions, negypositions)
    
    laser_wave =  Rigol.get_waveform(channel=1, include_x = True)
    integrate_signal = channel_integrator(laser_wave, pulse_finder(laser_wave))
    s.plot.xy.data(xdata = laser_wave[0], ydata = laser_wave[1])
    
    #close scope??  
    sc.closeall() #Shut down the modules.

    
if __name__ == '__main__':
    try:
        scan_with_SillyScope()
        print("Done! :)")

    except:
        #close scope??  
        print('Error. Consult README for list of common errors and their respective solutions.')
        