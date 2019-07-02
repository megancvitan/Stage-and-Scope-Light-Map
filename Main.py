# -*- coding: utf-8 -*-
"""
Created on Wed May 15 15:50:46 2019

@author: Tianyang Yu
"""
from multiprocessing import Process
import threading
import time 
import StepmotorController_Camera as sc
#import Mymerger as m

if __name__ == '__main__':
    try:
        sc.initialization()
        """
        write code below
        """
        #sc.Home()
        #sc.infopos()
        #sc.focus()
        sc.movexto(120)
        sc.stepx.getPosition()
        #sc.move_cam(5)
        #sc.infopos()
        """
        write code above
        """
        sc.closeall()
    except:
        print('An error occured.')