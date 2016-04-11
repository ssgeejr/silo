'''
Created on Jul 1, 2015
@author: sgee
'''

import traceback, os, urllib2, sys, getopt
from xml.dom import minidom
from xml.dom.minidom import parse
from xml.etree import ElementTree as validator
import __version__
# from configobj import ConfigObj
import posixpath, glob, json
import urlparse
import subprocess
import getpass
from Lockers import Container
from Lockers import Artifact
from datetime import datetime
# import LogUtil
import EventLogger
from collections import OrderedDict

class ContainerLoader(object):
    artifact_xml_doc = 'maven-metadata.xml'
    def main(self, argv):
#         sys.stdout = LogUtil.StandardLogWriter()
#         sys.stderr = LogUtil.ErrorLogWriter()
        self.STANDARD = 0
        self.SEEK_FILES_UPDATE_DB = 1
        self.DB_DOWNLOAD_FROM_DICT = 2
        self.build_container = {}

        self.STATE_RUNNING = 2
        self.STATE_SUCCESS = 3
        self.STATE_FAILED = 4
        self.VALIDATING = 5
        self.VALID = 6
        self.INVALID = 7

        self.check_arguments(argv)
        global enable_logging
        global target_file
        global use_recursive
        global dataMgr
        global BUILD_ID
        global CONTAINER_ID
        global USE_DB
        global skip_builds
        global skip_list
        global search_only
        global validate_only
        global debug_exceptions
        global master_start_time
        global total_container_count
        global total_success
        global total_fail
        global resultsLogger
        global failed_state
        global set_pip_index
        global pip_index_url
        global set_pip_host
        global pip_trusted_host
        json_dependencies = []                
        dep_images = []
        build_images = []
        
        if USE_DB and (not validate_only):
            from dataManager import dataManager

        failed_state = False
        if override_tag_version_val != '':
            resultsLogger = EventLogger.SiloResults(override_tag_version_val)
        else:
            resultsLogger = EventLogger.SiloResults(prod_profile_version)

        total_container_count = 0
        total_success = 0
        total_fail = 0
        saved_path = os.getcwd()
        resultsLogger.log('^-------- STARTING BUILD CYCLE -------------^')
        print ('Original Staring Directory: %s' % saved_path)
        master_start_time=datetime.now()
#         x.update({3:4})
        try:

            if set_pip_index:
                resultsLogger.log('Setting PIP_INDEX_URL to [%s]' % pip_index_url)
                os.environ["PIP_INDEX_URL"] = pip_index_url
            if set_pip_host:
                resultsLogger.log('Setting PIP_TRUSTED_HOST to [%s]' % pip_trusted_host)
                os.environ["PIP_TRUSTED_HOST"] = pip_trusted_host

#             USE_DB = True
            BUILD_ID = 0
            CONTAINER_ID = 0

#             will consider not writing to the DB on --verify
#             verify_valid_url
            if verify_valid_url: USE_DB = False
            if(USE_DB and (not validate_only)):
                dataMgr = dataManager()
                BUILD_ID = dataMgr.createNewBuild(argv, getpass.getuser())
                print ('XXX===>>  BUILD_ID: %s' % (BUILD_ID))
            
            
            if use_recursive or only_updates:
                print ('Seeking files under target directory: %s' % working_dir)
                files = []
                if (use_recursive):
                    print ('~~ USING RECURSIVE MODE ~~')
                    
                    if os.name == 'nt':
                        files = self.fetch_silo_files('C:/development/tmp/iris-deployment/docker', 'container.xml')
                    else:
                        files = self.fetch_silo_files(working_dir, 'container.xml')
                    
                else:
                    print ('~~ BUILDING ONLY CONTAINERS WITH UPDATES ~~')
                    os.chdir(working_dir)
                    git_diff = ['git', 'diff', '--name-only', '--stat', 'origin/master', 'HEAD']
                    lines = self.fetchGitChanges(git_diff)                    
                    build_contianers = []
                    for line in lines:
                        print(' >>> UPDATED_OBJECT: %s' % line)
                        
                        if line:
                            updated_file = ('%s%s%s' %(working_dir,os.path.sep,line))
                            print(' >>> FULL_PATH: %s' % updated_file)
                            change_dir = os.path.dirname(os.path.abspath(updated_file))
                            print(' >>> UPDATED_OBJECT_ROOT_DIR: %s' % change_dir)
                            container_xml = ('%s%scontainer.xml' % (change_dir,os.path.sep))
                            print(' >>> CONTAINER_XML_LOCATION: %s' % container_xml)
                            print('Searching for silo configuration [%s]' % container_xml)
                            if os.path.exists(container_xml):
                                print('[1] Adding change directory to build queue ... [%s]' % updated_file)
#                                 build_contianers.append(updated_file)
                                build_contianers.append(change_dir)
                            else:
                                print('Skipping directory [%s]' % change_dir)
                                print('Reason: silo configuration not found [%s]' % container_xml)
                    print('..................................................')
#                     unique_build_dir = set(build_contianers)
                    unique_build_dir = list(OrderedDict.fromkeys(build_contianers))
                    if len(unique_build_dir) > 0:
#                         print('Building %s container(s) ...' % len(uniqu_build_dir))
                        for build_dir in unique_build_dir:
#                             print('Found silo container.xml file, building [%s]' % build_dir)
#                             os.chdir(build_dir)
#                             command_set = ['silo', '--nopush']
#                             executeSystemCommand(command_set, use_shell)
                            container_dir = ('%s%scontainer.xml' % (build_dir,os.path.sep))
                            print('[2] Adding verified change directory to build queue ... [%s]' % build_dir)
                            files.append(container_dir)
                    else:
                        print(' NOTHING NEW TO BUILD ... EXITING ... ')
                        sys.exit(0)
                        
                if skip_builds:
                    print(' XX************** SKIPPING DEFINED BUILDS **************XX')
                    print ('SKIPPING CONTAINERS: %s' % (skip_list))
                print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')

                file_to_be_skipped = []
#                 for x in range(0, 3):
                
                for fileHandler in files:
                    container_name = os.path.basename(os.path.dirname(os.path.abspath(fileHandler)))
                    container_home = os.path.dirname(os.path.abspath(fileHandler))
                    print ('container_name: %s' % container_name)
                    
                    if container_name in skip_list:
                        file_to_be_skipped.append(fileHandler)
                    else:
                        print 'Build directory identified [' + container_home + ']'
                        if USE_DB and (not validate_only):
                            CONTAINER_ID = dataMgr.storeContainerData(BUILD_ID, os.path.dirname(os.path.abspath(fileHandler)), os.path.basename(fileHandler))
                        else:
                            CONTAINER_ID += 1

                        cntr = Container(BUILD_ID, CONTAINER_ID, container_name, argv, os.path.dirname(os.path.abspath(fileHandler)), os.path.basename(fileHandler))
                        self.build_container.update({container_name:cntr})

                        os.chdir(container_home)
#                         print ('FROM: %s' %))
#                         from_line = 'FROM java:7-jre'
#                         from_line = 
                        biscuits = self.fetchDependency().split(' ')
                        image_name = self.fetchImageName()
                        
                        build_images.append(image_name)
                        dep_images.append(biscuits[1].strip())
#                         for biscuit in biscuits:
#                             print biscuit
                        json_dependencies.append(
                                {
                                    'image': image_name,
                                    'directory': container_home,
                                    'container_name': container_name,
                                    'depends_on': biscuits[1].strip()
                                }
                        )
                        
                        os.chdir(saved_path)
                try:                   
                    for obj in json_dependencies:
                        print ('Container_Name [%s]' % obj.get('container_name'))

                    unique_dep_images = list(set(dep_images))
                    for dep in unique_dep_images:                        
                        print ('Dependency Image [%s]' % dep)
                        
                    
                    print('Checking dependency images for changes. If found, the child containers will be rebuilt because We can rebuild them. We have the technology. We can make them better than it was. Better...stronger...faster. We can create The Six-Million-Dollar image')
                    for dep in unique_dep_images:                        
                        print ('Dependency Image is in build list [%s] [%s]' % (dep, (dep in build_images)))
#                         if len(self.imageExist(dep)) == 12:
                        if self.imageExist(dep):
                            print('Image exist, rebuilding/pulling not required')
                   
#                     apt-get install docker-engine
                               
