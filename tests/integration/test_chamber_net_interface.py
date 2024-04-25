"""
These tests can only be run when connected to the local network of the
measurement chamber and the chamber_ip_address parameter is correct!
"""
import pytest
import PythonChamberApp.chamber_net_interface as chamber_cmd


@pytest.fixture
def chamber_ip_address():
    return '134.28.25.201'


@pytest.fixture
def chamber_api_key():
    return '03DEBAA8A11941879C08AE1C224A6E2C'


def test_chamber_serial_con_discon(chamber_ip_address, chamber_api_key):
    chamber = chamber_cmd.ChamberNetworkCommands(ip_address=chamber_ip_address, api_key=chamber_api_key)
    response_con = chamber.chamber_connect()
    # print("connection stat code: " + str(response_con['status_code']))
    assert response_con['status_code'] == 204, f"attempt to connect returned status code: {str(response_con['status_code'])}, 204 expected"

    response_discon = chamber.chamber_disconnect()
    # print("disconnect stat code: " + str(response_discon['status_code']))
    assert response_discon['status_code'] == 204, f"attempt to connect returned status code: {str(response_con['status_code'])}, 204 expected"
    return


