#pip install Flask
#pip install flask-restful
#pip install paho-mqtt

from flask import Flask, render_template
from flask_restful import Resource, Api
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt

app = Flask(__name__)
api = Api(app)

# Визначте список пінів, які ви хочете керувати
controlled_pins = [18, 23, 24, 25, 8, 7, 12, 16]

GPIO.setmode(GPIO.BCM)
for pin in controlled_pins:
    GPIO.setup(pin, GPIO.OUT)

class GPIOControl(Resource):
    def get(self, state, pin_number):
        if state == 'on':
            return self.turn_on(pin_number)
        elif state == 'off':
            return self.turn_off(pin_number)
        else:
            return {'message': 'Недопустимий стан'}

    def turn_on(self, pin_number):
        GPIO.output(pin_number, GPIO.HIGH)
        return {'message': f'GPIO {pin_number} ввімкнено'}

    def turn_off(self, pin_number):
        GPIO.output(pin_number, GPIO.LOW)
        return {'message': f'GPIO {pin_number} вимкнено'}

# Додайте ресурс для керування 8 пінами
api.add_resource(GPIOControl, '/gpio/<string:state>/<int:pin_number>')

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("gpio/control")

def on_message(client, userdata, msg):
    state = msg.payload.decode('utf-8')
    if state == 'on':
        GPIO.output(18, GPIO.HIGH)
    elif state == 'off':
        GPIO.output(18, GPIO.LOW)

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect("localhost", 1883, 60)

@app.route('/')
def index():
    return render_template('index.html')


def on_exit():
    GPIO.cleanup()
    mqtt_client.disconnect()

if __name__ == '__main__':
    mqtt_client.loop_start()
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False, threaded=True, 
            passthrough_errors=True, on_exit=on_exit)