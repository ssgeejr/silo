'''
Created on Jul 1, 2015

@author: sgee
'''

import traceback, os, urllib2, sys, getopt
from xml.dom import minidom
from xml.dom.minidom import parse
import __version__

import posixpath, glob
import urlparse 
import subprocess

#import logging
#from configobj import ConfigObj

#logging.config.fileConfig('logging.conf')
#logger = logging.getLogger('silo')
class ContainerLoader(object):  
    artifact_xml_doc = 'maven-metadata.xml'
    
    def main(self, argv):
        self.check_arguments(argv)
        global working_dir
        global target_file
        global use_recursive
        saved_path = os.getcwd()
        print 'Original Staring Directory: ', saved_path
        try:
            if use_recursive:
                print '~~ USING RECURSIVE MODE ~~'
                print 'Seeking files under target directory: ', working_dir
                files = self.fetch_silo_files(working_dir, 'container.xml')
                print'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
                for file in files:
                    print 'container.xml files found [', os.path.dirname(os.path.abspath(file)), ']'
                print'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

                for file in files:
                    os.chdir(saved_path)
                    self.parseFile(os.path.dirname(os.path.abspath(file)), os.path.basename(file))
            else:
                self.parseFile(working_dir, target_file)
                 
        except Exception as inst:
            traceback.print_exc()
            print (inst) 
            os.chdir(saved_path)   
            sys.exit(-1)
            
        os.chdir(saved_path)
        sys.exit(0)
     #end main   
        
    def parseFile(self, config_dir, config_file):
        global enforce_global_dir
        global global_dir
        
        global enforce_global_overwrite
        global global_overwrite
        
        global enforce_global_production
        global global_production
        
        global global_artifact_server
        global global_snapshot_repo
        global global_production_repo
        
        global tag_application_version
    
        global enforce_global_purge
        global global_purge
        global enforce_global_filetype
        global global_purge_filetype    
        global test_run_only
        try: 
############################################################         
            
            word = 'Successfully'
            mystring = 'Successfully built 3d7dda3dd42b'
            if word in mystring: 
                print 'success'



            mylist = mystring.split(' ')
            print ('BUILD_ID: ' + mylist[2])
            
            
            
            sys.exit(1)
