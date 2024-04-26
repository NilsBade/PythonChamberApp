"""
These tests can only be run when connected to the local network of the
measurement chamber and the chamber_ip_address parameter is correct!

--> these tests can only be run once the chamber_net_interface.__init__ again imports Chamber_websocket Class
"""
import pytest
import PythonChamberApp.chamber_net_interface as chamber_cmd

"""
@pytest.fixture
def chamber_ip_address():
    return '134.28.25.201'


def test_chamber_websocket(chamber_ip_address):
    new_socket = chamber_cmd.Chamber_websocket(ip_address=chamber_ip_address)
    properties = new_socket.get_properties()
    assert properties['ip_address'] == 'http://134.28.25.201', f"hallo"
    return

...

"""