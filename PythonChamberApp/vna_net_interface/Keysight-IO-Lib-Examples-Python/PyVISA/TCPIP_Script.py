import pyvisa

# Initialize the VISA resource manager
rm = pyvisa.ResourceManager()

# Define the resource string for your instrument
resource_string = "TCPIP0::134.28.25.191::PNA::INSTR"
ressource_string_GPIB_NI = "GPIB0::15::INSTR"

# Open the connection to the instrument
instrument = rm.open_resource(resource_string)

# Optional: Set a timeout (in milliseconds)
instrument.timeout = 5000

# Query the instrument for its identification string
idn_response = instrument.write("*IDN?")

# Print the response
print("Instrument ID:", idn_response)

# Close the connection
instrument.close()
