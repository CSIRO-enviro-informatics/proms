#!/bin/bash
# downlaod Fuseki with Jena
echo "downloading..."
wget http://apache.mirror.serversaustralia.com.au/jena/binaries/apache-jena-fuseki-2.3.0.tar.gz -O fuseki.tar.gz
sudo cp fuseki.tar.gz /opt
cd /opt
sudo tar -xzf fuseki.tar.gz
echo "owning..."
sudo chown -R ubuntu:ubuntu fuseki.tar.gz
#sudo chown -R $SUDO_USER:$SUDO_USER jena-fuseki1-1.1.2
sudo mv fuseki.tar.gz fuseki
cd /opt/fuseki

# make scripts executable
echo "making scripts..."
chmod +x fuseki-server s-*
# create log file
touch fuseki.log

# make config file
cat >config-tdb-all.ttl <<EOL
@prefix :        <#> .
@prefix fuseki:  <http://jena.apache.org/fuseki#> .
@prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
@prefix tdb:     <http://jena.hpl.hp.com/2008/tdb#> .
@prefix ja:      <http://jena.hpl.hp.com/2005/11/Assembler#> .

[] rdf:type fuseki:Server ;
   fuseki:services (
     <#service_tdb_all>
   ) .

[] ja:loadClass "com.hp.hpl.jena.tdb.TDB" .
tdb:DatasetTDB  rdfs:subClassOf  ja:RDFDataset .
tdb:GraphTDB    rdfs:subClassOf  ja:Model .

<#service_tdb_all> rdf:type fuseki:Service ;
    rdfs:label                      "TDB Service (RW)" ;
    fuseki:name                     "data" ;
    fuseki:serviceQuery             "query" ;
    fuseki:serviceQuery             "sparql" ;
    fuseki:serviceUpdate            "update" ;
    fuseki:serviceUpload            "upload" ;
    fuseki:serviceReadWriteGraphStore      "data" ;
    # A separate read-only graph store endpoint:
    fuseki:serviceReadGraphStore       "get" ;
    fuseki:dataset           <#tdb_dataset_readwrite> ;
    .

<#tdb_dataset_readwrite> rdf:type      tdb:DatasetTDB ;
    tdb:location "DB2" ;
.
EOL

# create start and stop files
cat >start.sh <<EOL
./fuseki-server --config=config-tdb-all.ttl > fuseki.log &
EOL
sudo chmod u+x start.sh

cat >stop.sh <<EOL
echo "kill -9 \`ps aux | grep fuseki | grep -v grep | awk '{print \$2}'\`" > stop.sh
EOL
sudo chmod u+x stop.sh

# set enviro vars
echo "setting enviro vars..."
export PATH=$PATH:/opt/fuseki
export FUSEKI_HOME=/opt/fuseki

# start Fuseki
echo "starting..."
sudo ./start.sh
