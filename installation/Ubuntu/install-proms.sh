#!/bin/bash
sudo pip install flask
sudo pip install rdflib
sudo pip install rdflib-jsonld
# install watchdog to avoid issued with six.py requiring _winreg
sudo pip install watchdog
sudo chmod u+wx start.sh
sudo chmod u+wx stop.sh
echo
echo "Please make you update the /opt/proms/settings.py file with the Fuseki password entered during installation"
echo "Then launch PROMS with:"
echo "    sudo /opt/proms/start.sh"
