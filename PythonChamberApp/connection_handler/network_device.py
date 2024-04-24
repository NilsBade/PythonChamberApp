"""
This module defines objects that store necessary data to configure network communication
"""

import requests


class NetworkDevice:

    # Private Properties
    ip_address = "0.0.0.0"
    api_key = "x"

    # Interfaces
    def set_ip_address(self, new_ip: str = None):
        if isinstance(new_ip, str):
            self.ip_address = new_ip
            print("ip address set successfully!")
        else:
            print("please input ip address as string")
        return


    def set_api_key(self, new_key: str = None):
        if isinstance(new_key, str):
            self.api_key = new_key
            self.set_ip_address()
            print("api set successfully!")
        else:
            print("please input api as string")
        return

    def get_ip_address(self):
        """returns IP-address (or url) as string"""
        return self.ip_address

    def get_api_key(self):
        """returns API key as string"""
        return self.api_key

    def check_if_reachable(self):
        """ Checks if ip-address responses within 5 seconds. Otherwise, prints timeout error."""
        try:
            response = requests.get(self.ip_address, timeout=5)
        except requests.Timeout as error:
            print(error)
            return None

        print("device is reachable! Statuscode: ")
        print(response.status_code)

        return response
