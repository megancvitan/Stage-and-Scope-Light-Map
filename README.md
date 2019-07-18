# Stage and Scope Light Map
----- **PROJECT SUMMARY** -----

Using a linear stage to image the light intensity of an LED with a photodiode. A stage will move and collect data over a predetermined grid. 
The data will be displayed in the form of a heatmap in order to demonstrate regions of varying light intensities. 

----- **ABOUT FILES** -----

*mainGrid* contains the required funcitons to move the linear stage and to communicate with the Rigol oscilloscope at the same time. Once the user determines the 
correct IP address, they will be asked to input a file name. If there is no folder already created with this name, the linear stage will begin to initialize. 

* The onemm value is from experimental measurements with a Vernier caliper. You must do your own callibration with each specific set up to strive for accuracy.
* Other features include direct plotting of a heatmap after data collection is complete. 
* The intervals on the heatmap are determined relatively, depending on the data that it is given. There is no need to set a minimum or maximum range for the colour gradient.
* Both '.csv' and a '.png' files will be found in a new directory, separate from the current one that the code runs from.
* You may need to restart the kernel frequently. This is because the port is still being in use before you begin another scan.
* Be careful when inputting the parameters for the grid; it can be tricky. Try printing the entries of the positions in the console prior to running a scan.

*TalkingToRigol* allows communication with a Rigol oscilloscope. It contains features that are specific to this type of scope, with model number DS1074. 

* Connect an ethernet cable from the scope to the computer.
* Always ensure that the IP address is correctly inputted in the code. It can be found on the scope by pressing on 'Utility' >> 'IO' >> 'LAN Config.' >> 'Apply'.
* You should get a message indicating a successful connection. If not, try checking the router (if applicable).

*StageController* outlines the linear stage's capabilities of motion, such as moving to a specific predetermined position and moving a certain number of steps. 

* To connect it properly, connect a USB from the control box to the computer. Also connect each axis to its own power supply coming from control box.
* Ensure that the control box is plugging in and also switched on.
* Each axis of the stage can also move in two directions: further from home or towards home, given sufficient distance from home to begin with. 
* If using the Phidget control panel, please ensure that you can see the digital outputs from the control box, otherwise something is not connected properly.

*sillyscope* is JS code for reading data from scope at 10 Hz. This code is for if you want to increase the speed at which data is taken from the scope. 
It is not used in my setup with the stage and scope.

----- **CONTACT INFORMATION** -----

If you have questions regarding the codes or the setup of the testing equipment/experiment, contact me at megan.cvitan@mail.mcgill.ca.

