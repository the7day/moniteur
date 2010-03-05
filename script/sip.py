#
"""
Ping a host using windows ping, expects english messages
returns:
  0: host ping successfully
  1: host ping failed
 -1: Invalid arguments
 -2: An exception occurred
 
0  [CALLING]
180 Ringing [EARLY]
200 OK [CONNECTING]
Media Active
200 OK [CONFIRMED]
200 Normal call clearing [DISCONNCTD]
"""

done = False;
success = False

try:
    import subprocess
    import sys
    import time
    import datetime
    import re
    
    if len(sys.argv) < 2:
        print "INVALID ARGUMENT:Specify SIP URI"
        sys.exit(-1)
    
    uri = sys.argv[1]
    port = 5060
    log_level = 3
    success_message = "CONFIRMED"
    timeout = 10000
    
    # Get the SIP port
    for k in sys.argv[2:]:
        try:
            if k.startswith('port='):
                port = int(k.split('=')[1])
        except:
             print "INVALID ARGUMENT:Specify a numeric port"
             sys.exit(-1)
             
        try:
            if k.startswith('log_level='):
                log_level = int(k.split('=')[1])
        except:
             print "INVALID ARGUMENT:Specify a numeric log level"
             sys.exit(-1)
             
        try:
            if k.startswith('timeout='):
                timeout = int(k.split('=')[1])
        except:
             print "INVALID ARGUMENT:Specify a numeric timeout"
             sys.exit(-1)
             
        try:
            if k.startswith('success_message='):
                success_message = k.split('=')[1]
        except:
             print "INVALID ARGUMENT:Enter a valid success message"
             sys.exit(-1)
            
    
    import pjsua as pj

    # Logging callback
    def log_cb(level, str, len):
        print str,

    # Callback to receive events from Call
    class MyCallCallback(pj.CallCallback):
        def __init__(self, call=None):
            pj.CallCallback.__init__(self, call)
    
        # Notification when call state has changed
        def on_state(self):
            global success
            global done
            if self.call.info().state_text == success_message:
                success = True;
                done = True
                call.hangup()
            elif self.call.info().state_text == "DISCONNCTD":
                done = True;
                 
            print "%s %s [%s] " % (self.call.info().last_code, self.call.info().last_reason, self.call.info().state_text)
            
        # Notification when call's media state has changed.
        def on_media_state(self):
            global lib
            if self.call.info().media_state == pj.MediaState.ACTIVE:
                # Connect the call to sound device
                call_slot = self.call.info().conf_slot
                # Loopback the audio
                lib.conf_connect(call_slot, call_slot)
                #lib.conf_connect(0, call_slot)
                #print "Media Active"

    
   
    # Create library instance
    lib = pj.Lib()
    
    # config
    my_ua_cfg = pj.UAConfig()
    
    # Init library with default config
    lib.init(log_cfg = pj.LogConfig(level=log_level, callback=log_cb))
    # disable audio from sound card
    lib.set_null_snd_dev()
    
    # Create UDP transport which listens to any available port
    transport_config = pj.TransportConfig()
    transport_config.port = port
    transport = lib.create_transport(pj.TransportType.UDP, cfg=transport_config)
    
    # Start the library
    lib.start(with_thread=True)

    # Create local/user-less account
    acc = lib.create_account_for_transport(transport)

    # Make call
    call = acc.make_call(uri, MyCallCallback())

    # Wait for ENTER before quitting
    start = datetime.datetime.now() 
    while not done:
        time.sleep(0.4)
        if (datetime.datetime.now() - start).seconds > timeout:
            print "Hanging up after timeout"
            success = False
            done = True
            call.hangup()
            
        

    # We're done, shutdown the library
    lib.destroy()
    lib = None

    if not success:
        print "SIP server '%s' is not available" % uri
        sys.exit(1)
        
    print "SIP server '%s' is available" % uri
    sys.exit(0)
        
except Exception, ex:
    print "Script error %s" % str(ex)
    if lib is not None:
        try:
            lib.destroy()
            lib = None
        except:
            pass
    
    sys.exit(-2)
