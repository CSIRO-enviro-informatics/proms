#!/bin/bash
sudo yum install -y git
sudo mkdir -p /opt/proms
cd /opt/proms
git clone https://stash.csiro.au/scm/eis/proms.git .
sudo pip install flask
sudo pip install rdflib
#sudo easy_install SPARQLWrapper
# install watchdog to avoid issued with six.py requiring _winreg
sudo pip install watchdog
cat >/opt/proms/start.sh <<EOL
#!/bin/bash
sudo python app.py proms_server &
echo "PROMS Server Flask App running..."
EOL
sudo chmod u+wx start.sh
cat >/opt/proms/stop.sh <<EOL
#!/bin/bash
sudo kill \`ps aux | grep proms_server | grep -v "grep" | head -3 | awk '{print \$2}'\`
EOL
sudo chmod u+wx stop.sh
echo
echo "Please make you update the /opt/proms/settings.py file with the Fuseki password entered during installation"
echo "Then launch PROMS with:"
echo "    sudo /opt/proms/start.sh"
