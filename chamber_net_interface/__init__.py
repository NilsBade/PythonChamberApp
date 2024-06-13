"""
This package abstracts the network protocol of the used measurement chamber to general commands in
a 'ChamberNetworkCommands' class. It is supposed to be used as interface for the high level
measurement-process-control and planning.
In case hardware changes, this is the place where a new hardware abstraction layer for the chamber should be realised.

Class ChamberNetworkCommands
    #properties
        ip_address : str
        api_key : str
    ... To Do ...
"""

from PythonChamberApp.chamber_net_interface.chamber_net_interface import ChamberNetworkCommands