############################################################            
            
            enforce_global_dir = False
            global_dir = ''
            
            enforce_global_overwrite = False
            global_overwrite = True
            
            enforce_global_production = False
            global_production = False
            
            tag_application = ''
            tag_application_version = ''
            fixed_version = False
            allow_empty_fixed_version = False
            fixed_application_version = ''

            enforce_global_purge = False
            global_purge = False
            enforce_global_filetype = False
            global_purge_filetype = '__'
            
            enable_docker_commands = False
            docker_clean = False
            docker_euthanize = False
            docker_push = False
            docker_tag = False
            docker_host = ''           
            dockerfile_dynamic_label = False
            
            print('Moving to working directory [%s]' % config_dir)
            os.chdir(config_dir)
            print('Loading configuration file [%s]' % config_file)
            containerData = parse(config_file)
            collection = containerData.documentElement
            
            config = collection.getElementsByTagName("config")[0]
    
            tag_application = config.getElementsByTagName("application")[0].firstChild.nodeValue.strip().lower()
            if tag_application == '':
                raise ValueError("application cannot be empty")
            
            dockerfile_dynamic_label = True if config.getElementsByTagName("label")[0].firstChild.nodeValue.strip().lower() == 'true' else False
            print ('[%s] Enable Version Labeling (>Docker 1.6)' % dockerfile_dynamic_label)
           
            application_version = config.getElementsByTagName("application_version")
            if application_version.length == 1:
                    
                if application_version[0].hasAttribute('fixed'):
                    if application_version[0].getAttribute('fixed').strip().lower() == 'true':
                        fixed_version = True
                        if application_version[0].hasAttribute('empty'):
                            if application_version[0].getAttribute('empty').strip().lower() == 'true':
                                allow_empty_fixed_version = True
                                fixed_application_version = ''
                        
                        
                if fixed_version and not allow_empty_fixed_version:
                    try:
                        fixed_application_version = application_version[0].firstChild.nodeValue.strip().lower()
                        if fixed_application_version == '':
                            raise ValueError()
                    except Exception as inst:
                        raise ValueError('When the Application Version is fixed, Application Version cannot be empty or null unless empty is set to true')
            
            global_artifact_server = config.getElementsByTagName("server")[0].firstChild.nodeValue
            if not (global_artifact_server).endswith('/'):
                global_artifact_server = global_artifact_server + '/'
            
            print 'Server: ' + global_artifact_server
            repo = collection.getElementsByTagName("repostiory")[0]
            global_snapshot_repo = repo.getElementsByTagName("snapshot")[0].firstChild.nodeValue
            if not (global_snapshot_repo).endswith('/'):
                global_snapshot_repo = global_snapshot_repo + '/'
            print 'Snapshot: ' + global_snapshot_repo
            
            global_production_repo = repo.getElementsByTagName("production")[0].firstChild.nodeValue
            if not (global_production_repo).endswith('/'):
                global_production_repo = global_production_repo + '/'
            print 'Production ' + global_production_repo

            docker = config.getElementsByTagName("docker")
            if docker:
                enable_docker_commands = True
                docker_clean = True if docker[0].getElementsByTagName('clean')[0].firstChild.nodeValue.strip().lower() == 'true' else False
                docker_euthanize = True if docker[0].getElementsByTagName('euthanize')[0].firstChild.nodeValue.strip().lower() == 'true' else False
                docker_push = True if docker[0].getElementsByTagName('push')[0].firstChild.nodeValue.strip().lower() == 'true' else False
                docker_tag = True if docker[0].getElementsByTagName('tag')[0].firstChild.nodeValue.strip().lower() == 'true' else False
                if docker_tag:
                    docker_host = docker[0].getElementsByTagName('host')[0].firstChild.nodeValue.strip().lower()
                
                print ('xxxxxxxxxxXXXXXXXXXXXXXX DOCKER COMMANDS ENABLED XXXXXXXXXXXXXXxxxxxxxxxx')
                print ('[%s] CLEAN' % docker_clean)
                print ('[%s] EUTHANIZE' % docker_euthanize)
                print ('[%s] PUSH' % docker_push)
                print ('[%s] TAG' % docker_tag)
                print ('[%s] HOST' % docker_host)
                print ('xxxxxxxxxxXXXXXXXXXXXXXX DOCKER COMMANDS ENABLED XXXXXXXXXXXXXXxxxxxxxxxx')
                print ('xxxxxxxxxxXXXXXXXXXXXXXXxxxxxxxxxxxxxxxxxxxxxxxxxXXXXXXXXXXXXXXxxxxxxxxxx')
                
    #         OVERWRITE
            globals_array = config.getElementsByTagName("global")
            if globals_array:
                global_config = globals_array[0]
                overwrite_node = global_config.getElementsByTagName('overwrite')[0]
                if overwrite_node.hasAttribute('enforce'):
                    if overwrite_node.getAttribute('enforce').strip().lower() == 'true':
                        enforce_global_overwrite = True
                        if overwrite_node.firstChild.nodeValue.strip().lower() == 'false':
                            global_overwrite = False
                print ('[%s] Setting global overwrite to: %s' % (enforce_global_overwrite,global_overwrite))
        
        #           DIR 
                dir_node = global_config.getElementsByTagName('dir')[0]
                if dir_node.hasAttribute('enforce'):
                    if dir_node.getAttribute('enforce').strip().lower() == 'true':
                        enforce_global_dir = True
                        global_dir =   self.validateURI(dir_node.firstChild.nodeValue)
                print ('[%s] Setting global directory to: %s' % (enforce_global_dir,global_dir))
                 
        #            PRODUCTION       
                prod_node = global_config.getElementsByTagName('production')[0]
                if prod_node.hasAttribute('enforce'):
                    if prod_node.getAttribute('enforce').strip().lower() == 'true':
                        enforce_global_production = True
                        if prod_node.firstChild.nodeValue.strip().lower() == 'true':
                            global_production = True
                print ('[%s] Setting global production repository to: %s' % (enforce_global_production,global_production))
     
        #           PURGE 
                purge_node = global_config.getElementsByTagName('purge')[0]
                if purge_node.hasAttribute('enforce'):
                    if purge_node.getAttribute('enforce').strip().lower() == 'true':
                        enforce_global_purge = True
                        if purge_node.firstChild.nodeValue.strip().lower() == 'true':
                            global_purge = True
                print ('[%s] Enforcing global purge: %s' % (enforce_global_purge,global_purge))
                
        #            PURGE_FILETYPE       
                dir_node = global_config.getElementsByTagName('purge_filetype')[0]
                if dir_node.hasAttribute('enforce'):
                    if dir_node.getAttribute('enforce').strip().lower() == 'true':
                        enforce_global_filetype = True
                        global_purge_filetype =  dir_node.firstChild.nodeValue
                            
                print ('[%s] Enforcing global purge filetype: %s' % (enforce_global_filetype,global_purge_filetype))
                #end global_config

            artifacts = containerData.getElementsByTagName('artifacts')        
            if artifacts:
                self.parseArtifacts(artifacts[0].getElementsByTagName('artifact'))
            else:
                print('Artifacts empty, skipping')
            
            staticFiles = containerData.getElementsByTagName('files')        
            if staticFiles:
                self.parseStaticFiles(staticFiles[0].getElementsByTagName('file'))
            else:
                print('Files empty, skipping')
            
            
            if fixed_version:
                if allow_empty_fixed_version:
                    print('Using empty version value [default]')
                else:
                    print('Using fixed application version: %s' % fixed_application_version)
                    
                tag_application_version = fixed_application_version
                
                
            if tag_application_version == '':
                docker_build_tag = tag_application
            else:
                docker_build_tag =  tag_application + ':' + tag_application_version
                
            build_command = 'docker build -t ' + tag_application + ':' + tag_application_version + ' .'


            
            global test_run_only
            print ('Build Command: ' + build_command)    
            if test_run_only:
                print ('... TEST_RUN_ENABLED - SKIPPING DOCKER BUILD ...')
            else:
                if os.name != 'nt':
                    if dockerfile_dynamic_label:
                        print ('XXXXXXXXXXXXXXX FIND/REPLACE THE #LABEL IN Dockerfile XXXXXXXXXXXXXXX')
