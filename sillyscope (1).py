# Windows:
#  Install Rhode & Schwarz VISA or NI-VISA
#  pip install pyvisa
#  Name the scope something reasonable in OpenChoice Instrument Manager
# 
# Linux
#  pip install pyvisa pyvisa-py
#  Let me know if you find out how to name the scope.

import numpy   as _n
import time    as _t
import spinmob as _s
import spinmob.egg as _egg
_g = _egg.gui



try:    import visa as _v
except: print('VISA driver and / or pyvisa not installed. On Windows, consider Rhode & Schwartz VISA or NI-VISA, then pip install pyvisa. On Linux, pip install pyvisa and pyvisa-py')

debug_enabled = False
def debug(*a):
    if debug_enabled: 
        s = []
        for x in a: s.append(str(x))
        print(', '.join(s))




class Sillyscope():
    """
    Class for talking to a Tektronix Scope. Designed for TDS 1000 series, but 
    simple enough that it probably works for other models.
    
    Parameters
    ----------
    name='TDS1012B'
        Name of the scope, as it appears in the VISA Instrument Manager.
        Note this name can be set in the OpenChoice Instrument Manager, and 
        the default value is uggly with lots of "::"
    pyvisa_py=False
        Set to true if using pyvisa-py instead of, e.g., TekVISA or NI-VISA.
    """
    
    
    def __init__(self, name='TDS1012B', pyvisa_py=False, simulation=False):
        
        # Create a resource management object
        if pyvisa_py: self.resource_manager = _v.ResourceManager('@py')
        else:         self.resource_manager = _v.ResourceManager()
        
        # Set up the info
        self.t_duty_cycle = 0
        self.t_get_waveform  = 0
        self.previous_header = dict()
        self.previous_header[1] = dict(xzero=0, xmultiplier=1, xoffset=0, yzero=0, ymultiplier=1, yoffset=0)
        self.previous_header[2] = dict(xzero=0, xmultiplier=1, xoffset=0, yzero=0, ymultiplier=1, yoffset=0)
        self.previous_header[3] = dict(xzero=0, xmultiplier=1, xoffset=0, yzero=0, ymultiplier=1, yoffset=0)
        self.previous_header[4] = dict(xzero=0, xmultiplier=1, xoffset=0, yzero=0, ymultiplier=1, yoffset=0)
        self.model = None
        self._channel = 1
        
        # If we're in simulation mode, return
        if simulation:
            self.instrument = None
            self._idn = 'Simulation Mode'
            return
        
        # Try to open the instrument.
        try:
            self.instrument = self.resource_manager.open_resource(name)

            # Test that it's responding and is a Tektronix device.
            try:
                # Get the ID of the instrument
                self._idn = idn = self.query('*IDN?').strip()
                
                # Remember if it's a Tektronix scope
                if   idn[0:9] == 'TEKTRONIX': self.model='TEKTRONIX'
                
                # Need to distinguish 'Rigol Technologies,DS1052E,DS1ET161453620,00.04.01.00.02'
                # Which is janky and not working. (What is the GD data format??)
                elif idn[0:5].upper() == 'RIGOL': 
                    
                    # Get the model string
                    m = idn.split(',')[1]
                    
                    # Find out if it's a d/e or a z:
                    if   m[-1] in ['Z']: self.model='RIGOLZ'
                    elif m[-1] in ['B']: self.model='RIGOLB'
                    else:                self.model='RIGOLDE'
                
                # Poop out.
                else: self.model=None
                
                # Set the type of encoding for the binary data returned
                self.set_binary_encoding()
            
            except:
                print("ERROR: Instrument did not reply to IDN query. Entering simulation mode.")
                self.instrument.close()
                self.instrument = None
        except:
            print("ERROR: Could not open instrument. Entering simulation mode.")
            self.instrument = None
            
            # Now list all available resources
            print("Available Instruments:")
            for name in self.resource_manager.list_resources(): print("  "+name)
        
        
    # These can be modified later to make them safe, add delays, etc.
    def command(self, message='*IDN?'):
        """
        Runs a query() if there is a question mark, and a write() if there is not.
        """
        if message[-1] == '?': return self.query(message)
        else:                  return self.write(message)
    
    def query(self, message='*IDN?'):
        """
        Sends the supplied message and returns the response.
        """
        debug('query('+"'"+message+"'"+')')
        
        if self.instrument == None: return
        else:                       
            #if self.model == 'RIGOLDE': _t.sleep(RIGOLDE_DELAY)
            return self.instrument.query(message)
    
    def write(self, message): 
        """
        Writes the supplied message.
        """
        debug('write('+"'"+message+"'"+')')
        
        if self.instrument == None: return
        else:                       
            #if self.model == 'RIGOLDE': _t.sleep(RIGOLDE_DELAY)
            return self.instrument.write(message)
    
    def read (self):          
        """
        Reads a message and returns it.
        """
        debug('read()')
        
        if self.instrument == None: return
        else:                       
            #if self.model == 'RIGOLDE': _t.sleep(RIGOLDE_DELAY)
            return self.instrument.read()
    
    def read_raw(self):       
        """
        Reads a raw message (e.g. a binary stream) and returns it.
        """
        debug('read_raw()')
        
        if self.instrument == None: return 
        else:                       
            #if self.model == 'RIGOLDE': _t.sleep(RIGOLDE_DELAY)
            return self.instrument.read_raw()

    def clear(self):
        """
        Clears the display if possible.
        """
        if   self.model in ['RIGOLZ']:           self.write(':CLE')
        elif self.model in ['RIGOLB','RIGOLDE']: self.write(':DISP:CLE')
        
    def get_waveform(self, channel=1, convert_to_float=True, include_x=True, use_previous_header=False, binary=None):
        """
        Queries the device for the currently shown data from the specified channel,
        returning a databox with all the information.
        
        The databox header contains all the information required to convert 
        from integer steps in x and y to time (or frequency) and voltage. If the
        databox is 'd', then the x-values are generated as
        
             d['x'] = d.h('xzeroN') + d.h('xmultiplierN')*(n-d.h('xoffsetN'))
             
        where 'n' is the step number and N is the channel number, while 
        the y-values are generated as
            
             d['yN'] = d.h('yzeroN') + d.h('ymultiplierN')*(v-d.h('yoffsetN'))
        
        where 'v' is the 'voltage' in 8-bit integer units (spanning -127 to 128
        over the full range).
        
        This function also times these calls and sets self.t_get_waveform to the
        total time of the function call in seconds, and self.t_duty_cycle to the
        ratio of time spent on the CURV query vs the total time.
            
        Parameters
        ----------
        channel=1
            Which channel to query. Must be an integer and channel 1 corresponds
            to the first channel.
        
        convert_to_float=True
            If True, convert the returned integers to floating point based on the 
            scope range. If False, just return the integers. Note the conversion
            factors will be in the returned databox header either way.
        
        include_x=True
            Whether to also generate a column of data for the x-values. 
        
        use_previous_header=False
            If True, this will not query the waveform preamble / header information,
            which is actually several times longer than the data query. The 
            header information from the previous query is stored in the 
            dictionary self.previous_header[channel].
        
        binary=None
            Can be set to any of the allowed databox (numpy), e.g. binary='float32',
            which will set the databox to this binary mode.
        """
        debug('get_waveform()')
        
        # For duty cycle calculation
        t0 = _t.time()
        
        # For easy coding
        c = str(channel)
        
        # Simulation mode
        if self.instrument == None:
            
            # For duty cycle calculation
            t1 = _t.time()
            
            # Create the fake data
            d = _s.fun.generate_fake_data('20*sin(x)', _n.linspace(-5,5,1024), 
                                          ey=2, include_errors=False)
            
            # Fake the acquisition time
            _t.sleep(0.01)
            
            # For duty cycle calculation
            t2 = _t.time()
            
            # Rename the columns to simulate the scope output
            d.rename_column(0, 't')
            d.rename_column(1, 'y'+c)
            
            # Shorten the bitdepth
            d[1] = _n.int8(d[1])
            
            # Get the fake header info. 
            d.insert_header('xzero'+c, 1)
            d.insert_header('xoffset'+c, 0)
            d.insert_header('xmultiplier'+c, 0.1)
            d.insert_header('yzero'+c, 1)
            d.insert_header('yoffset'+c, 0)
            d.insert_header('ymultiplier'+c, 0.1)
            
            # Remember this for next time.
            self.previous_header[channel].update(d.headers)
            
            # If we're converting to float voltages
            if convert_to_float:
                d['y'+c] = d.h('yzero'+c) + d.h('ymultiplier'+c)*(d['y'+c]-d.h('yoffset'+c))
                
            # Pop the time column if necessary
            if not include_x: d.pop(0)
            
            
            
        # Real deal
        else:    
            
            # Databox to fill
            d = _s.data.databox()
            
            # Set the source channel
            self.set_channel(channel)
            
            # For duty cycle calculation
            t1 = _t.time()
            
            # Transfer the waveform information
            v = self._query_and_decode_waveform()
            
            debug('_query_and_decode_waveform() done', len(v))
            
            # For duty cycle calculation
            t2 = _t.time()            

            # Get the waveform header
            
            # If we're using the previous header, just load in the values
            if use_previous_header:
                d.update_headers(self.previous_header[channel])
            
            else:
                self.get_header(d)
            
            # If we're supposed to include time, add the time column
            if include_x: 
                d['x'] = _n.arange(0, len(v), 1)
                if self.model[0:5] == 'RIGOL': d['x'] = d['x'] - int(len(v))/2
                d['x'] = d.h('xzero') + d.h('xmultiplier')*(d['x']-d.h('xoffset'))
            
            # If we're converting to float voltages
            if convert_to_float:
                d['y'+c] = d.h('yzero') + d.h('ymultiplier')*(v-d.h('yoffset'))
            else:
                d['y'+c] = v
          
        # Set the binary mode
        if not binary == None: d.h(SPINMOB_BINARY=binary)
    
        # For duty cycle calculation
        t3 = _t.time()
        self.t_get_waveform  = t3-t0
        if t3-t0>0: self.t_duty_cycle = (t2-t1)/(t3-t0)
        else:       print("WARNING: get_waveform() total time == 0")
        
        debug('get_waveform() complete')
        # End of getting arrays and header information
        return d

    def trigger_single(self):
        """
        After calling self.set_mode_single_trigger(), you can call this to
        tell it to wait for the next trigger. It's up to you to check if 
        the trigger is complete.
        """
        debug('trigger_single()')
        
        if   self.model=='TEKTRONIX': self.write('ACQ:STATE 1')
        elif self.model=='RIGOLDE':   self.write(':RUN')
        elif self.model=='RIGOLZ':    self.write(':SING')
        elif self.model=='RIGOLB':    self.write(':KEY:SING')
        
        debug('trigger_single() complete')


    def get_header(self, d=None):
        """
        Updates the header of databox d to include xoffset, xmultiplier, xzero, yoffset,
        ymultiplier, yzero. If d=None, creates a databox.
        """
        debug('get_header()')
        
        if d==None: d = _s.data.databox()
        
        if self.model == 'TEKTRONIX':
            # THIS TECHNIQUE REDUCES THE DUTY CYCLE FROM 85% to 15%!
            #
            #            p = '1;8;BIN;RI;LSB;2500;"Ch'+str(channel)+', DC coupling, 5.0E-1 V/div, 2.5E-4 s/div, 2500 points, Sample mode";Y;1.0E-6;0;-8.9E-4;"s";2.0E-2;0.0E0;2.6E1;"Volts"\n'
            #            p = self.query('WFMP?')
            #                
            #            # Get the relevant preamble information
            #            d.h(preamble=p)
            #            p = p.split(';')
            #            d.h(byte_number      = int(p[0]),
            #                bit_number       = int(p[1]),
            #                encoding         = p[2],
            #                binary_format    = p[3],
            #                byte_order       = p[4],
            #                number_of_points = int(p[5]),
            #                info_string      = p[6],
            #                point_format     = p[7],
            #                xmultiplier       = float(p[8]),
            #                xoffset          = float(p[9]),
            #                xzero            = float(p[10]), 
            #                xunit            = p[11], 
            #                ymultiplier      = float(p[12]), 
            #                yzero            = float(p[13]), 
            #                yoffset          = float(p[14]),
            #                yunit            = p[15])

            # This is noticeably faster
            d.h(xzero       = float(self.query('WFMP:XZE?')))
            d.h(xoffset     = 0) #float(self.query('WFMP:PT_O?').strip()))
            d.h(xmultiplier = float(self.query('WFMP:XIN?')))
            d.h(yzero       = float(self.query('WFMP:YZE?')))
            d.h(yoffset     = float(self.query('WFMP:YOF?')))
            d.h(ymultiplier = float(self.query('WFMP:YMUL?')))
            
        elif self.model == 'RIGOLDE':
            
            c = str(self._channel)
            
            # Convert the yoffset to the Tek format
            xinc = float(self.query(':TIM:SCAL?'))       * 0.04
            yinc = float(self.query(':CHAN'+c+':SCAL?')) * 0.04
            
            d.h(xzero       = -float(self.query(':TIM:OFFS?')))
            d.h(xoffset     = 0)
            d.h(xmultiplier = xinc)
            d.h(yzero       = -float(self.query(':CHAN'+c+':OFFS?')))
            d.h(yoffset     = 0)
            d.h(ymultiplier = yinc)

        elif self.model in ['RIGOLZ','RIGOLB']:
            
            # Convert the yoffset to the Tek format
            xinc = float(self.query(':WAV:XINC?'))
            yinc = float(self.query(':WAV:YINC?'))
            
            d.h(xzero       = -float(self.query(':WAV:XOR?'))*xinc)
            d.h(xoffset     = 0)
            d.h(xmultiplier = xinc)
            d.h(yzero       = -float(self.query(':WAV:YOR?'))*yinc)
            d.h(yoffset     = 0)
            d.h(ymultiplier = yinc)
            
        # Remember these settings for later.
        self.previous_header[self._channel].update(d.headers)
        
        return d

        
    def _query_and_decode_waveform(self):
        """
        Queries and then parses the waveform, returning the array of (int8)
        voltages. Prior to calling this, make sure the scope is ready to 
        transfer and you've run self.set_channel().
        """
        debug('_query_and_decode_waveform()')
        
        if self.model == 'TEKTRONIX':
            
            # May be an option to change later
            width = 1
            
            # Ask for the waveform and read the response
            try:
                # Get the curve raw data
                self.write('CURV?')
                s = self.read_raw()
                
            except:
                print('ERROR: Timeout getting curve.')
                return None
        
            # Get the length of the thing specifying the data length :)
            n = int(s[1:3].decode()[0])
            
            # Get the length of the data set
            N = int(int(s[2:2+n].decode())/width)
            
            # Take the rest of the buffer as the buffer
            s = s[2+n:2+n+N*width]
            
            # Convert to an array of integers
            return _n.frombuffer(s,_n.int8)
        
        elif self.model in ['RIGOLDE', 'RIGOLB', 'RIGOLZ']:
            
            # Ask for the data
            try:
                self.write(':WAV:DATA?')
                s = self.read_raw()

            except:
                print('ERROR: Timeout getting curve.')
                return None
            
            # Get the number of characters describing the number of points
            n = int(s[1:2].decode())
            
            # Get the number of points
            N = int(s[2:2+n].decode())
            debug(N)
        
            # Convert it to an array of integers. 
            # This hits the rails properly on the DS1074Z, but is one step off from 
            # The values reported on the main screen.
            if self.model == 'RIGOLDE': return -_n.int8(_n.frombuffer(s[2+n:2+n+N], _n.uint8)+128)
            else:                       return  _n.int8(_n.frombuffer(s[2+n:2+n+N], _n.uint8)+128)
        
        
    def set_binary_encoding(self):
        """
        Sets up the binary encoding mode for curve transfer.
        """
        debug('set_binary_encoding()')
        
        if self.model == 'TEKTRONIX':
            self.write('DATA:ENC SRI')
            self.write('DATA:WIDTH 1') # Use 2 for two bytes per point.
        
        elif self.model == 'RIGOL':
            self.write(':WAV:MODE NORM') # Just get the screen. Use RAW to access the full memory.
            self.write(':WAV:FORM BYTE') # Use WORD to have two bytes per point.

    def set_channel(self, channel=1):
        """
        Select the channel to get the waveform data.
        """
        debug('set_channel()')
        
        if self.model == 'TEKTRONIX':
            self.write('DATA:SOURCE CH%d' % channel)
            
        elif self.model == 'RIGOL': 
            self.write(':WAV:SOUR CHAN%d' % channel)
        
        # Keep this for future use.
        self._channel = channel
        
    def set_mode_single_trigger(self):
        """
        Stops acquisition and sets it up to take a single trace upon the 
        next self.acquire() command.
        """
        debug('set_mode_single_trigger()', self.model)

        if self.model == 'TEKTRONIX':
            self.write('ACQ:STATE STOP')
            self.write('ACQ:STOPA SEQ')
        
        elif self.model in ['RIGOLZ', 'RIGOLDE', 'RIGOLB']: 
            self.write(':STOP')
            self.write(':TRIG:EDGE:SWE SINGLE')


            


