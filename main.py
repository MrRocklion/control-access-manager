import jwt
import json
import requests
from db_manager import SqliteManager
from dotenv import load_dotenv
import os
load_dotenv()
tenant = os.getenv("TENANT_ID")
api_url = os.getenv("API_URL")
api_port = os.getenv("API_PORT")
def get_token():
    url = f"http://{api_url}:{api_port}/api/auth/login"

    payload = json.dumps({
    "email": "jhondoe@email.com",
    "password": "jhon@123"
    })
    headers = {
    'x-tenant-id': tenant,
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
    url = f"http://{api_url}:{api_port}/api/users"

    payload = {}
    headers = {
    'x-tenant-id':tenant,
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        try:
            data = response.json()  # Convertir la respuesta a JSON
            return data.get('result', [])  # Extraer 'result' o devolver una lista vacía si no existe
        except ValueError:
            print("Error: La respuesta no es un JSON válido")
            return []
    else:
        print(f"Error en la solicitud: {response.status_code}")
        return []


def get_suscriptions(token):
    url = f"http://{api_url}:{api_port}/api/user-subscriptions"
    headers = {
        'x-tenant-id': tenant,
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        try:
            data = response.json()  # Convertir la respuesta a JSON
            return data.get('result', [])  # Extraer 'result' o devolver una lista vacía si no existe
        except ValueError:
            print("Error: La respuesta no es un JSON válido")
            return []
    else:
        print(f"Error en la solicitud: {response.status_code}")
        return []

    




if __name__ == "__main__":
    database = SqliteManager()
    jwt = get_token()
    suscriptions = get_suscriptions(jwt)
    data_updated = []
    for _sub in suscriptions:
        formated_sub = {"start_date":_sub['start_date'],"end_date":_sub['end_date'],"duration":_sub['duration'],"entries":_sub['entries'],"user_id":_sub['user']['id']}
        database.insert_subscription(formated_sub)
    
