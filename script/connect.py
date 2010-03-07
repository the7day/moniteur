#
"""
connect to a host using tcp socket
returns:
  0: Test Successful
  1: Test failed
 -1: Invalid arguments
 -2: An exception occurred
"""

done = False;
success = False

try:
    import subprocess
    import sys
    import time
    import datetime
    import re
    
    if len(sys.argv) < 3:
        print "INVALID ARGUMENT:Specify HOST and PORT"
        sys.exit(-1)
    
    host = sys.argv[1]
    port = int(sys.argv[2])
   
    hello_message = None
    success_message = None
    bye_message = None
    
    timeout = 100.0
    
    # Get the SIP port
    for k in sys.argv[3:]:
           
        try:
            if k.startswith('timeout='):
                timeout = int(k.split('=')[1])
        except:
             print "INVALID ARGUMENT:Specify a numeric timeout"
             sys.exit(-1)
        
        try:
            if k.startswith('hello_message='):
                hello_message = k.split('=')[1]
                hello_message = hello_message.replace('\\r', '\r')
                hello_message = hello_message.replace('\\n', '\n')
        except:
             print "INVALID ARGUMENT:Enter a valid hello message"
             sys.exit(-1)
             
        try:
            if k.startswith('bye_message='):
                bye_message = k.split('=')[1]
                bye_message = bye_message.replace('\\r', '\r')
                bye_message = bye_message.replace('\\n', '\n')
        except:
             print "INVALID ARGUMENT:Enter a valid bye message"
             sys.exit(-1)
             
        try:
            if k.startswith('success_message='):
                success_message = k.split('=')[1]
                success_message = success_message.replace('\\r', '\r')
                success_message = success_message.replace('\\n', '\n')
        except:
             print "INVALID ARGUMENT:Enter a valid success message"
             sys.exit(-1)
            
    
   
    import socket
    
    error = None
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        s.connect((host, port))
        
        if hello_message:
            s.send(hello_message)
        
        if success_message:
            # We want to receive something
            data = s.recv(len(success_message))
            #print ">", "'%s'" % data
            #print "<", "'%s'" % success_message
            if data == success_message:
                success = True
        else:
            # The connection is the success
            success = True
        
        if bye_message:
            s.send(bye_message)

        s.close()
        
    except Exception, ex:
        sucess = False
        error = str(ex)

    if not success:
        print "TCP server '%s:%s' is not available. %s" % (host, port, error)
        sys.exit(1)
        
    print "TCP server '%s:%s' is available" % (host, port)
    sys.exit(0)
        
except Exception, ex:
    print "Script error %s" % str(ex)
    print ex
    sys.exit(-2)
