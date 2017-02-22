#!/bin/bash

INSTALL_DIR="`( pwd )`"

# installs Apache, mod_wsgi, sets a BASIC auth pwd
sudo yum install -y httpd
sudo yum install -y apache2-utils
sudo a2enmod wsgi
sudo a2enmod proxy
sudo a2enmod proxy_http
# used to secure the Fuseki update (write) endpoint
# Ensure this matches the SPARQL_AUTH_USR & SPARQL_AUTH_PWD in settings.py
sudo htpasswd -c /etc/httpd/htpasswd fusekiusr

# apply Apache config for WSGI & proxying
sudo rm /etc/httpd/sites-available/default.conf
sudo cp $INSTALL_DIR/apache-config.conf /etc/httpd/sites-available/default.conf

sudo service httpd restart
