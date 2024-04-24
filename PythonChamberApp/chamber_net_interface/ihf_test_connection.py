"""
This script documents the first approaches to reach the raspberry pi in the E3 local network
No functions are supposed to be used in the application! It is just a place for trial and error
"""

import requests


# WATCHOUT: needed protocol for octoprint is "http"

headers = {
    'X-Api-Key': '03DEBAA8A11941879C08AE1C224A6E2C'
}
# Server status
url1 = 'http://134.28.25.201/api/server'
# connection status
url2 = 'http://134.28.25.201/api/connection'

response = requests.get(url2, headers=headers)
print(response.status_code)

# issue a connection
url3 = 'http://134.28.25.201/api/connection'
headers['Content-Type'] = 'application/json'
payload = {
    "command": "connect",
}
response = requests.post(url3, headers=headers, payload=payload)
print(response.status_code)