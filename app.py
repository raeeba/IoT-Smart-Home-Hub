from flask import Flask, jsonify, render_template
import threading
import time
import sendEmail
import ledEmail
import receiveEmail
import DC_Motor
import RPi.GPIO as GPIO
import sqlite3
import datetime
import paho.mqtt.client as mqtt

from DHT11 import dht11_function

# Imports for mqtt
from flask import Flask, render_template
from flask_mqtt import Mqtt # python -m pip install flask_socketio --break-system-packages
from flask_socketio import SocketIO, emit # python -m pip install flask_socketio --break-system-packages

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED, GPIO.OUT)

# Initializing pins
LED = 5
DHTpin = 17

# Initializing values

# Light intensity
payload_value = 0.0
email_sent = False 
light_on = False
light = False
light_intensity = 0.0

# Temperature 
is_fan_on = False
emails = []
email_sent_time = 0
emailSendTime = None
temperature = 50.0
text = """\
    Hello,
    The temperature has exceeded your desired threshold. Would you like to turn on the fan?
    Please reply with "yes" or "no".

    Regards,
    IoT Smarthub"""

app = Flask(__name__) # Flask 
socketio = SocketIO(app) # SocketIO

# Setup MQTT server
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = '127.0.0.1'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False

mqtt = mqtt.Client()
mqtt_message = None
reply_thread_running = False

def cleanup_gpio():
    GPIO.cleanup()

def send_email_in_background(): # Send temperature email
    global reply_thread_running, emailSendTime

    if emailSendTime is None:
        emailSendTime = time.time()

    print("Sending email to user...") 
    emailSendTime = sendEmail.send_email_function(emailSendTime, text)

    if not reply_thread_running:
        print("Email sent, waiting for a reply...")
        reply_thread_running = True
        reply_thread = threading.Thread(target=check_for_reply, args=(emailSendTime,))
        reply_thread.daemon = True  
        reply_thread.start()
        print("Reply checking thread started.")

def send_led_email(): # Send low light email
    print("Sending email to user...") 
    ledEmail.ledEmail_function() 
    socketio.emit('led_email_sent', { # Show notification on dashboard
        'msg': 'An email has been sent to your inbox due to low light.',
        'status': 'sent'
    })
    time.sleep(10000) # Sleep for 10s
    return "Email sent"

def check_fan_status(): # Check if fan is ON or OFF
    global is_fan_on
    return is_fan_on

def check_for_reply(emailSendTime): # Check for temperature email reply
    global is_fan_on, email_sent, reply_thread_running

    timeout = 500 # 20 min
    start_time = time.time()

    print("Check reply")

    while True:
        elapsed_time = time.time() - start_time  # Time elapsed since starting

        if elapsed_time >= timeout:
            print("Timeout reached, no reply from client, no action to execute.")
            email_sent = False  
            reply_thread_running = False
            socketio.emit('email_sent', {'status': 'off'})
            return False  # Return False because no reply was received in time

        print("Checking for email reply... ")
        is_reply = receiveEmail.receive_email_function(emailSendTime)
        print(f"Received reply: {is_reply}")

        if is_reply == True: # Turn on fan if user replied 'yes' to email
            print("User replied 'yes'. Turning on the fan.")
            is_fan_on = True 

            DC_Motor.turnOnfan_function()
            email_sent = False  
            reply_thread_running = False
            socketio.emit('email_sent', {'status': 'off'})
            
            return True 
          
        elif is_reply == False:
            print("User replied 'no'. Turning off the fan.")  # Keep fan off if user replied 'no' to email
            is_fan_on = False
            DC_Motor.turnOffFan_Function()
            reply_thread_running = False

def read_dht11_data():
    global is_fan_on, email_sent, reply_thread_running, emailSendTime
    global temperature

    while True:
        dht_tmp = dht11_function() #  Return the temperature to compare it later

        if dht_tmp >= temperature:
            print("redh dht11 ")
            print(email_sent)
            
            if not email_sent:  # Not true
                print("Temperature is high, sending email...")
                email_thread = threading.Thread(target=send_email_in_background)
                email_thread.start()  # Starts sending email in a other thread

                email_sent = True
            elif not reply_thread_running:  
                print("Email has been sent to client... Waiting for a reply or timeout.")
                reply_thread_running = True
                reply_thread = threading.Thread(target=check_for_reply, args=(emailSendTime))
                reply_thread.daemon = True  
                reply_thread.start() 

        elif dht_tmp < temperature:
            print("Temperature is normal, fan off.")
            is_fan_on = False
            email_sent = False

        time.sleep(5)  # Wait for 5 seconds before checking temp again

