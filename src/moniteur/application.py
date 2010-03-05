'''
Created on Feb 20, 2010

@author: Boyd Ebsworthy

A simple monitoring application
'''
import sys
import os
import time
import datetime
import subprocess
#import logging
import string
import logging.config
import ConfigParser
import threading
import Queue
import pickle


class Notifier(threading.Thread):
    """ Notifier class. Post error message """
    
    def __init__(self, moniteur_settings, notifiers_config):
        self.settings = moniteur_settings
        self._notifiers = notifiers_config
        self._log = logging.getLogger("notifier")
        self._queue = Queue.Queue(maxsize=100)
        # Init thread
        threading.Thread.__init__(self)
    
    def post_error(self, test_name, error_code, message, repeat_count, notifiers=['EMAIL']):
        
        try:
            self._log.debug("posting error (%s:%s:%s)" % (test_name, error_code, message))  
            self._queue.put(dict(
                                 test=test_name,
                                 code=error_code, 
                                 message=message,
                                 repeat=repeat_count,
                                 date=datetime.datetime.now(),
                                 utcdate=datetime.datetime.utcnow(),
                                 notifiers=notifiers), True, None)

        except Exception:
            self._log.exception("Exception in post_error()")  

    def notify(self, item, notifier_name):
        """ Send a notification for an error item and a specific notifier """
        try:
            self._log.debug("notify(%s) called" % notifier_name)
            
            if not self._notifiers.has_section(notifier_name):
                self._log.error("Invalid notifier section name (%s)" % notifier_name)
                return
            
            # Get the parameters
            notifier_params = dict(self._notifiers.items(notifier_name))
            
            if not notifier_params.has_key('script'):
                self._log.error("Invalid notifier section script (%s)" % notifier_name)
                return
            
            # required when running as windows service (sys.executable is not pointing to python.exe)
            python = self.settings['python']
            # get the script
            script = "%s/%s" % ("notifier", notifier_params['script'])
            
            # check if the script exists
            if os.access(script, os.R_OK):
                
                # Execute the sub-process
                self._log.info("[Notifier:%s] running (%s)(%s)" % (notifier_name, python, script))
                process = subprocess.Popen(
                    [python, script],
                    shell = False,
                    stdin = subprocess.PIPE,
                    stdout = subprocess.PIPE,
                    stderr = subprocess.STDOUT
                )
                
                # add the item to the params
                notifier_params['item'] = item
                
                #print repr(notifier_params)
                
                # pickle and dump in the script stdin
                pickle.dump(notifier_params, process.stdin, 0)
                process.stdin.close()
                
                (stdout, stderr) = process.communicate()
                
                print stdout
                
            else:
                self._log.error("Invalid script file name (%s)" % script)
                return
            
            
        except Exception:
            self._log.exception("Exception in notify()")
        
    def run(self):
        """ Main notifier thread method """
        self.stop_required = False
        
        self._log.info("run()")
        
        while not self.stop_required:
            try:
                item = self._queue.get(True, 1)
                
                self._log.debug("Preparing to notify")
                
                for k in item['notifiers']:
                    self.notify(item, k)    
                
                #print "!!!! ERROR !!!: (%s:%s:%s) " % (item['test'], item['code'], item['message'])
            except Queue.Empty:
                pass   
            except Exception:
                self._log.exception("Exception in run()")
 
                
        
        self._log.info("end of thread")
    
    
    def stop(self):
        """ Stop the Notifier thread """
        try:
            self._log.info("stopping")
            self.stop_required = True
            self.join(1000)
            self._log.info("stopped")
        except Exception:
            self._log.exception("Exception in stop()")
            
            