#            dockerfile_dynamic_label = False
#             enable_docker_commands
                    if enable_docker_commands:
                        print ('............. ENABLE_DOCKER_COMMANDS .............')   
                        if docker_clean:
                            print ('............. DOCKER CLEAN .............')         
                            print('docker rmi -f %s' % docker_build_tag)   
                            print('docker rm %s' % docker_build_tag)   
                        if docker_euthanize:
                            print ('............. DOCKER EUTHANIZE .............')  
                            print('docker rmi -f %s' % docker_build_tag)   
                            print('docker rm %s' % docker_build_tag)   
                        if docker_tag:
                            print ('............. DOCKER PUSH .............') 
                        if docker_push:
                            print ('............. DOCKER PUSH .............')              

                            print ('............. DOCKER HOST .............')              
                       
   
                    self.runProcess(build_command)
            
        except Exception as inst:
            traceback.print_exc()
    #        logger.error('FATAL: ' + inst.message)
    #        logger.exception(inst)
            print (inst)
            raise ValueError('Silo has encountered an unrecoverable anomaly ...')
           
    #Exit without issue
        
    #end parseFile        
    
    
    def parseArtifacts(self, artifacts):
        global enforce_global_dir
        global global_dir
        
        global enforce_global_overwrite
        global global_overwrite
        
        global enforce_global_production
        global global_production
        
        global global_artifact_server
        global global_snapshot_repo
        global global_production_repo
        
        global tag_application_version
    
        global enforce_global_purge
        global global_purge
        global enforce_global_filetype
        global global_purge_filetype            
        
        print ('********************* INITIATING ARTIFACT LOOKUP *********************')
        for artifact in artifacts:
            artifact_dir = './'
            artifact_overwrite = False
            artifact_production = False
            artifact_purge = False
            artifact_filetype = '_x_x_x_'
            artifact_repostiory = ''
            artifact_target_name = ''
            artifact_extension = 'jar'
            artifact_classifier = ''
            
            if enforce_global_dir:
                artifact_dir = global_dir
            elif artifact.hasAttribute('dir'):
                if artifact.getAttribute('dir').strip() != '':
                    artifact_dir = self.validateURI(artifact.getAttribute('dir'))
                    self.validateDir(artifact_dir)
            
            print ('Using artifact_dir: %s' % artifact_dir)
            
            if enforce_global_overwrite:
                artifact_overwrite = global_overwrite
            elif artifact.hasAttribute('overwrite'):
                if artifact.getAttribute('overwrite').strip().lower() == 'true':
                    artifact_overwrite = True
            
            print ('overwrite artifact if it exist: %s' % artifact_overwrite)
    
            if enforce_global_production:
                artifact_production = global_production
            elif artifact.hasAttribute('production'):
                if artifact.getAttribute('production').strip().lower() == 'true':
                    artifact_production = True
            
            print ('use production artifact: %s' % artifact_production)
