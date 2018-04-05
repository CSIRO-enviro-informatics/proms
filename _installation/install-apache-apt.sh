#!/bin/bash

INSTALL_DIR="`( pwd )`"

# installs Apache, mod_wsgi, sets a BASIC auth pwd
sudo apt install -y apache2
sudo apt install -y apache2-utils
sudo apt install libapache2-mod-wsgi-py3
sudo a2enmod wsgi
sudo a2enmod proxy
sudo a2enmod proxy_http
# used to secure the Fuseki update (write) endpoint
# Ensure this matches the SPARQL_AUTH_USR & SPARQL_AUTH_PWD in settings.py
sudo htpasswd -c /etc/apache2/htpasswd fusekiusr

# apply Apache config for WSGI & proxying
sudo rm /etc/apache2/sites-available/000-default.conf
sudo cp $INSTALL_DIR/apache-config.conf /etc/apache2/sites-available/000-default.conf

sudo service apache2 restart
