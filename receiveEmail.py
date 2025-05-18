from email.utils import mktime_tz, parsedate_to_datetime, parsedate_tz
import imaplib
import email
from email.header import decode_header
import json
import re

turn_on = None

def receive_email_function(emailSendTime):
    global turn_on

    print("inside receive email function turn on: ")
    print(turn_on)

    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login("email@email.com", "password")

    imap.select("inbox")

    status, messages = imap.search(None, 'SUBJECT', '"RE: ATTENTION: IoT Smart Hub"')
    
    message_ids = messages[0].split()

    if not message_ids:
        print("No emails reply found.")
        return None  

    latest_email_id = message_ids[-1]
    status, msg_data = imap.fetch(latest_email_id, "(RFC822 FLAGS)")

    flags = imap.fetch(latest_email_id, "(FLAGS)")
                
    for response in msg_data:

        if isinstance(response[1], bytes):
            msg = email.message_from_bytes(response[1])

            subject = msg["Subject"]
            date = msg["Date"]

            print(emailSendTime)
            print(date)

            sent_time = parsedate_to_datetime(date)

            emailSendTime = emailSendTime.replace(tzinfo=None)
            sent_time = sent_time.replace(tzinfo=None)

            time_diff = (emailSendTime - sent_time).total_seconds()

            if time_diff <= 500: # Set timeout value
                print(subject)
                if subject:  
                    subject, encoding = decode_header(subject)[0]
                    
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else 'utf-8')

                byte_string = flags[1][0].decode('utf-8')

                if "\\Seen" in byte_string: # Check for 'Seen' flag
                    print("in seen")

                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))

                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                body = part.get_payload(decode=True).decode() # If user replied 'yes'
                                reply_body = body.split("On ")[0]

                                print(reply_body)

                                reply_match = re.search(r"\b(yes)\b", reply_body.strip())

                                if reply_match:
                                    print("Found 'yes' in the email body.")
                                    turn_on = True  
                                    return turn_on  
                                else:
                                    print("'yes' not found in this email.")
                                    turn_on = False
                                    return turn_on
                    else:
                        body = msg.get_payload(decode=True).decode("utf-8")
                        reply_body = body.split("On ")[0]

                        # reply_match = re.search(r"\b(yes)\b", reply_body.strip())

                        if "yes" in reply_body.lower():
                            print(f"Found reply with 'yes' in the body.")
                            turn_on = True
                            return turn_on  
                        else:
                            print("'yes' not found in this email.")
                            turn_on = False
                            return turn_on
            else:
                print(f"No reply received yet, checking will continue") # If no reply has been sent by the user
   
    print(turn_on)
                        
    imap.close()
    imap.logout()

    return turn_on