#                     print json.dumps(json_dependencies, sort_keys=True, indent=4, separators=(',', ': '))
                    
                except Exception, err:
                    print err
                    traceback.print_exc()
                
                sys.exit(1)
                
                if len(self.build_container) > 0:        
                    print('***** Building %s container(s) ... *****' % len(self.build_container))
                else:
                    print('NOTHING TO BUILD ... EXITING ... ')
                    sys.exit(0)
                print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX SKIPPED FILES XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
                for skipped in file_to_be_skipped:
                    print (   'Skipping build for [%s]' % (skipped))
                print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
                if search_only:
                    sys.exit(0)
            else:
                if USE_DB and (not validate_only):
                    CONTAINER_ID = dataMgr.storeContainerData(BUILD_ID, os.path.abspath(working_dir), target_file)

                container_name = os.path.basename(os.path.dirname(os.path.abspath(os.path.join(working_dir, target_file))))
                print('containerName: ' + container_name)
                cntr = Container(BUILD_ID, CONTAINER_ID, container_name,  argv, os.path.abspath(working_dir), target_file)
                self.build_container.update({container_name:cntr})

#             validate_only = True
            validation_errors = []
            if validate_only:
                print('********************************* VALIDATION ONLY *********************************')

            total_container_count = len(self.build_container)
            for item in self.build_container.values():
                try:
                    if validate_only:
                        try:
                            filepath = os.path.join(item.workingDir, item.fileName)
                            validator.parse(filepath)
                        except Exception as invalid:
                            validation_errors.append('Invalid File Format for: %s  Error: %s' % (filepath, invalid))
                    else:
                        print ('XXX===>>  BUILD_ID: %s' % (item.buildID))
                        print ('XXX===>>  CONTAINER_ID: %s' % item.containerID)
                        print ('XXX===>> WORKING_DIR %s' % (item.workingDir))
                        print ('XXX===>> BUILD_FILE %s' % ( item.fileName))
                        print ('***** Still need to insert into the database the contents of the two builds files *****')
                except Exception, err:
                    resultsLogger.log('Error processing container [%s]: %s' % (item.containerName, err))
                    if(debug_exceptions):
                        traceback.print_exc()
                        resultsLogger.error(err)
            #end FOR USE_DB and (not validate_only)
            if validate_only:
                print ('Validation complete: %s passed, %s failed' % ((len(self.build_container) - len(validation_errors)), len(validation_errors)))
                print ('********************************* FAILED DETAILS *********************************')
                for err in validation_errors:
                    print ('\t %s' % err)
            else:
                
#         json_dependencies = []                
#         dep_images = []
#         build_images = []
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                active_container = ''
                if USE_DB:
#                     total_container_count
#         global total_success
#         global total_fail
                    current_runtime = (datetime.now() - master_start_time)
                    dataMgr.updateBuild(BUILD_ID, self.STATE_RUNNING, total_container_count, total_success, total_fail, None, str(current_runtime))

                    for item in self.build_container.values():
                        try:
                            active_container = item.containerName
                            self.parseFile(item, self.SEEK_FILES_UPDATE_DB)
                        except Exception, err:
                            resultsLogger.log('Error attempting to load DB Files/Artifacts [%s]: %s' % (active_container, err))
                            if(debug_exceptions):
                                traceback.print_exc()
                                resultsLogger.error(err)
                    print('=========================================================================================')
                    print('----- NOW WE ACTUALLY PULL THE FILES AND BUILD THE CONTAINERS ------')
                    print('=========================================================================================')
                    for item in self.build_container.values():
                        try:
                            active_container = item.containerName
                            self.parseFile(item, self.DB_DOWNLOAD_FROM_DICT)
                        except Exception, err:
                            resultsLogger.log('Error attempting to Download files [%s]: %s' % (active_container, err))
                            if(debug_exceptions):
                                traceback.print_exc()
                                resultsLogger.error(err)

                else:
                    for item in self.build_container.values():
                        try:
                            active_container = item.containerName
                            self.parseFile(item)
                        except Exception, err:
                            resultsLogger.log('Error running Silo in Standard Mode [%s]: %s' % (active_container, err))
                            if(debug_exceptions):
                                traceback.print_exc()
                                resultsLogger.error(err)

                if True == False:
                    import time
                    debug_exceptions = True
                    for item in self.build_container.values():
                        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
                        xc_start = datetime.now()
                        try:
                            print('=========================================================================================')
                            active_container = item.containerName
                            print ('active_container [%s]' % active_container)
                            dataMgr.updateContainerState(self.STATE_RUNNING, item, xc_start)
                            print ('Container: %s' % active_container)
                            artifacts = item.getArtifact()
                            for key in artifacts.values():
                                print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
                                print ('key.artifact_id [%s]' % key.artifact_id)
                                print ('key.group_id [%s]' % key.group_id)
                                print ('key.url [%s]' % key.url)
                                print ('key.file_name [%s]' % key.file_name)
                                print ('item.workingDir [%s]' % item.workingDir)
#  DSA
                                artRuntime=datetime.now()
                                dataMgr.updateArtifactState(self.STATE_RUNNING,key,artRuntime )
                                time.sleep(5)
                                x_stop_time=datetime.now()
                                x_runtime = (x_stop_time - artRuntime)
                                dataMgr.updateArtifactState(self.STATE_SUCCESS,key,x_stop_time, x_runtime)
                                print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
                            print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
                            c_stop_time=datetime.now()
                            c_runtime = (c_stop_time - xc_start)

                            dataMgr.updateContainerState(self.STATE_SUCCESS, item, c_stop_time, c_runtime)
                            print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
                            print('=========================================================================================')

                        except Exception, err:
                            resultsLogger.log('Error attempting to load DB Files/Artifacts [%s]: %s' % (active_container, err))
                            if(debug_exceptions):
                                traceback.print_exc()
                                resultsLogger.error(err)

                    #end if True == False

        except Exception, err:
            resultsLogger.log('Unrecoverable Exception: %s' % (err))
            resultsLogger.error('Unrecoverable Exception: %s' % (err))
            if(debug_exceptions):
                traceback.print_exc()
            os.chdir(saved_path)

        master_stop_time=datetime.now()
        total_runtime = (master_stop_time - master_start_time)
        resultsLogger.log("Total Runtime [%s]" % total_runtime)
        print ("Total Runtime [%s]" % total_runtime)
        if USE_DB and (not validate_only):
            dataMgr = dataManager()
            dataMgr.updateBuild(BUILD_ID, self.STATE_SUCCESS if total_fail == 0 else self.STATE_FAILED, total_container_count, total_success, total_fail, master_stop_time, str(total_runtime))

        os.chdir(saved_path)
        sys.exit(total_fail)
#end main

#     def parseFile(self, arguments, config_dir, config_file):
    def parseFile(self, folio, magic_level=0):

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

        global use_prod_profile
        global prod_profile_version
        global use_alt_profile
        global alt_profile_name
        global use_alt_server
        global alt_server_url
        global authenticate_download
        global dataMgr
        global BUILD_ID
        global CONTAINER_ID
        global ARTIFACT_ID
        global override_docker_tag
        global override_docker_tag_val
        global override_docker_push
        global override_docker_push_val
        global override_docker_overwrite
        global override_docker_overwrite_val
        global override_registry
        global override_registry_url
        global skip_downloads
        global skip_container_build
        global CURRENT_CONTAINER
        global force_tag_overwrite
        global override_tag_version
        global override_tag_version_val
        global override_purge
        global override_purge_val
        global override_purge_type
        global override_prod_server
        global override_prod_server_url
        global verify_valid_url

        global master_start_time
        global total_container_count
        global total_success
        global total_fail
        global CLASS_MAGIC_LEVEL
        global failed_state
        global is_beta_build
        global USE_DB
        global is_beta_build
        global tag_latest
        global dirty_run
        global use_build_arg
        
        container_exit_status = True
        container_start_time=datetime.now()
        container_err_message = ''
        CLASS_MAGIC_LEVEL = magic_level

        if USE_DB:
            dataMgr.updateContainerState(self.STATE_RUNNING, folio, container_start_time)

        try:
            enforce_global_dir = False
            global_dir = ''

            enforce_global_overwrite = False
            global_overwrite = True

#             enforce_global_production = False
#             global_production = False

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

            authenticate_download = False
            CURRENT_CONTAINER = folio.containerName
            resultsLogger.log('^^^^^^^^^^ [%s] Initiating Silo File Management || Magic_Level [%s] ^^^^^^^^^^' % (CURRENT_CONTAINER, magic_level))
