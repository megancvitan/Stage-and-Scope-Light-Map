# -*- coding: utf-8 -*-
"""
Created on Wed Jul 02 10:24:45 2019

@author: Megan Cvitan
@author: Tianyang Yu
"""
#Phidget functions found in the Phidget22 folder.
from Phidget22.Devices.Stepper import *
from Phidget22.Devices.DigitalInput import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from Phidget22.Net import *

import sys
import time 
import matplotlib.pyplot as plt
import numpy as np

onemm=3328
#This is how many microsteps 1mm equals to, determined by experiment.

try:
    from PhidgetHelperFunctions import *
except ImportError:
    sys.stderr.write("\nCould not find PhidgetHelperFunctions. Either add PhdiegtHelperFunctions.py to your project folder "
                      "or remove the import from your project.")
    sys.stderr.write("\nPress ENTER to end program.")
    readin = sys.stdin.readline()
    sys.exit()
#Try to find phidget helper function in the same directory.

#Define the type of modules.   
stepx = Stepper() #This is a stepper type object. Defined in phidget.
stepy = Stepper()  
stepz = Stepper()  
chy = DigitalInput() #This is a digital input channel. It has a boolean status.
chx = DigitalInput()
chz = DigitalInput()  

def initialization(): 
    #Try to initialize the program.
    print("Initializing...")
    status=True #This will be true if no error occour during initialization.
    try:
        #Set up Z axis limit switch
        chz.setDeviceSerialNumber(527475) #The serial number you will find in phidget control panel.
        chz.setChannel(4) #The channel on the digital input.
        chz.setHubPort(0) #The Vinthub port which your input is connected to
        chz.setIsRemote(0) #If the device is remote. Here it is not remote.
        chz.openWaitForAttachment(5000) #Open the device and wait for 5000ms. It will send error message if it times out.
        
        #Set up Y axis limit switch
        chy.setDeviceSerialNumber(527475)
        chy.setChannel(2)
        chy.setHubPort(0)
        chy.setIsRemote(0)
        chy.openWaitForAttachment(5000)
        
        #Set up X axis limit switch
        chx.setDeviceSerialNumber(527475)
        chx.setChannel(0)
        chx.setHubPort(0)
        chx.setIsRemote(0)
        chx.openWaitForAttachment(5000)
        
        #Set up X axis step motor.
        stepx.setDeviceSerialNumber(523267) #Important: the serial number for the stepper. Check before you run the code.
        stepx.setChannel(0) #The channel on the digital input.
        stepx.setHubPort(0) #The Vinthub port which your input is connected to.
        stepx.setIsRemote(0) #The Vinthub port which your input is connected to.
        stepx.openWaitForAttachment(5000) #Open the device and wait for 5000ms. It will send error message if it times out.
        stepx.setCurrentLimit(2) #Set the current limit of the stepper in Amperes. The default is 1A.
        stepx.setEngaged(True) #Set the engagement of the stepper to be true. Only an engaged stepper can be operated.
        stepx.setControlMode(0) #The control mode of the stepper. 0 means it moves to target position. 1 means it moves with target speed. Check phidget API for more info.
        
        #Set up Y axis step motor.
        stepy.setDeviceSerialNumber(523253)
        stepy.setChannel(0)
        stepy.setHubPort(0)
        stepy.setIsRemote(0)
        stepy.openWaitForAttachment(5000)
        stepy.setCurrentLimit(2)
        stepy.setEngaged(True)
        stepy.setControlMode(0)
        
        #Set up Z axis step motor.
        stepz.setDeviceSerialNumber(522886)
        stepz.setChannel(0)
        stepz.setHubPort(0)
        stepz.setIsRemote(0)
        stepz.openWaitForAttachment(5000)
        stepz.setCurrentLimit(2)
        stepz.setEngaged(True)
        stepz.setControlMode(0) 
        
        #Print the infomation of each step motor.
        """
        print("-------------------------------------------------")
        print("x motor")
        print("Scale:",stepx.getRescaleFactor())
        print("Serial:",stepx.getDeviceSerialNumber())
        print("Channel:",stepx.getChannel())
        print("Engage:",stepx.getEngaged())
        print("Control Mode:",stepx.getControlMode())
        print("Position",stepx.getPosition())
        print("Acceleration Limit:",stepx.getAcceleration())
        print("Current Limit:",stepx.getCurrentLimit())
        print("Velocity Limit:",stepx.getVelocityLimit())
        print("Position:",stepx.getPosition())
        print("-------------------------------------------------")
        print("y motor")
        print("Scale:",stepy.getRescaleFactor())
        print("Serial:",stepy.getDeviceSerialNumber())
        print("Channel:",stepy.getChannel())
        print("Engage:",stepy.getEngaged())
        print("Control Mode:",stepy.getControlMode())
        print("Position",stepy.getPosition())
        print("Acceleration Limit:",stepy.getAcceleration())
        print("Current Limit:",stepy.getCurrentLimit())
        print("Velocity Limit:",stepy.getVelocityLimit())
        print("Position:",stepy.getPosition())
        print("-------------------------------------------------")
        print("z motor")
        print("Scale:",stepz.getRescaleFactor())
        print("Serial:",stepz.getDeviceSerialNumber())
        print("Channel:",stepz.getChannel())
        print("Engage:",stepz.getEngaged())
        print("Control Mode:",stepz.getControlMode())
        print("Position",stepz.getPosition())
        print("Acceleration Limit:",stepz.getAcceleration())
        print("Current Limit:",stepz.getCurrentLimit())
        print("Velocity Limit:",stepz.getVelocityLimit())
        print("Position:",stepz.getPosition())
        print("-------------------------------------------------")
        """
        #End the information section
        
    except PhidgetException as e:
        status=False
        print("Failed to open: " + e.details)
        return
        #Print the cause of error if initialization fails.
    if status==True:
        print("Initialization complete")
        #Otherwise print success message.
        
