import os, re
import sys

from smtplib import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com" #"smtpgate.email.arizona.edu"
SMTP_PORT = 465 #587

TEST_MODE = True #Set this to false to send emails to students

sender = "<YOUR_USER_HERE>@email.arizona.edu"
assert sender.split("@")[0] != "<YOUR_USER_HERE>", "Add your username to the script!"

secondary_pw = "catmail_pass"
if secondary_pw == "catmail_pass":
    print("Please add your secondary catmail password. This is not your netid password.")
    print("For more details, navigate to the following link and scroll down to the secondary password section")
    print("\thttps://it.arizona.edu/documentation/catmail-configuration-settings-imap")
    sys.exit(1)


def main():
    if TEST_MODE:
        print("Running in test mode, emails will only be sent to you, not the students.")
        print("To change this, edit the script and set TEST_MODE to false.")
    try:
        assignment = sys.argv[1]
    except:
        assignment = input("Enter the assignment number: ")
    email_dir = "Assignment " + assignment + "/Short Problems/_emails/"
    session = SMTP_SSL(SMTP_SERVER, SMTP_PORT)
    #session.set_debuglevel(1) #uncomment to see extra debug information
    while True:
        try:
            print("Attempting to login...")
            session.login(sender, secondary_pw)
            break
        except SMTPAuthenticationError as e:
            print("Server did not accept the credentials, check your username and password.", 
                    file = sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(e, file = sys.stderr)
            sys.exit(1)
    for email in os.listdir(email_dir):
        if email.startswith("_"):
            continue
        email_file = open(email_dir + email).readlines()
        msg = MIMEMultipart()
        msg['From'] = sender
        recipient = re.findall("^[a-zA-Z0-9]*", email)[0] + "@email.arizona.edu"
        if not TEST_MODE:
            msg['To'] = recipient
        else:
            msg['To'] = recipient + ".test"
        msg['Subject'] = email_file[0].strip()
        part = MIMEText('text', 'plain')
        email_txt = [line for line in email_file[1:]
                     if not (line.strip().endswith("Comments:")
                     and email_file[-1].strip() == '')]
        part.set_payload("".join(email_txt))
        msg.attach(part)
        email_to_send = msg.as_string()
        if not TEST_MODE:
            session.sendmail(sender, recipient, email_to_send)
        else:
            session.sendmail(sender, sender, email_to_send)
        os.rename(email_dir + email, email_dir + "_" + email)
        
    session.quit()

main()
        