#             sys.exit(1)
            print('Moving to working directory [%s]' % folio.workingDir)
            os.chdir(folio.workingDir)

            print('Loading configuration file [%s]' % folio.fileName)
            containerData = parse(folio.fileName)
            collection = containerData.documentElement

            config = collection.getElementsByTagName("config")[0]

            tag_application = str(config.getElementsByTagName("application")[0].firstChild.nodeValue.strip().lower())
            tag_application = tag_application.translate(None, " ?.!;\:*")

            if tag_application == '':
                raise ValueError("application cannot be empty")

            dockerfile_dynamic_label = False
            docker_label = config.getElementsByTagName("label")

            if docker_label.length == 1:
                dockerfile_dynamic_label = True if docker_label[0].firstChild.nodeValue.strip().lower() == 'true' else False

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
                    except Exception,err:
                        raise ValueError('When the Application Version is fixed, Application Version cannot be empty or null unless empty is set to true')

            server_names = config.getElementsByTagName("server")
            if server_names and server_names.length == 1:
                global_artifact_server = server_names[0].getElementsByTagName("default")[0].firstChild.nodeValue.strip()
                if not (global_artifact_server).endswith('/'):
                    global_artifact_server = global_artifact_server + '/'

                if server_names[0].getElementsByTagName("default")[0].hasAttribute('auth'):
                    if server_names[0].getElementsByTagName("default")[0].getAttribute('auth').strip().lower() == 'true':
                        authenticate_download = True

                production_artifact_server = server_names[0].getElementsByTagName("prod")
                if production_artifact_server and production_artifact_server.length == 1:
                    production_artifact_server = production_artifact_server[0].firstChild.nodeValue.strip().lower()
                else:
                    production_artifact_server = global_artifact_server

                if (production_artifact_server).endswith('/'):
                    production_artifact_server = production_artifact_server[:-1]
                if not production_artifact_server.endswith("artifactory"):
                    production_artifact_server = production_artifact_server + "/artifactory"

                if not (production_artifact_server).endswith('/'):
                    production_artifact_server = production_artifact_server + '/'
            else:
                raise ValueError('Error: server.dev must be supplied')


            if use_prod_profile:
                global_artifact_server = production_artifact_server
                if server_names[0].getElementsByTagName("prod")[0].hasAttribute('auth'):
                    if server_names[0].getElementsByTagName("prod")[0].getAttribute('auth').strip().lower() == 'true':
                        authenticate_download = True

            if use_alt_server:
                global_artifact_server = alt_server_url


            print ('XXXXXXXXXXXXX==============>>> OVERLOADED VARIABLED <<<==============XXXXXXXXXXXXX')
            if override_prod_server:
                print ('...........OVERRIDING PRODUCTION SERVER [prior][current] [%s][%s] ...........' % (global_artifact_server,override_prod_server_url))
                global_artifact_server = override_prod_server_url


            print ('Server: %s' % global_artifact_server)
            print ('Authenticate: %s' % authenticate_download)

            repo_array = collection.getElementsByTagName("repository")
            if not repo_array:
                repo = collection.getElementsByTagName("repostiory")[0]
            else:
                repo = repo_array[0]

            global_snapshot_repo = repo.getElementsByTagName("snapshot")[0].firstChild.nodeValue
            if not (global_snapshot_repo).endswith('/'):
                global_snapshot_repo = global_snapshot_repo + '/'
            print ('Snapshot [%s]' % global_snapshot_repo)

            global_production_repo = repo.getElementsByTagName("production")[0].firstChild.nodeValue
            if not (global_production_repo).endswith('/'):
                global_production_repo = global_production_repo + '/'
            print ('Production [%s]' % global_production_repo)

            docker = config.getElementsByTagName("docker")

            docker_hosts = []
            docker_force_overwrite = False
            docker_force_command = ''
            if docker:
                enable_docker_commands = True
                docker_clean = True if docker[0].getElementsByTagName('clean')[0].firstChild.nodeValue.strip().lower() == 'true' else False
                docker_euthanize = True if docker[0].getElementsByTagName('euthanize')[0].firstChild.nodeValue.strip().lower() == 'true' else False
                docker_push = True if docker[0].getElementsByTagName('push')[0].firstChild.nodeValue.strip().lower() == 'true' else False
                docker_tag = True if docker[0].getElementsByTagName('tag')[0].firstChild.nodeValue.strip().lower() == 'true' else False
                if docker[0].getElementsByTagName('force'):
                    docker_force_overwrite = True if docker[0].getElementsByTagName('force')[0].firstChild.nodeValue.strip().lower() == 'true' else False
                if docker_force_overwrite:
                    docker_force_command = '-f'
                if docker_tag:
#                     docker_host = docker[0].getElementsByTagName('host')[0].firstChild.nodeValue.strip().lower()
                    docker_host_list = docker[0].getElementsByTagName('host')
                    for dhosts in docker_host_list:
                        docker_host = dhosts.firstChild.nodeValue.strip().lower()
                        if len(docker_host) < 1:
                            raise ValueError('If tag container is true, host cannot be empty')
                        docker_hosts.append(docker_host)

#                         <push>false</push>
#                         <tag>false</tag>

                print ('xxxxxxxxxxXXXXXXXXXXXXXX DOCKER COMMANDS ENABLED XXXXXXXXXXXXXXxxxxxxxxxx')
#                 print ('...........OVERRIDING DOCKER_HOSTS...........')
#                 docker_hosts = ['iris-analytics.tk' + 'tekcomms-artifactory.global.tektronix.net']
#                 print ('...........OVERRIDING DOCKER TAG [prior][current] [%s][True] ...........' % (docker_tag))
#                 docker_tag = True
#                 print ('...........OVERRIDING DOCKER PUSH [prior][current] [%s][True] ...........' % (docker_push))
#                 docker_push = True
#                 print ('...........OVERRIDING FORCE_OVERWRITE [prior][current] [%s][True] ...........' % (docker_force_overwrite))
#                 docker_force_overwrite = True
#                 print ('...........OVERRIDING FORCE_OVERWRITE_COMMAND [prior][current] [%s][-f] ...........' % (docker_force_command))
#                 docker_force_command = '-f'
                print ('[%s] CLEAN' % docker_clean)
                print ('[%s] EUTHANIZE' % docker_euthanize)
                print ('[%s] PUSH' % docker_push)
                print ('[%s] FORCE' % docker_force_overwrite)
                print ('[%s] TAG' % docker_tag)
                print ('[%s] HOST' % docker_hosts)
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

#         global skip_container_build

            if override_purge:
                print ('...........OVERRIDING PURGE EXTENSION [prior][current][extension] [%s][%s][%s] ...........' % (override_purge,override_purge_val,override_purge_type))
                enforce_global_purge = override_purge
                global_purge = override_purge_val
                global_purge_filetype = override_purge_type


            if skip_downloads:
                print('XXXXXXXX SKIPPING FILE DOWNLOADS -- WARNING, old artifacts or missing files may cause issues XXXXXXXX')
            elif magic_level == self.DB_DOWNLOAD_FROM_DICT:

                artifacts = folio.getArtifact()
                for artObj in artifacts.values():
                    self.downloadFile(artObj)

            else:
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
            #end skip_downloads

            if verify_valid_url:
                total_success += 1
                container_stop_time=datetime.now()
                container_runtime = (container_stop_time - container_start_time)
                resultsLogger.log("Container Pre-Fetch State [%s][Success=True] [%s]" % (CURRENT_CONTAINER,container_runtime))
                return
            elif (magic_level == self.SEEK_FILES_UPDATE_DB):
                container_stop_time=datetime.now()
                container_runtime = (container_stop_time - container_start_time)
                resultsLogger.log("Container  Pre-Fetch/State [%s][Success=True] [%s]" % (CURRENT_CONTAINER,container_runtime))
                dataMgr.updateContainerState(self.VALID, folio, container_stop_time, container_runtime, '')
                return

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

            if use_prod_profile:
                if prod_profile_version != '?':
                    docker_build_tag =  tag_application + ':' + prod_profile_version

# ################################ CUT HERE .... DOCKER ###########################################
#         def runDockerCommands(self):
# ################################ DOCKER ###########################################

            print ('XXXXXXXXXXXXX==============>>> OVERLOADED VARIABLED <<<==============XXXXXXXXXXXXX')
            if override_registry:
                print ('...........OVERRIDING DOCKER HOST {[prior]}{[current]} {%s}{%s} ...........' % (docker_hosts,override_registry_url))
                docker_hosts = override_registry_url

            if override_docker_tag:
                print ('...........OVERRIDING DOCKER TAG [prior][current] [%s][%s] ...........' % (docker_tag, override_docker_tag_val))
                docker_tag = override_docker_tag_val

            if override_docker_push:
                print ('...........OVERRIDING DOCKER PUSH [prior][current] [%s][%s] ...........' % (docker_push, override_docker_push_val))
                docker_push = override_docker_push_val

            if override_docker_overwrite:
                print ('...........OVERRIDING FORCE_OVERWRITE [prior][current] [%s][%s] ...........' % (docker_force_overwrite,override_docker_overwrite_val))
                docker_force_overwrite = override_docker_overwrite_val

            if force_tag_overwrite:
                print ('...........OVERRIDING FORCE_TAG_OVERWRITE [prior][current] [%s][%s] ...........' % (docker_force_overwrite,'-f'))
                docker_force_command = '-f'

            if override_tag_version:
                print ('...........OVERRIDING TAG_VERSION [prior][current] [%s][%s][%s] ...........' % (docker_force_overwrite,override_tag_version,override_tag_version_val))
                tag_split = docker_build_tag.split(':')
                if len(tag_split) == 1:
                    docker_build_tag = docker_build_tag + ':' + override_tag_version_val
                if len(tag_split) == 2:
                    docker_build_tag = tag_split[1] + ':' +  override_tag_version_val
