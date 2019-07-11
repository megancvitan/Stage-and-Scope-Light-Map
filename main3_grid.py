# -*- coding: utf-8 -*-
"""
Created on Wed Jul 02 10:24:45 2019

@author: Megan Cvitan
@author: Tianyang Yu
"""
from multiprocessing import Process
import numpy as np
import threading
import time 
import StageController as sc
from StageController import onemm
import talkingtorigol2 as t
#import TalkingToRigol as tr

#Grid positions of the area that will be mapped.
#ypositions = []
#zpositions = []    

#Sidelengths of the square that will be scanned.
length = 5

#Voltage measurements from scope.
scope = np.empty

def scany(length, direction): #Moves stage and collects data along X axis.
    if direction==1:
        for i in range(length): #For each mm we want to scan
                sc.movey(onemm) #Move the stage onemm at a time.
                t.get_data() #Collect data from scope.
                time.sleep(3) #Wait 3s to ensure data collection occurred.
                #Do this for each mm in the square's side length.
                
    else: #To scan in the opposite direction.
        for i in range(length):
                sc.movey(-onemm)
                t.get_data() 
                time.sleep(3)     
'''
if __name__ == '__main__':
    try:
        sc.initialization() #Initialize the linear stage.
        time.sleep(1) #Wait 1s before setting home position.
        sc.Home() #Home the stage.
#        scany(length, 1)
#        sc.movez(onemm) #Moves Z axis onemm down
#        scany(length, -1)
#        sc.movez(onemm) #Moves Z axis onemm down
#        scany(length, 1)
#        sc.movez(onemm) #Moves Z axis onemm down
#        scany(length, -1)
#        sc.movez(onemm) #Moves Z axis onemm down
#        scany(length, 1)
        
        #Now data is ready to be taken.
#        for j in range(length): #For a number (onemm) of rows
#            scanx(length, 1) #Scan across X axis.
#            sc.movey(onemm) #Move up onemm.
#            scanx(length, -1) #Then scan in the other direction.
             
        sc.closeall() #Shut down the modules.
    except:
        print('An error occured.')

'''
if __name__ == '__main__':
    try:
        sc.initialization() #Initialize the linear stage.
        time.sleep(1) #Wait 1s before setting home position.
        sc.Home() #Home the stage.
        time.sleep(1)
        print('Ready to take data from scope.')
        print('Collecting data...')
        trial = t.get_data()
        scopedata = np.append(scope, trial)#Taking the waveform from the scope.
        print(scopedata)
        time.sleep(1)
        print('Data acquisition for this position is complete.')
        
        #Now data is ready to be taken.
#        for j in range(length): #For a number (onemm) of rows
#            scanx(length, 1) #Scan across X axis.
#            sc.movey(onemm) #Move up onemm.
#            scanx(length, -1) #Then scan in the other direction.
             
        sc.closeall() #Shut down the modules.
    except:
        print('An error occured.')
        