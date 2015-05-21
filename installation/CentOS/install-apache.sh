#!/bin/bash
sudo mkdir /var/log/httpd/proms
sudo yum install -y httpd
#sudo yum install -y apache2-utils
sudo htpasswd -c /etc/httpd/htpasswd fusekiusr

cat >/etc/httpd/conf.d/proms.conf <<EOL
<VirtualHost *:80>
        ErrorLog /var/log/httpd/proms/error.log
        CustomLog /var/log/httpd/proms/access.log combined

        ProxyRequests Off
        ProxyErrorOverride Off

        <Proxy *>
                Order deny,allow
                Allow from all
        </Proxy>

        ProxyPass   /fuseki/data/query   http://localhost:3030/data/query
        ProxyPassReverse   /fuseki/data/query   http://localhost:3030/data/query

        <Location /fuseki/data/query>
                AuthType Basic
                AuthName "Authentication Required"
                AuthUserFile "/etc/httpd/htpasswd"
                Require valid-user
                #AuthBasicAuthoritative Off
                SetEnv proxy-chain-auth On
                Order allow,deny
                Allow from all
        </Location>

        ProxyPass   /fuseki/data/update   http://localhost:3030/data/update
        ProxyPassReverse   /fuseki/data/update   http://localhost:3030/data/update

        <Location /fuseki/data/update>
                AuthType Basic
                AuthName "Authentication Required"
                AuthUserFile "/etc/httpd/htpasswd"
                Require valid-user
                #AuthBasicAuthoritative Off
                SetEnv proxy-chain-auth On
                Order allow,deny
                Allow from all
        </Location>

        ProxyPass   /fusekitest   http://localhost:3030/
        ProxyPassReverse   /fusekitest   http://localhost:3030/

        ProxyPass   /   http://localhost:9000/
        ProxyPassReverse   /   http://localhost:9000/
</VirtualHost>
EOL

sudo a2enmod proxy
sudo a2enmod proxy_http
sudo service httpd restart
