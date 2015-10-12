# Assumption #

I'll assume you're using windows. If you're using Linux you should be able to follow through and adapt accordingly.

# Requirements #

I haven't really kept track but it shouldn't require much above the standard python distribution.

  * Python 2.6
  * The pywin32 extension to run Moniteur as a windows service [sourceforge](http://sourceforge.net/projects/pywin32/). Not needed if you don't want to do that.
  * PJSIP's python binding if you want to run the SIP test. I don't think the nice folks at http://www.pjsip.org/ distribute a pre-compiled egg so you can the egg available in the repository here or compile it from the source available on pjsip.org yourself.

## Configuration ##

Moniteur has three configuration files.
All files use the python configuration file syntax also known as the infamous .ini syntax.

  * **config.cfg**: The application configuration and the python logging configuration.
  * **test.cfg**: The configuration of the tests you want to run
  * **notifier.cfg**: The configuration of the notifiers that should run when a test fails (or succeed after a failure)

### config.cfg ###

In this file you only need to change the path to the python executable if your setup is different from mine.

You can also modify the python logging configuration.

```
[moniteur]
; This is the path to the python executable that should be used to 
; run the test and notifiers. It has to be declared here because
; when running as windows service sys.executable points to the pythonservice.exe.
; TODO: This parameter needs to die.
python=C:\Python26\python.exe

; The name file containing the tests configuration
test_config=tests.cfg

; The name of the file containing the notifier configuration
notifier_config=notifier.cfg

;Logging configuration
; Add additional loggers, handlers, formatters here
; Uses python's logging config file format
; http=//docs.python.org/lib/logging-config-fileformat.html

[loggers]
keys = root, moniteur, notifier, service

; Logging configuration removed for brevity
; ...
; ...

```


### test.cfg ###

This file contains the definition of the tests. Test are defined by section (stuff between bracket [.md](.md)) in the configuration file. There can be as many section as you want in the configuration file.

Here is the basic format of a test configuration with comments.

```
; Definition of a "ping" test
; The name of the test does not matter
[Test_Ping_10.0.0.10]

; script=<name of python script>
; Name of the script to execute. Script are located in the "script" directory
; replace 'ping.py' by 'sip.py' or 'connect.py' to run another test.
script=ping.py

; arguments=<comma, separated, list>
; Argument for the script. Arguments are dependent on the script that you are running.
; Here we ping the host 10.0.0.10 with a timeout of 1000 ms
arguments=10.0.0.10, 1000

; period=<number of seconds>
; How often the script should run in seconds
period=10

; active=True|False
; Whether this script should run ('True') or not
active=True

; aggregate=<number> 
;When the script fails: How many failures do we wait until sending a new notification
; If the script runs every 10 seconds and you set aggregate to 20
; you should receive a notification of failure roughly every 200seconds (10x20) instead of
; a notification every 10 seconds.
;
; Please note that when the state of the test changes (from working to failing, or failing to working)
; the notification are sent right away.
aggregate=20
```

#### ping.py ####

(see above)

#### sip.py ####

```
; A SIP connection test
[SIP_localhost_5080]
; Use the python script 'sip.py'
script=sip.py

; arguments are:
; sip URI of the SIP server to connect to: sip:127.0.0.1:5080
;
; port=<number> : The local port for this SIP UA (set to something non-standard to avoid conflicting with another SIP UA on the same machine)
;
; timeout=<number> : Number of seconds after which to timeout if the connection fails
;
; log_level=<number> : Log level of the PJSIP library. Default is 3.
;
; success_message=<CALLING|EARLY|CONNECTING|CONFIRMED> : PJSIP message that we should consider indicating a successful connection.
;                  The default value is "CONFIRMED". Value are defined below as:
;
; SIP             PJSIP
; n/a            CALLING        : The call was just initiated
; 180 Ringing    EARLY          : Received a 180 ringing SIP code from the remote party (with media?)
; 200 OK         CONNECTING     : Received a 200 OK SIP code from the remote party
; 200 OK         CONFIRMED      : The RTP stream (audio) has been established
;
arguments=sip:127.0.0.1:5080, port=5090, timeout=5

; How often to run the test 
period=10

; Wait 100 failure after the first one to resend the alert
aggregate=100
```


#### connect.py ####

```
[CONNECT_10.0.0.11_80]
; The script to run
script=connect.py
; The arguments for the connect script:
; 1/ host to connect to
; 2/ port to connect to
;
; timeout=<number> : (OPTIONAL) Timeout in seconds
;
; hello_message=<string> : (OPTIONAL) String to write to the socket after the connection. Could be useful if your server requires some kind of handshake.
;
; success_message=<string> : (OPTIONAL) Message we expect to read from the socket to consider the connection a success. If this is not defined, the connection of the socket will considered a success.
;
; bye_message=<string> : (OPTIONAL) Message to write to the socket before disconnecting. So we can cleanly disconnect from the server
;
; Here we connect to 10.0.0.11 on port 80. If the connection is made the socket is closed and the test is considered successful
arguments=10.0.0.11, 80

; How often in seconds
period=10

; Wait 50 failure after the first one to resend the alert
aggregate=50
```

##### Using connect.py to test for a specific type of server server #####

Sometime you'll want to not only test that you can connect to your server but also that it is answering somewhat like it should.

**Test for an HTTP 200 response code**

With the configuration below if your server answers with anything but 'HTTP/1.1 200 OK' the test will be considered a failure.

```
script=connect.py
arguments=127.0.0.1, 80, hello_message=GET / HTTP/1.0\r\n\r\n, success_message=HTTP/1.1 200 OK
```


**Test for a POP3 email server**

While I don't have access to a POP3 server that allows non-ssl connection I guess something like that would work.

```
script=connect.py
arguments=127.0.0.1, 110, success_message=+OK POP3, bye_message=QUIT\n
```

**Testing gmail's STMP server**

Because you know, google really needs me to check if their servers are up. :)