def initializationz(): 
    #This section is the same as initialization except it only initialzes the Z axis.
    print("Initializing...")
    status=True
    try:
        chz.setDeviceSerialNumber(527475)
        chz.setChannel(5)
        chz.setHubPort(1)
        chz.setIsRemote(0)
        stepz.setDeviceSerialNumber(522886)
        stepz.setChannel(0)
        stepz.setHubPort(0)
        stepz.setIsRemote(0)
        stepz.openWaitForAttachment(5000)
        stepz.setCurrentLimit(1)
        stepz.setEngaged(True)
        stepz.setControlMode(0)
        """
        print("-------------------------------------------------")
        print("x motor")
        print("Scale:",stepx.getRescaleFactor())
        print("Serial:",stepx.getDeviceSerialNumber())
        print("Channel:",stepx.getChannel())
        print("Engage:",stepx.getEngaged())
        print("Control Mode:",stepx.getControlMode())
        print("Position",stepx.getPosition())
        print("Acceleration Limit:",stepx.getAcceleration())
        print("Current Limit:",stepx.getCurrentLimit())
        print("Velocity Limit:",stepx.getVelocityLimit())
        print("Position:",stepx.getPosition())
        print("-------------------------------------------------")
        print("y motor")
        print("Scale:",stepy.getRescaleFactor())
        print("Serial:",stepy.getDeviceSerialNumber())
        print("Channel:",stepy.getChannel())
        print("Engage:",stepy.getEngaged())
        print("Control Mode:",stepy.getControlMode())
        print("Position",stepy.getPosition())
        print("Acceleration Limit:",stepy.getAcceleration())
        print("Current Limit:",stepy.getCurrentLimit())
        print("Velocity Limit:",stepy.getVelocityLimit())
        print("Position:",stepy.getPosition())
        print("-------------------------------------------------")
        print("z motor")
        print("Scale:",stepz.getRescaleFactor())
        print("Serial:",stepz.getDeviceSerialNumber())
        print("Channel:",stepz.getChannel())
        print("Engage:",stepz.getEngaged())
        print("Control Mode:",stepz.getControlMode())
        print("Position",stepz.getPosition())
        print("Acceleration Limit:",stepz.getAcceleration())
        print("Current Limit:",stepz.getCurrentLimit())
        print("Velocity Limit:",stepz.getVelocityLimit())
        print("Position:",stepz.getPosition())
        print("-------------------------------------------------")
        """
    except PhidgetException as e:
        status=False
        print("Failed to open: " + e.details)
        
    if status==True:
        print("Initialization complete")
        
