# -*- coding: utf-8 -*-
"""
Created on Wed Jul 02 10:24:45 2019

@author: Megan Cvitan
@author: Tianyang Yu
"""
from multiprocessing import Process
import threading
import time 
import StageController as sc
from StageController import onemm
#import TalkingToRigol as tr

#Sidelengths of the square that will be scanned.
length = 5

def scany(length, direction): #Moves stage and collects data along X axis.
    if direction==1:
        for i in range(length): #For each mm we want to scan
                sc.movey(onemm) #Move the stage onemm at a time.
                #tr.get_data() #Collect data from scope.
                time.sleep(1) #Wait 3s to ensure data collection occurred.
                #Do this for each mm in the square's side length.
                
    else: #To scan in the opposite direction.
        for i in range(length):
                sc.movey(-onemm)
                #tr.get_data() 
                time.sleep(1)     
        
if __name__ == '__main__':
    try:
        sc.initialization() #Initialize the linear stage.
        #time.sleep(3) #Wait 3s before setting home position.
        sc.Home() #Home the stage.
        scany(length, 1)
        sc.movez(onemm)
        scany(length, -1)
        sc.movez(onemm)
        #Now data is ready to be taken.
#        for j in range(length): #For a number (onemm) of rows
#            scanx(length, 1) #Scan across X axis.
#            sc.movey(onemm) #Move up onemm.
#            scanx(length, -1) #Then scan in the other direction.
             
        sc.closeall() #Shut down the modules.
    except:
        print('An error occured.')