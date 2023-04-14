# Email notification plugin

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set up the SMTP server details for Outlook
smtp_server = "smtp.office365.com"
smtp_port = 587
smtp_username = "plume521@outlook.com"
smtp_password = "Tq49XUQ7"

# Set up the email details
sender = "plume521@outlook.com"
recipient = "andrew@tasmanpartners.com.au"
subject = "Sent From An ai generated script"
message = "Hi pooksta, i wrote this with a ai genrated email server, if this comes through that is very cool \n haz"

# Create a MIME message
msg = MIMEMultipart()
msg['From'] = sender
msg['To'] = recipient
msg['Subject'] = subject
msg.attach(MIMEText(message))

# Connect to the SMTP server and send the email
with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(sender, recipient, msg.as_string())