#The move function moves the stage a certain distance in a specified direction.

def movex(step): #This has a integer input: the number of microsteps.
    stepx.setVelocityLimit(10000)  #Set the velocity limit. The number here is default.
    stepx.setTargetPosition(stepx.getPosition()+step) #This moves the motor X microsteps from its current position. X is the step number entered.
    time.sleep(float(np.abs(step)/1000*0.5)) #It also waits until the movement is done. Wait time is 0.5s per 1000 microsteps. 

def movey(step):
    stepy.setVelocityLimit(10000)
    stepy.setTargetPosition(stepy.getPosition()+step)
    time.sleep(float(np.abs(step)/1000*0.5))

def movez(step):
    stepz.setVelocityLimit(10000)
    stepz.setTargetPosition(stepz.getPosition()+step)
    time.sleep(float(np.abs(step)/1000*0.5))
    
#The moveto function moves the stage to a certain position relative to the origin.

def movexto(position): #It takes one double input: position in unit of mm.
#    stepx.setVelocityLimit(10000) #Set the velocity limit. The number here is default.
    stepx.setTargetPosition(position*onemm) #This will move the stepper to the target position.
#    time.sleep(float(np.abs(stepx.getPosition()-position*onemm)/onemm*10*1.2)) #Wait time is 1.2s for each centimetre.
    infopos()
    
def moveyto(position):
#    stepy.setVelocityLimit(10000)
    stepy.setTargetPosition(position*onemm)
#    time.sleep(float(np.abs(stepy.getPosition()-position*onemm)/onemm*10*1.2))
    time.sleep(1)
    #infopos()
    
def movezto(position):
    stepz.setVelocityLimit(10000)
    stepz.setTargetPosition(position*onemm)
#    time.sleep(float(np.abs(stepz.getPosition()-position*onemm)/onemm*10*1.2))
    time.sleep(1)
    #infopos()
    
def Home(): #This will bring all 3 axes to their respective home positions.
    print("Homing...")
    """
    #Bringing X axis to home position.
    movex(8000) #Move in opposite direction a bit before home to prevent overshoot. Home process and switch response is not instant.
    time.sleep(1) #Wait 1s.
    stepx.setControlMode(1) #Now set the motor to constant velocity mode.
    stepx.setVelocityLimit(-10000) #This will define the speed. Negative indicates direction.
    while True:
        state=chx.getState() #Get the state of the limit switch.
        
        if state==True: #If the switch is activated.
            stepx.setControlMode(0) #Set stepper to default mode.
            break #End the loop.
    movex(2000) 
    time.sleep(0.5) 
    stepx.setControlMode(1)
    stepx.setVelocityLimit(-700)
    while True: 
        state=chx.getState()
        if state==True:
            stepx.setControlMode(0)
            break
    print("X axis complete.")
    """
    #Bringing Y axis to home position.
    movey(8000) 
    time.sleep(1) 
    stepy.setControlMode(1) 
    stepy.setVelocityLimit(-10000) 
    while True: 
        state=chy.getState() 
        if state==True: 
            stepy.setControlMode(0) 
            break 
    movey(2000) 
    time.sleep(0.5) 
    stepy.setControlMode(1)
    stepy.setVelocityLimit(-700)
    while True: 
        state=chy.getState()
        if state==True:
            stepy.setControlMode(0)
            break
    print("Y axis complete.")
    #Home Y is done.

    #Bringing Z axis to home position.
    movez(8000)
    time.sleep(1)
    stepz.setControlMode(1)
    stepz.setVelocityLimit(-10000)
    while True:
        state=chz.getState()
        
        if state==True:
            stepy.setControlMode(0)
            break
    movez(2000) 
    time.sleep(0.5) 
    stepz.setControlMode(1)
    stepz.setVelocityLimit(-700)
    while True: 
        state=chz.getState()
        if state==True:
            stepz.setControlMode(0)
            break
    print("Z axis complete.")
    
    time.sleep(0.5) #Wait 0.5s incase the process is not finished.
    closeall() #Close all channels.
    time.sleep(0.5) #Wait to make sure closeall is complete.
    initialization() #Re-initialize so the current position (after Homed) will be the new origin position.
    print("Homing completed. At home position.")
    
