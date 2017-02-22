#!/bin/bash

INSTALL_DIR="`( pwd )`"

# download Fuseki with Jena
# NOTE: update the Fuseki version number in file name to latest
wget http://apache.mirror.serversaustralia.com.au/jena/binaries/apache-jena-fuseki-2.5.0.tar.gz -O fuseki.tar.gz
sudo mkdir -p /opt/fuseki
sudo tar -C /opt/fuseki -xzf fuseki.tar.gz --strip 1
sudo rm fuseki.tar.gz
sudo chown -R ubuntu:ubuntu /opt/fuseki


# make scripts executable
chmod +x fuseki-server
# create log file
touch fuseki.log

# copy the config file to this installation's run/ dir
cp $INSTALL_DIR/fuseki-config.ttl run/

# create start and stop files
cat >start.sh <<EOL
./fuseki-server --config=fuseki-config.ttl > fuseki.log &
EOL
sudo chmod u+x start.sh

cat >stop.sh <<EOL
echo "kill -9 \`ps aux | grep fuseki | grep -v grep | awk '{print \$2}'\`" > stop.sh
EOL
sudo chmod u+x stop.sh

# set enviro vars
export PATH=$PATH:/opt/fuseki
export FUSEKI_HOME=/opt/fuseki

# start Fuseki
sudo ./start.sh


#
#   NOTE: remote admin
#
# In order to enable full use of the web UI from locations other than localhost, edit the settings in run/shiro.ini, as
# per the instructions given in that file.
