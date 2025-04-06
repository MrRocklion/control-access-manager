# import RPi.GPIO as GPIO
# import time

# class GpiosManager():
#     def __init__(self):
#         super().__init__()
#         GPIO.setmode(GPIO.BCM)
#         GPIO.setwarnings(False)
#         self.relay_1 = 20
#         self.relay_2 = 21
#         # declaracion de salidas
#         GPIO.setup(self.relay_1, GPIO.OUT)
#         GPIO.setup(self.relay_2, GPIO.OUT)
#         #inicializacion
#         GPIO.output(self.relay_1,GPIO.HIGH)
#         GPIO.output(self.relay_2,GPIO.HIGH)

#     def turnstileOpen(self):
#         GPIO.output(self.relay_1, GPIO.LOW)
#         GPIO.output(self.relay_1, GPIO.LOW)
#         time.sleep(1)
#         GPIO.output(self.relay_1, GPIO.HIGH)
#         GPIO.output(self.relay_1, GPIO.HIGH)
#         return "puerta general abierta"


class GpiosManager():
    def __init__(self):
        super().__init__()
        

    def turnstileOpen(self):
        return "puerta general abierta"