#    
            if enforce_global_purge:
                artifact_purge = global_purge
            elif artifact.hasAttribute('purge'):
                if artifact.getAttribute('purge').strip().lower() == 'true':
                    artifact_purge = True
            print ('Enforcing file purge %s' % artifact_purge)
            
#          
            if artifact_purge:
                if enforce_global_filetype:
                    artifact_filetype = global_purge_filetype
                elif artifact.hasAttribute('filetype'):
                    artifact_filetype = artifact.getAttribute('filetype').strip()
                print ('Purge file type %s' % artifact_filetype)
                self.purgeFiles(artifact_filetype)
#   
            artifact_group = self.validateURI(artifact.getElementsByTagName("groupid")[0].firstChild.nodeValue.replace('.','/'))
            artifact_id = artifact.getElementsByTagName("artifactid")[0].firstChild.nodeValue
    
            print ('Group ID: %s' % artifact_group)
            print ('Artifact ID: %s' % artifact_id)
            
            artifact_server_node = artifact.getElementsByTagName("server")
            if artifact_server_node.length == 1:
                artifact_server = artifact_server_node[0].firstChild.nodeValue
            else:
                artifact_server = global_artifact_server
            
            print ('Artifact Server: %s' % artifact_server)
            
            if artifact.hasAttribute("target"):
                artifact_target_name = artifact.getAttribute("target").strip()
                if (artifact_target_name)=='':
                    print '****** TARGET EMPTY :: RESETTING ***********'
                    artifact_target_name = ''
    
            #design question: should you be able to over ride the repository ... I would think so
            #simply because what if only one file changes
            #but if you did that, you would need to provide both snapshot and production
            
            artifact_repostiory_node = artifact.getElementsByTagName("repostiory")
            if artifact_repostiory_node.length == 1:
                artifact_repostiory = artifact_repostiory_node[0].firstChild.nodeValue
            elif artifact_production:
                artifact_repostiory = global_production_repo
            else:
                artifact_repostiory = global_snapshot_repo
            
            print ('Artifact Repository: %s' % artifact_repostiory)
                    
            artifact_url = self.validateURI(artifact_server) + self.validateURI(artifact_repostiory) + self.validateURI(artifact_group) + self.validateURI(artifact_id)
                    
            print ('Artifact URL: %s' % artifact_url) 
            
            artifact_classifier_node = artifact.getElementsByTagName("classifier")
            if artifact_classifier_node.length == 1:
                artifact_classifier = artifact_classifier_node[0].firstChild.nodeValue
            
            artifact_extension_node = artifact.getElementsByTagName("extension")
            if artifact_extension_node.length == 1:
                artifact_extension = artifact_extension_node[0].firstChild.nodeValue
            
            
            print ('artifact_extension: %s' % artifact_extension)
            print ('artifact_classifier: %s' % artifact_classifier)
    #         artifact_extension = 'jar'
    #         artifact_classifier = None
    
            
            self.extractArtifactDetails(artifact_id, artifact_dir, artifact_target_name, artifact_overwrite, artifact_production, artifact_extension, artifact_classifier, artifact_url)
            print 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
            
            
    #end parseArtifact
    
    def extractArtifactDetails(self, artifact_id, file_dir, target_name, clobber, release, extension_type, classifier, url):
    #     artifact_xml_doc
        versionXML = urllib2.urlopen(url + self.artifact_xml_doc)
        versionDOC = minidom.parse(versionXML)
    #     container_version_tag = 'EMPTY'
        
        if release:
            artifactVersion = versionDOC.getElementsByTagName('release')[0].firstChild.nodeValue
            container_version_tag = artifactVersion
            buildNumber = ''
            print ('VERSION: %s'  % container_version_tag)
            artifact_filename = artifact_id + '-' + artifactVersion + '.jar'
            latest_build_url = url + self.validateURI(artifactVersion) + artifact_filename
        else:
            artifactVersion=versionDOC.getElementsByTagName('latest')[0].firstChild.nodeValue
             
            print ('Version: %s'  % artifactVersion)
           
            latestBuild=artifactVersion.split("-")[0]  
            latest_build_url = url + self.validateURI(artifactVersion)
            latestXML = urllib2.urlopen(latest_build_url + self.artifact_xml_doc)
            latestDOC = minidom.parse(latestXML)
            buildNumber=latestDOC.getElementsByTagName('buildNumber')[0].firstChild.nodeValue
            
            snapshots = latestDOC.getElementsByTagName('snapshotVersion')
            
            print('**************************************************************************************************************')
            
            print ('Seeking extension_type: %s' % extension_type)
            print ('Seeking classifier: %s' % classifier)
            
            for version in snapshots:
                if classifier != '':
                    print ('1')
                    extension = version.getElementsByTagName('extension')
                    source_classifier = version.getElementsByTagName('classifier')
                    
                    
                    if extension.length == 1 and source_classifier.length == 1:
                        print ('2')
                        
                        
                        if (extension[0].firstChild.nodeValue == extension_type and
                            source_classifier[0].firstChild.nodeValue == classifier) :
                            print ('3')
                            artifact_file_detail = version.getElementsByTagName('value')[0].firstChild.nodeValue + "-" + classifier
                            print 'extension: ' + artifact_file_detail
                            print 'classifier: ' + classifier
                            artifact_filename = artifact_id + '-' + artifact_file_detail + '.' + extension_type
                            
                else:
                    extension = version.getElementsByTagName('extension')
                    if extension.length == 1:
                        if version.getElementsByTagName('extension')[0].firstChild.nodeValue == extension_type:
                            artifact_file_detail = version.getElementsByTagName('value')[0].firstChild.nodeValue
                            print 'extension: ' + artifact_file_detail
                            artifact_filename = artifact_id + '-' + artifact_file_detail + '.' + extension_type
                
                
                
            print('**************************************************************************************************************')
            latest_build_url = url + self.validateURI(artifactVersion) + artifact_filename                
                
            print 'Jar File URL: ' + latest_build_url
            
            if buildNumber == '':
                buildNumber = 'UNKN'
                
            container_version_tag = latestBuild + '-' + buildNumber
    #         if container_version_tag == '-':
    #             container_version_tag = 'UNKN'
            
            #### WARNING ####
            #### NEED TO ADD LABEL INFORMATION ... 
            
        print ('Tagging Container as: %s' % container_version_tag)
        
        if len(target_name) > 0:
            artifact_filename = target_name
               
        final_filename = file_dir + artifact_filename
        
        print 'Final file location is: ' + final_filename
        print 'clobber: ' + str(clobber)
        print 'File Exist: ' +  str(os.path.isfile(final_filename))
        
        global tag_application_version
        tag_application_version = container_version_tag
        
        if os.path.isfile(final_filename) and not clobber:
            print 'File exist, Overwrite set to False - skipping download'
            print '[RETURN] tag_application_version: ' + tag_application_version
            return None
        #end if
        
    #     print '[2] tag_application_version: ' + tag_application_version
        self.downloadFile(latest_build_url,final_filename) 
    #     print 'RETURNING CONTAINER VERSION TAG: ' + tag_application_version   
            
    #end extractArtifactDetails
    def parseStaticFiles(self, staticFiles):
            global enforce_global_dir
            global global_dir
            
            global enforce_global_overwrite
            global global_overwrite
            
            global enforce_global_production
            global global_production
            
            global global_artifact_server
            global global_snapshot_repo
            global global_production_repo
            
            global tag_application_version
        
            global enforce_global_purge
            global global_purge
            global enforce_global_filetype
            global global_purge_filetype    
                    
            
            print ('********************* INITIATING FILE LOOKUP *********************')
            for staticFile in staticFiles:
                target_dir = './'
                file_overwrite = False
                output_filename = ''
                file_purge = False
                purge_filetype = '_x_x_x_'
                
                print ('--------------------------------------------')
                file_source = staticFile.getAttribute("source")
                
                path = urlparse.urlsplit(file_source).path
                output_filename = posixpath.basename(path)
                
                if enforce_global_overwrite:
                    file_overwrite = global_overwrite
                elif staticFile.hasAttribute('overwrite'):
                    if staticFile.getAttribute('overwrite').strip().lower() == 'true':
                        file_overwrite = True
                 
                if enforce_global_dir:
                    target_dir = global_dir
                elif staticFile.hasAttribute('dir'):
                    if staticFile.getAttribute('dir').strip() != '':
                        target_dir = self.validateURI(staticFile.getAttribute('dir'))
                        self.validateDir(target_dir)
                
