import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

Motor1 = 22 #Enable Pin
Motor2 = 27 #Input Pin
Motor3 = 13 #Input Pin

GPIO.setup(Motor1,GPIO.OUT)
GPIO.setup(Motor2,GPIO.OUT)
GPIO.setup(Motor3,GPIO.OUT)

def turnOnfan_function():

    print("INSIDE DC MOTOR  -----------------------------")

    GPIO.output(Motor1,GPIO.HIGH)
    GPIO.output(Motor2,GPIO.LOW)
    GPIO.output(Motor3,GPIO.HIGH)

def turnOffFan_Function():
    GPIO.output(Motor1,GPIO.LOW)
    GPIO.output(Motor2,GPIO.LOW)
    GPIO.output(Motor3,GPIO.LOW)