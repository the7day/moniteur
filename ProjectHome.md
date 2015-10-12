Moniteur is a very simple server/service monitoring tool written in python 2.6 (YMMV with other versions).

## How it works ##

Moniteur runs python script (called "Test") roughly at the interval specified in the configuration file (Test.cfg). If the script returns 0 the test is considered successful. If the script return anything else the test is considered failed and the result of the test is passed on to another python script (called "Notifier") which can do whatever it wants with the information. The notifier script is called again when a test succeed following a failure. (So you can know when your server is back online).

## Feature list ##

  * Can run as a windows service
  * Can run any python script that returns 0 on success and anything else on error as a test
  * Can execute a python script when a test fails

The existing tests are:

  * **ping.py**: A "win7 EN-US" ping test. Since it need to run in unprivileged mode this test depends on the windows "ping.exe" executable output being in the same language and format as the computer I used to develop it.
  * **connect.py**: A TCP 'plain text' connect/write/read test. This test can open a connection to a server, optionally write something in the socket and optionally compare a few byte of the response with a specified string.
  * **sip.py**: This test uses the excellent pjsip library to initiate a SIP connection to a SIP server and confirm that it is up and can create RTP stream.

The only existing notifier is:

  * **email.py**: Sends an email using python smtp library. Works with gmail smtp server.


## Moniteur does **not** have ##

  * A user-interface; web or otherwise.
  * An API. (REST, xml-rpc, json == NO).
  * A database.
  * SNMP support.
  * A proper documentation.
  * A proper Unix/Linux support (I have no need for it atm)
  * Defined milestones.
  * Years of production use guaranteeing it's stability.
  * A sponsor that pays me to answer to bug report in a timely fashion.
  * Support for python 2.4 (Might work or not. Don't tell me if it doesn't. I don't care.)

If you were looking for that; You were most likely looking for [pymon](http://pymon.sourceforge.net/)


## Installation & Configuration ##

Read the InstallInfo.