#    
                if enforce_global_purge:
                    file_purge = global_purge
                elif staticFile.hasAttribute('purge'):
                    if staticFile.getAttribute('purge').strip().lower() == 'true':
                        file_purge = True
                print ('Enforcing file purge %s' % file_purge)
                
#          
                if file_purge:
                    if enforce_global_filetype:
                        purge_filetype = global_purge_filetype
                    elif staticFile.hasAttribute('filetype'):
                        purge_filetype = staticFile.getAttribute('filetype').strip()
                    print ('Purge file type %s' % purge_filetype)
                    self.purgeFiles(purge_filetype)

                if staticFile.hasAttribute("target"):
                    if staticFile.getAttribute("target").strip() != '':
                        print '****** TARGET FOUND / NOT EMPTY ***********'
                        output_filename = staticFile.getAttribute("target").strip()
            
                output_file = target_dir + output_filename
                print ('URL: %s' % file_source)
                print ('Output File: %s' % output_file)
                print ('Overwrite: %s' % file_overwrite)
                
                if os.path.isfile(output_file) and not file_overwrite:
                    print 'File exist, Overwrite set to False - skipping download'
                    return None
                #end if
                self.downloadFile(file_source, output_file)
                
    #end parseStaticFiles
    def purgeFiles(self, extension):
            global test_run_only
            
            if test_run_only:
                print ('... TEST_RUN_ENABLED - NO FILES WILL BE DELETED ... ')
                return
            else:
                filelist = glob.glob('*.' + extension)
                for purge_file in filelist:
                    print('>>>>>>>>>>>>>> DELETING >>>>>>>>>>>>>>>> %s'  % purge_file)
                    os.remove(purge_file)
        
    def runProcess(self, system_command):  
        print('running process: %s' % system_command)  
        p = subprocess.Popen([system_command], shell=True, stderr=subprocess.PIPE)
        while True:
            out = p.stderr.read(1)
            if out == '' and p.poll() != None:
                break
            if out != '':
                sys.stdout.write(out)
                sys.stdout.flush()
    #end runProcess
    
    def downloadFile(self, url, filename):
            global test_run_only
            
            if test_run_only:
                print ('... TEST_RUN_ENABLED - NO FILES WILL BE DOWNLOAD ... ')
                return
            else:
                print ('Initiating download ...')
                remoteFile = urllib2.urlopen(url)
                output = open(filename,'wb')
                output.write(remoteFile.read())
                output.close()
    #end downloadFile    
    
    def validateDir(self, tgt_dir):
        if not os.path.exists(tgt_dir):
            os.makedirs(tgt_dir) 
    #end validateDir
    
    def validateURI(self, uri):
        if not (uri).endswith('/'):
            uri = uri + '/'
        return uri
    
    def fetch_silo_dirs(self, rootdir='./', target=''):
        return [looproot
                for looproot, _, filenames in os.walk(rootdir)
                for filename in filenames if filename == target]
    #end fetch_silo_dir
     
    def fetch_silo_files(self, rootdir='./', target=''):
        return [os.path.join(looproot, filename)
                for looproot, _, filenames in os.walk(rootdir)
                for filename in filenames if filename == target]
    #end fetch_silo_files

    def check_arguments(self, argv):
        global working_dir
        global target_file
        global use_recursive
        global test_run_only
        working_dir = os.path.abspath('./')
        target_file = 'container.xml'
        test_run_only = False
        
        options, args = getopt.getopt(argv, 'rvtf:', ['file','version',])
        use_recursive = False
        
        for opt, arg in options:
            if opt in ('-f', '--file'):
                user_file = arg
                print 'Using user provided file: ', os.path.isfile(user_file)
                if os.path.isfile(user_file):
                    working_dir = os.path.dirname(user_file)
                    target_file = os.path.basename(user_file)
                else:
                    working_dir = os.path.abspath(user_file)
            elif opt == '-r':
                use_recursive = True
            elif opt == '-t':
                test_run_only = True
            elif opt in ('-v', '--verbose'):                
                print '\tSilo Docker dynamic file pre-loader, Version ', __version__.__version__
                sys.exit(0)
       
#         sys.exit(1)
                         
    #end check_arguments
        
