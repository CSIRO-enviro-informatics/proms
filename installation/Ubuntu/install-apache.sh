#!/bin/bash
sudo aptitude install -y apache2
sudo aptitude install -y apache2-utils
# Ensure this matches the secure user name and password in settings.py
sudo htpasswd -c /etc/apache2/htpasswd fusekiusr

cat >/etc/apache2/sites-available/proms.conf <<EOL
<VirtualHost *:80>
        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined

        ProxyRequests Off
        ProxyErrorOverride Off

        <Proxy *>
                Order deny,allow
                Allow from all
        </Proxy>

        # only the secure query endpoint is used
        ProxyPass   /fuseki/data/query   http://localhost:3030/data/query
        ProxyPassReverse   /fuseki/data/query   http://localhost:3030/data/query
        <Location /fuseki/data/query>
                AuthType Basic
                AuthName "Authentication Required"
                AuthUserFile "/etc/apache2/htpasswd"
                Require valid-user
                SetEnv proxy-chain-auth On
                Order allow,deny
                Allow from all
        </Location>

        # only the secure update endpoint is used
        ProxyPass   /fuseki/data/update   http://localhost:3030/data/update
        ProxyPassReverse   /fuseki/data/update   http://localhost:3030/data/update
        <Location /fuseki/data/update>
                AuthType Basic
                AuthName "Authentication Required"
                AuthUserFile "/etc/apache2/htpasswd"
                Require valid-user
                SetEnv proxy-chain-auth On
                Order allow,deny
                Allow from all
        </Location>

        ProxyPass   /   http://localhost:9000/
        ProxyPassReverse   /   http://localhost:9000/
</VirtualHost>
EOL

sudo a2enmod proxy
sudo a2enmod proxy_http
sudo service apache2 restart
