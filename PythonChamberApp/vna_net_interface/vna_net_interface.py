import pyvisa
import time

class E8361RemoteGPIB:
    """
    This object implements a pyvisa interface that communicates with the E8361A PNA of Agilent / Keysight.
    Available visa commands are abstracted and summed up to a higher level to improve usability.
    """
    # private properties
    resource_manager: pyvisa.ResourceManager = None
    pna_device: pyvisa.Resource = None
    running_measurements: list = None   # stores all configured measurements as dict with measurement infos

    def __init__(self):
        self.resource_manager = pyvisa.ResourceManager()
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
        configures terminations as '\n' and sets timeout to 5sec.

        :return: open successful >> true, open failed >> false
        """
        try:
            self.pna_device = self.resource_manager.open_resource(resource_name=resource_name)
        except pyvisa.VisaIOError as ex:
            print(f'VISA ERROR - Resources could not be opened!\nMSG: {ex}')
            return False

        self.pna_device.read_termination = '\n'
        self.pna_device.write_termination = '\n'
        self.pna_device.timeout = 5000
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

    def pna_add_measurement(self, meas_name: str, parameter: str):
        """
        Adds measurement with given 'meas_name' to internal list of active measurements.
        Once added, configuration commands can be used in combination with 'meas_name' to configure the right measurement on pna.

        :param meas_name: Unique name of measurement to find measurement later
        :param parameter: Parameter that should be measured as string 'S11', 'S12', 'S21' or 'S22'
        :return: int, Number of stored/active measurements // -1 if duplicate meas-name
        """
        # check for availability of meas-name
        for meas in self.running_measurements:
            if meas['meas_name'] == meas_name:
                return -1

        # add new measurement with next cnum
        new_cnum = self.running_measurements.__len__() + 1  # returns next available index - PNA starts count at 1, thus '+1' offset
        self.running_measurements.append({'meas_name': meas_name, 'cnum': new_cnum, 'parameter': parameter, 'avg_num': 1, 'trigger': 'continuous'})

        self.pna_device.write(f"CALC{new_cnum}:PAR:DEF:EXT '{meas_name}',{parameter}")
        self.pna_device.write(f"DISPlay:WINDow{new_cnum}:STATE ON")
        self.pna_device.write(f"DISPlay:WINDow{new_cnum}:TRACe1:FEED '{meas_name}'")

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

        self.pna_device.write(f"CALC{cnum}:PAR:SEL '{meas_name}'")
        response = self.pna_device.query(f"SENS{cnum}:X?")
        x_axis_stim_points = [float(x) for x in response.split(',')]
        return x_axis_stim_points

    def pna_read_meas_data(self, meas_name: str) -> list[list[float]]:
        """
        Reads data according to given measurement name.
        Reads measurement data as complex numbers, thus two numbers per frequency-stimulus-point.
        Returns list as following...

            [
                [frequency0: float, real0: float, imag0: float],
                [frequency1: float, real1: float, imag1: float],
                ... ]
        """
        meas_idx = self.get_idx_of_meas(meas_name)
        if meas_idx == -1:
            print("Error - meas_name not found in running_measurements-list!")
            return False

        meas_cnum = self.running_measurements[meas_idx]['cnum']
        # Get stimulus points in Hz
        self.pna_device.write(f"CALC{meas_cnum}:PAR:SEL '{meas_name}'")
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

    def pna_set_trigger_manual(self, meas_name: str):
        """
        Disables continuous pna-internal trigger for given measurement.
        pna_trigger_measurement() can be used to trigger future measurements from software.

        :return: True >> success, False >> failed
        """
        meas_idx = self.get_idx_of_meas(meas_name)
        if meas_idx == -1:
            print("Error - meas_name not found in running_measurements-list!")
            return False

        meas_cnum = self.running_measurements[meas_idx]['cnum']
        self.running_measurements[meas_idx]['trigger'] = 'manual'
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
                time.sleep(0.3)

        number_of_triggers = self.running_measurements[meas_idx]['avg_num']

        # PNA E8361A bug: If there is more than one measurement configured, the PNA always misses one trigger when the
        # first measurement is addressed. Therefor in this case we trigger one more time.
        if meas_idx == 0 and self.running_measurements.__len__() > 1:
            number_of_triggers += 1

        for i in range(number_of_triggers):
            print(f"Trigger {i}\n")
            self.pna_device.write(f"INIT{meas_cnum}:IMM")
            while self.pna_device.query('*OPC?') != '+1':   # busy wait for measurement to finish before next trigger
                print("chamber ist beschäftigt!\n")
                time.sleep(0.3)

        return True

    def pna_set_trigger_continuous(self, meas_name: str):
        """
        Enables continuous pna-internal trigger for given measurement.

        :return: True >> success, False >> failed
        """
        meas_idx = self.get_idx_of_meas(meas_name)
        if meas_idx == -1:
            print("Error - meas_name not found in running_measurements-list!")
            return False

        meas_cnum = self.running_measurements[meas_idx]['cnum']
        self.running_measurements[meas_idx]['trigger'] = 'continuous'

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
        self.pna_device.write(f"SENS{meas_cnum}:AVER:MODE SWEEP")
        self.pna_device.write(f"SENS{meas_cnum}:AVER:COUN {avg_number}")
        return True

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

    def pna_add_measurement_detailed(self, meas_name: str, parameter: str, freq_start: float, freq_stop: float,
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
            self.pna_set_trigger_manual(meas_name=meas_name)
        if average_number > 1:
            self.pna_set_average_number(meas_name=meas_name, avg_number=average_number)
        return True


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

