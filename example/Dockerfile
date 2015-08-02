FROM centos:centos6
MAINTAINER ssgeejr 

ADD files/jdk.tar.gz /opt
ENV PATH /bin:/usr/bin:/sbin:/usr/sbin:/opt/jdk1.7.0_71/bin
ENV JAVA_HOME /opt/jdk1.7.0_71/

ENV ENV_VAR_01="variable_zero_one"  ENV_VAR_02="variable_zero_two"
CMD ["/bin/bash"]
