"""
This script documents the first approaches to reach the raspberry pi in the E3 local network
No functions are supposed to be used in the application! It is just a place for trial and error
"""
import json

import requests


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
