# -*- coding: utf-8 -*-
"""
Created on Wed Jul 02 10:24:45 2019

@author: Megan Cvitan
@author: Tianyang Yu
"""
import pyvisa as visa
import time 
import StageController2 as sc
from StageController2 import onemm #In the Z direction
import talkingtorigol5 as t
import seaborn
#import TalkingToRigol as tr

# Create a ResourceManager object and connect to the Rigol oscilloscope
rm = visa.ResourceManager()
Rigol = rm.open_resource('TCPIP0::172.16.0.101::inst0::INSTR', write_termination ='\n')
#Rigol = rm.open_resource('TCPIP0::169.254.116.38::inst0::INSTR', write_termination ='\n') 

onemmy = 3148

#Grid positions of the area that will be mapped.
#zpositions = [35*onemm, 35*onemm*10, 35*onemm*100]
#ypositions = [7*onemmy, 7*onemmy*10, 7*onemmy*100]
#negypositions = [7*onemmy*100, 7*onemmy*10, 7*onemmy]

#Grid positions of the area that will be mapped.
zpositions = list(range(10, 50, 1)) #Given a positive number, this motor will move away from home
ypositions = list(range(10, 50, 1)) #Given a positive number, this motor will move away from home
negypositions = list(range(50, 10, -1)) #Given a positive number, this motor will move away from home

data = []

def scan(zpositions, ypositions, negypositions): #Moves stage and collects data along y axis.
    #FileName = raw_input("W")
    
    File_object = open(r"StageAndScope-FirstScan.txt","a") # Change to variable from raw_input or similar

    for enum , z in enumerate(zpositions):
        print('Moving Z')
        sc.movezto(z)
        print('Done moving Z')
        if enum%2 == 0:
            for y in ypositions: #For each cm we want to scan from our array
                print('Moving Y')
                sc.moveyto(y) #Move the stage one position in mm at a time.
                print('Done moving Y')
                #t.get_data() #Collect data from scope.
                time.sleep(2) #Wait 3s to ensure data collection occurred.
                print("Writing to file ...")

                File_object.write(str(y) +"\t"+ str(z) +"\t" + str(t.get_data()) + "\n") #will append mean
                print("Recorded data")



        else:
            for y in negypositions: #For each cm we want to scan from our array
                print('Moving Y')
                sc.moveyto(y) #Move the stage one position in mm at a time.
                print('Done moving Y')
                #t.get_data() #Collect data from scope.
                time.sleep(2) #Wait 3s to ensure data collection occurred.
                print("Writing to file ...")
                File_object.write(str(y) +"\t"+ str(z) +"\t" + str(t.get_data()) + "\n") #will append mean
                
                print("Recorded data")

                
        File_object.close()


def plot(filename): #quick heatmap
    file1 = open(filename,"r") 
    print( "Output of Readlines after appending")
    print(file1.readlines())
    
    file1.close() 


if __name__ == '__main__':
    try:
        #print("Are you on the EXO-SW5 computer?")
        
#        ipCheck = raw_input("Are you on the EXO-SW5 computer?: (yes/no)")
#        if ipCheck == "no":
#            print("Check IP of scope and input into here and talkingtorigol.py")
#        else:
#            
#        File_object = open(r"test.txt","a")
#        File_object.write(str(zpositions[1])+"Hello \n") #will append mean
#
#        File_object.close()


        sc.initialization() #Initialize the linear stage.
        time.sleep(0.5) #Wait 1s before setting home position.
        sc.Home() #Home the stage.
        time.sleep(1)
        print('Ready to take data.')
        
        scan(zpositions, ypositions, negypositions)
#        plot("StageAndScope-FirstScan.txt")       
        
        
        Rigol.close()     
        sc.closeall() #Shut down the modules.
        
        print("Done! :)")

    except:
        Rigol.close()
        print('An error occured.')
