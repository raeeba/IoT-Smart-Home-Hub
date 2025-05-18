 
import time
import json
from Freenove_DHT import DHT
import RPi.GPIO as GPIO

DHTPin = 17 # Define the pin of DHT11

# Gets the DHT11 values and writes them to a JSON file
# Only one record is in the file at a time to prevent slow down and increasing file size
def dht11_function():
    dht = DHT(DHTPin)

    dht_humidity = 0.00
    dht_temp = 0.00
    counts = 0  

    # Open DHT JSON file
    try:
        with open("static/data/dht_data.json", "w") as f:
            f.truncate()
            measurements = []
            
    except (FileNotFoundError, json.JSONDecodeError):
        print("An error has occurred")

    time.sleep(1)  

    while True:
        counts += 1
        print("Measurement count: ", counts)
        for i in range(0, 15):            
            chk = dht.readDHT11()     
            if chk == 0:      
                print("DHT11, OK!")
                break
            time.sleep(0.1)
        
        dht_humidity = dht.getHumidity()
        dht_temp = dht.getTemperature()

        print("Humidity : %.2f, \t Temperature : %.2f \n" % (dht_humidity, dht_temp))

        measurement = {
            "count": counts,
            "humidity": dht_humidity,
            "temp": dht_temp
        }

        measurements.append(measurement)

        json_data = {"measurements": measurements}
        json_string = json.dumps(json_data, indent=4)

        # Add new DHT11 values to file
        with open("static/data/dht_data.json", "w") as f:
            f.write(json_string + "\n")

        time.sleep(1)
        # GPIO.cleanup()
        return dht_temp
