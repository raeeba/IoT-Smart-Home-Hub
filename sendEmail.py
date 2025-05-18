from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import uuid
import json
import ssl


timeSent = 0
text = ""

def send_email_function(emailSendTime, text): # Sending low light intensity email

    global timeSent

    sender_email = "senderemail@email"
    receiver_email = "receiveremail@email"
    password = "password"


    message = MIMEMultipart("alternative")
    message["Subject"] = "ATTENTION: IoT Smart Hub"
    message["From"] = sender_email
    message["To"] = receiver_email

    part1 = MIMEText(text, "plain")
    message.attach(part1)

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            emailSendTime = datetime.now()
            timeSent = emailSendTime

    except Exception as e:
        print(f"Error occured in sendEmail.py : {e}")
    
    return timeSent

send_email_function(timeSent, text)