class Moniteur(threading.Thread):
   
    def __init__(self, config_file):
        print "Using config file '%s'" % config_file
        # init python logging
        logging.config.fileConfig(config_file)
        # create a logger
        self._log = logging.getLogger("moniteur")
        # Load the config file
        config = ConfigParser.SafeConfigParser()
        config.read(config_file)
        # store settings
        self.settings = dict(config.items("moniteur"))
        self._log.info("Settings: %s" % self.settings)
        
        # Load the notifier configuration
        notifier_file = self.settings['notifier_config']
        self._log.debug("Loading notifier definition from '%s'" % notifier_file)
        if not os.access(notifier_file, os.R_OK):
            m = "Unable to load tests configuration file: '%s'" %  notifier_file
            self._log.error(m)
            raise Exception(m)
        notifier_config = ConfigParser.SafeConfigParser()
        notifier_config.read(notifier_file)
        
        self._notifier = Notifier(self.settings, notifier_config)
        
        # Init thread
        threading.Thread.__init__(self)

    def load_tests(self):
        """ Load the test definition from the configuration file """
        try:
            test_file = self.settings['test_config']
            
            self._log.debug("Loading test definition from '%s'" % test_file)
            
            if not os.access(test_file, os.R_OK):
                self._log.error("Unable to load tests configuration file: '%s'" %  test_file)
                return

            self.test_config = ConfigParser.SafeConfigParser()
            self.test_config.read(test_file)
            
        except Exception:
            self._log.exception("Exception in load_test()")    
        
    def start(self):
        """ Start the monitoring server """
        try:
            self._log.info("starting")
            self.load_tests()
            self._notifier.start()
            super(Moniteur, self).start()

        except Exception:
            self._log.exception("Exception in start()")

    def stop(self):
        """ Stop the monitoring server """
        try:
            
            self._log.info("stopping")
            self.stop_required = True
            self.join(1000)
            self._log.info("stopped")
            
            self._notifier.stop()
        except Exception:
            self._log.exception("Exception in stop()")
    
    
    def run_test(self, section_name):
        """ Stop the monitoring server """
        run_info=None
        try:
            self._log.debug("[Test:%s] preparing" % (section_name,))
            
            # Get the run information for this test
            if self.run_times.has_key(section_name):
                run_info = self.run_times[section_name]
            else:
                run_info = dict(last_run = None, last_returncode=0, last_message=None, repeat_count=0)
                self.run_times[section_name] = run_info
            
            # get active and arguments (optional)
            active = True
            arguments = None
            period = 30
            aggregate = 10
            
            if self.test_config.has_option(section_name, 'active'):
                active = self.test_config.getboolean(section_name, 'active')
            if self.test_config.has_option(section_name, 'arguments'):
                arguments = self.test_config.get(section_name, 'arguments')
                arguments = map(string.strip, arguments.split(","));
                self._log.debug("[Test:%s] arguments %s" % (section_name, arguments))
            if self.test_config.has_option(section_name, 'period'):
                period = self.test_config.getint(section_name, 'period')
            if self.test_config.has_option(section_name, 'aggregate'):
                aggregate = self.test_config.getint(section_name, 'aggregate')
                
            # Check if test is active
            if not active:
                self._log.debug("[Test:%s] is not active" % (section_name,))
                return
            
            # Check the period
            self._log.debug("[Test:%s] Last run time %s" % (section_name, run_info['last_run']))
            if run_info['last_run'] is not None:
                distance = datetime.datetime.now() - run_info['last_run']
                if distance.seconds < period:
                    self._log.debug("[Test:%s] last run %s/%s ago " % (section_name, distance.seconds, period))
                    return;
                
            # Get the two mandatory parameters "script" and "period"
            python = self.settings['python']
            script = "%s%s" % ( "script/", self.test_config.get(section_name, 'script') )   
            
            # This is needed when running as a win-service
            script = os.path.abspath(script)
            
            # Check if the script file is valid
            if os.access(script, os.R_OK):
                
                # Execute the sub-process
                self._log.info("[Test:%s] running (%s)(%s) (%s)" % (section_name, python, script, arguments))
                process = subprocess.Popen(
                    [python, script]+arguments,
                    shell = False,
                    stdout = subprocess.PIPE,
                    stderr = subprocess.STDOUT
                )
                
                # Wait for the process to complete
                # TODO: asynchronize this shit
                # TODO: put a time limit on script (kill it after x seconds)
                while process.poll() is None:
                    self._log.debug("[Test:%s] still running" % (section_name,))
                    time.sleep(0.5)
                
                stdout_message = ""
                for k in process.stdout:
                    stdout_message += k.strip() + "\n"
                    self._log.debug("[Test:%s] output:%s" % (section_name, k.strip()))
                  
                # Get the result
                if process.returncode != 0:
                    """ This is a failure
                    We always send a notification unless
                        - The error code is the same as previous and it has been repeated less than X time
                        
                        TODO:THIS SECTION COULD USE A GOOD REWRITE
                    """
                    self._log.warn("[Test:%s] result code: %s" % (section_name, process.returncode))
                    post_error = True
                    
                    #print "------------------------------------------------------"
                    #print "last_returncode", run_info['last_returncode']
                    #print "last_message", "'%s'" % run_info['last_message']
                    #print "repeat_count", run_info['repeat_count']
                    #print "returncode", process.returncode
                    #print "message", "'%s'" % stdout_message
                    #print "------------------------------------------------------"
                    
                    if run_info['last_returncode'] == process.returncode:# and run_info['last_message'] == stdout_message:
                        # This is a repeat message
                        run_info['repeat_count'] = run_info['repeat_count'] + 1
                        
                        self._log.debug("[Test:%s] Duplicate message: repeated: %s/%s" % (section_name, run_info['repeat_count'], aggregate))
                        
                        # we only repeat every 'aggregate' similar error
                        if (run_info['repeat_count'] % aggregate) != 0:
                            self._log.debug("[Test:%s] not enough repeat (%s)" % (section_name, run_info['repeat_count']))
                            post_error = False
                    else:
                        # This is a new error message or error code
                        if run_info['repeat_count'] > 0:
                            self._log.warn("[Test:%s] Flushing previous message: %s" % (section_name, process.returncode))
                            # We are about to report a new message => flush the old message
                            self._notifier.post_error(section_name, run_info['last_returncode'], run_info['last_message'], run_info['repeat_count'])
                            
                        # reset the error count
                        run_info['repeat_count'] = 0
                    
                    if post_error:
                        self._notifier.post_error(section_name, process.returncode, stdout_message, run_info['repeat_count'])
                    
                else:
                    # This is a success message
                    self._log.info("[Test:%s] result code: %s" % (section_name, process.returncode))
                    
                    # NO NEED TO RESEND LAST ERROR MESSAGE
                    #Check if the previous message had a 'repeat_count' and flush it
                    #if run_info['repeat_count'] > 0:
                    #    self._log.warn("[Test:%s] Flushing previous message: %s" % (section_name, process.returncode))
                    #    # We are about to report a new message => flush the old message
                    #    self._notifier.post_error(section_name, run_info['last_returncode'], run_info['last_message'], run_info['repeat_count'])
                    
                    # reset the repeat count
                    run_info['repeat_count'] = 0
                    
                    # Check if the last message was an error.  If yes send a "success notification"
                    if run_info['last_returncode'] != 0:
                        self._notifier.post_error(section_name, process.returncode, stdout_message, 0)


                    
                # Store the information
                run_info['last_returncode'] = process.returncode
                run_info['last_message'] = stdout_message

            else:
                self._log.error("[Test:%s] Invalid script: '%s'" %  (section_name, script))
           
            # store the run information
            run_info['last_run'] = datetime.datetime.now()
                
            self._log.debug("[Test:%s] done" % (section_name,))
            
        except ConfigParser.NoOptionError, ex:
            self._log.error("[Test:%s] Invalid configuration. %s" %  (section_name, str(ex)))
            if run_info is not None:
                run_info['last_run'] = datetime.datetime.now()
        except Exception:
            self._log.exception("[Test:%s] Exception in run_test()" % (section_name,))
        finally:
            self._log.debug("[Test:%s] completed" % (section_name, ))
                    
           
    
    def run(self):
        """ Main monitoring thread method """
        self.stop_required = False
        
        # dict that stores the last run time
        self.run_times = dict()
        
        self._log.info("run()")
        
        while not self.stop_required:
            sections = self.test_config.sections()
            for k in sections:
                self.run_test(k)
                
            time.sleep(1)
        
        self._log.info("end of thread")


if __name__ == "__main__":
    
    config_file = "config.cfg"
    
    if len(sys.argv) > 2:
        config_file = sys.argv[0]
    
    if not os.access(config_file, os.R_OK):
        print 'Error: Invalid configuration file'
        sys.exit(1)
    
    mon = Moniteur(config_file)
    mon.start()
    
    # Read command line and wait
    """ Provide an interactive 'shell' for the user """
    done = False
    try:
        while not done:
            line = sys.stdin.readline().strip()
            if line == 'q' or line == "quit" or line == "exit":
                done = True
            else:
                print line
    except KeyboardInterrupt:
        print "Ctrl-C. Exiting..."
        pass
    except Exception as e:
        print "Exception (%s). Exiting..." % (e)
    
    # stop application    
    mon.stop()
    