class SillyscopeGUI(_g.BaseObject):
    """
    Graphical front-end for the TekScope interface.
    """
    def __init__(self, autosettings_path='scope_gui.txt', pyvisa_py=False):
        
        # No scope selected yet
        self.scope = None

        # Build the GUI
        self.window    = _g.Window('TekScope', autosettings_path='window')
        self.grid_top  = self.window.place_object(_g.GridLayout(False))
        self.window.new_autorow()
        self.grid_bot  = self.window.place_object(_g.GridLayout(False), alignment=0)
        
        self.button_connect   = self.grid_top.place_object(_g.Button('Connect', True, False))
        self.button_1         = self.grid_top.place_object(_g.Button('1',True).set_width(25))
        self.button_2         = self.grid_top.place_object(_g.Button('2',True).set_width(25))
        self.button_3         = self.grid_top.place_object(_g.Button('3',True).set_width(25))
        self.button_4         = self.grid_top.place_object(_g.Button('4',True).set_width(25))
        self.button_acquire   = self.grid_top.place_object(_g.Button('Acquire',True).disable())
        self.number_count     = self.grid_top.place_object(_g.NumberBox(0).disable())
        self.button_waiting   = self.grid_top.place_object(_g.Button('Waiting', True).set_width(70))
        self.button_transfer  = self.grid_top.place_object(_g.Button('Transfer',True).set_width(70))
        self.label_scope_name = self.grid_top.place_object(_g.Label('Disconnected'))
        
        self.settings  = self.grid_bot.place_object(_g.TreeDictionary('settings.txt'))
        self.tabs_data = self.grid_bot.place_object(_g.TabArea('tabs_data'), alignment=0)
        self.tab_raw   = self.tabs_data.add_tab('Raw Data')
        self.plot_raw  = self.tab_raw.place_object(_g.DataboxPlot('*.txt', 'plot_raw'), alignment=0)
        
        # Create a resource management object
        if pyvisa_py: self.resource_manager = _v.ResourceManager('@py')
        else:         self.resource_manager = _v.ResourceManager()
        
        names = []
        for x in self.resource_manager.list_resources():
            names.append(x)
                
        # VISA settings
        self.settings.add_parameter('VISA/Device', 0, type='list', values=['Simulation']+names)

        # Acquisition settings
        self.settings.add_parameter('Acquisition/Iterations',       0)
        self.settings.add_parameter('Acquisition/Trigger',          True)
        self.settings.add_parameter('Acquisition/Get_First_Header', True)
        self.settings.add_parameter('Acquisition/Get_All_Headers',  True)
        self.settings.add_parameter('Acquisition/Always_Clear',True)
        self.settings.add_parameter('Acquisition/RIGOL1000BDE/Trigger_Delay', 0.05, bounds=(1e-3,10), siPrefix=True, suffix='s', dec=True)
        self.settings.add_parameter('Acquisition/RIGOL1000BDE/Unlock', True)
        
        # Connect all the signals
        self.settings.connect_signal_changed('Acquisition/Trigger', self._settings_trigger_changed)
        self.button_connect.signal_clicked.connect(self.button_connect_clicked)
        self.button_acquire.signal_clicked.connect(self.button_acquire_clicked)
        self.button_1.signal_toggled.connect(self.save_gui_settings)
        self.button_2.signal_toggled.connect(self.save_gui_settings)
        self.button_3.signal_toggled.connect(self.save_gui_settings)
        self.button_4.signal_toggled.connect(self.save_gui_settings)
        


        # Convenience
        self.d = self.plot_raw

        # Run the base object stuff and autoload settings
        _g.BaseObject.__init__(self, autosettings_path=autosettings_path)
        self._autosettings_controls = ['self.button_1', 'self.button_2',
                                       'self.button_3', 'self.button_4']
        self.load_gui_settings()
        
        
        # Show the window.
        self.window.show()
    
    def _unlock(self):
        """
        If we're using a RIGOLDE/B and wish to unlock, send the :FORC command.
        """
        if self.settings['Acquisition/RIGOL1000BDE/Unlock']:
            if self.scope.model in ['RIGOLDE']:
                self.scope.write(':KEY:FORC')   
            elif self.scope.model in ['RIGOLB']:
                self.scope.write(':KEY:LOCK DIS')
    
    def _settings_trigger_changed(self, *a):
        """
        Called when someone clicks the Trigger checkbox.
        """
        if self.settings['Acquisition/Trigger']: 
            self.scope.set_mode_single_trigger()
            self._unlock()
    
    def connect(self):
        """
        Pushes the Connect button.
        """
        self.button_connect.set_checked()
        self.button_connect_clicked()

    def acquire(self):
        """
        Presses the Acquire button.
        """
        self.button_acquire.set_checked()
        self.button_acquire_clicked()        

    def get_status_finished(self):
        """
        Returns True if the acquisition is complete.
        
        For RIGOL scopes, this uses get_waveforms(), which also updates 
        self.plot_raw(), which is the best way to get the status. This avoids
        the issue of the single trigger taking time to get moving.
        """
        debug('get_status_finished()')
        
        if self.scope.model == 'TEKTRONIX':
            debug('  TEK')
            return not bool(int(self.scope.query('ACQ:STATE?')))
        
        elif self.scope.model == 'RIGOLZ':
            debug('  RIGOLZ')
            
            # If the waveforms are empty (we cleared it!)
            self.get_waveforms()
            if len(self.plot_raw[0]) > 0: return True
            else:                         return False
       
        elif self.scope.model in ['RIGOLDE', 'RIGOLB']:
            debug('  RIGOLDE/B')
                        
            self.window.sleep(self.settings['Acquisition/RIGOL1000BDE/Trigger_Delay'])
            s = self.scope.query(':TRIG:STAT?').strip()
            return s == 'STOP'
            

    def get_waveforms(self):
        """
        Queries all the waveforms that are enabled, overwriting self.plot_raw
        """
        debug('get_waveforms()')
        
        # Find out if we should get the header
        get_header = self.settings['Acquisition/Get_All_Headers']  \
                  or self.settings['Acquisition/Get_First_Header'] \
                 and self.number_count.get_value() == 0
        
        # Tell the user we're getting data
        self.button_transfer.set_checked(True)
        self.window.process_events()
                
        # Clear it.
        self.plot_raw.clear()
        
        # If we're supposed to get curve 1
        if self.button_1.get_value():
            
            # Actually get it.
            d = self.scope.get_waveform(1, use_previous_header=not get_header)
            
            # Update the main plot
            self.plot_raw.copy_all(d)
            self.window.process_events()
        
        # If we're supposed to get curve 2
        if self.button_2.get_value():
            
            # Actually get it
            d = self.scope.get_waveform(2, use_previous_header=not get_header)
            
            # Update teh main plot
            self.plot_raw['y2'] = d['y2']
            self.plot_raw.copy_headers(d)
            self.window.process_events()
        
        # If we're supposed to get curve 2
        if self.button_3.get_value():
            
            # Actually get it
            d = self.scope.get_waveform(3, use_previous_header=not get_header)
            
            # Update teh main plot
            self.plot_raw['y3'] = d['y3']
            self.plot_raw.copy_headers(d)
            self.window.process_events()
          
        # If we're supposed to get curve 2
        if self.button_4.get_value():
            
            # Actually get it
            d = self.scope.get_waveform(4, use_previous_header=not get_header)
            
            # Update teh main plot
            self.plot_raw['y4'] = d['y4']
            self.plot_raw.copy_headers(d)
            self.window.process_events()
        
        # Tell the user we're done transferring data
        self.button_transfer.set_checked(False)
        self.window.process_events()
        
        debug('get_waveforms() complete')

        

    def button_connect_clicked(self, *a):
        """
        Connects or disconnects the VISA resource.
        """
        
        # If we're supposed to connect
        if self.button_connect.get_value():
            
            # Close it if it exists for some reason
            if not self.scope == None: self.scope.instrument.close()
            
            # Make the new one
            self.scope = Sillyscope(self.settings['VISA/Device'], 
                    simulation = self.settings['VISA/Device']=='Simulation')
            
            # Tell the user what scope is connected
            self.label_scope_name.set_text(self.scope._idn)
            
            # Enable the Acquire button
            self.button_acquire.enable()
            
        elif not self.scope == None:
            
            # Close down the instrument
            if not self.scope.instrument == None:
                self.scope.instrument.close()
            self.scope = None
            self.label_scope_name.set_text('Disconnected')
            
            # Disable the acquire button
            self.button_acquire.disable()
            
    def button_acquire_clicked(self, *a):
        """
        Get the enabled curves, storing them in plot_raw.
        """
        debug('button_acquire_clicked()')
        
        # Don't double-loop!
        if not self.button_acquire.is_checked(): return

        # Don't proceed if we have no connection
        if self.scope == None: 
            self.button_acquire.set_checked(False)
            return

        # Disable the connection button
        self.button_connect.disable()
        
        # Reset the counter
        self.number_count.set_value(0)
        
        # If we're triggering, set to single sequence mode
        if self.settings['Acquisition/Trigger']: 
            self.scope.set_mode_single_trigger()
            
        debug('  beginning loop')

        # Continue until unchecked        
        while self.button_acquire.is_checked():
            
            # For RIGOL scopes, the most reliable / fast way to wait for a trace
            # is to clear it and keep asking for the waveform.
            
            self.button_waiting.set_checked(True)
            
            # Trigger
            if self.settings['Acquisition/Trigger']:
                
                debug('  TRIGGERING')
                
                # Set it to acquire the sequence.
                self.scope.trigger_single()
                
                # Simulation mode: "wait" for it to finish
                debug('  WAITING')
                if self.scope.instrument == None: self.window.sleep(0.1)
                
                # Actual scope: wait for it to finish
                else:
                    while not self.get_status_finished() and self.button_acquire.is_checked(): 
                        self.window.sleep(0.02)
                
                # Tell the user it's done acquiring.
                debug('  TRIGGERING DONE')
            
            # Not triggering but RIGOLZ mode: clear the data first and then wait for data
            elif self.scope.model in ['RIGOLZ']:
                
                # Clear the scope
                if self.settings['Acquisition/Always_Clear']: 
                    self.scope.write(':CLE')
                    
                # Wait for it to complete
                while not self.get_status_finished() and self.button_acquire.is_checked(): 
                    self.window.sleep(0.005)
            
            
            self.button_waiting.set_checked(False)
                
            # If the user hasn't canceled yet
            if self.button_acquire.is_checked():
                
                debug('  getting data')
        
                # The Z RIGOL models best check the status by getting the waveforms
                # after clearing the scope and seeing if there is data returned.
                
                # Triggered RIGOLZ scopes already have the data
                if self.scope.model in [None, 'TEKTRONIX', 'RIGOLDE', 'RIGOLB'] or \
                   not self.settings['Acquisition/Trigger']: 
                       # Query the scope for the data and stuff it into the plotter
                       self.get_waveforms()
                       debug('  got '+str(self.plot_raw))
                
                debug('  processing')
            
                # Increment the counter
                self.number_count.increment()
                
                # Update the plot
                debug('  plotting', len(self.plot_raw[0]), len(self.plot_raw[1]))
                self.plot_raw.plot()
                
                debug('  plotting done')
                self.window.process_events()
        
                # Autosave if enabled.
                debug('  autosaving')
                self.plot_raw.autosave()
            
                # End condition
                debug('  checking end condition')
                N = self.settings['Acquisition/Iterations']
                if self.number_count.get_value() >= N and not N <= 0: 
                    self.button_acquire.set_checked(False)
        
        debug('  loop done')
        
        # Enable the connect button
        self.button_connect.enable()
        
        # Unlock the RIGOL1000E front panel
        self._unlock()
        
            
            

############################
# Example code
############################

if __name__ == '__main__':
    
    # create the scope object
#    self = Sillyscope('DS1074Z')
     
    
    self = SillyscopeGUI()
    
    
#    resource_manager = _v.ResourceManager()
#    print(resource_manager.list_resources())
#    s = resource_manager.open_resource('USB0::0x0699::0x03B5::C010585::INSTR')
#    s.write('*IDN?')
#    print(s.read())
