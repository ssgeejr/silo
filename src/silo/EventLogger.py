'''
Created on Aug 31, 2015

@author: sgee
'''
import logging,sys,os

class SiloResults:
    def __init__(self, version=''):
        logDir = os.path.expanduser('~/silo')
        if not os.path.exists(logDir):  os.makedirs(logDir)

# Loggers 
        logger = logging.getLogger('results')
        logger.setLevel(logging.DEBUG)        
        errorLogger = logging.getLogger('err-results')
        errorLogger.setLevel(logging.ERROR)
      
# Formatter  
        formatter = logging.Formatter('%(asctime)s [%(name)s][%(levelname)s] %(message)s')

# Stream (command line) Handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        
# File Handler
        fh = logging.FileHandler(os.path.join(logDir, 'silo.results' + version + '.log'),mode='w')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        efh = logging.FileHandler(os.path.join(logDir, 'silo.results' + version + '.err.log'),mode='w')
        efh.setLevel(logging.ERROR)
        efh.setFormatter(formatter)

# Add handlers 
        logger.addHandler(ch)
        logger.addHandler(fh)
        errorLogger.addHandler(efh)

# self-loggers
        self.logger = logger.debug
        self.errLogger = errorLogger.error
        
# -------------------------------------------------------------------------------
     
    def log(self, msg):
        self.logger(msg)

    def error(self, err):
        self.errLogger(err, exc_info=True)
       
    