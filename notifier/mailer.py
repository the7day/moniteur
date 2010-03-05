#
"""
Sends an email
returns:
  0: host ping successfully
  1: host ping failed
 -1: Invalid arguments
 -2: An exception occurred
"""
import sys
import string
import pickle
import smtplib
import email
import datetime
from time import time as _time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

done = False;
success = False

#try:
print "NEW MAILER"

# Load the settings from stdin
settings = pickle.load(sys.stdin)
#print repr(settings)
    
# Connect to the mail server (works with gmail)
smtpserver = None
if settings['ssl_required']=='True':
    smtpserver = smtplib.SMTP_SSL(settings['server_host'], settings['server_port'], timeout=30)
else:
    smtpserver = smtplib.SMTP(settings['server_host'], settings['server_port'], timeout=30)

smtpserver.ehlo()

if settings['tls_required'] == 'True':
   smtpserver.starttls()
   smtpserver.ehlo() # Needs a second ehlo?

if settings['auth_required']:
   smtpserver.login(settings['login'], settings['password'])

# Build a message
msg = MIMEMultipart()
msg['From'] = settings['from']
msg['To'] = settings['to']
msg['Subject'] = settings['subject'] % (settings['item'])
msg['Date'] = email.Utils.formatdate()
msg['Message-ID'] = email.Utils.make_msgid()
msg['User-Agent'] = "Moniteur/0.1"
msg['X-Priority'] = '3'
msg['Importance'] = 'normal'
msg['Precedence'] = 'bulk'
msg['List-Id'] = '<Moniteur>'

# build a message
text = settings['body'] % (settings['item'])

msg.attach( MIMEText( text ) )

to_addrs = map(string.strip, settings['to'].split(","));

print "sending email to ", settings['to']
# Send the message
res = smtpserver.sendmail(settings['from'], to_addrs, msg.as_string())

print "email sent"
# log-off
smtpserver.close()
        
#except Exception, ex:
#    print "Script error %s" % str(ex)
    
#    sys.exit(-2)
