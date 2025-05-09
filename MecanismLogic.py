import threading
import requests
import json
import logging
from gpiosManager import GpiosManager
from dateutil import parser
from datetime import datetime, timezone
from db_manager import SqliteManager
import time

# Configuración del logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
        def periodic_subscription_update():
            updated_today = False  # bandera para evitar múltiples actualizaciones en una misma madrugada

            while not self.stop_event.is_set():
                now = datetime.now()
                hour = now.hour

                if 2 <= hour < 3 and not updated_today:
                    try:
                        logger.info("[SubsUpdater] Iniciando actualización programada entre 2 y 3 a.m.")
                        self.jwt = self.get_token()
                        self.update_db_from_backend()
                        self.update_db_admin_from_backend()
                        logger.info("[SubsUpdater] ✅ Actualización completada correctamente.")
                        updated_today = True
                    except Exception as e:
                        logger.error(f"[SubsUpdater] ❌ Error durante actualización: {e}")

                elif hour >= 3:
                    updated_today = False  # resetea la bandera para la próxima madrugada

                time.sleep(60)  # espera 1 minuto antes de revisar otra vez

        updater_thread = threading.Thread(target=periodic_subscription_update, daemon=True)
        updater_thread.start()

        while not self.stop_event.is_set():
            with self.rs232.lock:
                if self.pending_passes > 0:
                    self.open_turnstile()
                    self.pending_passes = max(0, self.pending_passes - 1)
                elif self.rs232.validation:
                    self.check_and_open_turnstile(self.rs232.data)

    def generate_pass(self):
        self.pending_passes += 1

    def update_db_admin_from_backend(self):
        url = f"{self.api_url}/api/users/admins"
        headers = {
            'x-tenant-id': self.tenant,
            'Authorization': f'Bearer {self.jwt}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                logger.warning(f"Error en la solicitud: {response.status_code}")
                return
            admins = response.json().get('result', [])
            for admin in admins:
                formatted_admin = {
                    "admin_id": admin['id'],
                    "name": admin['name'],
                    "lastname": admin['lastname'],
                    "email": admin['email'],
                    "account_type": admin['account_type']['name']
                }
                existing_data = self.database.get_admin_by_id(formatted_admin['admin_id'])
                if not existing_data:
                    logger.info("No existe, registrando nuevo administrador.")
                    self.database.insert_admin(formatted_admin)
        except Exception as e:
            logger.error(f"Error al obtener o actualizar administradores: {e}")

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
                logger.warning(f"Error en la solicitud: {response.status_code}")
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
                    self.database.update_subscription_dates(
                        formatted_sub['user_id'],
                        formatted_sub['start_date'],
                        formatted_sub['end_date']
                    )
                else:
                    logger.info("No existe, registrando nueva suscripción.")
                    self.database.insert_subscription(formatted_sub)
        except Exception as e:
            logger.error(f"Error al obtener o actualizar suscripciones: {e}")

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
                logger.warning(f"Error en la solicitud: {response.status_code}")
        except Exception as e:
            logger.error(f"Error al obtener usuarios: {e}")
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
            logger.info(response)
            if response.status_code == 201:
                data = response.json()
                return data['result']['token']
            else:
                logger.info(f"Error al obtener token: {response.status_code}")
        except Exception as e:
            logger.error(f"Excepción al obtener token: {e}")
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
            if response.status_code == 200:
                data = response.json().get('result')
                if data and 'end_date' in data and data['end_date']:
                    end_date = parser.isoparse(data['end_date'])
                    return datetime.now(timezone.utc) <= end_date
        except Exception as e:
            logger.error(f"Error validando con backend: {e}")
        return False

    def open_turnstile(self):
        gpios.turnstileOpen()

    def check_and_open_turnstile(self, user_data):
        try:
            user_id = user_data['user_id']
            if not self.database.get_admin_by_id(user_id):
                subscription = self.database.get_subscription_by_user_id(user_id)
                logger.info(subscription)
                if subscription:
                    if 'end_date' in subscription:
                        end_date = parser.isoparse(subscription['end_date'])
                        if datetime.now(timezone.utc) <= end_date:
                            logger.info("Tiene suscripción vigente (local).")
                            self.open_turnstile()
                            self.rs232.validation = False
                            self.rs232.data = None
                            return True
                        else:
                            logger.info("Parece que caducó su suscripción. Verificaremos con el backend.")
                            if self.validate_with_backend(user_id):
                                logger.info("ABRIMOS EL TORNIQUETE")
                                self.open_turnstile()
                                self.rs232.validation = False
                                self.rs232.data = None
                                return True
                else:
                    logger.info("Verificando con backend...")
                    if self.validate_with_backend(user_id):
                        self.open_turnstile()
                        self.rs232.validation = False
                        self.rs232.data = None
                        return True
            else:
                self.open_turnstile()
                self.rs232.validation = False
                self.rs232.data = None
                logger.info("Acceso permitido para administrador o instructor.")
                return True
        except Exception as e:
            logger.error(f"Error en validación de acceso: {e}")
        return False
