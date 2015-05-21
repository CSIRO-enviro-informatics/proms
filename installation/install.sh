#!/bin/bash

usage() {
    echo "Usage:"
    echo "      install <Linux_Distribution>"
    echo
    echo "Valid Linux distributions:"
    echo "      Ubuntu"
    echo "      CentOS"
}

DISTRIBUTION=0
if [ $# == 0 ]
then
    while [ $DISTRIBUTION == 0 ]
    do
        echo "Please choose Linux distribution (type 1 or 2):"
        echo "    1. Ubuntu"
        echo "    2. CentOS"
        read d
        if [ $d == "1" ]
        then
            DISTRIBUTION=1
        elif [ $d == "2" ]
        then
            DISTRIBUTION=2
        else
            echo "Invalid choice, please select 1 (Ubuntu) or 2 (CentOS)"
        fi
    done
elif [ $# == 1 ]
then
    dist_string=$(echo $1 | tr "[:upper:]" "[:lower:]")
    if [ $dist_string == "ubuntu" ]
    then
        DISTRIBUTION=1
    elif [ $dist_string == "centos" ]
    then
        DISTRIBUTION=2
    else
        usage
    fi
elif [ $# > 1 ]
then
    usage
    exit 2
fi


if [ $DISTRIBUTION == 1 ]
then
    echo "Installing PROMS for Ubuntu..."A
    sudo apt-get update
    which git || sudo aptitude install -y git
    which default-jre || sudo aptitude install -y default-jre
    ./Ubuntu/install-fuseki.sh
    ./Ubuntu/install-apache.sh
    ./Ubuntu/install-proms.sh
elif [ $DISTRIBUTION == 2 ]
then
    echo "Installing PROMS for CentOS..."
    sudo yum update
    which git || sudo yum install -y git
    which java || sudo yum install -y java
    ./CentOS/install-fuseki.sh
    ./CentOS/install-apache.sh
    ./CentOS/install-proms.sh
fi
