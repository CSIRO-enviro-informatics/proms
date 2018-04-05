#!/bin/bash
# updated to Ubuntu 16.04

# basic server setup
sudo timedatectl set-timezone Australia/Brisbane
sudo apt update
sudo apt upgrade -y

# install Python packages
sudo apt install -y python3-pip
sudo pip3 install --upgrade pip
sudo pip3 install flask
sudo pip3 install rdflib
sudo pip3 install rdflib-jsonld
sudo pip3 install lxml
# install watchdog to avoid issued with six.py requiring _winreg
sudo pip3 install watchdog

# install Apache as per install-apache-apt.sh

# install Git
sudo apt install -y git

# clone PROMS code
sudo mkdir /var/www/proms
sudo chown -R ubuntu:ubuntu /var/www/proms
cd /var/www/proms
git clone https://bitbucket.csiro.au/scm/eis/proms.git .
git checkout eudm
