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
        self.pna_device.write("CALC1:PAR:DEL:ALL")
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
        new_cnum = self.running_measurements.__len__()  # returns next available index since counting from zero
        self.running_measurements.append({'meas_name': meas_name, 'cnum': new_cnum, 'parameter': parameter})

        self.pna_device.write(f"CALC{new_cnum}:PAR:DEF:EXT '{meas_name}',{parameter}")

    def get_cnum_of_meas(self, meas_name: str):
        """
        Returns index of measurement in local running_measurements-list as int.
        Returns -1 if given 'meas_name' not found.
        """
        idx = -1
        counter = 0

        for meas in self.running_measurements:
            if meas['meas_name'] == meas_name:
                idx = counter
            counter += 1

        return idx





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

    creation_string = f"CALC{cnum}:PAR:DEF:EXT '{messungs_name}',{param}"
    chamber.write(creation_string)
    chamber.write("DISPlay:WINDow1:STATE ON")
    chamber.write(f"DISPlay:WINDow1:TRACe1:FEED '{messungs_name}'")
    chamber.write(f"SENSe{cnum}:FREQuency:STAR {frequency_start}")
    chamber.write(f"SENSe{cnum}:FREQ:STOP {frequency_stop}")
    chamber.write(f"SENSe{cnum}:BANDwidth:RESolution {IF_bw}")
    chamber.write(f"SENSe{cnum}:SWEep:POINts {num_of_points}")
    chamber.write(f"SOURce{cnum}:POWer{pnum}:LEVel:IMMediate:AMPLitude {max_pow_dbm}")

    # Read from Measurement
    chamber.write(f"CALCulate{cnum}:PARameter:SELect '{messungs_name}'")
    chamber.write(f"CALC{cnum}:DATA FDATA,Data(x)") # ToDo Reading measurement data does not work! find out how the syntax is meant

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