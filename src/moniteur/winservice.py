'''
Created on Mar 5, 2010

@author: Random Internet people
@author: Boyd Ebsworthy
'''
import sys
import time
import win32service
import win32serviceutil
import logging
from application import Moniteur
            
class winservice(win32serviceutil.ServiceFramework):
    """
    The windows service that handles stopping and starting the service
    """
    _svc_name_ = "MoniteurSvc"
    _svc_display_name_ = "Moniteur Service"

    def __init__(self,args):
        self._log = logging.getLogger("service")
        self._log.debug("%s - Init" % self._svc_name_)
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.isAlive = True

    def SvcDoRun(self):
        import servicemanager
        
        self._log.info("%s - Starting" % self._svc_name_)
        servicemanager.LogInfoMsg("%s - Starting" % self._svc_name_)
        try:
            # Config file name is hardcoded
            config_file = "config.cfg"
    
            # Try to find the configuration file looking up
            # from the script file
            # It's a messy kludge but I couldn't find better
            import os.path
            path = os.path.abspath(os.path.dirname(__file__))
           
            last_path = path
            self._log.info("%s - Searching for config in (%s)" % (self._svc_name_, last_path))
            while not os.access(path + "/" + config_file, os.R_OK):
                (path, _) = os.path.split(path)
                if path == last_path:
                    last_path = None
                    print "Not found aborting"
                    break
                last_path = path
                self._log.info("%s - Searching for config in (%s)" % (self._svc_name_, last_path))
                
            if last_path == None:
                self._log.error("%s - Unable to locate configuration file (%s)" % (self._svc_name_, config_file))
                servicemanager.LogErrorMsg("%s - Unable to locate configuration file (%s)" % (self._svc_name_, config_file))
                return
            
            # Change working directory
            os.chdir(last_path)
            
            # init python logging (Anything logged before that had been lost)
            logging.config.fileConfig(config_file)
            self._log.info("%s - Changing working directory to (%s)" % (self._svc_name_, last_path))
            
            # Start
            self._log.info("%s - Starting Moniteur" % self._svc_name_)
            self.application = Moniteur(config_file)
            self.application.start()
            
            self._log.info("%s - Started" % self._svc_name_)
            servicemanager.LogInfoMsg("%s - Started" % self._svc_name_)
            
            while self.isAlive:
                time.sleep(5)
            
            self._log.info("%s - Stopping" % self._svc_name_)
            servicemanager.LogInfoMsg("%s - Stopping" % self._svc_name_)
        except:
            pass
        
    def SvcStop(self):
        try:
            import servicemanager
            self._log.info("%s - Received stop signal" % self._svc_name_)
            servicemanager.LogInfoMsg("%s - Received stop signal" % self._svc_name_)
            
            self.application.stop()
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            
        except:
            pass
        self.isAlive = False
        
if __name__ == '__main__':
    
    win32serviceutil.HandleCommandLine(winservice) # this line sets it all up to run properly.