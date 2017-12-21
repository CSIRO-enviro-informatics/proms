#!/usr/bin/env bash
# install Apache
sudo apt install -y apache2
sudo apt install apache2-utils

# create an Apache user with password in order to simpleauth protect some services
sudo htpasswd -c /etc/apache2/.htpasswd fuseki

# enable Apache proxying to proxy to Fuseki (via Tomcat) on Port 80 in order to add in auth (rather than the native Tomcat Port 8080)
sudo a2enmod proxy proxy_http proxy_html

# enable Apache <--> Python3 interactions via mod_wsgi
sudo apt install libapache2-mod-wsgi-py3
sudo apt install python3-flask

# enable Git in order to clone in PROMS from its Git repo on CSIRO BitBucket
sudo apt install git

# test install the minimal Flask WMV app
mkdir /var/www/minimal
sudo chown -R ubuntu /var/www/minimal
cd /var/www/minimal
git clone https://github.com/nicholascar/minimal-flask-mvc.git .

# adjust the app.wsgi file to point to this dir
nano app.wsgi

# configure Apache to point to this app at /minimal
sudo nano /etc/apache2/sites-available/000-default.conf
# add in the settings from the example apache.conf in this repo

