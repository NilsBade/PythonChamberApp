# test_assert_examples.py

import PythonChamberApp.connection_handler as connection_handler

def test_network_device_url():
    new_dev = connection_handler.NetworkDevice()
    new_dev.set_ip_address("https://github.com/NilsBade/PythonChamberApp")
    response = new_dev.check_if_reachable()
    return


