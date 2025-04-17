from flask import Flask, request, jsonify, abort,render_template
from datetime import datetime, timezone
from dateutil import parser
from db_manager import SqliteManager
from dotenv import load_dotenv
import os
from MecanismLogic import Manager
from rs232 import rs232Comunication
import threading
app = Flask(__name__)
stop_event = threading.Event()

@app.route('/api/hmi', methods=['POST'])
def api_hmi():
    data = request.json
    action = data.get("action")
    if action == "generate_pass":
        manager.generate_pass()
        return jsonify({"message": "Sistema genera Pase"})
    elif action == "update":
        manager.update_db_from_backend()
        return jsonify({"message": "Actualizando sistema"})
    else:
        return jsonify({"message": "Acción no reconocida"}), 400


@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    return render_template('index.html', result=result)
if __name__ == "__main__":
    try:
        load_dotenv(dotenv_path=".env", override=True)
        api_port = os.getenv("API_PORT")
        api_url = os.getenv("API_URL")
        tenant = os.getenv("TENANT_ID")
        user_name = os.getenv("USER_NAME")
        pass_word = os.getenv("PASSWORD")
        com_port = os.getenv("COM_PORT")

        print("API_PORT: ", api_port)
        print("API_URL: ", api_url)
        print("TENANT_ID: ", tenant)
        print("USER_NAME: ", user_name)
        print("PASSWORD: ", pass_word)
        print("COM_PORT: ", com_port)

        rs232 = rs232Comunication(stop_event=stop_event,com=com_port)
        manager = Manager(api_port=api_port, api_url=api_url, tenant=tenant, pass_word=pass_word, user_name=user_name,stop_event=stop_event,rs232=rs232)
        rs232.start()
        manager.start()

        app.run(host='0.0.0.0', port=5000,use_reloader=False)
    finally:
        stop_event.set()
        rs232.join()
        manager.join()

        print("programa terminado!")