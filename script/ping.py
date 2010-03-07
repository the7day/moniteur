#
"""
Ping a host using windows ping, expects english messages
returns:
  0: Test Successful
  1: Test failed
 -1: Invalid arguments
 -2: An exception occurred
"""
try:
    
    import subprocess
    import sys
    import time
    import re

    if len(sys.argv) < 2:
        print "INVALID ARGUMENT"
        sys.exit(-1)
    host = sys.argv[1]
    
    # second argument is the timeout
    timeout = "5000"
    if len(sys.argv) > 2:
        timeout = sys.argv[2]
    
    process = subprocess.Popen(
        ["ping", "-n", "1", "-w", timeout, sys.argv[1]],
        shell = False,
        stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT
    )
    
    pattern1 = re.compile("\s*Packets:\s*Sent\s*=\s*(\d),\s*Received\s*=\s*(\d),\s*Lost\s*=\s*(\d)", re.I)
    pattern2 = re.compile(".*Destination\s*host\s*unreachable", re.I)
    #out, error = ping.communicate()
    sent = 0
    received = -1
    lost = -2
    unreachable = False
    
    for k in process.stdout:
        print k
        match = re.match(pattern1, k)
        if match is not None:
            sent = match.group(1)
            received = match.group(2)
            lost = match.group(3)
        if re.match(pattern2, k) is not None:
            unreachable = True
            
    if sent != received or unreachable:
        print "Host '%s' is not available" % host
        sys.exit(1)
        
    print "Host '%s' is available" % host
    sys.exit(0)
    
except Exception, ex:
    print "Script error %s" % str(ex)
    sys.exit(-2)
