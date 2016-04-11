'''
Created on Aug 28, 2015

@author: sgee


pip install mysql-python
Note pre-requisites here:
# sudo yum install -y python-pip
# sudo yum install -y python-devel
# sudo yum install -y mysql-devel



select
A.*,
B.*,
C.*
from 
silobuild A,
container B,
artifact C
where 
A.silobuild_id = (select max(silobuild_id) from silobuild)
and
B.silobuild_id = A.silobuild_id
and
C.container_id = B.container_id

'''
import MySQLdb as mdb
import traceback,os,sys

class dataManager(object):

    def __init__(self):
        self.STATE_RUNNING = 2
        self.STATE_SUCCESS = 3
        self.STATE_FAILED = 4
        auth_file = os.path.expanduser('~/.silo')
        print 'auto_file_exist: ', os.path.isfile(auth_file)
        if not os.path.isfile(auth_file):
            auth_file = '/etc/silo.cfg'                    
        if not  os.path.isfile(auth_file):
            print('No credential file provided')
            sys.exit(1)    
        self.auth_creds = dict(line.strip().split('=',1) for line in open(auth_file))
        self.conn = None
 
    def openConnection(self):
        if (not self.conn) or (not self.conn.open):
# #             self.conn = mdb.connect('bodea-vm4.rich.tek.com', 'silo', 'tops3kret', 'silo')
#             print ('1URL: %s' % self.auth_creds.get('db_url'))
#             print ('1UN: %s' % self.auth_creds.get('dbuser'))
#             print ('1PW: %s' % self.auth_creds.get('dbpass'))
#             print ('1DB: %s' % self.auth_creds.get('db'))
            self.conn = mdb.connect(self.auth_creds.get('db_url'),self.auth_creds.get('dbuser'),self.auth_creds.get('dbpass'),self.auth_creds.get('db'))

    def createNewBuild(self, args, startedby):        
        self.openConnection()
        cursor = None
        buildid = -1
        try:
            data = (1,str(args).strip('[]'), startedby)
            print ("insert into silobuild(state_id,arguments,started_by) values (%s,%s,%s)", data)
            cursor = self.conn.cursor()
            cursor.execute("insert into silobuild(state_id,arguments,started_by) values (%s,%s,%s)", data)
            self.conn.commit()
            buildid = cursor.lastrowid
        except Exception as inst:
            print "Unrecoverable SQL Exception ... "
            traceback.print_exc()
            print (inst) 
            raise ValueError(inst) 
        finally:
            cursor.close()
#         print ('buildid: ', buildid)
        return buildid
# end createNewBuild
    

#     BUILD_ID, 0 if total_fail == 0 else 1, total_container_count, total_success, total_fail, master_stop_time, total_runtime
    def updateBuild(self, buildid, exitStatus, countainers, successes, failures, stop_time, run_time):        
        self.openConnection()
        cursor = None
        try:
            #we add 3 so we can match the states in the state table
            data = ( exitStatus, countainers, successes, failures, stop_time, run_time, buildid)
            print ("update silobuild set state_id = %s, total_containers = %s, total_pass = %s, total_fail = %s, stop_time = %s, total_build_time = %s where silobuild_id = %s", data)
            cursor = self.conn.cursor()
            cursor.execute("update silobuild set state_id = %s, total_containers = %s, total_pass = %s, total_fail = %s, stop_time = %s, total_build_time = %s where silobuild_id = %s", data)
            self.conn.commit()
            buildid = cursor.lastrowid
        except Exception as inst:
            print "Unrecoverable SQL Exception ... "
            traceback.print_exc()
            print (inst) 
            raise ValueError(inst) 
        finally:
            cursor.close()
#         print ('buildid: ', buildid)
        return buildid
# end createNewBuild

    def storeContainerData(self, buildid, working_dir, file_name):
        self.openConnection()
        cursor = None
        containerid = -1
        try:
            data = ( buildid, working_dir, file_name)
#             container:silobuild_id, state_id, working_dir, file_name

            print ("insert into container(state_id,silobuild_id,working_dir,file_name) values (0,%s,%s,%s)", data)
            cursor = self.conn.cursor()
            cursor.execute("insert into container(state_id,silobuild_id,working_dir,file_name) values (0,%s,%s,%s)", data)
            self.conn.commit()
            containerid = cursor.lastrowid
        except Exception as inst:
            print "Unrecoverable SQL Exception ... "
            traceback.print_exc()
            print (inst) 
            raise ValueError(inst) 
        finally:
            cursor.close()
