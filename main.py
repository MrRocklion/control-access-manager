from flask import Flask, request, jsonify, abort,render_template
from datetime import datetime, timezone
from dateutil import parser
import jwt
import json
import requests
from db_manager import SqliteManager
from dotenv import load_dotenv
import os

app = Flask(__name__)


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

def get_users():
    url = f"http://{api_url}:{api_port}/api/users"

    payload = {}
    headers = {
    'x-tenant-id':tenant,
    'Authorization': f'Bearer {jwt}',
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


def get_suscriptions():
    url = f"http://{api_url}:{api_port}/api/user-subscriptions"
    headers = {
        'x-tenant-id': tenant,
        'Authorization': f'Bearer {jwt}',
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
def validate_with_backend(user_id):
    url = f"http://{api_url}:{api_port}/api/user-subscriptions/{user_id}"
    headers = {
        'x-tenant-id': tenant,
        'Authorization': f'Bearer {jwt}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    data = response.json()  # Convertir la respuesta a JSON
    user_find = data.get('result') 
    #falta validar la fecha 
    print(user_find)
    return False
    
def update_db(suscriptions):
    for _sub in suscriptions:
        formated_sub = {"start_date":_sub['start_date'],"end_date":_sub['end_date'],"duration":_sub['duration'],"entries":_sub['entries'],"user_id":_sub['user']['id']}
        data_exist = database.get_subscription_by_user_id(formated_sub['user_id'])
        if data_exist != None:
            print("ya existe")
            database.update_subscription_dates(formated_sub['user_id'],formated_sub['start_date'],formated_sub['end_date'])
        else:
            print("no existe, se procede a registrar")
            database.insert_subscription(formated_sub)

@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    return render_template('home.html', result=result)



@app.route('/api/validate', methods=['POST'])
def validate_suscription():
    if not request.is_json:
        abort(400, description="Se esperaba un JSON válido")

    data = request.get_json()
    if 'operation' not in data:
        abort(400, description="Falta el parámetro 'operation' en la solicitud")
    if data['operation'] == "validate_user":
        try:
            id_target = data['user_id']
            data_exist = database.get_subscription_by_user_id(id_target)
            if data_exist != None:
                fecha_objetivo = parser.isoparse(data_exist['end_date'])
                fecha_actual = datetime.now(timezone.utc)
                if fecha_actual <= fecha_objetivo:
                    return jsonify({"message": "Operación realizada con éxito", "status": 200,"access":True}), 200
                else:
                    flag = validate_with_backend(id_target)
                    if flag:
                        return jsonify({"message": "Operación realizada con éxito", "status": 200,"access":True}), 200
                    else:
                        return jsonify({"message": "Operación realizada con éxito", "status": 200,"access":False}), 200
            else:
                flag = validate_with_backend(id_target)
                if flag:
                    return jsonify({"message": "Operación realizada con éxito", "status": 200,"access":True}), 200
                else:
                    return jsonify({"message": "Operación realizada con éxito", "status": 200,"access":False}), 200
                
            
        except Exception as e:
            abort(500, description=f"Error al ejecutar la operación: {str(e)}")
  

if __name__ == "__main__":
    try:
        load_dotenv()
        tenant = os.getenv("TENANT_ID")
        api_url = os.getenv("API_URL")
        api_port = os.getenv("API_PORT")
        database = SqliteManager()
        jwt = get_token()
        suscriptions = get_suscriptions()
        update_db(suscriptions)
        app.run(host='0.0.0.0', port=5000,use_reloader=False)
    finally:
        print("programa terminado!")