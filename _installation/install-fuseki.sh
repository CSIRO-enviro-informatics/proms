#!/bin/bash

# this installs Fuseki as a normal Tomcat web application on Debian-like systems (e.g. Ubuntu)

# install Tomcat 8
sudo apt install -y tomcat8 tomcat8-admin
# restruct access to Tomcat admin
sudo nano /var/lib/tomcat8/conf/tomcat-users.xml
# add in         <user username="admin" password="{TOMCAT_ADMIN_PWD}" roles="manager-gui,admin-gui"/>


# download Fuseki with Jena
# NOTE: update the Fuseki version number in file name to latest
wget http://apache.mirror.serversaustralia.com.au/jena/binaries/apache-jena-fuseki-3.5.0.tar.gz -O fuseki.tar.gz
# load the Fuseki WAR into Tomcat
tar -xzf apache-jena-fuseki-3.5.0.tar.gz
sudo cp apache-jena-fuseki-3.5.0/fuseki.war /var/lib/tomcat8/webapps/

# create the Fuseki data dir
sudo mkdir /etc/fuseki
sudo chown tomcat8 /etc/fuseki/

# start the Fuseki webapp in Tomcat manager http://{IP-ADDRESS}/manager/html/
# all config for Fuseki is now in /etc/fuseki/
# visit Fuseki web UI: http://{IP-ADDRESS}/fuseki/


# set up auth for Fuseki HTML admin
# edit /etc/fuseki/shiro.ini as per instructions in file. pwd {FUSEKI_WEB_ADMIN_PWD}
