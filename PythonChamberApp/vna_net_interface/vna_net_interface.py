import pyvisa

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