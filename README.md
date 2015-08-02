## Silo: Docker artifact/file pre-fetching engine

**Current Version: 1.3.1**

**The basics ...**
Silo reads container.xml, downloads production/snapshot artifacts as well as static files before building the new Docker container
Snapshots are currently set to find the latest build, latest version of that build, then download the given file.
The latest version now supports selecting artifacts by 'classification' and 'extension' (neither element is required)

###Configuration ###

Python scripts can be run directly from the command using `python silo.py` ... needs updating to reflect pip and install instructions

### XSD Dictionary ###

** *outdated* **

*First pass will not have all the definitions due to time constraints*

```
 <container>
    <config>
        <application />
        <application_version fixed="" />
        <server>
            <repository />
            <production />
            <snapshot />
        </repository>
        <global>
            <overwrite enforce="" />
            <dir enforce="" />
            <production enforce="" />
        </global>
    </config>

    <artifacts>
        <artifact dir="" overwrite="" production="" target="" >
            <groupid />
            <artifactid />
            <repository />
            <server />
            <classifier />
            <extension />
        </artifact>
    </artifacts>

    <files
        <file dir="" overwrite="" target="" source="" />
    </files>
 </container>
```

###To run the example###
clone the project, enter the working directory and execute the following command:
`python silo.py`
This will download java 7_71, drop it into the container, build the container and exit

**Build output should be similar to the following**

```
[sgee@gee-5 silo]$ silo
Server: http://gee-5//artifactory/
Snapshot: libs-snapshot-local/
Production libs-release-local/
[True] Setting global overwrite to: True
[False] Setting global directory to:
[False] Setting global production repository to: False
********************* INITIATING ARTIFACT LOOKUP *********************
********************* INITIATING FILE LOOKUP *********************
--------------------------------------------
****** TARGET FOUND / NOT EMPTY ***********
URL: http://gee-5/artifactory/remote/oracle/jdk/7u71-linux/jdk-7u71-linux-x64.tar.gz
Output File: files/jdk.tar.gz
Overwrite: True
Initiating download ...
Using fixed application version: test
running process: docker build -t test:test .
Sending build context to Docker daemon 142.4 MB
Sending build context to Docker daemon
Step 0 : FROM centos:centos6
 ---> a005304e4e74
Step 1 : MAINTAINER gee-5
 ---> Using cache
 ---> ebee65e84e68
Step 2 : ADD files/jdk.tar.gz /opt
 ---> e1bd02a95718
Removing intermediate container dd79e301c636
Step 3 : ENV PATH /bin:/usr/bin:/sbin:/usr/sbin:/opt/jdk1.7.0_71/bin
 ---> Running in b32d3988452e
 ---> f40b764fbc72
Removing intermediate container b32d3988452e
Step 4 : ENV JAVA_HOME /opt/jdk1.7.0_71/
 ---> Running in a48068a45f9e
 ---> fb2d1fdb00c4
Removing intermediate container a48068a45f9e
Step 5 : ENV ENV_VAR_01 "variable_zero_one" ENV_VAR_02 "variable_zero_two"
 ---> Running in f8cca4c5e0c2
 ---> 54744185c2a4
Removing intermediate container f8cca4c5e0c2
Step 6 : CMD /bin/bash
 ---> Running in c4820f1213fa
 ---> d287092c6d6d
Removing intermediate container c4820f1213fa
Successfully built d287092c6d6d
```

Once the process completes, you should be able to check success by executing: `docker images`
You should see the test:test container, to run the container, execute `docker run -ti test:test /bin/bash`
once inside the container, check the java version and environment variables by executing the following

```
java -version
echo $ENV_VAR_01
echo $ENV_VAR_02
```

**Test output should be similar to the following**

```
[sgee@gee-5 silo]$ docker run -ti test:test /bin/bash
[root@d5819e7e5b05 /]# java -version
java version "1.7.0_71"
Java(TM) SE Runtime Environment (build 1.7.0_71-b14)
Java HotSpot(TM) 64-Bit Server VM (build 24.71-b01, mixed mode)
[root@d5819e7e5b05 /]# echo $ENV_VAR_01
variable_zero_one
[root@d5819e7e5b05 /]# echo $ENV_VAR_02
variable_zero_two
[root@d5819e7e5b05 /]# exit
exit
```

** Add setup build and pip instructions **

**Change Request:**
 
  * add the ability to purge/delete existing files (feature/closed)
  * add capability to remove files by file-type in the working directory (feature/closed)
  * ability to set a static version (feature/closed)
  * ability to skip the version, defaulting to 'latest' (feature/closed)
  * add the ability to select a different folder and/or file name (feature/closed)
  * add the ability to do recurse a folder (feature/closed)
  * have the ability to update the Dockerfile's #SILO_LABEL with the files and versions that are inside the container  (feature/open)
  * expand the Dockerfile update #SILO_LABEL feature to include the ability to attach the contents of a file  (feature/open)
  
