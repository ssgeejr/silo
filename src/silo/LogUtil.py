'''
Created on Aug 31, 2015

@author: sgee
'''
import logging,sys,os

class StandardLogWriter:
    def __init__(self):
        logger = logging.getLogger('silo')
        logDir = os.path.expanduser('~/silo')
        if not os.path.exists(logDir):  os.makedirs(logDir)
        logger.setLevel(logging.INFO)        
        formatter = logging.Formatter('%(asctime)s [%(name)s][%(levelname)s] %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        fh = logging.FileHandler(os.path.join(logDir, 'silo.log'))
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        self.logger = logger
        
    def write(self, message):
        if message != '\n':
            self.logger.info(message)
#         if len(message) == 1:
#             new_list = []
#             convertedVal = message.encode("hex")
#             convertedVal.strip()
#             for i in convertedVal:
#                 new_list = ord(i)
#             self.logger.info("Ascii value: " + str(new_list) + " ** Hex value: " + str(convertedVal))
#             
#         else:
#             self.logger.info('newline found')

    def flush(self):
        self.logger.info(sys.stderr)
        
        
        
class ErrorLogWriter:
    def __init__(self):
        logger = logging.getLogger('siloERR')
        logDir = os.path.expanduser('~/silo')
        if not os.path.exists(logDir):  os.makedirs(logDir)
        logger.setLevel(logging.INFO)        
        formatter = logging.Formatter('%(asctime)s [%(name)s][%(levelname)s] %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        fhe = logging.FileHandler(os.path.join(logDir, 'silo.err.log'))
        fhe.setLevel(logging.ERROR)
        fhe.setFormatter(formatter)
        logger.addHandler(fhe)
        self.logger = logger

    def write(self, message):
        if message != '\n':
            self.logger.error(message)

    def flush(self):
        self.logger.error(sys.stderr)