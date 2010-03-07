#
"""
Sends an email
returns:
  0: Mail sent successfully
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

msg = None

try:
    # Load the settings from stdin
    settings = pickle.load(sys.stdin)
    
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
    
    # build the body of the message
    text = settings['body'] % (settings['item'])
    
    msg.attach( MIMEText( text ) )
    
    # split the addresses
    to_addrs = map(string.strip, settings['to'].split(","));
    
    # connect to the mail server (works with gmail)
    smtpserver = None
    if settings['ssl_required']=='True':
        smtpserver = smtplib.SMTP_SSL(settings['server_host'], settings['server_port'], timeout=30)
    else:
        smtpserver = smtplib.SMTP(settings['server_host'], settings['server_port'], timeout=30)
    
    smtpserver.ehlo()
    
    if settings['tls_required'] == 'True':
       smtpserver.starttls()
       smtpserver.ehlo() # Needs a second ehlo? <-- possible cargo culting
    
    if settings['auth_required']:
       smtpserver.login(settings['login'], settings['password'])

    # Send the message
    res = smtpserver.sendmail(settings['from'], to_addrs, msg.as_string())
    # If this method does not throw an exception, it returns a dictionary, with one entry for each recipient that was refused. 
    # Each entry contains a tuple of the SMTP error code and the accompanying error message sent by the server.
    print "email sent to (%s) (refused entry: %s)" % (str(settings['to']), str(res))
    
    # log-off
    smtpserver.close()
    
    sys.exit(0)
       
except Exception, ex:
    print "Mailer script error %s" % str(ex)
    try:
        if msg is not None:
            print msg.as_string()
    except:
        pass
    sys.exit(-2)
