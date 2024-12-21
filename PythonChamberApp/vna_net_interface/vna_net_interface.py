import importlib
import os

import numpy as np
import pyvisa
import time

class E8361RemoteGPIB:
    """
    This object implements a pyvisa interface that communicates with the E8361A PNA of Agilent / Keysight.
    Available visa commands are abstracted and summed up to a higher level to improve usability.
    """
    # private properties
    resource_manager: pyvisa.ResourceManager = None
    pna_device: pyvisa.resources.gpib.GPIBInstrument = None
    running_measurements: list = None   # stores all configured measurements as dict with measurement infos {'meas_name', 'cnum', 'parameter' (S-param), 'avg_num', 'trigger': 'continuous'}
    __busy_wait_timeout = 0.3

    def __init__(self, use_keysight: bool = False):
        if use_keysight:
            # Import and path adaptation on the fly not necessary since python 3.11 by default uses NI and keysight
            # if stated explicitly by 'ktvisa32' >> Not sure if that is true... but NI and agilent hardware works fine
            # dependent on ressource-manager library-path declaration!
            #os.add_dll_directory('C:\\Program Files\\Keysight\\IO Libraries Suite\\bin')
            #os.add_dll_directory('C:\\Program Files (x86)\\Keysight\\IO Libraries Suite\\bin')
            #importlib.reload(pyvisa)
            self.resource_manager = pyvisa.ResourceManager('ktvisa32')
            # ToDo check and how the different adapters really work and when which library is used!
            #  Both adapters work on laptop as development-base, but checkbox seems to have no clear effect - maybe
            #  Keysight implementation is always used with extra dll-paths?! >> Fix when deployed on institut PC.
        else:
            self.resource_manager = pyvisa.ResourceManager() # default path seems to find NI visa lib. Adapter works 06.06.2024.
        self.running_measurements = []

    # private / internal


    # public
    def list_resources(self):
        """
        Returns tuple(str, ...) of available devices that fit '?*::INSTR' naming-scheme.
        """
        return tuple(self.resource_manager.list_resources())

    def list_resources_all(self):
        """
        Returns tuple(str, ...) of available devices without any filter.
        """
        return tuple(self.resource_manager.list_resources('?*'))

    def connect_pna(self, resource_name: str):
        """
        Opens the pyvisa resource with the given name.
        Stores the opened resource in pna_device object property for use with functions.
        configures terminations as '\n' and sets timeout to 2sec.

        :return: open successful >> true, open failed >> false
        """
        try:
            self.pna_device = self.resource_manager.open_resource(resource_name=resource_name)
        except pyvisa.VisaIOError as ex:
            print(f'VISA ERROR - Resources could not be opened!\nMSG: {ex}')
            return False

        self.pna_device.read_termination = '\n'
        self.pna_device.write_termination = '\n'
        self.pna_device.timeout = 2000
        return True

    def disconnect_pna(self):
        if self.pna_device is not None:
            self.pna_device.close()
            self.pna_device = None
        return

    def pna_read_idn(self):
        """
        :return: str of pna-response. returns error message if error occurs.
        """
        if self.pna_device is None:
            return str("No pna device stored in Remote Object!")

        try:
            self.pna_device.write('*IDN?')
        except pyvisa.VisaIOError as ex:
            return str(f'VISA ERROR - IDN Request failed!\nMSG: {ex}')

        try:
            idn_response = self.pna_device.read()
        except pyvisa.VisaIOError as ex:
            return str(f'VISA ERROR - IDN Read failed!\nMSG: {ex}')

        return idn_response

    def pna_preset(self):
        """
        Presets whole PNA system and deletes all standard measurements.
        :return: successful >> True, Failed >> False
        """
        if self.pna_device is None:
            return False

        self.pna_device.write("SYSTem:PRESet")
        self.pna_device.write("CALC:PAR:DEL:ALL")
        self.running_measurements = []
        return True

    def pna_add_measurement(self, meas_name: str, parameter: list[str]):
        """
        Adds measurement with given 'meas_name' to internal list of active measurements.
        Once added, configuration commands can be used in combination with 'meas_name' to configure the right measurement on pna.

        :param meas_name: Unique name of measurement to find measurement later
        :param parameter: Parameter list of 'S11', 'S12' or 'S22' to be measured
        :return: int, Number of stored/active measurements // -1 if duplicate meas-name
        """
        # check for availability of meas-name
        for meas in self.running_measurements:
            if meas['meas_name'] == meas_name:
                return -1

        # add new measurement with next cnum
        new_cnum = self.running_measurements.__len__() + 1  # returns next available index - PNA starts count at 1, thus '+1' offset
        self.running_measurements.append({'meas_name': meas_name, 'cnum': new_cnum, 'parameter': parameter, 'avg_num': 1, 'trigger': 'continuous'})

        self.pna_device.write(f"DISPlay:WINDow{new_cnum}:STATE ON") # creates window with cnum as identifier
        tnum = 0
        for param in parameter:
            tnum +=1
            new_meas_name = meas_name + '_' + param
            self.pna_device.write(f"CALC{new_cnum}:PAR:DEF:EXT '{new_meas_name}',{param}") # Calculate:Parameter:Define:Extended - creates new measurement
            self.pna_device.write(f"DISPlay:WINDow{new_cnum}:TRACe{tnum}:FEED '{new_meas_name}'") # creates measurement trace to window (for each S-param)

    def get_idx_of_meas(self, meas_name: str):
        """
        Returns index of measurement in local running_measurements-list as int.
        Returns -1 if given 'meas_name' not found.
        """
        idx = 0

        for meas in self.running_measurements:
            if meas['meas_name'] == meas_name:
                return idx
            idx += 1

        return -1

    def pna_set_freq_start(self, meas_name: str, freq_start: float):
        """
        Stores given start frequency in measurement-dict in running_measurements-list as 'freq_start'
        and sends start frequency to pna.
        If measurement name not found or other error, returns False.

        :param meas_name: unique name of measurement
        :param freq_start: start frequency in Hz
        :return: successful >> True, Failed >> False
        """
        meas_idx = self.get_idx_of_meas(meas_name)
        if meas_idx == -1:
            print("Error - meas_name not found in running_measurements-list!")
            return False

        meas_cnum = self.running_measurements[meas_idx]['cnum']

        self.running_measurements[meas_idx]['freq_start'] = freq_start
        self.pna_device.write(f"SENS{meas_cnum}:FREQ:STAR {freq_start}")
        return True

    def pna_get_freq_start(self, meas_name: str):
        """
        Reads start frequency from PNA and returns it as float.
        If measurement name not found or other error, returns False.

        :param meas_name: unique name of measurement
        :return: start frequency in Hz as float, False if error
        """
        meas_idx = self.get_idx_of_meas(meas_name)
        if meas_idx == -1:
            print("Error - meas_name not found in running_measurements-list!")
            return False

        meas_cnum = self.running_measurements[meas_idx]['cnum']

        response = self.pna_device.query(f"SENS{meas_cnum}:FREQ:STAR?")
        return float(response)

    def pna_set_freq_stop(self, meas_name: str, freq_stop: float):
        """
        Stores given stop frequency in measurement-dict in running_measurements-list as 'freq_stop'
        and sends stop frequency to pna.
        If measurement name not found or other error, returns False.

        :param meas_name: unique name of measurement
        :param freq_stop: stop frequency in Hz
        :return: successful >> True, Failed >> False
        """
        meas_idx = self.get_idx_of_meas(meas_name)
        if meas_idx == -1:
            print("Error - meas_name not found in running_measurements-list!")
            return False

        meas_cnum = self.running_measurements[meas_idx]['cnum']

        self.running_measurements[meas_idx]['freq_stop'] = freq_stop
        self.pna_device.write(f"SENS{meas_cnum}:FREQ:STOP {freq_stop}")
        return True

    def pna_get_freq_stop(self, meas_name: str):
        """
        Reads stop frequency from PNA and returns it as float.
        If measurement name not found or other error, returns False.

        :param meas_name: unique name of measurement
        :return: stop frequency in Hz as float, False if error
        """
        meas_idx = self.get_idx_of_meas(meas_name)
        if meas_idx == -1:
            print("Error - meas_name not found in running_measurements-list!")
            return False

        meas_cnum = self.running_measurements[meas_idx]['cnum']

        response = self.pna_device.query(f"SENS{meas_cnum}:FREQ:STOP?")
        return float(response)

    def pna_set_IF_BW(self, meas_name: str, if_bw: float):
        """
        Stores given IF Bandwidth in measurement-dict in running_measurements-list as 'IF_BW'
        and sends IF Bandwidth to pna.
        If measurement name not found or other error, returns False.

        :param meas_name: unique name of measurement
        :param if_bw: IF Bandwidth in Hz
        :return: successful >> True, Failed >> False
        """
        meas_idx = self.get_idx_of_meas(meas_name)
        if meas_idx == -1:
            print("Error - meas_name not found in running_measurements-list!")
            return False

        meas_cnum = self.running_measurements[meas_idx]['cnum']

        self.running_measurements[meas_idx]['IF_BW'] = if_bw
        self.pna_device.write(f"SENSe{meas_cnum}:BAND:RES {if_bw}")
        return True

    def pna_get_IF_BW(self, meas_name: str):
        """
        Reads IF Bandwidth from PNA and returns it as float.
        If measurement name not found or other error, returns False.

        :param meas_name: unique name of measurement
        :return: IF Bandwidth in Hz as float, False if error
        """
        meas_idx = self.get_idx_of_meas(meas_name)
        if meas_idx == -1:
            print("Error - meas_name not found in running_measurements-list!")
            return False

        meas_cnum = self.running_measurements[meas_idx]['cnum']

        response = self.pna_device.query(f"SENSe{meas_cnum}:BAND:RES?")
        return float(response)

    def pna_set_sweep_num_of_points(self, meas_name: str, num_of_points: int):
        """
        Stores given num_of_points in measurement-dict in running_measurements-list as 'sweep_num_of_points'
        and sends sweep number of points to pna.

        :param meas_name: unique name of measurement
        :param num_of_points: number of points to measure throughout frequency sweep
        :return: successful >> True, Failed >> False
        """
        meas_idx = self.get_idx_of_meas(meas_name)
        if meas_idx == -1:
            print("Error - meas_name not found in running_measurements-list!")
            return False

        meas_cnum = self.running_measurements[meas_idx]['cnum']

        self.running_measurements[meas_idx]['sweep_num_of_points'] = num_of_points
        self.pna_device.write(f"SENS{meas_cnum}:SWE:POIN {num_of_points}")
        return True

    def pna_get_sweep_num_of_points(self, meas_name: str):
        """
        Reads number of sweep points from PNA and returns it as int.
        If measurement name not found or other error, returns False.

        :param meas_name: unique name of measurement
        :return: number of sweep points as int, False if error
        """
        meas_idx = self.get_idx_of_meas(meas_name)
        if meas_idx == -1:
            print("Error - meas_name not found in running_measurements-list!")
            return False

        meas_cnum = self.running_measurements[meas_idx]['cnum']

        response = self.pna_device.query(f"SENS{meas_cnum}:SWE:POIN?")
        return int(response)

    def pna_set_output_power(self, meas_name: str, power_dbm: float):
        """
        Stores given power_dbm in measurement-dict in running_measurements-list as 'output_power'
        and sends the dbm value to the PNA.

        :param meas_name: unique name of measurement
        :param power_dbm: RF output Power in [dBm]
        :return: successful >> True, Failed >> False
        """
        meas_idx = self.get_idx_of_meas(meas_name)
        if meas_idx == -1:
            print("Error - meas_name not found in running_measurements-list!")
            return False

        meas_cnum = self.running_measurements[meas_idx]['cnum']

        self.running_measurements[meas_idx]['ouput_power'] = power_dbm
        self.pna_device.write(f"SOURce{meas_cnum}:POWer{1}:LEVel:IMMediate:AMPLitude {power_dbm}") # Not sure about Power-number but seems to work!
        return True

    def pna_get_output_power(self, meas_name: str):
        """
        Reads output power from PNA and returns it as float.
        If measurement name not found or other error, returns False.

        :param meas_name: unique name of measurement
        :return: output power in dBm as float, False if error
        """
        meas_idx = self.get_idx_of_meas(meas_name)
        if meas_idx == -1:
            print("Error - meas_name not found in running_measurements-list!")
            return False

        meas_cnum = self.running_measurements[meas_idx]['cnum']

        response = self.pna_device.query(f"SOURce{meas_cnum}:POWer{1}:LEVel:IMMediate:AMPLitude?")
        return float(response)

    def pna_is_busy(self):
        """
        Checks if PNA is busy doing some operation via GPIB.
        :return: True >> PNA busy, False >> PNA waiting
        """
        busy_bool = bool(self.pna_device.query('*OPC?') != '+1')
        return busy_bool

    def pna_get_x_axis(self, meas_name: str) -> list:
        """
        Gets x axis values for given measurement name from PNA device
        """
        meas_idx = self.get_idx_of_meas(meas_name)
        if meas_idx == -1:
            print("Error - meas_name not found in running_measurements-list!")
            return False

        meas_cnum = self.running_measurements[meas_idx]['cnum']

        self.pna_device.write(f"CALC{meas_cnum}:PAR:SEL '{meas_name}'")
        response = self.pna_device.query(f"SENS{meas_cnum}:X?")
        x_axis_stim_points = [float(x) for x in response.split(',')]
        return x_axis_stim_points

    def pna_read_meas_data(self, meas_name: str, parameter: str) -> list[list[float]]:
        """
        Reads data according to given measurement name and parameter.
        Reads measurement data as complex numbers, thus two numbers per frequency-stimulus-point.
        Returns list as following...
            [

            [frequency0: float, real0: float, imag0: float],

            [frequency1: float, real1: float, imag1: float],

            ...

            ]

        *Returns False if meas_name is invalid or S-parameter not configured for given meas_name.

        :param meas_name:   unique measurement identifier
        :param parameter:   S-Parameter that should be read from measurement (S11, S12 or S22)
        """
        meas_idx = self.get_idx_of_meas(meas_name)
        if meas_idx == -1:
            print("Error - meas_name not found in running_measurements-list!")
            return False

        if parameter not in self.running_measurements[meas_idx]['parameter']:
            print("Error - S-Parameter is not configured in given measurement!")
            return False

        meas_cnum = self.running_measurements[meas_idx]['cnum']
        detailed_meas_name = meas_name + '_' + parameter
        # Get stimulus points in Hz
        self.pna_device.write(f"CALC{meas_cnum}:PAR:SEL '{detailed_meas_name}'")
        x_axis_string = self.pna_device.query(f"SENS{meas_cnum}:X?")
        x_axis_stim_points = [float(x) for x in x_axis_string.split(',')]

        data_string = self.pna_device.query(f'CALC{meas_cnum}:DATA? SDATA')
        data_r_i_list = [float(x) for x in data_string.split(',')]

        # Assemble data list from X axis and real imaginary measurement data
        meas_data_list = []
        counter = 0
        for freq in x_axis_stim_points:
            meas_data_list.append([freq, data_r_i_list[counter], data_r_i_list[counter+1]])
            counter += 2

        return meas_data_list

    def pna_set_trigger_manual(self):
        """
        Disables continuous pna-internal trigger for all measurements.
        pna_trigger_measurement() can be used to trigger future measurements from software.

        :return: True >> success, False >> failed
        """
        for meas in self.running_measurements:
            meas['trigger'] = 'manual'
        self.pna_device.write("INIT:CONT OFF")
        return True

    def pna_trigger_measurement(self, meas_name: str):
        """
        Triggers one measurement process of given meas_name on PNA.
            >> Not sure if all configured measurements are triggered in reality.

        :return: True >> success, False >> failed
        """
        meas_idx = self.get_idx_of_meas(meas_name)
        if meas_idx == -1:
            print("Error - meas_name not found in running_measurements-list!")
            return False

        meas_cnum = self.running_measurements[meas_idx]['cnum']

        # Clear average buffer if averaged measurement should be triggered
        if self.running_measurements[meas_idx]['avg_num'] != 1:
            self.pna_device.write(f"SENS{meas_cnum}:AVER:CLE")
            while self.pna_device.query('*OPC?') != '+1':
                time.sleep(self.__busy_wait_timeout)

        number_of_triggers = self.running_measurements[meas_idx]['avg_num']

        # PNA E8361A bug: If there is more than one measurement configured, the PNA always misses one trigger when the
        # first measurement is addressed. Therefor in this case we trigger one more time.
        if meas_idx == 0 and self.running_measurements.__len__() > 1:
            number_of_triggers += 1

        for i in range(number_of_triggers):
            # print(f"Trigger {i}\n") # debug
            self.pna_device.write(f"INIT{meas_cnum}:IMM")
            while self.pna_device.query('*OPC?') != '+1':   # busy wait for measurement to finish before next trigger
                print("chamber ist beschäftigt!\n")
                time.sleep(self.__busy_wait_timeout)

        return True

    def pna_set_trigger_continuous(self):
        """
        Enables continuous pna-internal trigger for all measurement.

        :return: True >> success, False >> failed
        """
        for meas in self.running_measurements:
            meas['trigger'] = 'continuous'

        self.pna_device.write("INIT:CONT ON")
        return True

    def pna_set_average_number(self, meas_name: str, avg_number: int):
        """
        Enables average function for given measurement.
        Stores number of averaged sweeps in local running-measurements-list measurement dict as ['avg_num']

        If avg_number == 0, average function is disabled for given measurement.

        :param meas_name:   unique measurement name
        :param avg_number:  number of sweeps that should be averaged (1 - 65536)
        :return: True >> success, False >> failed
        """
        meas_idx = self.get_idx_of_meas(meas_name)
        if meas_idx == -1:
            print("Error - meas_name not found in running_measurements-list!")
            return False

        meas_cnum = self.running_measurements[meas_idx]['cnum']

        if avg_number < 0:
            avg_number *= -1

        if avg_number == 0:
            self.pna_disable_average(meas_name)
            return True

        self.running_measurements[meas_idx]['avg_num'] = avg_number
        self.pna_device.write(f"SENS{meas_cnum}:AVER:STAT ON")
        #self.pna_device.write(f"SENS{meas_cnum}:AVER:MODE SWEEP") # command unknown and not necessary
        self.pna_device.write(f"SENS{meas_cnum}:AVER:COUN {avg_number}")
        return True

    def pna_get_average_number(self, meas_name: str):
        """
        Reads number of sweeps that are averaged for given measurement.
        If measurement name not found or other error, returns False.

        :param meas_name: unique name of measurement
        :return: number of sweeps that are averaged for given measurement, False if error
        """
        meas_idx = self.get_idx_of_meas(meas_name)
        if meas_idx == -1:
            print("Error - meas_name not found in running_measurements-list!")
            return False

        meas_cnum = self.running_measurements[meas_idx]['cnum']

        """ Check if averaging enabled """
        avg_status = self.pna_device.query(f"SENS{meas_cnum}:AVER:STAT?")
        if avg_status == '0':   # average is disabled
            return 1

        """ Check average number if necessary """
        avg_num = self.pna_device.query(f"SENS{meas_cnum}:AVER:COUN?")
        return int(avg_num)

    def pna_disable_average(self, meas_name: str):
        """
        Disables average function for given measurement.
        :return: True >> success, False >> failed
        """
        meas_idx = self.get_idx_of_meas(meas_name)
        if meas_idx == -1:
            print("Error - meas_name not found in running_measurements-list!")
            return False

        meas_cnum = self.running_measurements[meas_idx]['cnum']

        self.running_measurements[meas_idx]['avg_num'] = 1
        self.pna_device.write(f"SENS{meas_cnum}:AVER:STAT OFF")
        return True

    def pna_add_measurement_detailed(self, meas_name: str, parameter: list[str], freq_start: float, freq_stop: float,
                                     if_bw: float, sweep_num_points: int, output_power: float, trigger_manual: bool,
                                     average_number: int):
        """
        Configures PNA measurement with all available configurations right away.
        :param meas_name:           unique measurement name
        :param parameter:           standard PNA Parameter 'S11', 'S12', 'S21' or 'S22'
        :param freq_start:          start frequency for sweep in [Hz]
        :param freq_stop:           stop frequency for sweep in [Hz]
        :param if_bw:               IF Bandwidth in [Hz]
        :param sweep_num_points:    Number of frequency points stimulated throughout sweep
        :param output_power:        RF Output Power in [dBm]
        :param trigger_manual:      enables manual triggering if True. Otherwise, internal continuous trigger.
        :param average_number:      number of sweeps that should be averaged for one measurement result
        :return: True >> success, False >> failed
        """
        self.pna_add_measurement(meas_name=meas_name, parameter=parameter)
        self.pna_set_freq_start(meas_name=meas_name, freq_start=freq_start)
        self.pna_set_freq_stop(meas_name=meas_name, freq_stop=freq_stop)
        self.pna_set_IF_BW(meas_name=meas_name, if_bw=if_bw)
        self.pna_set_sweep_num_of_points(meas_name=meas_name, num_of_points=sweep_num_points)
        self.pna_set_output_power(meas_name=meas_name, power_dbm=output_power)
        if trigger_manual:
            self.pna_set_trigger_manual()
        if average_number > 1:
            self.pna_set_average_number(meas_name=meas_name, avg_number=average_number)
        return True

    def pna_preset_from_file(self, file_name: str, meas_name: str, set_trigger_manual: bool = True):
        """
        Presets whole PNA system to a locally stored '.cst' file on PNA.

        The current implementation supports only one channel, namely channel 1 (default cnum = 1), to be used by the preconfiguration.
        Measurements/Parameters not in channel 1 will not be detected.

        dict on return:
        pna_info = {
            'meas_name': str,
            'parameter': list[str],
            'freq_start': float,
            'freq_stop': float,
            'IF_BW': float,
            'sweep_num_of_points': int,
            'output_power': float,
            'avg_num': int,
            }


        :param file_name:  name of cst-file to load on PNA
        :param meas_name:  unique name of measurement to read results from later
        :param set_trigger_manual:  if True, manual triggering is set. Otherwise, no command modifying the trigger is sent.
        :return: dict (pna-info) >> success, False >> failed
        """
        if file_name.split('.')[-1] != 'cst':
            print("Error preset PNA from file - File is not a CST file!")
            return False

        default_cnum = 1
        self.pna_preset()

        """ Modify filepath if only filename given """
        default_pna_rootpath = "C:/Program Files/Agilent/Network Analyzer/Documents/"   # specific to keysight PNA
        if file_name.split('\\').__len__() == 1 and file_name.split('/').__len__() == 1:
            file_name = default_pna_rootpath + file_name

        """ Load file on PNA """
        self.pna_device.write(f"MMEM:LOAD '{file_name}'")

        """ Read measured parameters in channel 1 """
        meas_list = self.pna_read_configured_measurements_on_channel(channel_number=default_cnum)
        if meas_list.__len__() == 0:
            print("Error preset PNA from file - No measurements found on preset PNA (On channel number 1)!")
            return False
        parameter_list = [meas[1] for meas in meas_list]

        """ Update local running_measurements-list with minimum information """
        self.running_measurements.append(
            {'meas_name': meas_name, 'cnum': default_cnum, 'parameter': parameter_list})

        """ Assure manual triggering if needed """
        if set_trigger_manual:
            self.pna_set_trigger_manual()

        """ Get PNA info for return dict """
        freq_start = self.pna_get_freq_start(meas_name)
        freq_stop = self.pna_get_freq_stop(meas_name)
        if_bw = self.pna_get_IF_BW(meas_name)
        sweep_num_points = self.pna_get_sweep_num_of_points(meas_name)
        output_power = self.pna_get_output_power(meas_name)
        avgerage_number = self.pna_get_average_number(meas_name)

        pna_info = {
            'meas_name': meas_name,
            'parameter': parameter_list,
            'freq_start': freq_start,
            'freq_stop': freq_stop,
            'IF_BW': if_bw,
            'sweep_num_of_points': sweep_num_points,
            'output_power': output_power,
            'avg_num': avgerage_number,
            }

        return pna_info

    def pna_read_configured_measurements_on_channel(self, channel_number: int = 1):
        """
        Reads configured measurements from PNA and returns them as list.
        :param channel_number:  channel number to read measurements from (<cnum>)
        :return: list of lists with measurement names and parameters [ ['meas_name1', 'param1'], ['meas_name2', 'param2'], ...]. Empty list if no parameters measured on given channel.
        """
        meas_list_str = self.pna_device.read(f"CALC{channel_number}:PAR:CAT:EXT?")  # example response: "CH1_S11_1,S11,CH1_S12_2,S12"
        if meas_list_str == '"NO CATALOG"':
            return []  # return empty list if no parameters measured on given cnum
        meas_list_parts = meas_list_str.split(',')  # sorted like ['meas_name1', 'param1', 'meas_name2', 'param2', ...]
        meas_list = [meas_list_parts[i:i + 2] for i in range(0, len(meas_list_parts), 2)]  # sorted [ ['meas_name1', 'param1'], ['meas_name2', 'param2'], ...]
        return meas_list

    def pna_write_custom_string(self, visa_str: str):
        try:
            self.pna_device.write(visa_str)
        except pyvisa.VisaIOError as ex:
            return str(f"ERROR - Error occurred while write.\nMSG: {ex}")

        return None

    def pna_read_custom_string(self, visa_str: str):
        try:
            response = self.pna_device.read(visa_str)
        except pyvisa.VisaIOError as ex:
            return str(f"ERROR - Error occurred while read.\nMSG: {ex}")
        return response

    def pna_query_custom_string(self, visa_str: str):
        try:
            response = self.pna_device.query(visa_str)
        except pyvisa.VisaIOError as ex:
            return str(f"ERROR - Error occurred while query.\nMSG: {ex}")
        return response


    # sample code for terminal try'n error
    # from PythonChamberApp.vna_net_interface.vna_net_interface import E8361RemoteGPIB as pna
    # pna = pna()
    # pna.connect_pna("GPIB0::15::INSTR")
    # pna.pna_preset()
    # pna.pna_add_measurement_detailed("mess1", "S11", 10e9, 11e9, 1000, 201, -20, True, 10)
    # pna.pna_add_measurement_detailed("mess2", "S12", 12e9, 13e9, 500, 402, -30, True, 5)
    # pna.trigger_measurement("mess1")
    # pna.trigger_measurement("mess2")

