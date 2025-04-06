import threading
import time
import serial

class rs232Comunication(threading.Thread):
    def __init__(self, stop_event, com):
        super().__init__()
        self.lock = threading.Lock()
        self.stop_event = stop_event
        self.data = {}
        self.validation = False
        self.n_validations = 0
        self.valor_actual = 0
        self.ser = serial.Serial(com, 9600, timeout=0.5)
        self.invalid = 0

    def run(self):
        while not self.stop_event.is_set():
            with self.lock:
                if self.ser.in_waiting > 0:
                    data = self.ser.readline().decode().strip()
                    result_list = data.split("|")
                    print({"qr debug >> " + data})

                    current_timestamp = int(time.time() * 1000)
                    if len(result_list) == 4:
                        exp_timestamp = int(result_list[3])
                        exp_timestamp += 30000

                        if current_timestamp <= exp_timestamp:
                            query_data = {
                                'user_id': result_list[0],
                                'tenant_id': result_list[1],
                                'iat': result_list[2],
                                'exp': result_list[3]
                            }
                            self.validation = True
                            self.data = query_data
                            print("VALIDACION QR")
                            # consultamos
                        else:
                            self.validation = False
                            print("CODIGO EXPIRADO")
                    elif len(result_list) == 3:
                        exp_timestamp = int(result_list[2])
                        exp_timestamp += 30000
                        if current_timestamp <= exp_timestamp:
                            query_data = {
                                'user_id': result_list[0],
                                'tenant_id': result_list[1],
                                'exp': result_list[2]
                            }
                            self.validation = True
                            self.data = query_data
                            print("VALIDACION QR 3 DIGITOS")
                        else:
                            self.validation = False
                            print("CODIGO EXPIRADO 3 DIGITOS")
                    else:
                        self.invalid += 1
                        self.validation = False
                        print("BAD QR CODE")
                else:
                    self.validation = False
            time.sleep(0.1)            

    def getData(self):
        return str(self.data)

    def updateValidations(self, number):
        self.n_validations = number
