# Stage and Scope Light Map
----- **PROJECT SUMMARY** -----

Using a linear stage to image the light intensity of an LED with a photodiode. A stage will move and collect data over a predetermined grid. 
The data will be displayed in the form of a heatmap in order to demonstrate regions of varying light intensities. 

One can also record waveforms from an oscilloscope, identify pulses, and integrate between a specified range to get values for light intensity.

----- **ABOUT FILES** -----

*mainGrid_sillyscope* contains the required funcitons to move the linear stage and to communicate with the Rigol oscilloscope at the same time. Once the user determines the 
correct IP address, they will be asked to input a file name. If there is no folder already created with this name, the linear stage will begin to initialize. Data will be saved in
two different '.csv' files: one for all of the waveforms recorded during data collection, and one for the X, Y and Z positions, start and stop times of the detected pulses, and
integral values.

* The onemm value is from experimental measurements with a Vernier caliper. You must do your own callibration with each specific set up to strive for accuracy.
* Other features include direct plotting of a heatmap after data collection is complete. 
* The intervals on the heatmap are determined relatively, depending on the data that it is given. There is no need to set a minimum or maximum range for the colour gradient.
* Both '.csv' and a '.png' files will be found in a new directory, separate from the current one that the code runs from.
* You may need to restart the kernel frequently. This is because the port is still being in use before you begin another scan.
* Be careful when inputting the parameters for the grid; it can be tricky. Try printing the entries of the positions in the console prior to running a scan.
* If you wish to play with the parameters of heatmap() to yield different-looking plots, copy the heatmap function into another '.py' file and feed it your desired '.csv' file.
* I suggest reading up on how spinmob works to get familiar with the syntax and how some of the data is stored: [spinmob documentation.](https://github.com/Spinmob/spinmob/wiki)

*TalkingToRigol* allows communication with a Rigol oscilloscope. It contains features that are specific to this type of scope, with model number DS1074. 

* Connect an ethernet cable from the scope to the computer.
* Always ensure that the IP address is correctly inputted in the code. It can be found on the scope by pressing on 'Utility' >> 'IO' >> 'LAN Config.' >> 'Apply'.
* You should get a message indicating a successful connection. If not, try checking the router (if applicable).

*StageController* outlines the linear stage's capabilities of motion, such as moving to a specific predetermined position and moving a certain number of steps. 

* To connect it properly, connect a USB from the control box to the computer. Also connect each axis to its own power supply coming from control box.
* Ensure that the control box is plugging in and also switched on.
* Each axis of the stage can also move in two directions: further from home or towards home, given sufficient distance from home to begin with. 
* If using the Phidget control panel, please ensure that you can see the digital outputs from the control box, otherwise something is not connected properly.
* The stage may have difficulties moving past ~55mm from home on the labelled Z axis. If you accidentally go over this threshold, you may hear a loud buzzing noise. 
  To fix it, unplug the USB from the control box.
* Tianyang Yu worked on the original code for the linear stage. I suggest contacting him regarding any questions related to the stage.

*sillyscope* is JS code for reading data from scope at 10 Hz. This code is for if you want to increase the speed at which data is taken from the scope. 
There is an option to use it in this experiment if you are looking to record waveforms. 

* It would be very useful to be able to use sillyscope with the Rohde & Schwarz oscilloscope in the lab. This has not yet been implemented in sillyscope, but one can attempt to do so by using the compatible commands for a R&S scope, found in the manual: [R&S Manual.](https://www.batronix.com/files/Rohde-&-Schwarz/Oscilloscope/RTM3000/RTM3000_UserManual.pdf)
* Connecting the R&S scope to the computer involves connecting an ethernet cable and then clicking on the square found in the top right corner of the scope's screen. Click on 'Ethernet' and you should see updates on the connection status.

    *sillyscope_with_R&S* contains the edits made towards this goal.

----- **CONTACT INFORMATION** -----

If you have questions regarding the codes or the setup of the testing equipment/experiment, dont't hesitate to contact me at megan.cvitan@mail.mcgill.ca.

