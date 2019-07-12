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
import talkingtorigol4 as t
#import TalkingToRigol as tr

# Create a ResourceManager object and connect to the Rigol oscilloscope
rm = visa.ResourceManager()
#Rigol = rm.open_resource('TCPIP0::172.16.0.101::inst0::INSTR', write_termination ='\n')
Rigol = rm.open_resource('TCPIP0::169.254.116.38::inst0::INSTR', write_termination ='\n') 

onemmy = 3148

#Grid positions of the area that will be mapped.
#zpositions = [35*onemm, 35*onemm*10, 35*onemm*100]
#ypositions = [7*onemmy, 7*onemmy*10, 7*onemmy*100]
#negypositions = [7*onemmy*100, 7*onemmy*10, 7*onemmy]

#Grid positions of the area that will be mapped.
zpositions = [10, 20, 30, 40, 50] #Given a positive number, this motor will move down.
ypositions = [10, 20, 30, 40, 50] #Given a positive number, this motor will move down.
negypositions = [50, 40, 30, 20, 10]

def scany(position): #Moves stage and collects data along y axis.
    for i in range(len(position)): #For each cm we want to scan from our array
        sc.moveyto(position[i]) #Move the stage one position in mm at a time.
        t.get_data() #Collect data from scope.
        time.sleep(30) #Wait 3s to ensure data collection occurred.
        #Do this for each mm in the square's side length.
        
if __name__ == '__main__':
    try:
        sc.initialization() #Initialize the linear stage.
        time.sleep(1) #Wait 1s before setting home position.
        sc.Home() #Home the stage.
        time.sleep(2)
        print('Ready to take data.')
        time.sleep(3)
        sc.movezto(zpositions[0])
        scany(ypositions)
        sc.movezto(zpositions[1])
        scany(negypositions)
        sc.movezto(zpositions[2])
        scany(ypositions)
        sc.movezto(zpositions[3])
        scany(negypositions)
        sc.movezto(zpositions[4])
        scany(ypositions)
#        sc.movezto(zpositions[1])
#        scany(ypositions, -1)
#        sc.movezto(zpositions[2])
#        scany(ypositions, -1)
#        for j in range(zpositions):
#            sc.movezto(zpositions[j])
#            if j%2 == 0:
#                scany(ypositions, -1)
#            if j%2 != 0:
#                scany(negypositions, 1)
                
        Rigol.close()     
        sc.closeall() #Shut down the modules.
    except:
        Rigol.close()
        print('An error occured.')