#             print 'docker_build_tag: ' + docker_build_tag

            docker_push_image_name = docker_build_tag
            
            docker_build_arg = ''
            if use_build_arg:
                docker_build_arg = ' --build-arg BUILD=' + str(BUILD_ID)
                
            build_command = 'docker build -t ' + docker_build_tag + docker_build_arg + ' .'
            global test_run_only
            print ('Build Command: ' + build_command)

            print ('os.name [%s]' % os.name)

            if os.name == 'nt':
                print ('... WINDOWS DETECTED * TEST_RUN_ENABLED - SKIPPING DOCKER BUILD ...')
#                 test_run_only = True

            if dockerfile_dynamic_label:
                print ('XXXXXXXXXXXXXXX FIND/REPLACE THE #LABEL IN Dockerfile (not yet implemented) XXXXXXXXXXXXXXX')
#            dockerfile_dynamic_label = False
#             enable_docker_commands
            if skip_container_build:
                print ('XXXXXXXXXXXXXXX SKIPPING DOCKER COMMANDS XXXXXXXXXXXXXXX')
            else:
                if enable_docker_commands:
                    print ('............. ENABLE_DOCKER_COMMANDS .............')

                    if docker_clean:
                        print ('............. DOCKER CLEAN .............')
                        clean_command = ("docker ps -a | grep %s | awk '{print $1}' | xargs docker rm" % docker_build_tag)
                        print(clean_command)
                        self.clean_euthanize(clean_command)
                        clean_command = ('docker rmi -f %s' % docker_build_tag)
                        print(clean_command)
                        self.clean_euthanize(clean_command)

                    print('***************----------------***************')
                    resultsLogger.log('[%s] Build: [%s]' % (CURRENT_CONTAINER,build_command))
                    build_id = self.docker_build_command(build_command)
                    print('returning build_id [%s]' % build_id)
                    print('***************----------------***************')
                    print docker_hosts
                    if docker_tag:
                        for tag_host in docker_hosts:
                            print ('............. DOCKER TAG .............')
                            tmp_name = docker_build_tag.split("/")
#                             print ('len of temp_name %s' % str(len(tmp_name)))
                            if len(tmp_name) == 2:
                                docker_build_tag = tmp_name[1]
                            print ('XXXXXXXXXXXXXXX docker_build_tag %s' % docker_build_tag)

                            docker_push_image_name = tag_host + "/" + docker_build_tag
                            tag_command = ('docker tag %s %s %s' % (docker_force_command, build_id, docker_push_image_name))
                            print 'tag_command: ', tag_command
                            self.docker_command(tag_command)
                            if docker_push:
                                print ('............. DOCKER PUSH .............')
                                push_command = ('docker push %s %s' % ('', docker_push_image_name))
                                resultsLogger.log('[%s] Push: [%s]' % (CURRENT_CONTAINER,push_command))
                                self.docker_command(push_command)
                            docker_build_tag = docker_push_image_name
    #                    end tag_host
                        print ('tag_latest %s' % tag_latest)
                        if tag_latest:
                            container_target_name = docker_push_image_name
                            tags = docker_push_image_name.split(':')
                            print ('TAGS-LEN [%s] TAGS: %s' % (len(tags),tags))

                            if len(tags) > 1:
#                                 print ('TAG.1: %s' % tags[0])
                                container_target_name = tags[0]
#                                 print ('TAG.2: %s' % tags[1])

                            tag_command = ('docker tag -f %s %s:latest' % (build_id, container_target_name))
                            resultsLogger.log ('Docker Tag: %s' % tag_command)
                            self.docker_command(tag_command)
                            resultsLogger.log ('Docker Push: docker push %s:latest' % container_target_name)
                            push_command = ('docker push %s:latest' % container_target_name)
                            resultsLogger.log('[%s] Push: [%s]' % (CURRENT_CONTAINER,push_command))
                            self.docker_command(push_command)
                        #end tag_latest
    #               end if

                    if docker_euthanize:
                        print ('............. DOCKER EUTHANIZE .............')
                        clean_command = ("docker ps -a | grep %s | awk '{print $1}' | xargs docker rm" % docker_build_tag)
                        print(clean_command)
                        self.clean_euthanize(clean_command)
                        clean_command = ('docker rmi -f %s' % docker_build_tag)
                        print(clean_command)
                        self.clean_euthanize(clean_command)
                else:
                    resultsLogger.log('[%s] Build: [%s]' % (CURRENT_CONTAINER,build_command))
                    build_id = self.docker_build_command(build_command)
                    print('returning build_id [%s]' % build_id)

                resultsLogger.log('[%s] Success, Container-ID [%s]' % (CURRENT_CONTAINER,build_id))

            total_success += 1

        except Exception,err:
            container_err_message = err
            container_exit_status = False
            if magic_level == self.SEEK_FILES_UPDATE_DB:
                resultsLogger.log('[%s] Validation Failed: [%s]' % (CURRENT_CONTAINER,err))
            else:
                total_fail += 1
                resultsLogger.log('[%s] Failed: [%s]' % (CURRENT_CONTAINER,err))
            if(debug_exceptions):
                traceback.print_exc()
                resultsLogger.error(err)

        if magic_level != self.SEEK_FILES_UPDATE_DB:
            container_stop_time=datetime.now()
            container_runtime = (container_stop_time - container_start_time)
            resultsLogger.log("Container Runtime/State [%s][Success=%s] [%s]" % (CURRENT_CONTAINER,container_exit_status,container_runtime))
            print ("Container Runtime/State [%s][Success=%s] [%s]" % (CURRENT_CONTAINER,container_exit_status,container_runtime))
        else:
            current_build_runtime = (container_stop_time - master_start_time)
            containers_remaining = total_container_count -total_success - total_fail
            resultsLogger.log("Current stats: [total=%s][#passed=%s][#failed=%s][#remaining=%s] Runtime [%s]" % (total_container_count,total_success,total_fail,containers_remaining,current_build_runtime))
            print("Current stats: [total=%s][#passed=%s][#failed=%s][#remaining=%s] Runtime [%s]" % (total_container_count,total_success,total_fail,containers_remaining,current_build_runtime))

        if(USE_DB):
            if (magic_level == self.SEEK_FILES_UPDATE_DB):
                dataMgr.updateContainerState(self.INVALID, folio, container_stop_time, container_runtime, container_err_message)
            else:
                if not container_exit_status: failed_state = False

                dataMgr.updateContainerState(self.STATE_SUCCESS if container_exit_status else self.STATE_FAILED, folio, container_stop_time, container_runtime, container_err_message)
                current_runtime = (datetime.now() - master_start_time)
                dataMgr.updateBuild(BUILD_ID, self.STATE_RUNNING, total_container_count, total_success, total_fail, None, str(current_runtime))

        if total_fail > 0 and is_beta_build:
            print("Failed build - forcing exit status. Reason: %s" % container_err_message)
            sys.exit(-1)

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
        global USE_DB
        global resultsLogger
        print ('********************* INITIATING ARTIFACT LOOKUP *********************')
        for artifact in artifacts:
            artifact_dir = './'
            artifact_overwrite = False
            artifact_production = False
            artifact_purge = False
            artifact_filetype = '_x_x_x_'
            artifact_repository = ''
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
            artifact_group_array = artifact.getElementsByTagName("groupId")
            if not artifact_group_array:
                artifact_group_array = artifact.getElementsByTagName("groupid")
            artifact_group = self.validateURI(artifact_group_array[0].firstChild.nodeValue.replace('.','/'))

            artifact_array = artifact.getElementsByTagName("artifactId")
            if not artifact_array:
                artifact_array = artifact.getElementsByTagName("artifactid")

            artifact_id = artifact_array[0].firstChild.nodeValue

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

            artifact_repostiory_node = artifact.getElementsByTagName("repository")
            if not artifact_repostiory_node:
                artifact_repostiory_node = artifact.getElementsByTagName("repostiory")

            if artifact_repostiory_node.length == 1:
                artifact_repository = artifact_repostiory_node[0].firstChild.nodeValue
            elif artifact_production:
                artifact_repository = global_production_repo
            else:
                artifact_repository = global_snapshot_repo

            print ('Artifact Repository: %s' % artifact_repository)

            artifact_url = self.validateURI(artifact_server) + self.validateURI(artifact_repository) + self.validateURI(artifact_group) + self.validateURI(artifact_id)

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
#             print ('Group ID: %s' % artifact_group)
#             print ('Artifact ID: %s' % artifact_id)

