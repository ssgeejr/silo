'''
Created on Mar 24, 2016

@author: sgee
'''
from xml.dom import minidom
from xml.dom.minidom import parse, parseString
import sys, requests, json, re, traceback, datetime, os
import subprocess

class Dependency(object):
    '''
    classdocs
    '''

    def main(self):
        
        os.chdir('C:/development/tmp/iris-deployment/docker')
        working_dir = os.getcwd()
        file_name = 'container.xml'
        print ('working_dir [%s]' % working_dir)
        os.path.dirname
        
        allSiloContainers = []
        
        for looproot, bingbong, filenames in os.walk(working_dir):
            for filename in filenames:
                if filename == 'container.xml':
#                     print ('looproot: %s' % looproot)
                    allSiloContainers.append(looproot)
                    
        for dockerfile in allSiloContainers:
            print dockerfile
            os.chdir(dockerfile) 
            p = subprocess.Popen('head Dockerfile | grep FROM',
                                              shell=True,
                                              bufsize=0,  # 0=unbuffered, 1=line-buffered, else buffer-size
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE)
            change_results = []
            while True:
                    line = p.stdout.readline()
                    if not line: break
                    change_results.append(line.strip())
                    print line.strip()
            
            while True:
                    line = p.stderr.readline()
                    if not line: break
                    print line.strip()
            
            
            
#         mellow = [os.path.join(looproot, filename)
#                 for looproot, _, filenames in os.walk(working_dir)
#                 
#                 for filename in filenames if filename == 'container.xml']
#         
#         for mel in mellow:
#             print mel
# 
#         pavs = [os.path.join(working_dir,fn) for fn in next(os.walk(working_dir))[2]]
#         for mel in pavs:
#             print mel




















    def NOPE_checkDeps(self, argv):
        os.chdir('C:/development/tmp/iris-deployment/docker')
        working_dir = os.getcwd()
        print ('working_dir [%s]' % working_dir)
        dependency_exist = os.path.isfile('dependency.xml')
        print ('Dependency File Exist [%s]' % dependency_exist)
        if not dependency_exist:  return
        
        containerData = parse('dependency.xml')
        collection = containerData.documentElement
        dependencies = collection.getElementsByTagName("dependencies")[0]
        containers = dependencies.getElementsByTagName('image')
        print('Found [%s] images that have dependencies' % len(containers))
        for container in containers:
            print('Name [%s] Dependency [%s] Public [%s] Location [%s]' % (
                container.getAttribute('name').strip(),
                container.getAttribute('dependency').strip(),
                container.getAttribute('public').strip().lower(),
                container.getAttribute('location').strip()))
            
            if container.getAttribute('public').strip().lower() == 'true':
                print('need to pull from remote repo ... ')
            else:
                print('Execute Silo command on this directory [%s]' % container.getAttribute('location').strip())
                
            try:
                pass
                
                
            except Exception, err:
                print('Error processing container [%s]: %s' % err)
                
if __name__ == '__main__':
#     Example().run()#     deputyDawg = Dependency() 
    Dependency().main()