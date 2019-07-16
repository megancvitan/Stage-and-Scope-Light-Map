# -*- coding: utf-8 -*-
"""
Created on Wed Jul 02 10:24:45 2019

@author: Megan Cvitan
@author: Tianyang Yu
"""
import pyvisa as visa
import time 
import StageController2 as sc
from StageController2 import onemm #In the Z direction.
import talkingtorigol5 as t
import seaborn

onemmy = 3148 #In the Y direction. There is a slight varition in this calibration parmeter between axes.

#Grid positions of the area that will be mapped.
zpositions = list(range(10, 50, 1)) #Given a positive number, this motor will move away from home.
ypositions = list(range(10, 50, 1)) #Given a positive number, this motor will move away from home.
negypositions = list(range(50, 10, -1)) #Given a positive number, this motor will move away from home.

data = []

def scan(zpositions, ypositions, negypositions): #Moves stage and collects data along y axis.
    File_name = file + ".txt"
    File_object = open(File_name,"a") # Change to variable from input.
    print("Saving data to " + File_name)

    for enum , z in enumerate(zpositions):
        print('Moving Z')
        sc.movezto(z) #Moves the Z axis to the designated position in mm found in the zth entry.
        print('Done moving Z')
         print('Current Z position: ' + zpositions[z])
        if enum%2 == 0: #Check odd or even row number to determine direction of Y axis.
            for y in ypositions: #For each mm we want to scan from our array
                print('Moving Y')
                sc.moveyto(y) #Move the stage one position in mm at a time.
                print('Done moving Y')
                print('Current Y position: ' + ypositions[y])
                t.get_data() #Collect data from scope.
                time.sleep(2) #Wait to ensure data collection occurred.
                print("Writing to file ...")

                File_object.write(str(y) +"\t"+ str(z) +"\t" + str(t.get_data()) + "\n") #Will append mean value.
                print("Recorded data")

        else:
            for y in negypositions: #For each cm we want to scan from our array
                print('Moving Y')
                sc.moveyto(y) #Move the stage one position in mm at a time.
                print('Done moving Y')
                print('Current Y position: ' + negypositions[y])
                t.get_data() #Collect data from scope.
                time.sleep(2) #Wait to ensure data collection occurred.
                print("Writing to file ...")
                File_object.write(str(y) +"\t"+ str(z) +"\t" + str(t.get_data()) + "\n") #Will append mean.
                
                print("Recorded data")
                
        File_object.close()

def plot(filename): #Heatmap for plotting 
    file1 = open(filename,"r") 
    print( "Output of Readlines after appending")
    print(file1.readlines())
    
    file1.close() 

if __name__ == '__main__':
    try:
        #Determine that the correct IP address is in the resource name. 
        ipCheck = input("Are you on the EXO-SW5 computer?: (yes/no)")
        if ipCheck == "no":
            print("Check IP of scope and edit talkingtorigol.py")
        if ipCheck == "yes":
            print("Good! Continuing on...")
            
         #See if the filename exists already to prevent loss of data.
         file = input("Enter file name.")
        
        sc.initialization() #Initialize the linear stage.
        time.sleep(0.5) #Wait 1s before setting home position.
        sc.Home() #Home the stage.
        time.sleep(1)
        print('Ready to take data.')
        
        scan(zpositions, ypositions, negypositions)   
        
        t.Rigol.close()     
        sc.closeall() #Shut down the modules.
        
        print("Done! :)")

    except:
        t.Rigol.close()
        print('Error. Consult README for list of common errors and their respective solutions.')
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 02 10:24:45 2019

@author: Megan Cvitan
@author: Tianyang Yu
"""
import pyvisa as visa
import time 
import StageController2 as sc
from StageController2 import onemm #In the Z direction.
import talkingtorigol5 as t
import seaborn

onemmy = 3148 #In the Y direction. There is a slight varition in this calibration parmeter between axes.

#Grid positions of the area that will be mapped.
zpositions = list(range(10, 50, 1)) #Given a positive number, this motor will move away from home.
ypositions = list(range(10, 50, 1)) #Given a positive number, this motor will move away from home.
negypositions = list(range(50, 10, -1)) #Given a positive number, this motor will move away from home.

data = []

def scan(zpositions, ypositions, negypositions): #Moves stage and collects data along y axis.
    File_name = file + ".txt"
    File_object = open(File_name,"a") # Change to variable from input.
    print("Saving data to " + File_name)

    for enum , z in enumerate(zpositions):
        print('Moving Z')
        sc.movezto(z) #Moves the Z axis to the designated position in mm found in the zth entry.
        print('Done moving Z')
         print('Current Z position: ' + zpositions[z])
        if enum%2 == 0: #Check odd or even row number to determine direction of Y axis.
            for y in ypositions: #For each mm we want to scan from our array
                print('Moving Y')
                sc.moveyto(y) #Move the stage one position in mm at a time.
                print('Done moving Y')
                print('Current Y position: ' + ypositions[y])
                t.get_data() #Collect data from scope.
                time.sleep(2) #Wait to ensure data collection occurred.
                print("Writing to file ...")

                File_object.write(str(y) +"\t"+ str(z) +"\t" + str(t.get_data()) + "\n") #Will append mean value.
                print("Recorded data")

        else:
            for y in negypositions: #For each cm we want to scan from our array
                print('Moving Y')
                sc.moveyto(y) #Move the stage one position in mm at a time.
                print('Done moving Y')
                print('Current Y position: ' + negypositions[y])
                t.get_data() #Collect data from scope.
                time.sleep(2) #Wait to ensure data collection occurred.
                print("Writing to file ...")
                File_object.write(str(y) +"\t"+ str(z) +"\t" + str(t.get_data()) + "\n") #Will append mean.
                
                print("Recorded data")
                
        File_object.close()

def plot(filename): #Heatmap for plotting 
    file1 = open(filename,"r") 
    print( "Output of Readlines after appending")
    print(file1.readlines())
    
    file1.close() 

if __name__ == '__main__':
    try:
        #Determine that the correct IP address is in the resource name. 
        ipCheck = input("Are you on the EXO-SW5 computer?: (yes/no)")
        if ipCheck == "no":
            print("Check IP of scope and edit talkingtorigol.py")
        if ipCheck == "yes":
            print("Good! Continuing on...")
            
         #See if the filename exists already to prevent loss of data.
         file = input("Enter file name.")
        
        sc.initialization() #Initialize the linear stage.
        time.sleep(0.5) #Wait 1s before setting home position.
        sc.Home() #Home the stage.
        time.sleep(1)
        print('Ready to take data.')
        
        scan(zpositions, ypositions, negypositions)   
        
        t.Rigol.close()     
        sc.closeall() #Shut down the modules.
        
        print("Done! :)")

    except:
        t.Rigol.close()
        print('Error. Consult README for list of common errors and their respective solutions.')
