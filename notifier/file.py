#
"""
Write the error to a time stamped file

NOT YET IMPLEMENTED

returns:
  0: File written successfully
 -1: Invalid arguments
 -2: An exception occurred
"""
import sys
import string
import pickle
import datetime
import time

msg = None

try:
    # Load the settings from stdin
    settings = pickle.load(sys.stdin)
   
    # build the body of the message
    # text = settings['body'] % (settings['item'])
   
    sys.exit(0)
       
except Exception, ex:
    print "File script error %s" % str(ex)
    try:
        if msg is not None:
            print msg.as_string()
    except:
        pass
    sys.exit(-2)
