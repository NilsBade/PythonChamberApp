import pyvisa

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
        self.running_measurements.append({'meas_name': meas_name, 'cnum': new_cnum, 'parameter': parameter})

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

    def setup_pna_add_measurement_detailed(self, meas_name: str, parameter: str, freq_start: float, freq_stop: float, if_bw: float, sweep_num_points: int, output_power: float):
        """
        Configures PNA measurement with all available configurations right away.
        :param meas_name:           unique measurement name
        :param parameter:           standard PNA Parameter 'S11', 'S12', 'S21' or 'S22'
        :param freq_start:          start frequency for sweep in [Hz]
        :param freq_stop:           stop frequency for sweep in [Hz]
        :param if_bw:               IF Bandwidth in [Hz]
        :param sweep_num_points:    Number of frequency points stimulated throughout sweep
        :param output_power:        RF Output Power in [dBm]
        :return: True >> success, False >> failed
        """
        self.pna_add_measurement(meas_name=meas_name, parameter=parameter)
        self.pna_set_freq_start(meas_name=meas_name, freq_start=freq_start)
        self.pna_set_freq_stop(meas_name=meas_name, freq_stop=freq_stop)
        self.pna_set_IF_BW(meas_name=meas_name, if_bw=if_bw)
        self.pna_set_sweep_num_of_points(meas_name=meas_name, num_of_points=sweep_num_points)
        self.pna_set_output_power(meas_name=meas_name, power_dbm=output_power)
        return True


    def pna_write_custom_string(self, visa_str: str):
        self.pna_device.write(visa_str)

    def pna_read_custom_string(self, visa_str: str):
        return self.pna_device.read(visa_str)

    def pna_query_custom_string(self, visa_str: str):
        return self.pna_device.query(visa_str)

if __name__ == '__main__':
    manager = pyvisa.ResourceManager()
    print(manager)
    print(manager.list_resources('?*'))

    chamber = manager.open_resource('GPIB0::15::INSTR')
    chamber.read_termination = '\n'
    chamber.write_termination = '\n'
    chamber.timeout = 5000.0
    # Identität des Gerät abfragen
    print(chamber.query('*IDN?'))

    # Auf Preset stellen und alle messungen löschen
    chamber.write("SYSTem:PRESet")
    chamber.write("CALC1:PAR:DEL:ALL")

    # Messung erstellen
    cnum = 1 # Einzigartige channel nummer im PNA
    pnum = 1 # Port number
    messungs_name = "meas1"
    frequency_start = 10e9
    frequency_stop = 12e9
    span = frequency_stop - frequency_start
    num_of_points = 1000
    param = 'S12'   # ggf. nicht nötig in chamber messung >> S12 nutzen heißt messung VON Port2 nach Port1 >> ProbeHead an Port 1, AUT an Port 2
    IF_bw = 1000
    max_pow_dbm = -3

    creation_string = f"CALC{cnum}:PAR:DEF:EXT '{messungs_name}',{param}"                   #
    chamber.write(creation_string)
    chamber.write("DISPlay:WINDow1:STATE ON")
    chamber.write(f"DISPlay:WINDow1:TRACe1:FEED '{messungs_name}'")
    chamber.write(f"SENSe{cnum}:FREQuency:STAR {frequency_start}")                          #
    chamber.write(f"SENSe{cnum}:FREQ:STOP {frequency_stop}")                                #
    chamber.write(f"SENSe{cnum}:BANDwidth:RESolution {IF_bw}")                              #
    chamber.write(f"SENSe{cnum}:SWEep:POINts {num_of_points}")                              #
    chamber.write(f"SOURce{cnum}:POWer{pnum}:LEVel:IMMediate:AMPLitude {max_pow_dbm}")      #

    # Read from Measurement
    chamber.write(f"CALCulate{cnum}:PARameter:SELect '{messungs_name}'")
    chamber.query(f"CALC{cnum}:DATA? SDATA") # First select the measurement you are interested in, then query data with '?' in visa string!
    # Use 'SDATA' to get complex values and calculate amplitude and phase later by yourself.
    # Otherwise, Amplitude and phase would have needed two separate measurements on the PNA with different cnums.

    # Zustand chamber abfragen ('+1' bedeutet chamber hat alle prozesse beendet)
    while chamber.query('*OPC?') != '+1':
        print("chamber ist beschäftigt!")
        # wait...


    print(chamber.query("CALCulate1:PARameter:CATalog?"))
    print(chamber.query("CALCulate2:PARameter:CATalog?"))
    print(chamber.write("CALCulate1:PARameter:DEFine:EXT 'Meas1',S11"))
    print(chamber.write("CALCulate2:PARameter:DEFine:EXT 'Meas2',S21"))
    chamber.write("DISPlay:WINDow1:STATE ON")
    chamber.write("DISPlay:WINDow2:STATE ON")

    chamber.write("DISPlay:WINDow1:TRACe1:FEED 'Meas1'")
    chamber.write("DISPlay:WINDow2:TRACe2:FEED 'Meas2'")

    chamber.write("SENSe1:FREQuency:SPAN 1e9")
    chamber.write("SENSe2:FREQuency:SPAN 2e9")

    #'Select both measurements
    chamber.write("CALCulate1:PARameter:SELect 'Meas1'")
    chamber.write("CALCulate2:PARameter:SELect 'Meas2'")
    #'Turn marker 1 ON for each measurement
    chamber.write("CALCulate1:MARKer:STATe ON")
    chamber.write("CALCulate2:MARKer:STATE ON")

    chamber.close()

