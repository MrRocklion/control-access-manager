import jwt
import json
import requests

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
        token = data['result']['token']
        
    except:
        print('error')

    return token

def get_users(token):
    url = "http://localhost:3000/api/users"

    payload = {}
    headers = {
    'x-tenant-id': 'd9c08603-4039-4b7d-8afe-29ff53ef06f8',
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)

def get_suscription(token,id):
    url = "http://localhost:3000/api/users/id"
    payload = {}
    headers = {
    'x-tenant-id': 'd9c08603-4039-4b7d-8afe-29ff53ef06f8',
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)

jwt = get_token()
users=get_users(jwt)



