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
import TalkingToRigol as t
import csv 
import seaborn as sns
import pandas as pd
import spinmob as s
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os.path 
import datetime


name = datetime.datetime.now().strftime("_%Y-%m-%d_%H-%M")
onemmy = 3148 #In the Y direction. There is a slight varition in this calibration parmeter between axes.
File_name = ""
output_dir = ""

#Grid positions of the area that will be mapped - don't go past 55 mm
#Default
#zpositions = list(range(10, 50, 1)) #Given a positive number, this motor will move away from home.
#ypositions = list(range(10, 50, 1)) #Given a positive number, this motor will move away from home.
#negypositions = list(range(50, 10, -1)) #Given a positive number, this motor will move away from home.

#zpositions = list(range(10, 50, 10)) #Given a positive number, this motor will move away from home.
#ypositions = list(range(10, 50, 10)) #Given a positive number, this motor will move away from home.
#negypositions = list(range(40, 1, -10)) #Given a positive number, this motor will move away from home.

zpositions = list(range(10, 50, 5)) #Given a positive number, this motor will move away from home.
ypositions = list(range(10, 50, 5)) #Given a positive number, this motor will move away from home.
negypositions = list(range(45, 5, -5)) #Given a positive number, this motor will move away from home.

data = []

def scan(zpositions, ypositions, negypositions): #Moves stage and collects data along y axis.
    File_name = output_dir + '\\' + file + ".csv"
    File_object = open(File_name,"a") # Change to variable from input.
    print("Saving data to " + File_name)
    File_object.write("Y (mm)" +", "+ "Z (mm)" +", " + "Voltage (V)" + "\n") #Will append mean value.

    for enum , z in enumerate(zpositions):
        print('Moving Z')
        sc.movezto(z) #Moves the Z axis to the designated position in mm found in the zth entry.
        print('Done moving Z')
        print('Current Z position: ' + str(z))
        if enum%2 == 0: #Check odd or even row number to determine direction of Y axis.
            for y in ypositions: #For each mm we want to scan from our array
                print('Moving Y')
                sc.moveyto(y) #Move the stage one position in mm at a time.
                print('Done moving Y')
                print('Current Y position: ' + str(y))
                voltage=t.get_data() #Collect data from scope.
                time.sleep(2) #Wait to ensure data collection occurred.
                print("Writing to file ...")

                File_object.write(str(y) +", "+ str(z) +", " + str(voltage) + "\n") #Will append mean value.
                print("Recorded data")

        else:
            for y in negypositions: #For each cm we want to scan from our array
                print('Moving Y')
                sc.moveyto(y) #Move the stage one position in mm at a time.
                print('Done moving Y')
                print('Current Y position: ' + str(y))
                voltage=t.get_data() #Collect data from scope.
                time.sleep(2) #Wait to ensure data collection occurred.
                print("Writing to file ...")
                File_object.write(str(y) +", "+ str(z) +", " + str(voltage) + "\n") #Will append mean.
                
                print("Recorded data")
     
    #At the end of the file, you will find ***
    #File_object.write('***' +', '+ '***' +", " + '***' + "\n")
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
    df = pd.pivot_table(pd.read_csv(filenameWithDir),
                        index='Y (mm)',
                        values=' Voltage (V)',
                        columns=' Z (mm)')
    df.head()
    print('Read from data file...')
    #Plot the data in a heatmap; can adjust the style and labels.
    plt.figure(figsize=(16,16))
    sns.heatmap(df, robust = True)
    
    #Axis titles and size.
    plt.xlabel('Stage Y Axis Position')
    plt.ylabel('Stage Z Axis Position')
    plt.title(file)
    ax.set_ylim((0,10))
    


if __name__ == '__main__':
    try:
        #Determine that the correct IP address is in the resource name.y
        ipCheck = input("Are you on the EXO-SW5 computer?:  ")
        if ipCheck == "no" or "n" or "non":
            print("Check IP of scope and edit talkingtorigol.py")
        if ipCheck == "yes" or "y" or "oui":
            print("Good! Continuing on...")
            
        #See if the filename exists already to prevent loss of data.
        #Rename the file with a name of your choice.
        file = input("Enter file name (without extension).  ")
        
        #Creating a new file to save all the data from one scan in one place.
        current_dir = os.getcwd()  
        print ("The current working directory is %s" % current_dir)  
        output_dir = file + name
        
        try:  
            os.mkdir(output_dir)
        except OSError:  
            print ("Creation of the directory %s failed" % output_dir)
        else:  
            print ("Successfully created the directory %s " % output_dir)
        
        sc.initialization() #Initialize the linear stage.
        time.sleep(0.5) #Wait 1s before setting home position.
        sc.Home() #Home the stage.
        time.sleep(1)
        print('Ready to take data.')
        
        #Scan and take data
        scan(zpositions, ypositions, negypositions) 
        
        #Plot the data and save into same folder as the csv
        os.chdir(output_dir) #Changing the directory so it goes to the correct folder
        heatmap(file + '.csv')
        Image_name = file + '.png'
        plt.savefig(Image_name) 
        
        t.Rigol.close()     
        
        sc.closeall() #Shut down the modules.
        
        print("Done! :)")

    except:
        t.Rigol.close()
        print('Error. Consult README for list of common errors and their respective solutions.')
