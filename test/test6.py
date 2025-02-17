import requests
import json



def get_token():
    url = "http://localhost:3000/api/auth/login"

    payload = json.dumps({
    "email": "jhondoe@email.com",
    "password": "jhon@123"
    })
    headers = {
    'x-tenant-id': 'd9c08603-4039-4b7d-8afe-29ff53ef06f8',
    'Content-Type': 'application/json'
    }
    token = ''
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        data = response.json()
        print(data)
        token = data['result']['token']
    except:
        print("error")

    return token

print(get_token())

