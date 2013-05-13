#!/bin/bash

if [ "$(whoami)" != "root" ]; then
	echo "Elixys server install require root priveleges"
	exit 1
fi

#Install Elixys Dependencies

apt-get update
export DEBIAN_FRONTEND=noninteractive
apt-get -q -y install python python-mysqldb python-mysql.connector \
		 python-configobj python-setuptools python-pip \
		 ipython ipython-notebook-common ipython-qtconsole
pip install rpyc
pip install twilio
apt-get -q -y install vim git-core binutils
apt-get -q -y install autojump
echo "source /usr/share/autojump/autojump.bash" >> .bashrc
apt-get -q -y install mysql-common mysql-server
apt-get -q -y install apache2 apache2-utils \
			libapache2-mod-wsgi apache2-threaded-dev 
			# \ apache2-prefork-dev

sudo apt-get -q -y install crtmpserver

export ADOBE_POL_PATH_SRC=/usr/local/src/mod_adobe_crossdomainpolicy
rm -Rf $ADOBE_POL_PATH_SRC
mkdir -p $ADOBE_POL_PATH_SRC
cd $ADOBE_POL_PATH_SRC
wget http://www.beamartyr.net/projects/mod_adobe_crossdomainpolicy.c
apxs2 -cia mod_adobe_crossdomainpolicy.c
cd

a2enmod adobe_crossdomainpolicy
a2enmod wsgi
a2enmod authn_dbd
a2enmod authz_host
a2enmod authz_user

