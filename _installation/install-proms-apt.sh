#!/bin/bash
# install Git
sudo aptitude install -y git

# install Python packages
sudo aptitude install -y python-pip
sudo pip install flask
sudo pip install rdflib
sudo pip install rdflib-jsonld
# install watchdog to avoid issued with six.py requiring _winreg
sudo pip install watchdog

# clone PROMS code
mkdir /var/www/proms
cd /var/www/proms
git clone https://bitbucket.csiro.au/scm/eis/proms.git .