#         print ('buildid: ', buildid)
        return containerid
# end storeContainerData

    def storeArtifactdData(self, artifact, state=0):
        self.openConnection()
        cursor = None
        artifactid = -1
        try:
            data = (state,
                    artifact.container_id,
                    artifact.protocol,
                    artifact.url,
                    artifact.group_id,
                    artifact.server,
                    artifact.repo,
                    artifact.extension,
                    artifact.classifier,
                    artifact.build_number,
                    artifact.file_detail,
                    artifact.version,
                    artifact.file_name)
            
            
            newArtifactSQL = ('insert into artifact('
                                'state_id,'
                                ' container_id,'
                                ' protocol,'
                                ' url,'
                                ' group_id,'
                                ' server,'
                                ' repo,'
                                ' extension,'
                                ' classifier,'
                                ' build_number,'
                                ' file_detail,'
                                ' version,'
                                ' file_name)'
                                ' values('
                                ' %s,'         #state_id,
                                ' %s,'        #container_id,
                                ' %s,'        #protocol,
                                ' %s,'        #url,
                                ' %s,'        #group_id,
                                ' %s,'        #server,
                                ' %s,'        #repo,
                                ' %s,'        #extension,
                                ' %s,'        #classifier,
                                ' %s,'        #build_number,
                                ' %s,'        #file_detail,
                                ' %s,'        #version,
                                ' %s)'        #file_name
                              )
            
# artifact:container_id, name, url, protocol
            print (newArtifactSQL % data)
            cursor = self.conn.cursor()
            cursor.execute(newArtifactSQL, data)
            self.conn.commit()
            artifactid = cursor.lastrowid
        except Exception as inst:
            print "Unrecoverable SQL Exception ... "
            traceback.print_exc()
            print (inst) 
            raise ValueError(inst) 
        finally:
            cursor.close()
#         print ('buildid: ', buildid)
        return artifactid
# end storeContainerData

    def updateContainerState(self, state, container, time, build_time='', errMsg=''):
        self.openConnection()
        cursor = None
        updateContainerSQL = ''
  
        try:
            if state == self.STATE_RUNNING:
                updateContainerSQL = ('update container set'
                            ' state_id = %s,'
                            ' start_time = %s,'
                            ' build_time = %s,'
                            ' error_message = %s'
                            ' where '
                            ' container_id = %s'
                          )
            else:
                updateContainerSQL = ('update container set'
                            ' state_id = %s,'
                            ' stop_time = %s,'
                            ' build_time = %s,'
                            ' error_message = %s'
                            ' where '
                            ' container_id = %s'
                          )
                
            data = (state,
                    time,
                    build_time,
                    errMsg,
                    container.containerID)
            
# artifact:container_id, name, url, protocol
            print (updateContainerSQL % data)
            cursor = self.conn.cursor()
            cursor.execute(updateContainerSQL, data)
            self.conn.commit()
        except Exception as inst:
            print "Unrecoverable SQL Exception ... "
            traceback.print_exc()
            print (inst) 
            raise ValueError(inst) 
        finally:
            cursor.close()

    def updateArtifactState(self, state, artifact, time, fetch_time='', errorMsg=''):
        self.openConnection()
        cursor = None
        updateArtifactSQL = ''
        try:
            if state == self.STATE_RUNNING:
                updateArtifactSQL = ('update artifact set'
                            ' state_id = %s,'
                            ' start_time = %s,'
                            ' fetch_time = %s,'
                            ' error_message = %s'
                            ' where '
                            ' artifact_id = %s'
                          )
            else:
                updateArtifactSQL = ('update artifact set'
                            ' state_id = %s,'
                            ' stop_time = %s,'
                            ' fetch_time = %s,'
                            ' error_message = %s'
                            ' where '
                            ' artifact_id = %s'
                          )
                
            data = (state,
                    time,
                    fetch_time,
                    errorMsg,
                    artifact.artifact_id)
            
# artifact:container_id, name, url, protocol
            print (updateArtifactSQL % data)
            cursor = self.conn.cursor()
            cursor.execute(updateArtifactSQL, data)
            self.conn.commit()
        except Exception as inst:
            print "Unrecoverable SQL Exception ... "
            traceback.print_exc()
            print (inst) 
            raise ValueError(inst) 
        finally:
            cursor.close()
#         print ('buildid: ', buildid)
# end storeContainerData


    def __del__(self):
        try:
            self.conn.close()
        except Exception:
            pass
        