```
script=connect.py
arguments=smtp.gmail.com, 587, success_message=220 mx.google.com ESMTP, bye_message=QUIT\n
```

etc... connect.py is not netcat but it's already enough to test quite a few types of servers as long as they speak plain text.


### notifier.cfg ###

This is where you configure your notifiers (or at least where you will in the future)

Currently only the notifier called [EMAIL](EMAIL.md) is used. Its syntax is defined below.

```

[EMAIL]
; The name of the script to run. Notifier are stored in the "notifier" directory.
script=mailer.py

; Email server information

; The SMTP server hostname
server_host=smtp.gmail.com

; The SMTP server port 
server_port=587

; Do we need to authenticate
auth_required=True

; Do we need to use TLS
tls_required=True

; OR do we need to use SSL
ssl_required=False

; Login for the SMTP server (only required if auth_required=True)
login=moniteur-account@gmail.com

; Password for the SMTP server (only required if auth_required=True)
password=PASSWORD

; Sender information
from="Moniteur" <moniteur-account@gmail.com>

; Recipient information 
to="John Doe" <Jd@email.com>

; Template of the message
; Allowable code are:
; 
; %%(code)s    :  The return code of the test
; %%(test)s    :  The name of the test
; %%(date)s    :  The Date and time at which the test was run
; %%(repeat)s  :  How many time this message was repeated (For when message are aggregated)
; %%(message)s :  The output of the test  

; Subject of the email 
subject=Moniteur message (%%(code)s) %%(test)s - %%(date)s

; Body of the email
body=Moniteur test report
	Test name:%%(test)s
	Date:%%(date)s
	Test return code:%%(code)s
	Message repeated:%%(repeat)s
	Message:
	%%(message)s

```


## Running Moniteur ##

### From the command line ###

Assuming you know how to open a 'shell' and cd into the directory where you have checked-out moniteur, you can simply run:

```
python src/moniteur/application.py
```

(and yes, forward slashes work on windows just fine)

Press 'q' or ctrl-c to exit.


### As a windows service ###

**Install the service**
```
python src\moniteur\winservice.py install
```

**Start the service**
```
python src\moniteur\winservice.py start
```

**Stop the service**
```
python src\moniteur\winservice.py stop
```

Note: By default the service when installed is not set to start automatically, you may want to change that using the service manager if you want moniteur to run at startup.


-- The End --