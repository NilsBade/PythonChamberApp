
import requests
import json
import websocket

# chamber_ip = 'http://134.28.25.201'

class Chamber_websocket():

    # properties
    ip_address: str = None
    auth_socket_key: str = None

    def __init__(self, ip_address:str = None, login_user: str = 'bade', login_pass: str = 'bade'):
        self.ip_address = 'http://' + ip_address
        login_url = self.ip_address + '/api/login'

        # log in octoprint and store socket-auth-key
        response = requests.post(login_url, json={'user': login_user, 'pass': login_pass})
        data = json.loads(response.content)
        self.auth_socket_key = data['session']

        # subscribe for PositionUpdate-Event
        payload = {
            'auth': login_user + ":" + self.auth_socket_key,
            'subscribe': {
                'events': ['PositionUpdate', 'CommandSuppressed']
                }
            }
        return

    def get_properties(self):
        print('\nip_address: ' + self.ip_address + ' | auth-key: ' + self.auth_socket_key)
        return {'ip_address': self.ip_address, 'auth-key': self.auth_socket_key}