def Homez(): #This part is the same has Home() except it only homes the Z axis and re-initializes the Z axis.
    movez(20000)
    stepz.setControlMode(1)
    stepz.setVelocityLimit(-8000)
    while True:
        state=chz.getState()
        if state==True:
            stepz.setControlMode(0)
            break
    movez(2000) 
    time.sleep(0.5) 
    stepz.setControlMode(1)
    stepz.setVelocityLimit(-700)
    while True: 
        state=chz.getState()
        if state==True:
            stepz.setControlMode(0)
            infopos()
            break
    time.sleep(0.5)
    closez()
    time.sleep(0.5)
    initializationz() 
    
def closeall(): #This method shuts down all the modules.
    stepx.setEngaged(False) #Disengaged the stepper
    stepx.close() #Close the serial port.
    stepy.setEngaged(False)
    stepy.close()
    stepz.setEngaged(False)
    stepz.close()
    chy.close() #Close the serial port.
    chx.close()
    chz.close()
    
def closez():#This is the same as closeall() except it only closes the Z axis stepper and the limit switch.
    stepz.setEngaged(False)
    stepz.close()
    chz.close
    
def info():
    print("Info")
    status=True
    try:
        print("-------------------------------------------------")
        print("x motor")
        print("Scale:",stepx.getRescaleFactor())
        print("Serial:",stepx.getDeviceSerialNumber())
        print("Channel:",stepx.getChannel())
        print("Engage:",stepx.getEngaged())
        print("Control Mode:",stepx.getControlMode())
        print("Position",stepx.getPosition())
        print("Acceleration Limit:",stepx.getAcceleration())
        print("Current Limit:",stepx.getCurrentLimit())
        print("Velocity Limit:",stepx.getVelocityLimit())
        print("Position:",stepx.getPosition()/onemm)
        print("-------------------------------------------------")
        print("y motor")
        print("Scale:",stepy.getRescaleFactor())
        print("Serial:",stepy.getDeviceSerialNumber())
        print("Channel:",stepy.getChannel())
        print("Engage:",stepy.getEngaged())
        print("Control Mode:",stepy.getControlMode())
        print("Position",stepy.getPosition())
        print("Acceleration Limit:",stepy.getAcceleration())
        print("Current Limit:",stepy.getCurrentLimit())
        print("Velocity Limit:",stepy.getVelocityLimit())
        print("Position:",stepy.getPosition()/onemm)
        print("-------------------------------------------------")
        print("z motor")
        print("Scale:",stepz.getRescaleFactor())
        print("Serial:",stepz.getDeviceSerialNumber())
        print("Channel:",stepz.getChannel())
        print("Engage:",stepz.getEngaged())
        print("Control Mode:",stepz.getControlMode())
        print("Position",stepz.getPosition())
        print("Acceleration Limit:",stepz.getAcceleration())
        print("Current Limit:",stepz.getCurrentLimit())
        print("Velocity Limit:",stepz.getVelocityLimit())
        print("Position:",stepz.getPosition()/onemm)
        print("-------------------------------------------------")
    except PhidgetException as e:
        status=False
        print("Failed to open: " + e.details)
        
    if status==True:
        print("Info off")
        
def infopos(): #Information about current position of stage.
    print("Info")
    status=True
    try:
        print("-------------------------------------------------")
        print("x motor")
        print("Position:",stepx.getPosition()/onemm)
        print("-------------------------------------------------")
        print("y motor")
        print("Position:",stepy.getPosition()/onemm)
        print("-------------------------------------------------")
        print("z motor")
        print("Position:",stepz.getPosition()/onemm)
        print("-------------------------------------------------")
    except PhidgetException as e:
        status=False
        print("Failed to open: " + e.details)
        
    if status==True:
        print("Info off")


    
    

