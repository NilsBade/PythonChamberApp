"""
These tests can only be run when connected to the local network of the
measurement chamber and the chamber_ip_address parameter is correct!
"""
import json

import pytest
import PythonChamberApp.chamber_net_interface as chamber_cmd


@pytest.fixture
def chamber_ip_address():
    return '134.28.25.201'


@pytest.fixture
def chamber_api_key():
    return '03DEBAA8A11941879C08AE1C224A6E2C'


def test_chamber_serial_connect(chamber_ip_address, chamber_api_key):
    chamber = chamber_cmd.ChamberNetworkCommands(ip_address=chamber_ip_address, api_key=chamber_api_key)
    response_con = chamber.chamber_connect_serial()
    assert response_con['status_code'] == 204, f"attempt to connect returned status code: {str(response_con['status_code'])}, 204 expected"
    return

def test_chamber_serial_con_discon(chamber_ip_address, chamber_api_key):
    chamber = chamber_cmd.ChamberNetworkCommands(ip_address=chamber_ip_address, api_key=chamber_api_key)
    response_con = chamber.chamber_connect_serial()
    # print("connection stat code: " + str(response_con['status_code']))
    assert response_con['status_code'] == 204, f"attempt to connect returned status code: {str(response_con['status_code'])}, 204 expected"

    response_discon = chamber.chamber_disconnect_serial()
    # print("disconnect stat code: " + str(response_discon['status_code']))
    assert response_discon['status_code'] == 204, f"attempt to connect returned status code: {str(response_con['status_code'])}, 204 expected"
    return

def test_chamber_jog_rel(chamber_ip_address, chamber_api_key):
    chamber = chamber_cmd.ChamberNetworkCommands(ip_address=chamber_ip_address, api_key=chamber_api_key)
    chamber.chamber_connect_serial()
    response_jog = chamber.chamber_jog_rel(x=10, y=0, z=0, speed=10)
    assert response_jog['status_code'] == 204, f"attempt to connect returned status code: {str(response_jog['status_code'])}, 204 expected"
    # chamber.chamber_disconnect_serial()
    return

def test_chamber_level_bed(chamber_ip_address, chamber_api_key):
    chamber = chamber_cmd.ChamberNetworkCommands(ip_address=chamber_ip_address, api_key=chamber_api_key)
    response_lvl = chamber.chamber_level_bed()
    print(response_lvl['status_code'])
    assert response_lvl['status_code'] == 204, f"attempt to connect returned status code: {str(response_lvl['status_code'])}, 204 expected"
    return

def test_chamber_set_reset_flag(chamber_ip_address, chamber_api_key):
    chamber = chamber_cmd.ChamberNetworkCommands(ip_address=chamber_ip_address, api_key=chamber_api_key)
    chamber.chamber_reset_flag()
    flag_state = chamber.chamber_isflagset()
    assert flag_state == False, f"Flag should have been reset but it is unequal 0"
    chamber.chamber_set_flag()
    flag_state = chamber.chamber_isflagset()
    assert flag_state == True, f"Flag should have been set but is unequal 1"
    chamber.chamber_reset_flag()
    flag_state = chamber.chamber_isflagset()
    assert flag_state == False, f"Flag should have been reset but it is unequal 0"
    return

def test_conversions():
    a = 3.567
    stra = 'X'+str(round(a,1))
    assert stra == "X3.6", f"Round and type conversion must give 'X3.6' but is {stra}"
    return