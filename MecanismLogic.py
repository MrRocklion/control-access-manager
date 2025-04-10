import threading
import requests
import json
from gpiosManager import GpiosManager
from dateutil import parser
from datetime import datetime, timezone
from db_manager import SqliteManager
import time

gpios = GpiosManager()
class Manager(threading.Thread):
    def __init__(self, rs232, stop_event, api_url, api_port, tenant, user_name, pass_word):
        super().__init__()
        self.rs232 = rs232
        self.stop_event = stop_event
        self.pending_passes = 0
        self.api_url = api_url
        self.api_port = api_port
        self.tenant = tenant
        self.jwt = ''
        self.user_name = user_name
        self.pass_word = pass_word
        self.database = SqliteManager()


    def run(self):
        self.jwt = self.get_token()
        self.update_db_from_backend()
        def periodic_subscription_update():
            while not self.stop_event.is_set():
                try:
                    print("[SubsUpdater] Esperando 15 horas para la próxima actualización...")
                    time.sleep(15 * 60 * 60)  # 7 horas en segundos

                    print("[SubsUpdater] Actualizando token y suscripciones...")
                    self.jwt = self.get_token()
                    self.update_db_from_backend()
                    print("[SubsUpdater] Actualización completada correctamente.")

                except Exception as e:
                    print(f"[SubsUpdater] ❌ Error durante actualización periódica: {e}")

        updater_thread = threading.Thread(target=periodic_subscription_update, daemon=True)
        updater_thread.start()

        # Hilo principal de lectura RS232
        while not self.stop_event.is_set():
            with self.rs232.lock:
                if self.pending_passes > 0:
                    self.open_turnstile()
                    self.pending_passes = max(0, self.pending_passes - 1)
                elif self.rs232.validation:
                    self.check_and_open_turnstile(self.rs232.data)


    def generate_pass(self):
        self.pending_passes += 1

    def update_db_from_backend(self):
        url = f"{self.api_url}/api/user-subscriptions"
        headers = {
            'x-tenant-id': self.tenant,
            'Authorization': f'Bearer {self.jwt}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"Error en la solicitud: {response.status_code}")
                return

            subscriptions = response.json().get('result', [])
            for sub in subscriptions:
                formatted_sub = {
                    "start_date": sub['start_date'],
                    "end_date": sub['end_date'],
                    "duration": sub['duration'],
                    "entries": sub['entries'],
                    "user_id": sub['user']['id']
                }
                existing_data = self.database.get_subscription_by_user_id(formatted_sub['user_id'])
                if existing_data:
                    print("Ya existe, actualizando fechas.")
                    self.database.update_subscription_dates(
                        formatted_sub['user_id'],
                        formatted_sub['start_date'],
                        formatted_sub['end_date']
                    )
                else:
                    print("No existe, registrando nueva suscripción.")
                    self.database.insert_subscription(formatted_sub)
        except Exception as e:
            print(f"Error al obtener o actualizar suscripciones: {e}")


    def get_users(self):
        url = f"{self.api_url}/api/users"
        headers = {
            'x-tenant-id': self.tenant,
            'Authorization': f'Bearer {self.jwt}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get('result', [])
            else:
                print(f"Error en la solicitud: {response.status_code}")
        except Exception as e:
            print(f"Error al obtener usuarios: {e}")
        return []

    def get_token(self):
        url = f"{self.api_url}/api/auth/login"
        payload = json.dumps({
            "email": self.user_name,
            "password": self.pass_word
        })
        headers = {
            'x-tenant-id': self.tenant,
            'Content-Type': 'application/json'
        }
        try:
            response = requests.post(url, headers=headers, data=payload)
            print(response)
            if response.status_code == 201:
                data = response.json()
                return data['result']['token']
            else:
                print(f"Error al obtener token: {response.status_code}")
        except Exception as e:
            print(f"Excepción al obtener token: {e}")
        return ''

    def validate_with_backend(self, user_id):
        url = f"{self.api_url}/api/user-subscriptions/{user_id}"
        headers = {
            'x-tenant-id': self.tenant,
            'Authorization': f'Bearer {self.jwt}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 201:
                data = response.json().get('result')
                if data and 'end_date' in data and data['end_date']:
                    end_date = parser.isoparse(data['end_date'])
                    return datetime.now(timezone.utc) <= end_date
        except Exception as e:
            print(f"Error validando con backend: {e}")
        return False



    def open_turnstile(self):
        gpios.turnstileOpen()

    def check_and_open_turnstile(self, user_data):
        try:
            user_id = user_data['user_id']
            subscription = self.database.get_subscription_by_user_id(user_id)

            if subscription and 'end_date' in subscription:
                end_date = parser.isoparse(subscription['end_date'])
                if datetime.now(timezone.utc) <= end_date:
                    print("Tiene suscripción vigente (local).")
                    self.open_turnstile()
                    self.rs232.validation = False
                    self.rs232.data = None
                    return True

            print("Verificando con backend...")
            if self.validate_with_backend(user_id):
                self.open_turnstile()
                self.rs232.validation = False
                self.rs232.data = None
                return True

        except Exception as e:
            print(f"Error en validación de acceso: {e}")
        return False
