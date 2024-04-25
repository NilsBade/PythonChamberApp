"""
This script documents the first approaches to reach the raspberry pi in the E3 local network
No functions are supposed to be used in the application! It is just a place for trial and error
"""
import json

import requests
import websocket

# [!NOTE]: needed protocol for octoprint is "http"

chamber_ip = 'http://134.28.25.201'
headers_api = {
    'X-Api-Key': '03DEBAA8A11941879C08AE1C224A6E2C'
}
# Server status - checked!
url1 = chamber_ip + '/api/server'
response = requests.get(url1, headers=headers_api)
print(response.status_code)
# connection status
url2 = chamber_ip + '/api/connection'
response = requests.get(url2, headers=headers_api)
print(response.status_code)

# issue a connection - checked!
url3 = chamber_ip + '/api/connection'
headers_tjson = headers_api
headers_tjson['Content-Type'] = 'application/json'
payload = {
    "command": "connect"
}
response = requests.post(url3, headers=headers_tjson, json=payload)
print(response.status_code)

# issue a disconnect - checked
payload = {
    "command": "disconnect"
}
response = requests.post(url3, headers=headers_tjson, json=payload)
print(response.status_code)

# get printer status - checked
"""if response status code 409 - Conflict, this means printer not connected (klipper not running)"""
url4 = chamber_ip + '/api/printer'
response = requests.get(url4, headers=headers_api)

## Websocket tests
import websocket


def on_message(ws, message):
    print("Received:", message)


def on_error(ws, error):
    print("Error:", error)


def on_close(ws):
    print("### Connection closed ###")


def on_open(ws):
    print("### Connection opened ###")


if __name__ == "__main__":
    # Replace 'ws://example.com/sockjs_endpoint' with the actual SockJS endpoint URL
    websocket.enableTrace(True)  # Enable trace to see connection details
    ws = websocket.WebSocket()
    ws.connect('ws://134.28.25.201/sockjs/websocket',
               on_message=on_message,
               on_error=on_error,
               on_close=on_close)
    print(ws.recv())
