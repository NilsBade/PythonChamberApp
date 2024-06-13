"""
Can not manage to open websocket and authenticate successfully...
Don't quite get how to do authentication via websocket module and what octoprint expects.
--> This topic is cancelled unless viable reasons occur why the information "what klipper **thinks**
    where the print-head is", is an important information. For now the chamber will be assumed to follow all
    instructions (exactly like in GCode) without further checking for errors.
"""


import requests
import websocket
import json


## Websocket tests
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
        """returns dict of {'ip_address': str, 'auth_key': str}"""
        print('\nip_address: ' + self.ip_address + ' | auth-key: ' + self.auth_socket_key)
        return {'ip_address': self.ip_address, 'auth_key': self.auth_socket_key}



def on_message(ws, message):
    print("Received:", message)


def on_error(ws, error):
    print("Error:", error)


def on_close(ws):
    print("### Connection closed ###")


def on_open(ws):
    print("### Connection opened ###")


if __name__ == "__main__":
    new_ws = Chamber_websocket('134.28.25.201')
    properties = new_ws.get_properties()
    # Replace 'ws://example.com/sockjs_endpoint' with the actual SockJS endpoint URL
    websocket.enableTrace(True)  # Enable trace to see connection details
    ws = websocket.WebSocketApp(url='ws://134.28.25.201/sockjs/websocket',
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close
                                )
    ws.on_open = on_open
    ws.run_forever()


    authenticate = '{\"auth\": \"bade:' + properties['auth_key'] + '"}'
    print(authenticate)
    ws.send(authenticate)
    data = '{"subscribe": {"events": ["PositionUpdate"]}}'
    print(data)
    ws.send(data=data)