#             if USE_DB:
#                 ARTIFACT_ID = dataMgr.storeArtifactdData(CONTAINER_ID, artifact_url, 'artifact')
#                 print ('XXX===>>  ARTIFACT_ID: %s' % (ARTIFACT_ID))

            self.extractArtifactDetails(artifact_group, artifact_id, artifact_dir, artifact_target_name, artifact_overwrite,
                                        artifact_production, artifact_extension, artifact_classifier, artifact_url,
                                        artifact_server,artifact_repository)
            print 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    #end parseArtifact

    def extractArtifactDetails(self, artifact_group, artifact_id, file_dir, target_name, clobber, release, extension_type, classifier, url,artifact_server,artifact_repository):
    #     artifact_xml_doc
        global authenticate_download
        global USE_DB
        global CURRENT_CONTAINER
        artifact_file_detail = ''
#         print '------>>> ',  url
#         print 'url + self.artifact_xml_doc ',  url + self.artifact_xml_doc
        print ('Attempting to fetch latest version from : %s' % (url + self.artifact_xml_doc))
        if authenticate_download:
            auth_file = os.path.expanduser('~/.silo')
            print 'auto_file_exist: ', os.path.isfile(auth_file)
            if not os.path.isfile(auth_file):
                auth_file = '/etc/silo.cfg'
            auth_creds = dict(line.strip().split('=',1) for line in open(auth_file))
            p = urllib2.HTTPPasswordMgrWithDefaultRealm()
            p.add_password(None, url, auth_creds.get('username'), auth_creds.get('password'))
            handler = urllib2.HTTPBasicAuthHandler(p)
            opener = urllib2.build_opener(handler)
            urllib2.install_opener(opener)

        versionXML = urllib2.urlopen(url + self.artifact_xml_doc, timeout=10)
        versionDOC = minidom.parse(versionXML)
    #     container_version_tag = 'EMPTY'
#         artifact_filename = artifact_id + 'wait_wat'
        if release:
            artifactVersion = versionDOC.getElementsByTagName('release')[0].firstChild.nodeValue
            container_version_tag = artifactVersion
            buildNumber = ''
            print ('VERSION: %s'  % container_version_tag)
            file_extension = 'jar'
            if extension_type:
                file_extension = extension_type

            if classifier:
                artifact_filename = artifact_id + '-' + artifactVersion + '-' + classifier + '.' + file_extension.strip(".")
            else:
                artifact_filename = artifact_id + '-' + artifactVersion + '.' + file_extension.strip(".")

            latest_build_url = url + self.validateURI(artifactVersion) + artifact_filename
        else:
            artifactVersion=versionDOC.getElementsByTagName('latest')[0].firstChild.nodeValue

            print ('Version: %s'  % artifactVersion)

            latestBuild=artifactVersion.split("-")[0]
            latest_build_url = url + self.validateURI(artifactVersion)
#             print 'latestBuild: ', latestBuild
#             print 'latest_build_url: ', latest_build_url

            latestXML = urllib2.urlopen(latest_build_url + self.artifact_xml_doc)
            latestDOC = minidom.parse(latestXML)
            buildNumber=latestDOC.getElementsByTagName('buildNumber')[0].firstChild.nodeValue

            snapshots = latestDOC.getElementsByTagName('snapshotVersion')

            print('**************************************************************************************************************')
            print 'snapshots.length: ', snapshots.length
            print 'buildNumber: ', buildNumber

            print ('Seeking extension_type: %s' % extension_type)
            print ('Seeking classifier: %s' % classifier)

            if snapshots:
                for version in snapshots:
                    if classifier != '':
                        extension = version.getElementsByTagName('extension')
                        source_classifier = version.getElementsByTagName('classifier')

                        extension = version.getElementsByTagName('extension')
                        source_classifier = version.getElementsByTagName('classifier')


                        if extension.length == 1 and source_classifier.length == 1:
#                             print ('2')

                            if (extension[0].firstChild.nodeValue == extension_type and
                                source_classifier[0].firstChild.nodeValue == classifier) :
#                                 print ('3')
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
            else:
                print ('XXXXXXXXXXXXXXXXXXX WARNING --- NO VERSIONS FOUND - ASSUMING JAR FILE (check your repo) XXXXXXXXXXXXXXXXXXX')
                artifact_file_detail = '7.13.2.2-SNAPSHOT'
                artifact_filename = artifact_id + '-' + artifact_file_detail + '.jar'

            print 'artifact_id ', artifact_id
            print 'artifact_file_detail ', artifact_file_detail
            print 'extension_type ', extension_type
            print 'artifact_filename ', artifact_filename

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

#         if USE_DB:
#             dataMgr.setArtifactFileName(containerID, final_filename)

        resultsLogger.log('[%s] Download Artifact [%s]' % (CURRENT_CONTAINER,latest_build_url))
        artObj = Artifact(-1,
                          -1,
                            'artifact',
                            latest_build_url,
                            final_filename,
                            artifact_group,
                            artifact_server,
                            artifact_repository,
                            extension_type,
                            classifier,
                            buildNumber,
                            container_version_tag,
                            artifact_file_detail)

        self.downloadFile(artObj)
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
            global USE_DB
            global CONTAINER_ID
            global CURRENT_CONTAINER

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

#                 if USE_DB:
#                     ARTIFACT_ID = dataMgr.storeFileData(CONTAINER_ID, file_source, output_file, 'file')
#                     print ('XXX===>>  ARTIFACT_ID: %s' % (ARTIFACT_ID))

                print ('URL: %s' % file_source)
                print ('Output File: %s' % output_file)

                print ('Overwrite: %s' % file_overwrite)

                if os.path.isfile(output_file) and not file_overwrite:
                    print 'File exist, Overwrite set to False - skipping download'
                    return None
                #end if

