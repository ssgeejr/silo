


class Artifact(object):
    artifact_id  = -1
    container_id = -1
    protocol = ''
    url = ''
    group_id = ''
    server = ''
    repo = ''
    extension = ''
    classifier = ''
    build_number = ''
    file_detail = ''
    version = ''
    file_name = ''

    def __init__(self, _artifact_id,
                       _container_id,
                        _protocol,
                        _url,
                        _file_name,
                        _group_id='',
                        _server='',
                        _repo='',
                        _extension='',
                        _classifier='',
                        _build_number='',
                        _vesion='',
                        _file_detail=''):
        
        self.artifact_id = _artifact_id        #INT(11)
        self.container_id = _container_id      #INT(11)
        self.protocol = _protocol        #VARCHAR(8)
        self.url = _url        #VARCHAR(512)
        self.group_id = _group_id.strip("/").replace('/','.')        #VARCHAR(128)
        self.server = _server        #VARCHAR(128)
        self.repo = _repo        #VARCHAR(128)
        self.extension = _extension        #VARCHAR(64)
        self.classifier = _classifier        #VARCHAR(64)
        self.build_number = _build_number        #VARCHAR(64)
        self.file_detail = _file_detail        #VARCHAR(64)
        self.vesion = _vesion        #VARCHAR(64)
        self.file_name = _file_name        #VARCHAR(128)
        
    def setArtifactID(self, artID):
        self.artifact_id = artID
        
    def setContainerID(self, cID):
        self.container_id = cID
        
    def setID(self, artID, cID):
        self.artifact_id = artID
        self.container_id = cID


class Container(object):
    
    def addArtifact(self, artid, artob):
        self.artifacts.update({artid: artob})

    def getArtifact(self, name=''):
        if name:
            return self.artifacts.get(name)
        else:
            return self.artifacts

    def __init__(self, build_id, container_id, container_name,  args, working_dir, file_name):
        self.buildID = build_id
        self.containerID = container_id
        self.containerName = container_name
        self.arguments = args
        self.workingDir = working_dir
        self.fileName = file_name
        self.artifacts = {}


        
        
        
        
        