@app.route("/get_fan_status") # To change fan image on dashboard based on fan status 
def get_fan_status():
    global is_fan_on
    print("inside get_fan_status")
    print(is_fan_on)
    return jsonify({"is_fan_on": str(is_fan_on)})

@app.route("/")
def dashboard():
    global is_fan_on
    print("inside main route")
    print(is_fan_on)

    return render_template('index.html', is_fan_on=is_fan_on, mqtt_message=mqtt_message, payload_value=payload_value)


@app.before_first_request
def start_fan_monitor_thread():
    fan_thread = threading.Thread(target=check_fan_status)
    fan_thread.daemon = True  
    fan_thread.start()

# MQTT server
mqtt_message = {}

def connect_to_db(): # Connect to smarthome database to get user information from users table
    return sqlite3.connect('smarthome.db') 

def check_rfid_in_db(rfid_tag): # Check if RFID tag number matches a user in the database's tag number
    global light_intensity
    global temperature

    conn = connect_to_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE tag=?", (rfid_tag,))
    user = cursor.fetchone()
    
    conn.close()
    
    if user: # If user found, initialize user values
        socketio.emit('user', {
                'first': user[2], 
                'last': user[3],
                'email': user[4],
                'profile_picture': user[5],
                'light_intensity': user[6],
                'temperature': user[7],
                'humidity': user[8],
                'theme': user[9],
        })  
        # thresholds
        light_intensity = user[6]
        temperature = user[7]

        return ({'first': user[2],'last': user[3], 'email': user[4], 'theme': user[9]})
    else:
        return None   

# Subscribe to MQTT  topic on startup 
def handle_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Server {rc}")
    mqtt.subscribe('IoTlab/ESP32')  
    mqtt.subscribe('light/led')
    mqtt.subscribe('user/rfid')    

def handle_mqtt_message(client, userdata, message):
    global mqtt_message
    light = 'off'
    global LED  
    global light_intensity, emailSendTime
    # is_led_email_sent

    payload = message.payload.decode().strip()
    print(f"Received payload: {payload}")

    if message.topic == "user/rfid": # Get messages from RFID topic
        print(f"Received RFID tag: {payload}")
        
        username = check_rfid_in_db(payload)
        now = datetime.datetime.now()
        timE = now.strftime("%H:%M:%S")
        # time.time()
        userMssg = f"User {username} has entered at {timE}"

        if username:
            print(f"RFID tag recognized! Welcome, {username}.")
            sendEmail.send_email_function(timE,userMssg) # Send user email
            
        else:
            print("RFID tag not recognized. Access denied.")
    
    elif message.topic == 'IoTlab/ESP32': # Get messages from LED (light intensity) topic
        float_payload = float(payload) # Get the value of the light intensity from topic

        if float_payload < light_intensity: # If light intensity is lower than threshold
            # Email is sent
                print("Light intensity is low, turning LED on...") # If light intensity is low
                email_thread = threading.Thread(target=send_led_email)
                email_thread.start()

                GPIO.output(LED, GPIO.HIGH)
                mqtt.publish('light/led', 'ON') # Publish ON message to LED (light status) topic 
                light = 'on'

        else: # If light intensity is high
            print(f"Light intensity is high: {float_payload}")
            GPIO.output(LED, GPIO.LOW)
            mqtt.publish('light/led', 'OFF') # Publish OFF message to LED (light status) topic
            light = 'off'

        socketio.emit('led', { # Light values
                'light': light, # Light status
                'float_payload': float_payload # Light intensity value 
        })  

        mqtt_message = {
            'topic': message.topic,
            'payload': float_payload
        }
        print(f"MQTT Message: {mqtt_message}")
    

def start_mqtt(): # Start MQTT server
    mqtt.connect("127.0.0.1", 1883, 60)
    mqtt.loop_start()

mqtt.on_connect = handle_connect
mqtt.on_message = handle_mqtt_message

if __name__ == "__main__":

    print("Starting the Flask app...")

    mqtt_thread = threading.Thread(target=start_mqtt)
    mqtt_thread.daemon = True
    mqtt_thread.start()

    # Start the DHTT11 value reading thread
    sensor_thread = threading.Thread(target=read_dht11_data)
    sensor_thread.daemon = True
    sensor_thread.start()

    print("Sensor checking thread started.")

    app.run(debug=True, use_reloader=False, threaded=True)

# cleanup_gpio()