#                 if USE_DB:
#                     ARTIFACT_ID = dataMgr.storeArtifactdData(CONTAINER_ID, file_source, 'file')
#                     print ('XXX===>>  ARTIFACT_ID: %s' % (ARTIFACT_ID))

                resultsLogger.log('[%s] Download Static File [%s]' % (CURRENT_CONTAINER,file_source))

                artObj = Artifact(-1,
                                  -1,
                                    'file',
                                    file_source,
                                    output_file)

                self.downloadFile(artObj)

    #end parseStaticFiles
    def purgeFiles(self, ext):
            global test_run_only


            extension = str(ext)
            extension = extension.translate(None, " ?.!/;\:*")

            print('>>>>>>>>XXXXXXXXXXXXXXX>>>>>>>>>>> %s ' % extension)
            if test_run_only:
                print ('... TEST_RUN_ENABLED - NO FILES WILL BE DELETED ... ')
                filelist = glob.glob('./*' + extension)
                for purge_file in filelist:
                    print('>>>>>>>>>>>>>> [TEST] DELETING >>>>>>>>>>>>>>>> %s'  % purge_file)
                return
            else:
                filelist = glob.glob('./*' + extension)
                for purge_file in filelist:
                    print('>>>>>>>>>>>>>> DELETING >>>>>>>>>>>>>>>> %s'  % purge_file)
                    os.remove(purge_file)

    def fetchGitChanges(self, command):
        p = subprocess.Popen(command,
                              shell=use_process_shell,
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
 
        return change_results
 
    def docker_build_command(self, system_command):
        global test_run_only
        BUILD_ID = 'UNDEFINED'
        if test_run_only or (os.name == 'nt'):
            BUILD_ID = 'TEST-UNDEFINED'
            print('[TEST] running docker command: %s' % system_command)
        else:
            print('running process: %s' % system_command)
            error_message = ''
            rc = -99
            last_line = None
            try:
                process = subprocess.Popen([system_command],
                                           shell=True,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           universal_newlines=True)


                out, err = process.communicate()
#                 print ("*****Own output*****")
                resultsLogger.log(out)
#                 print ("*****Own error output*****")
                error_message = err.strip()
#                 resultsLogger.error(error_message)

                rc = process.poll()
                print ('Docker build exit code [%s]' % rc)
                if rc != 0:
                    print('the docker_command [%s] has exited with a non-zero response code [%s]' % (system_command, rc))
                    print('Current working directory [%s]' % os.getcwd())
                    resultsLogger.log('The docker_command [%s] has failed to complete * response code[%s] Message[%s]' % (system_command, rc,last_line))
                    resultsLogger.log('Current working directory [%s]' % os.getcwd())
                    raise ValueError()
                else:
                    lines = out.split('\n')
                    for line in lines:
                        if line.strip() != '' :
                            last_line = line.strip()

#                     if 'Successfully' in last_line:
                    mylist = last_line.split(' ')
                    BUILD_ID =  mylist[2]
                    print ('BUILD_ID: ' + BUILD_ID)
                    resultsLogger.log('The docker build command [%s] was Successful' % (system_command))

            except ValueError:
                raise ValueError('The docker_command [%s] was unable to complete [%s]' % (system_command,error_message))
            except Exception, err:
                resultsLogger.log('The docker_command [%s] has thrown an unrecoverable exception [%s]' % (system_command,err))
                resultsLogger.error('The docker_command [%s] has thrown an unrecoverable exception [%s]' % (system_command,err))
                resultsLogger.log('Current working directory [%s]' % os.getcwd())
                resultsLogger.error('Current working directory [%s]' % os.getcwd())
                if(debug_exceptions):
                    traceback.print_exc()
                    resultsLogger.error(err)
                raise ValueError('The docker_command [%s] has thrown an unrecoverable exception [%s]' % (system_command,err))

        return BUILD_ID

    #end runProcess

    def docker_command(self, system_command):
        global test_run_only
        global resultsLogger

        if test_run_only or (os.name == 'nt'):
            print('[TEST] running docker command: %s' % system_command)
        else:
            print('running process: %s' % system_command)
            error_message = ''
            rc = -99
            try:
                process = subprocess.Popen([system_command],
                                           shell=True,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           universal_newlines=True)

                out, err = process.communicate()
                resultsLogger.log(out)
                error_message = err.strip()

                rc = process.poll()
                print ('Docker build exit code [%s]' % rc)
                if rc != 0:
                    print('the docker_command [%s] has exited with a non-zero response code [%s]' % (system_command, rc))
                    resultsLogger.log('The docker_command [%s] has failed to complete * response code[%s] Message[%s]' % (system_command, rc, error_message))
                    raise ValueError()
                else:
                    resultsLogger.log('The docker build command [%s] was Successful' % (system_command))

            except ValueError:
                raise ValueError('The docker_command [%s] has was unable to complete [%s]' % (system_command,error_message))
            except Exception, err:
                resultsLogger.log('The docker_command [%s] has thrown an unrecoverable exception [%s]' % (system_command,err))
                resultsLogger.error('The docker_command [%s] has thrown an unrecoverable exception [%s]' % (system_command,err))
                resultsLogger.log('Current working directory [%s]' % os.getcwd())
                resultsLogger.error('Current working directory [%s]' % os.getcwd())
                if(debug_exceptions):
                    traceback.print_exc()
                    resultsLogger.error(err)
                raise ValueError('The docker_command [%s] has thrown an unrecoverable exception [%s]' % (system_command,err))

    #end runProcess

    def clean_euthanize(self, system_command):
        global test_run_only
        global resultsLogger

        if test_run_only or (os.name == 'nt'):
            print('[TEST] running docker command: %s' % system_command)
        else:
            print('running process: %s' % system_command)
            error_message = ''
            rc = -99
            try:
                process = subprocess.Popen([system_command],
                                           shell=True,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           universal_newlines=True)

                out, err = process.communicate()
                resultsLogger.log(out)
                error_message = err.strip()

                rc = process.poll()
                print ('Docker build exit code [%s]' % rc)
                if rc != 0:
                    print('the docker_command [%s] has exited with a non-zero response code [%s]' % (system_command, rc))
                    resultsLogger.log('[WARNING] The docker_command [%s] has failed to complete * response code[%s] Message[%s]' % (system_command, rc,error_message))
                else:
                    resultsLogger.log('[WARNING] The docker build command [%s] was Successful' % (system_command))

            except Exception, err:
                resultsLogger.log('[WARNING] The docker_command [%s] has thrown an unrecoverable exception [%s]' % (system_command,err))
                resultsLogger.error('[WARNING] The docker_command [%s] has thrown an unrecoverable exception [%s]' % (system_command,err))
                resultsLogger.log('Current working directory [%s]' % os.getcwd())
                resultsLogger.error('Current working directory [%s]' % os.getcwd())
                if(debug_exceptions):
                    traceback.print_exc()
                    resultsLogger.error(err)
    #clean_euthanize


    def downloadFile(self, artObj):
            global test_run_only
            global authenticate_download
            global verify_valid_url
            global debug_exceptions
            global USE_DB
            global DB_LOOKUP_PASS
            global CONTAINER_ID
            global CURRENT_CONTAINER
            global dataMgr
            global CLASS_MAGIC_LEVEL
            err_msg = ''
            exit_state=self.STATE_FAILED
            download_start=datetime.now()

#             magic_level = self.SEEK_FILES_UPDATE_DB

            print ('XZXZXZXZXZ MAGIC-LEVEL [%s] XZXZXZXZXZ' % CLASS_MAGIC_LEVEL)

            if test_run_only:
                print ('... TEST_RUN_ENABLED - NO FILES WILL BE DOWNLOAD ... ')
                print ('URL: [%s]' % artObj.url)
                return
            elif verify_valid_url:
                print ('... VERIFYING URLS - NO FILES WILL BE DOWNLOAD ... ')
                try:
                    if authenticate_download:
                        auth_file = os.path.expanduser('~/.silo')
                        print 'auto_file_exist: ', os.path.isfile(auth_file)
                        if not os.path.isfile(auth_file):
                            auth_file = '/etc/silo.cfg'
                        print 'Auth-File (remove me please): ', auth_file
                        auth_creds = dict(line.strip().split('=',1) for line in open(auth_file))
                        print 'username: ', auth_creds.get('username')
                        print 'password: ***********'
                        p = urllib2.HTTPPasswordMgrWithDefaultRealm()
                        p.add_password(None, artObj.url, auth_creds.get('username'), auth_creds.get('password'))
                        handler = urllib2.HTTPBasicAuthHandler(p)
                        opener = urllib2.build_opener(handler)
                        urllib2.install_opener(opener)
                        download_start=datetime.now()
                        rcode = urllib2.urlopen(urllib2.Request(artObj.url)).getcode()
                        if rcode == 200:
                            resultsLogger.log('[%s] URL end-point is [VALID] [%s]' % (CURRENT_CONTAINER,artObj.url))
                        else:
    #                         resultsLogger.log('[%s] URL end-point is [INVALID] Response Code [%s] URL [%s]' % (CURRENT_CONTAINER, rcode, artObj.url))
                            raise Exception('[%s] URL end-point is [INVALID] Response Code [%s] URL [%s]' % (CURRENT_CONTAINER, rcode, artObj.url))
                except Exception, err:
                    resultsLogger.log('[%s] URL end-point is [INVALID] Reason [%s] [%s]' % (CURRENT_CONTAINER,err, artObj.url))
                    if(debug_exceptions):
                        traceback.print_exc()
                        resultsLogger.error(err)
                    sys.exit(-999)
                    raise Exception('[%s] URL end-point is [INVALID] Reason [%s] [%s]' % (CURRENT_CONTAINER,err, artObj.url))

                return
            elif CLASS_MAGIC_LEVEL == self.SEEK_FILES_UPDATE_DB:
                try:
                    print ('77777777777777777777 ======> Im probably not making it this far')
                    fcontainer = self.build_container.get(CURRENT_CONTAINER)
                    print ('Pre-Fetch::container_name [%s]' % CURRENT_CONTAINER)
                    print ('Pre-Fetch::fcontainer.containerID %s' % fcontainer.containerID)
                    print ('Pre-Fetch::url %s' % artObj.url)
                    print ('Pre-Fetch::filename %s' % artObj.file_name)
                    print ('Pre-Fetch::workingDir %s' % fcontainer.workingDir)
                    artObj.setContainerID(fcontainer.containerID)
                    artID = dataMgr.storeArtifactdData(artObj)
                    artObj.setArtifactID(artID)
                    fcontainer.addArtifact(artID,artObj)
                    self.build_container.update({CURRENT_CONTAINER:fcontainer})
                except Exception,err:
                    err_msg = err
                    exit_state=self.STATE_FAILED
                    resultsLogger.log('[%s] URL end-point is [INVALID] Reason [%s] [%s]' % (CURRENT_CONTAINER, err, artObj.url))
                    if(debug_exceptions):
                        traceback.print_exc()
                        resultsLogger.error(err)
                    raise Exception('[%s] URL end-point is [INVALID] Reason [%s] [%s]' % (CURRENT_CONTAINER,err, artObj.url))
                finally:
                    artID = dataMgr.storeArtifactdData(artObj,exit_state)
                    dataMgr.updateArtifactState(exit_state, artObj, None, None, err_msg)
                return
            elif CLASS_MAGIC_LEVEL == self.DB_DOWNLOAD_FROM_DICT:
                dataMgr.updateArtifactState(self.STATE_RUNNING, artObj, download_start)
                try:
                    print ('... Initiating dictionary download ...')
                    if authenticate_download:
                        auth_file = os.path.expanduser('~/.silo')
                        print 'auto_file_exist: ', os.path.isfile(auth_file)
                        if not os.path.isfile(auth_file):
                            auth_file = '/etc/silo.cfg'
                        auth_creds = dict(line.strip().split('=',1) for line in open(auth_file))
                        p = urllib2.HTTPPasswordMgrWithDefaultRealm()
                        p.add_password(None, artObj.url, auth_creds.get('username'), auth_creds.get('password'))
                        handler = urllib2.HTTPBasicAuthHandler(p)
                        opener = urllib2.build_opener(handler)
                        urllib2.install_opener(opener)
                    print('URL: %s' % artObj.url)
                    print('FILE: %s' % artObj.file_name)

                    remoteFile = urllib2.urlopen(artObj.url)
                    output = open(artObj.file_name,'wb')
                    output.write(remoteFile.read())
                    output.close()
                    exit_state=self.STATE_SUCCESS

                except Exception,err:
                    err_msg = err
                    exit_state=self.STATE_FAILED
                    resultsLogger.log('[%s] URL end-point is [INVALID] Reason [%s] [%s]' % (CURRENT_CONTAINER, err, artObj.url))
                    if(debug_exceptions):
                        traceback.print_exc()
                        resultsLogger.error(err)
                    raise Exception('[%s] URL end-point is [INVALID] Reason [%s] [%s]' % (CURRENT_CONTAINER,err, artObj.url))
                finally:
                    download_stop=datetime.now()
                    download_runtime= (download_stop - download_start)
                    dataMgr.updateArtifactState(exit_state, artObj, download_stop, download_runtime, err_msg)
            else:
                print ('Initiating default download ...')
                try:
                    if authenticate_download:
                        auth_file = os.path.expanduser('~/.silo')
                        print 'auto_file_exist: ', os.path.isfile(auth_file)
                        if not os.path.isfile(auth_file):
                            auth_file = '/etc/silo.cfg'
                        auth_creds = dict(line.strip().split('=',1) for line in open(auth_file))
                        p = urllib2.HTTPPasswordMgrWithDefaultRealm()
                        p.add_password(None, artObj.url, auth_creds.get('username'), auth_creds.get('password'))
                        handler = urllib2.HTTPBasicAuthHandler(p)
                        opener = urllib2.build_opener(handler)
                        urllib2.install_opener(opener)
                    remoteFile = urllib2.urlopen(artObj.url)
                    output = open(artObj.file_name,'wb')
                    output.write(remoteFile.read())
                    output.close()
                    exit_state=self.STATE_SUCCESS
                except Exception,err:
                    err_msg = err
                    exit_state=self.STATE_FAILED
                    resultsLogger.log('[%s] URL end-point is [INVALID] Reason [%s] [%s]' % (CURRENT_CONTAINER, err, artObj.url))
                    if(debug_exceptions):
                        traceback.print_exc()
                        resultsLogger.error(err)
                    raise Exception('[%s] URL end-point is [INVALID] Reason [%s] [%s]' % (CURRENT_CONTAINER,err, artObj.url))
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

    def fetchDependency(self):
            proc = subprocess.Popen('head Dockerfile | grep -i from',
                                              shell=True,
                                              bufsize=0,  # 0=unbuffered, 1=line-buffered, else buffer-size
                                              stdout=subprocess.PIPE)
            line = proc.stdout.readline()
            return line.strip()
        
    def fetchImageName(self):
        containerData = parse('container.xml')
        collection = containerData.documentElement
        config = collection.getElementsByTagName("config")[0]
        return str(config.getElementsByTagName("application")[0].firstChild.nodeValue.strip().lower()).translate(None, " ?.!;\:*")
       
    def imageExist(self, image):
        p = subprocess.Popen(('docker images -q %s' % image),
                                          shell=True,
                                          bufsize=0,  # 0=unbuffered, 1=line-buffered, else buffer-size
                                          stdout=subprocess.PIPE)
        line = p.stdout.readline()
#         print ('LINE: %s' % line.strip())
        return line.strip()
            
        
        
        
        
    def check_arguments(self, argv):
        global working_dir
        global target_file
        global use_recursive
        global test_run_only
        global user_defined_file
#       ..................
        global use_prod_profile
        global prod_profile_version
        global use_alt_profile
        global alt_profile_name
        global use_alt_server
        global alt_server_url
        global override_registry
        global override_registry_url
        global override_docker_tag
        global override_docker_tag_val
        global override_docker_push
        global override_docker_push_val
        global override_docker_overwrite
        global override_docker_overwrite_val
        global skip_builds
        global skip_list
        global search_only
        global validate_only
        global skip_downloads
        global skip_container_build
        global debug_exceptions
        global enable_logging
        global force_tag_overwrite
        global override_tag_version
        global override_tag_version_val
        global override_purge
        global override_purge_val
        global override_purge_type
        global override_prod_server
        global override_prod_server_url
        global verify_valid_url
        global USE_DB
        global is_beta_build
        global tag_latest
        global dirty_run
        global set_pip_index
        global pip_index_url
        global set_pip_host
        global pip_trusted_host
        global enforce_global_production
        global global_production
        global use_build_arg
        global only_updates
        global use_process_shell
        global git_clone
        global git_pull
        global git_checkout
        global git_branch
        global skip_dependency_check

#       ..................
#       ..................
        use_prod_profile = False
        use_alt_profile = False
        use_alt_server = False
        alt_profile_name = ''
        alt_server_url = ''
        user_defined_file = ''
        prod_profile_version = ''
        override_registry = False
        override_registry_url = []
        override_docker_tag = False
        override_docker_tag_val = False
        override_docker_push = False
        override_docker_push_val = False
        override_docker_overwrite = False
        override_docker_overwrite_val = False
        skip_builds = False
        skip_list = []
        search_only = False
        validate_only = False
        skip_downloads = False
        skip_container_build = False
        debug_exceptions = False
        enable_logging = False
        force_tag_overwrite = False
        override_tag_version = False
        override_tag_version_val = ''
        override_purge = False
        override_purge_val = False
        override_purge_type = '__X'
        override_prod_server = False
        override_prod_server_url = ''
        verify_valid_url = False
        USE_DB = False
        is_beta_build = False
        tag_latest = False
        dirty_run = False
        set_pip_index = False
        pip_index_url = ''
        set_pip_host = False
        pip_trusted_host = ''
        enforce_global_production = False
        global_production = False
#       ..................
        working_dir = os.path.abspath('./')
        target_file = 'container.xml'
        test_run_only = False
        use_recursive = False
        use_build_arg = False
        only_updates = False
        git_clone = False
        git_pull = False
        git_checkout = False
        git_branch = 'master'
        skip_dependency_check = False
#       ...................
        user_file = ''
        use_process_shell = False
        if os.name == 'nt':
            print ('... WINDOWS DETECTED * enabling processes Shell ...')
            use_process_shell = True


        try:
#             docker tag [OPTIONS] IMAGE[:TAG] [REGISTRYHOST/][USERNAME/]NAME[:TAG]
#             options, args = getopt.getopt(argv, 'rvtf:', ['file','version','prod','server'])
#             print ('argv: %s' % argv)
            options, remainder = getopt.getopt(argv, 'hvrtP::p::f::s::V', ['help',
                                                                            'version',
                                                                            'recursive',
                                                                            'test',
                                                                            'prod=',
                                                                            'profile=',
                                                                            'server=',
                                                                            'file=',
                                                                            'config=',
                                                                            'validate',
                                                                            'registry=',
                                                                            'skip-artifacts',
                                                                            'skip-files',
                                                                            'dry-run',
                                                                            'purge=',
                                                                            'nopurge',
                                                                            'file-dir',
                                                                            'pre-clean',
                                                                            'pro-clean',
                                                                            'overwrite',
                                                                            'parent',
                                                                            'buildfile=',
                                                                            'tag',
                                                                            'push',
                                                                            'overwrite',
                                                                            'notag',
                                                                            'nopush',
                                                                            'nooverwrite',
                                                                            'skip=',
                                                                            'search',
                                                                            'nobuild',
                                                                            'buildonly',
                                                                            'debug',
                                                                            'log',
                                                                            'forcetag',
                                                                            'forcever=',
                                                                            'pserver=',
                                                                            'verify',
                                                                            'usedb',
                                                                            'deploylocal',
                                                                            'localport',
                                                                            'betabuild',
                                                                            'taglatest',
                                                                            'dirty',
                                                                            'pipindex=',
                                                                            'piphost=',
                                                                            'usebuildarg',
                                                                            'only-updates',
                                                                            'shell',
                                                                            'git-clone'
                                                                            'git-pull',
                                                                            'git-checkout=',
                                                                            'nodep'
                                                                            ])
        except getopt.GetoptError as err:
            print ('Invalid argument: %s' % err) # will print something like "option -a not recognized"
#             usage()
            sys.exit(2)

        for opt, arg in options:
            if opt in ('-v', '--version'):
                print '\tSilo Docker dynamic file pre-loader, Version ', __version__.__version__
                sys.exit(0)
            elif opt in ('-h', '--help'):
                build_file = arg
                print ('888888888888888 USE -- BUILD -- FILE: [%s] 888888888888888' % build_file)
            elif opt in ('--buildfile'):
                build_file = arg
                print ('888888888888888 USE -- BUILD -- FILE: [%s] 888888888888888' % build_file)
            elif opt in ('-r', '--recursive'):
                use_recursive = True
            elif opt in ('-t', '--test'):
                test_run_only = True
            elif opt in ('-P', '--prod'):
                use_prod_profile = True
                prod_profile_version = arg
            elif opt in ('-p', '--profile'):
                #Not yet implemented ...
                profile = True
                profile_name = arg
            elif opt in ('-s', '--server'):
                use_alt_server = True
                alt_server_url = arg
                alt_server_url = alt_server_url + '/'
            elif opt in ('--registry'):
                override_registry = True
                override_registry_url.append(arg)
            elif opt in ('-f', '--file'):
                user_defined_file = True
                user_file = arg
                if os.path.isfile(user_file):
                    working_dir = os.path.dirname(user_file)
                    target_file = os.path.basename(user_file)
                else:
                    working_dir = os.path.abspath(user_file)
            elif opt in ('--tag'):
                override_docker_tag = True
                override_docker_tag_val = True
            elif opt in ('--push'):
                override_docker_push = True
                override_docker_push_val = True
            elif opt in ('--overwrite'):
                override_docker_overwrite = True
                override_docker_overwrite_val = True
            elif opt in ('--notag'):
                override_docker_tag = True
                override_docker_tag_val = False
            elif opt in ('--nopush'):
                override_docker_push = True
                override_docker_push_val = False
            elif opt in ('--nooverwrite'):
                override_docker_overwrite = True
                override_docker_overwrite_val = False
            elif opt in ('--skip'):
                skip_builds = True
                skip_list = arg.split(",")
            elif opt in ('--search'):
                search_only = True
            elif opt in ('--validate'):
                validate_only = True
            elif opt in ('--nobuild'):
                skip_container_build = True
            elif opt in ('--buildonly'):
                skip_downloads = True
            elif opt in ('--debug'):
                debug_exceptions = True
            elif opt in ('--log'):
                enable_logging = True
            elif opt in ('--forcetag'):
                force_tag_overwrite = True
            elif opt in ('--forcever'):
                override_tag_version = True
                override_tag_version_val = arg
            elif opt in ('--purge'):
                override_purge = True
                override_purge_val = True
                override_purge_type = arg
            elif opt in ('--nopurge'):
                override_purge = True
                override_purge_val = False
            elif opt in ('--pserver'):
                override_prod_server = True
                override_prod_server_url = arg
                print arg
            elif opt in ('--verify'):
                verify_valid_url = True
            elif opt in ('--usedb'):
                USE_DB = True
            elif opt in ('--betabuild'):
                is_beta_build = True
            elif opt in ('--taglatest'):
                tag_latest = True
            elif opt in ('--dirty'):
                dirty_run = True
            elif opt in ('--pipindex'):
                set_pip_index = True
                pip_index_url = arg
            elif opt in ('--piphost'):
                set_pip_host = True
                pip_trusted_host = arg
            elif opt in ('--usebuildarg'):
                use_build_arg = True
            elif opt in ('--only-updates'):
                only_updates = True
            elif opt in ('--shell'):
                use_process_shell = True                
            elif opt in ('--git-clone'):
                git_clone = True
            elif opt in ('--git-pull'):
                git_pull = True
            elif opt in ('--git-checkout'):
                git_checkout = True
            elif opt in ('--nodep'):
                skip_dependency_check = True
                
#         print 'OPTIONS   :', options

        enforce_global_production = use_prod_profile
        global_production = use_prod_profile

        print('test_run_only [%s]' % (test_run_only))
        print('use_recursive [%s]' % (use_recursive))
        print('use_prod_profile [%s]' % (use_prod_profile))
        print('enforce_global_production [%s]' % (enforce_global_production))
        print('global_production [%s]' % (global_production))
        print('prod_profile_version [%s]' % (prod_profile_version))
        print('use_alt_profile [%s]' % (use_alt_profile))
        print('alt_profile_name [%s]' % (alt_profile_name))
        print('use_alt_server [%s]' % (use_alt_server))
        print('alt_server_url [%s]' % (alt_server_url))
        print('user_defined_file [%s]' % (user_defined_file))
        print('user_file [%s]' % (user_file))
        print('override_registry [%s]' % (override_registry))
        print('override_registry_url [%s]' % (override_registry_url))
        print('override_docker_tag [%s]' % (override_docker_tag))
        print('override_docker_tag_val [%s]' % (override_docker_tag_val))
        print('override_docker_push [%s]' % (override_docker_push))
        print('override_docker_push_val [%s]' % (override_docker_push_val))
        print('override_docker_overwrite [%s]' % (override_docker_overwrite))
        print('override_docker_overwrite_val [%s]' % (override_docker_overwrite_val))
        print('skip_builds [%s]' % (skip_builds))
        print('skip_list [%s]' % (skip_list))
        print('search_only [%s]' % (search_only))
        print('validate_only [%s]' % (validate_only))
        print('skip_downloads [%s]' % (skip_downloads))
        print('skip_container_build [%s]' % (skip_container_build))
        print('debug_exceptions [%s]' % (debug_exceptions))
        print('enable_logging [%s]' % (enable_logging))
        print('force_tag_overwrite [%s]' % (force_tag_overwrite))
        print('override_tag_version [%s]' % (override_tag_version))
        print('override_tag_version_val [%s]' % (override_tag_version_val))
        print('override_purge [%s]' % (override_purge))
        print('override_purge_val [%s]' % (override_purge_val))
        print('override_purge_type [%s]' % (override_purge_type))
        print('override_prod_server [%s]' % (override_prod_server))
        print('override_prod_server_url [%s]' % (override_prod_server_url))
        print('verify_valid_url [%s]' % (verify_valid_url))
        print('USE_DB [%s]' % (USE_DB))
        print('is_beta_build [%s]' % (is_beta_build))
        print('tag_latest [%s]' % (tag_latest))
        print('dirty [%s]' % (dirty_run))
        print('set_pip_index [%s]' % (set_pip_index))
        print('pip_index_url [%s]' % (pip_index_url))
        print('set_pip_host [%s]' % (set_pip_host))
        print('pip_trusted_host [%s]' % (pip_trusted_host))
        print('use_build_arg [%s]' % (use_build_arg))
        print('only_updates [%s]' % (only_updates))
        print('use_process_shell [%s]' % (use_process_shell))
        print('git_clone [%s]' % (git_clone))
        print('git_pull [%s]' % (git_pull))
        print('git_checkout [%s]' % (git_checkout))
        print('git_branch [%s]' % (git_branch))
        print('skip_dependency_check [%s]' % (skip_dependency_check))


        if git_clone and git_pull:
            raise ValueError('I must have misunderstood, you are going to clone a repo and then pull it ... #unlikely')

#         sys.exit(0)
'''
        for opt, arg in options:
            if opt in ('-f' + '--file'):
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
            elif opt in ('-v' + '--verbose'):
                print '\tSilo Docker dynamic file pre-loader, Version ', __version__.__version__
                sys.exit(0)
'''
#         sys.exit(1)

    #end check_arguments
